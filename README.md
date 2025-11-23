# Universal Steam Workshop Mod Downloader

A powerful, cross-platform tool to download Steam Workshop mods for supported games (via the Skymods network) without a Steam account.

> [!WARNING]
> **Reliability Notice**: This tool relies on third-party websites (Skymods network) which frequently change their URL structures, domains, and protection mechanisms (Cloudflare, etc.).
> While we include a list of verified presets, **we cannot guarantee they will always work**.
> If a preset fails, please use the `preset_scraper.py` tool to find the latest URL, or manually find the correct URL and use the "Custom (Advanced)" mode.

## Features
- **GUI & CLI**: Easy-to-use Graphical User Interface and robust Command Line Interface.
- **Verified Presets**: Built-in support for popular games like *Cities: Skylines*, *Stellaris*, *RimWorld*, *Hearts of Iron IV*, and many more.
- **Preset Scraper**: Includes a separate tool to verify and update game URLs automatically.
- **Auto-Unzip**: Automatically extracts downloaded mod archives.
- **Cross-Platform**: Works on Windows, Linux, and macOS.
- **Headless Mode**: Run downloads in the background without opening a browser window.

## Requirements
- Python 3.x
- Firefox Browser
- Dependencies:
  ```bash
  pip install selenium geckodriver-autoinstaller
  ```

## Usage

### 1. Standard Downloader (GUI)
Simply run the script to open the GUI:
```bash
python mod_harvester.py
```
Select your game from the list. If your game isn't listed or the preset isn't working, choose **"Custom (Advanced)"** and enter the App ID and Base URL manually.

### 2. Updating Presets (The Scraper)
If you find that the built-in presets are outdated (e.g., a site moved from `smods.ru` to `catalogue.smods.ru`), you can run the scraper tool:
```bash
python preset_scraper.py
```
This will:
1.  Scan the Skymods catalogue for verified game links.
2.  Generate a `verified_presets.json` file.
3.  The main `mod_harvester.py` will automatically load this file next time you run it, overriding the built-in defaults with the fresh URLs.

### 3. Command Line Interface (CLI)
For servers or headless environments:
```bash
python mod_harvester.py --cli
```

### Advanced Arguments
```bash
python mod_harvester.py [options]
```

| Option | Description |
| :--- | :--- |
| `-u`, `--base_url` | Base URL template (required if not using a preset). Use `{mod_id}` and `{app_id}` placeholders. |
| `-a`, `--app_id` | Steam App ID of the game. |
| `-f`, `--file` | Path to the text file containing Mod IDs (default: `mod_ids.txt`). |
| `-o`, `--output` | Output directory for downloads (default: `Mod_Downloads`). |
| `--unzip` | Automatically unzip downloaded files. |
| `--headless` | Run in headless mode (no visible browser). |
| `--cli` | Force Interactive CLI mode. |
| `--gui` | Force GUI mode. |

**Example:**
```bash
python mod_harvester.py -u "https://catalogue.smods.ru/archives/{mod_id}" -a "255710" -f my_mods.txt --unzip
```

## Supported Games
The tool includes built-in presets for over 50 games including:
- Cities: Skylines
- Stellaris
- Hearts of Iron IV
- RimWorld
- Crusader Kings III
- Europa Universalis IV
- ...and many more.

## Disclaimer
This tool is for educational purposes and interoperability. Please support developers by buying games and mods on Steam when possible.
We are not affiliated with Valve, Steam, or Skymods. Use at your own risk.

## License
This project is licensed under the MIT License.