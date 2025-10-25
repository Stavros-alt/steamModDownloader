# Skymods Harvester: A Universal Steam Workshop Downloader

A Python script to automate the downloading of mods and collections from Skymods for any supported game, designed for players with non-Steam versions.

This tool uses Selenium to control a headless Firefox browser, methodically navigating the multi-page download process and handling interruptions like pop-ups and cookie banners automatically.

## What it Does
- Reads a simple text file of Steam Workshop IDs for **any game**.
- For each ID, it constructs the correct Skymods URL using your specified **App ID**.
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

You must provide the game's **App ID** when running the script. You can find any game's App ID using sites like [SteamDB](https://steamdb.info/).

### Example: Downloading a Hearts of Iron IV Mod Collection

1.  **Find the App ID:** Search for "Hearts of Iron IV" on SteamDB. The App ID is **394360**.

2.  **Get the Mod IDs:** Go to a Workshop collection (like the "Road to 56" collection you found). Use a tool like [steamworkshopdownloader.io](https://steamworkshopdownloader.io/) to paste the collection URL. It will generate `workshop_download_item` commands for all mods. Copy just the final number (the Workshop ID) for each mod into your `hoi4_mods.txt` file.

3.  **Run the script:**
    ```bash
    python mod_harvester.py --app_id "394360" --profile "/home/stavros/.mozilla/firefox/xxxxxxxx.SeleniumBot" --file "hoi4_mods.txt" --output "HOI4_Mods"
    ```

### Platform Disclaimer
This script was developed and tested on **Linux (Nobara/Fedora)**. It is provided as-is and has not been tested on Windows or macOS. Community contributions and forks to improve cross-platform compatibility are welcome.

### License
This project is licensed under the MIT License.