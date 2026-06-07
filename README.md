<div align="center">
  <img src="https://media.valorant-api.com/weapons/9c82e19d-4575-0200-1a81-3eacf00cf872/displayicon.png" width="300" alt="Vandal" />
  <h1>🎯 Tung Tung Tracker</h1>
  <p><strong>L'outil ultime d'analyse de skins et de Live Tracking pour Valorant, conçu pour les passionnés.</strong></p>
  <p>
    <img src="https://img.shields.io/badge/API-100%25%20GET-brightgreen" alt="100% GET" />
    <img src="https://img.shields.io/badge/Ban%20Risk-0%25-blue" alt="Zero Ban Risk" />
    <img src="https://img.shields.io/badge/Python-3.10+-yellow" alt="Python" />
  </p>
</div>

<br>
## 🌟 Présentation

**Tung Tung Tracker** va au-delà des trackers classiques. Son concept original ? **Lier vos performances à vos skins.** Vous vous demandez si vous êtes vraiment plus fort avec votre Kuronami Vandal ou votre Prime ? Cet outil vous le dira.

Grâce à son système avancé exploitant l'API locale (Lockfile) de Valorant, l'application fonctionne entièrement en tâche de fond pour garantir un respect strict de l'anonymat et des conditions de Riot Games.

## 🚀 Fonctionnalités Clés

- 🕵️ **Live Match Tracker (WAIUA intégré)** : Dès qu'une partie se lance, le tracker révèle les alliés et les adversaires avec leurs agents, rangs, niveaux, et même les **skins exacts équipés** par chacun (Vandal, Phantom et Couteau).
- 🔫 **Casier d'Armes Intelligent** : Classe vos skins d'armes selon vos statistiques et détermine le Top 3 des skins avec lesquels vous êtes le plus performant.
- 🛡️ **Zéro Risque (100% Lecture Seule)** : Le code source a été certifié pour n'utiliser **que des requêtes GET locales**. Aucune donnée n'est altérée, envoyée ou modifiée. L'outil respecte le mode "Streamer/Anonyme" de vos adversaires.
- 📊 **Dashboard Complet** : Profil dynamique avec votre rang (icônes HD) et statistiques de la session (HS%, K/D, Winrate).
- 🔄 **Auto-Sync 60s** : Le client vérifie automatiquement vos parties toutes les minutes et capture votre équipement instantanément.

## 🛠️ Stack Technique

- **Backend** : Python 3.10+ (Flask, Requests)
- **Frontend** : Vanilla JavaScript, HTML5, TailwindCSS (Styling)
- **APIs** : Riot Local Client (Lockfile LCU), Valorant-API.com
- **Base de Données** : JSON Local (`database.json`)

## 💻 Installation & Utilisation

1. Assurez-vous d'avoir [Python 3](https://www.python.org/downloads/) installé.
2. Clonez ce dépôt sur votre machine :
   ```bash
   git clone https://github.com/votre-nom/tung-tung-valo-ritual.git
   ```
3. Installez les dépendances :
   ```bash
   pip install flask flask-cors requests
   ```
4. **Lancez Valorant** (L'application a besoin du jeu ouvert pour lire le *lockfile* local).
5. Lancez l'application :
   ```bash
   python app.py
   ```
6. Ouvrez le tableau de bord à l'adresse `http://127.0.0.1:5000`.

## ⚠️ Avertissement & Conformité (Riot ToS)

Ce projet est conçu comme un projet pédagogique et personnel. Il adhère au principe de **"Lecture Seule" (Strict GET API)** et ne manipule en aucun cas la mémoire vive du jeu (`Valorant.exe`). Il s'appuie sur des appels API non-officiels (LCU / GLZ) mais largement documentés.

Tant que le code n'est pas modifié pour exécuter des actions POST/PUT (comme automatiser l'Agent Select ou changer des skins en direct), il est techniquement aligné sur le comportement autorisé d'outils comme *WAIUA* ou *Tracker.gg*. **Utilisez ce code à vos propres risques.**

<div align="center">
  <br>
  <i>Développé avec ❤️ pour la communauté Valorant.</i>
</div>
