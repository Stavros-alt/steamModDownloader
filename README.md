# CK3 Skymods Harvester

A Python script to automate the downloading of Crusader Kings 3 mods from Skymods, designed for players with non-Steam versions of the game.

This tool uses Selenium to control a headless Firefox browser, methodically navigating the multi-page download process and handling interruptions like pop-ups and cookie banners automatically.

## What it Does
- Reads a simple text file of Steam Workshop IDs.
- For each ID, it constructs the correct Skymods URL.
- Navigates through the Skymods -> File Host (Modsbase) redirect chain.
- Intelligently handles cookie banners and closes ad-related pop-up tabs.
- Waits for the JavaScript timer and clicks the download links.
- Downloads all mods into a single, organized folder.

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

3.  **(Highly Recommended) Create a dedicated Firefox Profile for ad-blocking:**
    This allows the script to run with an ad-blocker, making it much more reliable.
    -   Close Firefox, then run `firefox -P` in your terminal to open the Profile Manager.
    -   Create a new profile (e.g., name it "SeleniumBot").
    -   Launch Firefox with that new profile: `firefox -P SeleniumBot`.
    -   Install your preferred ad-blocker (like **uBlock Origin**) from the Firefox Add-ons store.
    -   Close Firefox.
    -   Find the full path to this profile. You can find it by going to `about:profiles` in Firefox. It will look something like `/home/user/.mozilla/firefox/xxxxxxxx.SeleniumBot`.

4.  **Create your mod list file:**
    -   Create a file in this directory named `mod_ids.txt`.
    -   Paste the Steam Workshop IDs of the mods you want to download, one ID per line.

## How to Use

Run the script from your terminal. You **must** provide the path to your Firefox profile for the best results.

**Example Usage (Linux):**
```bash
python mod_harvester.py --profile "/home/stavros/.mozilla/firefox/xxxxxxxx.SeleniumBot"
```

### Command-Line Options:

-   `--profile "PATH"`: **(Required for best results)** The full, absolute path to your Firefox profile directory.
-   `--file "FILENAME"`: Use a different file for your mod IDs (default is `mod_ids.txt`).
-   `--output "FOLDERNAME"`: Specify a different folder to download the mods into (default is `CK3_Mod_Downloads`).

## Troubleshooting

- **`WebDriverException: Message: Process unexpectedly closed with status 11`**: This often means there's a conflict between Selenium/geckodriver and your system's display server (like Wayland). Try running the script in a `X11` or `Xorg` session instead of Wayland.
- **`ElementNotInteractableException`**: A pop-up or another element is blocking the button. Ensure your Firefox profile has a working ad-blocker.
- **`NoSuchElementException`**: The script can't find a button or link. The website's layout has probably changed. This script may need to be updated.

## Disclaimer
This script was designed for a specific workflow and may break if the target websites change their layout. It is provided as-is under the MIT License. Please support the mod authors on the Steam Workshop if you can!