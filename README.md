<div align="center">
  <img src="https://media.valorant-api.com/weapons/9c82e19d-4575-0200-1a81-3eacf00cf872/displayicon.png" width="300" alt="Vandal" />
  <h1>🎯 Tung Tung Tracker</h1>
  <p><strong>The ultimate skin analysis and Live Tracking tool for Valorant, designed for enthusiasts.</strong></p>
  <p>
    <img src="https://img.shields.io/badge/API-100%25%20GET-brightgreen" alt="100% GET" />
    <img src="https://img.shields.io/badge/Ban%20Risk-0%25-blue" alt="Zero Ban Risk" />
    <img src="https://img.shields.io/badge/Python-3.10+-yellow" alt="Python" />
  </p>
</div>

<br>

## 🌟 Overview

**Tung Tung Tracker** goes beyond classic trackers. Its original concept? **Linking your performance to your skins.** Wondering if you're really better with your Kuronami Vandal or your Prime? This tool will tell you.

Thanks to its advanced system leveraging Valorant's local API (Lockfile), the application runs entirely in the background to ensure strict compliance with anonymity and Riot Games' terms of service.

## 🚀 Key Features

- 🕵️ **Live Match Tracker (Built-in WAIUA)**: As soon as a game starts, the tracker reveals allies and opponents with their agents, ranks, levels, and even the **exact skins equipped** by everyone (Vandal, Phantom, and Knife).
- 🔫 **Smart Weapon Locker**: Ranks your weapon skins according to your statistics and determines the Top 3 skins you perform best with.
- 🛡️ **Zero Risk (100% Read-Only)**: The source code has been certified to use **only local GET requests**. No data is altered, sent, or modified. The tool respects the "Streamer/Anonymous" mode of your opponents.
- 📊 **Comprehensive Dashboard**: Dynamic profile with your rank (HD icons) and session statistics (HS%, K/D, Winrate).
- 🔄 **60s Auto-Sync**: The client automatically checks your games every minute and captures your loadout instantly.

## 🛠️ Tech Stack

- **Backend**: Python 3.10+ (Flask, Requests)
- **Frontend**: Vanilla JavaScript, HTML5, TailwindCSS (Styling)
- **APIs**: Riot Local Client (Lockfile LCU), Valorant-API.com
- **Database**: Local JSON (`database.json`)

## 💻 Installation & Usage

1. Make sure you have [Python 3](https://www.python.org/downloads/) installed.
2. Clone this repository to your machine:
   ```bash
   git clone https://github.com/your-name/tung-tung-valo-ritual.git
   ```
3. Install dependencies:
   ```bash
   pip install flask flask-cors requests
   ```
4. **Launch Valorant** (The app needs the game open to read the local *lockfile*).
5. Start the application:
   ```bash
   python app.py
   ```
6. Open the dashboard at `http://127.0.0.1:5000`.

## ⚠️ Warning & Compliance (Riot ToS)

This project is designed as an educational and personal project. It adheres to the **"Read-Only" (Strict GET API)** principle and does not manipulate the game's RAM (`Valorant.exe`) in any way. It relies on unofficial (LCU / GLZ) but widely documented API calls.

As long as the code is not modified to execute POST/PUT actions (like automating Agent Select or changing skins live), it is technically aligned with the authorized behavior of tools like *WAIUA* or *Tracker.gg*. **Use this code at your own risk.**

<div align="center">
  <br>
  <i>Developed with ❤️ for the Valorant community.</i>
</div>
