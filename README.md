# steam mod harvester

this tool downloads mods from steam workshop. it bypasses steamcmd because that thing never works for me. it uses selenium to scrape smods.ru.

if it breaks, check if smods is down. or if firefox updated. or if you looked at it wrong.

## requirements

you need python 3. you need firefox.
`pip install selenium geckodriver-autoinstaller`

## usage

don't overcomplicate it.

**download one mod:**
```bash
python3 mod_harvester.py https://steamcommunity.com/sharedfiles/filedetails/?id=2858562094
```
it'll try to find the mod, handle the popup junk, and wait for the file.

**download a list (if you have friends or something):**
```bash
python3 mod_harvester.py -u "https://catalogue.smods.ru" -a "255710" -f list.txt
```
put just the mod ids in `list.txt`. one per line.

## flags

* `-u`: base url. smods has different subdomains for different games. check the presets in the code if you care.
* `-a`: app id. steam's id for the game.
* `-p`: firefox profile path. **recommended**. use this if you want adblock. the script tries to close spam tabs, but adblock is better.
* `--headless`: runs without a window. good for servers or if you hate seeing it work.
* `--unzip`: unzips the files. obviously.

## notes

* the script tries to be smart about popups. it closes new tabs that aren't the download site. it's not magic though.
* if it hangs, ctrl+c and try again. i made it timeout eventually but sometimes it's just stuck.
* it defaults to `Mod_Downloads` folder. just look there.

## supported games

it tries to auto-detect the big ones (cities skylines, hoi4, rimworld, etc). if it fails, just use the flags.