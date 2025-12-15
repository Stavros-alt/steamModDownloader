# steam workshop downloader script

this thing downloads mods from skymods so you don't have to use steamcmd or whatever. it works on my machine. if it doesn't work on yours, check your python install.

## reliability warning
these sites change their urls constantly. this script will break. eventually.
if the presets don't work, go find the url yourself and use custom mode. i can't fix the internet.

## features (i guess)
- downloads mods. obviously.
- has some presets for games i dont actually play.
- tries to unzip files so you don't have to.
- includes a barely funtional scraper (`preset_scraper.py`) if you want to try and update the links yourself. good luck.

## requirements
- python 3
- firefox (installed and in your path)
- `pip install selenium geckodriver-autoinstaller`

## how to run

### the gui way (if you like buttons)
```bash
python mod_harvester.py
```
pick a game. click start. wait.

### the scraping tool
if links are dead, try running this. it might fix `verified_presets.json`. it might also crash if the site changed its layout again.
```bash
python preset_scraper.py
```

### cli (if you're into that)
```bash
python mod_harvester.py --cli
```
or just pass args:
```bash
python mod_harvester.py -u "URL_HERE" -a "APP_ID" --unzip
```

## supported games
check the dropdown. i added:
- cities skylines
- stellaris
- rimworld
- and some others.

## disclaimer
i don't own the sites. i don't own the mods. don't blame me if anything breaks.
code is provided as-is.