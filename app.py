import os
import base64
import requests
import urllib3
import json
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__, static_folder='.')
CORS(app)

DB_FILE = 'database.json'

class ValorantAPI:
    def __init__(self):
        self.lockfile_path = os.path.join(os.getenv('LOCALAPPDATA'), r"Riot Games\Riot Client\Config\lockfile")
        self.db = self.load_db()
        self.agents_map = {}
        self.weapons_map = {}
        self.load_static_data()

    def load_db(self):
        if os.path.exists(DB_FILE):
            try:
                with open(DB_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {
            "processed_matches": [],
            "matches": {},
            "agents": {},
            "skins": {},
            "locked_loadouts": {}
        }

    def save_db(self):
        with open(DB_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.db, f, ensure_ascii=False, indent=2)

    def load_static_data(self):
        # Fetch Agents
        try:
            res = requests.get("https://valorant-api.com/v1/agents?isPlayableCharacter=true")
            if res.status_code == 200:
                for agent in res.json().get('data', []):
                    self.agents_map[agent['uuid'].lower()] = {
                        "name": agent['displayName'],
                        "icon": agent['displayIconSmall']
                    }
        except Exception as e:
            print("Failed to load agents:", e)

        # Fetch Version
        self.riot_version = "release-09.00-shipping-1-2345678"
        try:
            res = requests.get("https://valorant-api.com/v1/version")
            if res.status_code == 200:
                self.riot_version = res.json()['data']['riotClientVersion']
        except Exception as e:
            print("Failed to load version:", e)

        # Fetch Weapons
        try:
            res = requests.get("https://valorant-api.com/v1/weapons")
            if res.status_code == 200:
                for w in res.json().get('data', []):
                    cat = w.get('category', '').split('::')[-1]
                    self.weapons_map[w['uuid'].lower()] = {
                        "name": w['displayName'],
                        "category": cat,
                        "icon": w['displayIcon'],
                        "skins": {skin['uuid'].lower(): {"name": skin['displayName'], "icon": skin.get('displayIcon') or (skin['levels'][0]['displayIcon'] if skin.get('levels') else '')} for skin in w.get('skins', [])}
                    }
        except Exception as e:
            print("Failed to load weapons:", e)

    def get_shard(self, region):
        region = region.lower()
        if region in ['latam', 'br']: return 'na'
        elif 'eu' in region: return 'eu'
        elif 'ap' in region: return 'ap'
        elif 'kr' in region: return 'kr'
        return region

    def get_data(self):
        try:
            if not os.path.exists(self.lockfile_path):
                return {"error": "Valorant n'est pas lancé (lockfile introuvable)."}

            with open(self.lockfile_path, 'r') as f:
                content = f.read().strip()
            
            parts = content.split(':')
            if len(parts) < 5: return {"error": "Format du lockfile invalide."}
            
            port, password, protocol = parts[2], parts[3], parts[4]
            auth = base64.b64encode(f"riot:{password}".encode()).decode()
            headers = {"Authorization": f"Basic {auth}"}
            base_url = f"{protocol}://127.0.0.1:{port}"
            
            # 1. Tokens
            ent_res = requests.get(f"{base_url}/entitlements/v1/token", headers=headers, verify=False)
            if ent_res.status_code != 200:
                return {"error": "Impossible de s'authentifier à l'API locale. Lancez le jeu."}
            
            ent_data = ent_res.json()
            access_token = ent_data.get('accessToken')
            entitlements_token = ent_data.get('token')
            puuid = ent_data.get('subject')
            if not puuid or not access_token: return {"error": "Tokens introuvables."}

            # 2. Region
            region_res = requests.get(f"{base_url}/riotclient/region-locale", headers=headers, verify=False)
            region = region_res.json().get('region', 'eu') if region_res.status_code == 200 else "eu"
            shard = self.get_shard(region)

            pd_headers = {
                "Authorization": f"Bearer {access_token}",
                "X-Riot-Entitlements-JWT": entitlements_token,
                "X-Riot-ClientVersion": self.riot_version,
                "X-Riot-ClientPlatform": "ew0KCSJwbGF0Zm9ybVR5cGUiOiAiUEMiLA0KCSJwbGF0Zm9ybU9TIjogIldpbmRvd3MiLA0KCSJwbGF0Zm9ybU9TVmVyc2lvbiI6ICIxMC4wLjE5MDQyLjEuMjU2LjY0Yml0IiwNCgkicGxhdGZvcm1DaGlwc2V0IjogIkludGVsIg0KfQ=="
            }

            # 3. Loadout actuel
            pd_url = f"https://pd.{shard}.a.pvp.net/personalization/v2/players/{puuid}/playerloadout"
            loadout_res = requests.get(pd_url, headers=pd_headers)
            current_equipped = {} # weapon_id -> skin_id
            user_level = 0
            if loadout_res.status_code == 200:
                l_data = loadout_res.json()
                user_level = l_data.get('Identity', {}).get('AccountLevel', 0)
                for gun in l_data.get('Guns', []):
                    current_equipped[gun['ID'].lower()] = gun['SkinID'].lower()
            
            # 3.2 User Profile & Names (GET Only via Local Chat API)
            user_profile = {"level": user_level, "rank": 0, "name": "Joueur"}
            names_dict = {}
            try:
                local_url = f"{protocol}://127.0.0.1:{port}"
                local_headers = {"Authorization": f"Basic {auth}"}
                pres_res = requests.get(f"{local_url}/chat/v4/presences", headers=local_headers, verify=False)
                if pres_res.status_code == 200:
                    for p in pres_res.json().get("presences", []):
                        pid = p.get("puuid")
                        if pid:
                            names_dict[pid] = f"{p.get('game_name', 'Joueur')}#{p.get('game_tag', '')}"
                
                user_profile["name"] = names_dict.get(puuid, "Moi")
                
                mmr_res = requests.get(f"https://pd.{shard}.a.pvp.net/mmr/v1/players/{puuid}/competitiveupdates?queue=competitive&startIndex=0&endIndex=1", headers=pd_headers)
                if mmr_res.status_code == 200:
                    m_data = mmr_res.json().get("Matches", [])
                    if m_data: user_profile["rank"] = m_data[0].get("TierAfterUpdate", 0)
            except:
                pass

            # 3.5 Détection de partie en cours (Live Tracking & WAIUA)
            if "locked_loadouts" not in self.db:
                self.db["locked_loadouts"] = {}
            
            is_in_game = False
            active_match_id = None
            match_state = ""
            
            glz_headers = pd_headers.copy()
            pregame_res = requests.get(f"https://glz-{shard}-1.{shard}.a.pvp.net/pregame/v1/players/{puuid}", headers=glz_headers)
            if pregame_res.status_code == 200:
                active_match_id = pregame_res.json().get("MatchID")
                is_in_game = True
                match_state = "pregame"
            else:
                coregame_res = requests.get(f"https://glz-{shard}-1.{shard}.a.pvp.net/core-game/v1/players/{puuid}", headers=glz_headers)
                if coregame_res.status_code == 200:
                    active_match_id = coregame_res.json().get("MatchID")
                    is_in_game = True
                    match_state = "coregame"
            
            if active_match_id and active_match_id not in self.db["locked_loadouts"]:
                self.db["locked_loadouts"][active_match_id] = current_equipped
                self.save_db()

            # Live Match Caching
            live_match_data = None
            if active_match_id:
                if not hasattr(self, 'live_cache') or self.live_cache.get("match_id") != active_match_id:
                    self.live_cache = {"match_id": active_match_id, "state": match_state, "players": []}
                    endpoint = "core-game" if match_state == "coregame" else "pregame"
                    
                    # Fetch Match Details
                    m_res = requests.get(f"https://glz-{shard}-1.{shard}.a.pvp.net/{endpoint}/v1/matches/{active_match_id}", headers=glz_headers)
                    
                    # Fetch Live Loadouts
                    l_res = requests.get(f"https://glz-{shard}-1.{shard}.a.pvp.net/{endpoint}/v1/matches/{active_match_id}/loadouts", headers=glz_headers)
                    live_loadouts = []
                    if l_res.status_code == 200:
                        live_loadouts = l_res.json().get("Loadouts", [])
                    
                    if m_res.status_code == 200:
                        players_data = m_res.json().get("Players", [])
                        if match_state == "pregame":
                            if "AllyTeam" in m_res.json():
                                players_data = m_res.json()["AllyTeam"].get("Players", [])
                            if "EnemyTeam" in m_res.json() and m_res.json()["EnemyTeam"]:
                                players_data.extend(m_res.json()["EnemyTeam"].get("Players", []))
                        
                        for p in players_data:
                            pid = p["Subject"]
                            ident = p.get("PlayerIdentity", {})
                            incognito = ident.get("Incognito", False)
                            level = ident.get("AccountLevel", 0)
                            char_id = p.get("CharacterID", "")
                            team_id = p.get("TeamID", "")
                            
                            p_name = names_dict.get(pid, "Joueur")
                            if incognito and pid != puuid:
                                p_name = "Anonyme"
                                
                            rank_id = 0
                            try:
                                r_res = requests.get(f"https://pd.{shard}.a.pvp.net/mmr/v1/players/{pid}/competitiveupdates?queue=competitive&startIndex=0&endIndex=1", headers=pd_headers)
                                if r_res.status_code == 200 and r_res.json().get("Matches"):
                                    rank_id = r_res.json()["Matches"][0].get("TierAfterUpdate", 0)
                            except:
                                pass
                                
                            # Match loadout
                            player_loadout = {}
                            for ld in live_loadouts:
                                if ld.get("CharacterID") == char_id or ld.get("Subject") == pid:
                                    player_loadout = ld.get("Loadout", {})
                                    break
                                
                            self.live_cache["players"].append({
                                "puuid": pid,
                                "name": p_name,
                                "level": level,
                                "character": char_id.lower() if char_id else "",
                                "team": team_id,
                                "rank_id": rank_id,
                                "is_me": pid == puuid,
                                "loadout": player_loadout
                            })
                live_match_data = self.live_cache
            else:
                self.live_cache = {}

            # 4. Match History
            history_url = f"https://pd.{shard}.a.pvp.net/match-history/v1/history/{puuid}?startIndex=0&endIndex=15"
            history_res = requests.get(history_url, headers=pd_headers)
            
            if history_res.status_code == 200:
                history = history_res.json()
                match_ids = [m['MatchID'] for m in history.get('History', [])]
                
                new_data = False
                for match_id in match_ids:
                    if match_id in self.db["processed_matches"]:
                        continue # Déjà traité

                    # On fetch les détails
                    m_res = requests.get(f"https://pd.{shard}.a.pvp.net/match-details/v1/matches/{match_id}", headers=pd_headers)
                    if m_res.status_code != 200: continue
                    
                    m_data = m_res.json()
                    
                    # Ignorer deathmatch (optionnel, mais mieux pour les vraies stats)
                    queue_id = m_data.get('matchInfo', {}).get('queueID', 'unrated')
                    if queue_id in ['deathmatch', 'ggteam']:
                        self.db["processed_matches"].append(match_id)
                        new_data = True
                        continue

                    players = m_data.get('players', [])
                    my_player = next((p for p in players if p.get('subject', '').lower() == puuid.lower()), None)
                    if not my_player: continue

                    agent_id = my_player.get('characterId', '').lower()
                    team_id = my_player.get('teamId')
                    my_team = next((t for t in m_data.get('teams', []) if t.get('teamId') == team_id), None)
                    won = my_team.get('won', False) if my_team else False
                    
                    stats = my_player.get('stats', {})
                    kills = stats.get('kills', 0)
                    deaths = stats.get('deaths', 0)
                    assists = stats.get('assists', 0)

                    # Analyser les Rounds pour HS% et Kills par Arme
                    match_hs = 0
                    match_total_hits = 0
                    weapon_kills = {} # weapon_id -> count
                    
                    for rd in m_data.get('roundResults', []):
                        for ps in rd.get('playerStats', []):
                            if ps.get('subject', '').lower() == puuid.lower():
                                # Dégâts pour HS
                                for d in ps.get('damage', []):
                                    match_hs += d.get('headshots', 0)
                                    match_total_hits += (d.get('headshots', 0) + d.get('bodyshots', 0) + d.get('legshots', 0))
                                
                                # Kills pour les armes
                                for k in ps.get('kills', []):
                                    wpn_id = k.get('finishingDamage', {}).get('damageItem', '').lower()
                                    if wpn_id in self.weapons_map: # C'est bien une arme (pas le spike/fall)
                                        weapon_kills[wpn_id] = weapon_kills.get(wpn_id, 0) + 1

                    hs_percent = int((match_hs / match_total_hits * 100)) if match_total_hits > 0 else 0

                    # Best weapons par catégorie
                    best_weapons_cat = {}
                    for wpn_id, k_count in weapon_kills.items():
                        cat = self.weapons_map[wpn_id]['category']
                        if cat not in best_weapons_cat or k_count > best_weapons_cat[cat]['count']:
                            best_weapons_cat[cat] = {"id": wpn_id, "count": k_count}

                    # Enregistrer Match
                    self.db["matches"][match_id] = {
                        "queue": queue_id,
                        "agent": agent_id,
                        "won": won,
                        "kills": kills,
                        "deaths": deaths,
                        "assists": assists,
                        "hs_percent": hs_percent,
                        "best_weapons": {cat: v["id"] for cat, v in best_weapons_cat.items()}
                    }

                    # Enregistrer Agent Stats
                    if agent_id not in self.db["agents"]:
                        self.db["agents"][agent_id] = {"queues": {}}
                    if queue_id not in self.db["agents"][agent_id]["queues"]:
                        self.db["agents"][agent_id]["queues"][queue_id] = {"matches": 0, "wins": 0, "kills": 0, "deaths": 0}
                    
                    self.db["agents"][agent_id]["queues"][queue_id]["matches"] += 1
                    if won: self.db["agents"][agent_id]["queues"][queue_id]["wins"] += 1
                    self.db["agents"][agent_id]["queues"][queue_id]["kills"] += kills
                    self.db["agents"][agent_id]["queues"][queue_id]["deaths"] += deaths

                    # Déterminer quel loadout utiliser (Live Tracking prioritaire)
                    equipped_for_match = self.db.get("locked_loadouts", {}).get(match_id, current_equipped)

                    # Enregistrer Skins Stats
                    for wpn_id, k_count in weapon_kills.items():
                        if wpn_id in equipped_for_match:
                            skin_id = equipped_for_match[wpn_id]
                            if wpn_id not in self.db["skins"]: self.db["skins"][wpn_id] = {}
                            if skin_id not in self.db["skins"][wpn_id]: self.db["skins"][wpn_id][skin_id] = {"queues": {}}
                            if queue_id not in self.db["skins"][wpn_id][skin_id]["queues"]:
                                self.db["skins"][wpn_id][skin_id]["queues"][queue_id] = {"kills": 0, "matches": 0}
                            
                            self.db["skins"][wpn_id][skin_id]["queues"][queue_id]["kills"] += k_count
                            self.db["skins"][wpn_id][skin_id]["queues"][queue_id]["matches"] += 1 
                    
                    self.db["processed_matches"].append(match_id)
                    new_data = True

                if new_data:
                    self.save_db()

            # Préparer la réponse riche
            response_data = {
                "success": True,
                "agents": self.agents_map,
                "weapons": self.weapons_map,
                "db": self.db,
                "current_loadout": current_equipped,
                "is_in_game": is_in_game,
                "user_profile": user_profile,
                "live_match": live_match_data
            }
            return response_data

        except Exception as e:
            import traceback
            traceback.print_exc()
            return {"error": f"Erreur interne : {str(e)}"}

valorant_api = ValorantAPI()

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/api/scan')
def api_scan():
    return jsonify(valorant_api.get_data())

if __name__ == '__main__':
    print("Démarrage du Valorant Tracker sur http://127.0.0.1:5000")
    app.run(port=5000, debug=True, use_reloader=False)
