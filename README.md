# Skymods Harvester: A Universal Steam Workshop Downloader

A Python script to automate the downloading of mods and collections from Skymods for any supported game, designed for players with non-Steam versions.

This tool uses Selenium to control a headless Firefox browser, methodically navigating the multi-page download process and handling interruptions like pop-ups and cookie banners automatically.

## What it Does
- Reads a simple text file of Steam Workshop IDs for **any game**.
- Constructs the correct Skymods URL using your specified **Base URL Template**.
- Navigates the redirect chain, handles cookie banners, and closes ad tabs.
- Waits for timers and clicks the download links, saving all files to an organized folder.

## Prerequisites
- [Python 3](https://www.python.org/) (and `pip` for installing packages)
- [Mozilla Firefox](https://www.mozilla.org/en-US/firefox/new/)

## Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Stavros-alt/steamModDownloader.git
    cd steamModDownloader
    ```

2.  **Install Python dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **(Highly Recommended) Create a Firefox Profile with an Ad-blocker:**
    This is essential for the script to run smoothly.
    -   Run `firefox -P` in your terminal to open the Profile Manager.
    -   Create a new profile (e.g., "SeleniumBot").
    -   Launch Firefox with that profile: `firefox -P SeleniumBot`.
    -   Install **uBlock Origin** from the Firefox Add-ons store.
    -   Close Firefox and find the full path to this profile (e.g., `/home/user/.mozilla/firefox/xxxxxxxx.SeleniumBot`).

4.  **Create your Mod ID list file:**
    -   Create a file (e.g., `hoi4_mods.txt`).
    -   Paste the Steam Workshop IDs of the mods you want to download, one ID per line.

## How to Use

This script is a universal tool. You must provide the **App ID** for the game and the **Base URL Template** for the specific Skymods site you are targeting.

### Step 1: Find the App ID and Base URL

1.  **Find the App ID:** Use a site like [SteamDB](https://steamdb.info/) to find the numeric App ID for your game (e.g., CK3 is `1158310`, HOI4 is `394360`).
2.  **Find the Base URL:** Go to Skymods and find the page for your game. Look at the URL structure. Your template must include `{mod_id}` as a placeholder for the workshop ID.

    *   **CK3:** `https://catalogue.smods.ru/?s={mod_id}&app={app_id}`
    *   **HOI4:** `https://hearts-of-iron-4.smods.ru/?s={mod_id}`
    *   **Cities: Skylines:** `https://smods.ru/?s={mod_id}`

### Step 2: Run the Script

Provide the arguments in your terminal.

**Example for Hearts of Iron IV:**
```bash
python mod_harvester.py --base_url "https://hearts-of-iron-4.smods.ru/?s={mod_id}" --app_id "394360" --profile "/path/to/your/profile" --file "hoi4_mods.txt"
```

### Platform Disclaimer
This script was developed and tested on **Linux (Nobara/Fedora)**. It is provided as-is and has not been tested on Windows or macOS. Community contributions and forks to improve cross-platform compatibility are welcome.

### License
This project is licensed under the MIT License.