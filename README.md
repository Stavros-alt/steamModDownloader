# CK3 Skymods Harvester

A Python script to automate the downloading of Crusader Kings 3 mods from Skymods, designed for non-Steam users.

This script uses Selenium to control a headless Firefox browser, navigating through the multi-page download process and handling cookie banners automatically.

## Features
- Automates downloading of multiple mods from a simple text file list.
- Uses a dedicated Firefox profile to leverage ad-blockers (like uBlock Origin) for a smoother process.
- Runs in headless mode for clean, background operation.
- Creates a dedicated folder for all your downloads.

## Prerequisites
- [Python 3](https://www.python.org/)
- [Mozilla Firefox](https://www.mozilla.org/en-US/firefox/new/)

## Setup
1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Stavros-alt/your-repo-name.git
    cd your-repo-name
    ```
2.  **Install Python dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
3.  **(Highly Recommended) Create a dedicated Firefox Profile for ad-blocking:**
    -   Close Firefox, then run `firefox -P` in your terminal.
    -   Create a new profile (e.g., "SeleniumBot").
    -   Launch Firefox with that profile (`firefox -P SeleniumBot`).
    -   Install your preferred ad-blocker (like uBlock Origin).
    -   Close Firefox.
    -   Find the full path to this profile (e.g., `/home/user/.mozilla/firefox/xxxxxxxx.SeleniumBot`).

4.  **Create your mod list file:**
    -   Create a file named `mod_ids.txt` (or any name you prefer).
    -   Paste the Steam Workshop IDs of the mods you want to download, one ID per line.

## How to Use
Run the script from your terminal. You must provide the path to your ad-blocking Firefox profile.

```bash
python mod_harvester.py --profile "/path/to/your/firefox/profile"
```

**Other options:**
-   `--file`: Specify a different name for your mod list file (e.g., `python mod_harvester.py --profile "..." --file my_mods.txt`).
-   `--output`: Specify a different name for the download folder.

## Disclaimer
This script was designed for a specific workflow and may break if the target websites change their layout. It is provided as-is. Please support the mod authors on the Steam Workshop if you can!