# filename: mod_harvester.py
# look, it downloads mods. don't ask me how logic works.
import time
import os
import sys
import argparse
import logging
import platform
import zipfile
import json
import re
from pathlib import Path
from urllib.parse import urlparse, parse_qs

# setup logging. force it to be useful.
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', force=True)

# check dependencies. if you don't have them, that's your problem.
STARTUP_ERROR = None
try:
    import geckodriver_autoinstaller
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.firefox.options import Options as FirefoxOptions
except ImportError as e:
    STARTUP_ERROR = str(e)

# --- config ---

# generated this list. don't touch it. i don't know why half of these exist.
GAME_PRESETS = {
    "Cities: Skylines": {"app_id": "255710", "base_url": "https://smods.ru"},
    "Hearts of Iron IV": {"app_id": "394360", "base_url": "https://hearts-of-iron-4.smods.ru"},
    "Stellaris": {"app_id": "281990", "base_url": "https://catalogue.smods.ru"},
    "RimWorld": {"app_id": "294100", "base_url": "https://catalogue.smods.ru"},
    "Crusader Kings III": {"app_id": "1158310", "base_url": "https://catalogue.smods.ru"},
    "Europa Universalis IV": {"app_id": "236850", "base_url": "https://catalogue.smods.ru"},
    "Darkest Dungeon": {"app_id": "262060", "base_url": "https://catalogue.smods.ru"},
    "Barotrauma": {"app_id": "602960", "base_url": "https://catalogue.smods.ru"},
    "Teardown": {"app_id": "1167630", "base_url": "https://catalogue.smods.ru"},
    "Total War: WARHAMMER III": {"app_id": "1142710", "base_url": "https://catalogue.smods.ru"},
    "Garry's Mod": {"app_id": "4000", "base_url": "https://catalogue.smods.ru"},
    "XCOM 2": {"app_id": "268500", "base_url": "https://catalogue.smods.ru"},
    "Sid Meier's Civilization VI": {"app_id": "289070", "base_url": "https://catalogue.smods.ru"},
    "Terraria": {"app_id": "105600", "base_url": "https://catalogue.smods.ru"},
    "Project Zomboid": {"app_id": "108600", "base_url": "https://catalogue.smods.ru"},
    "Darkest Dungeon II": {"app_id": "1940340", "base_url": "https://catalogue.smods.ru"}
}

# fallback for when logic fails (which is often)
DEFAULT_BASE_URL = "https://catalogue.smods.ru"

# external config because hardcoding is "bad practice" apparently
external_presets_path = Path("verified_presets.json")
if external_presets_path.exists():
    try:
        with open(external_presets_path, 'r') as f:
            external_presets = json.load(f)
            # prioritize external file. obviously.
            for name, data in external_presets.items():
                # normalize keys
                clean_name = name.replace(" Mods", "")
                # strip legacy archive path if present (lazy migration)
                url = data.get("base_url", "")
                if "/archives/" in url:
                    url = url.split("/archives/")[0]
                GAME_PRESETS[clean_name] = {"app_id": data.get("app_id"), "base_url": url}
    except Exception as e:
        # i don't care enough to print the stack trace
        print(f"warning: verified_presets.json is broken: {e}", flush=True)

class ModHarvester:
    def __init__(self, base_url=None, app_id=None, download_folder="Mod_Downloads", mod_file=None, profile_path=None, headless=True, unzip=False):
        if STARTUP_ERROR:
            print(f"error: required libraries missing. {STARTUP_ERROR}. pip install selenium geckodriver-autoinstaller", flush=True)
            sys.exit(1)
            
        self.base_url = base_url
        self.app_id = app_id
        self.download_folder = Path(download_folder).resolve()
        self.mod_file = Path(mod_file).resolve() if mod_file else None
        self.profile_path = profile_path
        self.headless = headless
        self.unzip = unzip
        self.driver = None
        self.wait = None
        self.start_time = time.time()
        
    def setup_driver(self):
        logging.info("checking geckodriver...")
        
        # try auto-install, but don't die if it fails or hangs
        try:
            geckodriver_autoinstaller.install()
        except Exception as e:
            logging.warning(f"auto-install failed ({e}). assuming geckodriver is in path.")
        
        logging.info("launching firefox...")
        options = FirefoxOptions()
        if self.headless:
            options.add_argument("--headless")
        
        if self.profile_path:
            logging.info(f"using profile: {self.profile_path}")
            options.add_argument("-profile")
            options.add_argument(self.profile_path)
        else:
            logging.warning("no profile found. adblockers are gone. godspeed.")

        # force firefox to save where i tell it to. stop asking me permissions.
        options.set_preference("browser.download.folderList", 2)
        options.set_preference("browser.download.dir", str(self.download_folder))
        options.set_preference("browser.download.folderList", 2)
        options.set_preference("browser.download.dir", str(self.download_folder))
        options.set_preference("browser.download.useDownloadDir", True)
        options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/zip, application/octet-stream")
        
        try:
            self.driver = webdriver.Firefox(options=options)
            self.driver.set_page_load_timeout(30)
            self.wait = WebDriverWait(self.driver, 20)
            logging.info("firefox is alive.")
        except Exception as e:
            logging.error(f"failed to start firefox: {e}")
            logging.error("make sure firefox is installed and geckodriver is in your path.")
            sys.exit(1)

    def resolve_steam_url(self, url):
        # find the mod id from the url
        # usually ?id=XXXXX
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        mod_id = params.get('id', [None])[0]
        
        if not mod_id:
            logging.error(f"could not parse mod id from url: {url}")
            return None, None, None

        logging.info(f"detected mod id: {mod_id}")

        # if we already have app_id and base_url from flags, just use them
        if self.app_id and self.base_url:
            return mod_id, self.app_id, self.base_url

        # otherwise, we have to go look for it. sigh.
        if not self.driver:
            self.setup_driver()

        logging.info(f"visiting steam to find app id: {url}")
        self.driver.get(url)
        
        found_app_id = None
        
        # try method 1: the app hub link
        try:
            # this works on most workshop pages
            element = self.driver.find_element(By.CSS_SELECTOR, "div.apphub_HeaderStandardTop")
            # it might be in a data attribute? no, usually easier to regex the page source if this fails.
            # actually, let's look for the 'All Games' breadcrumb or check the url of the game hub
        except:
            pass
            
        # try method 2: regex the page source. reliable and ugly.
        try:
            import re
            # look for "appid": 12345 or data-appid="12345"
            match = re.search(r'"appid":\s*(\d+)', self.driver.page_source)
            if match:
                found_app_id = match.group(1)
            else:
                # try another pattern
                match = re.search(r'data-appid="(\d+)"', self.driver.page_source)
                if match:
                    found_app_id = match.group(1)
        except Exception as e:
            logging.warning(f"regex failed: {e}")

        if not found_app_id:
            logging.error("could not determine app id. defaulting to generic smods. good luck.")
            # i'm not asking the user. they'll just mess it up.
            return mod_id, "0", DEFAULT_BASE_URL
        
        logging.info(f"found app id: {found_app_id}")
        
        # now find the right smods url
        target_base_url = DEFAULT_BASE_URL
        
        # check if we have a preset for this app id
        for game, data in GAME_PRESETS.items():
            if data["app_id"] == found_app_id:
                logging.info(f"matched preset: {game}")
                target_base_url = data["base_url"]
                break
        
        return mod_id, found_app_id, target_base_url

    def safe_click(self, element, expected_domain=None):
        # clicks things. handles the million spam tabs that pop up.
        # if a tab opens and it's not the site proper, i kill it.
        current_handle = self.driver.current_window_handle
        initial_handles = self.driver.window_handles
        
        # force js click because selenium is trash
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
        time.sleep(0.5)
        self.driver.execute_script("arguments[0].click();", element)
        time.sleep(2)
        
        new_handles = self.driver.window_handles
        if len(new_handles) > len(initial_handles):
            # great, a new tab. probably spam.
            for handle in new_handles:
                if handle not in initial_handles:
                    self.driver.switch_to.window(handle)
                    current_url = self.driver.current_url
                    logging.info(f"popup opened: {current_url}")
                    
                    is_safe = False
                    if expected_domain and expected_domain in current_url:
                        is_safe = True
                    elif "modsbase.com" in current_url or "smods.ru" in current_url:
                        is_safe = True
                    # blank pages sometimes mean the download actually started. weird.
                    elif current_url == "about:blank":
                        is_safe = True
                        
                    if not is_safe:
                        logging.warning("closing spam popup. nice try.")
                        self.driver.close()
                        self.driver.switch_to.window(current_handle)
                        # if we closed a popup, the click was likely intercepted. try again.
                        logging.info("retrying click...")
                        time.sleep(1)
                        try:
                            self.driver.execute_script("arguments[0].click();", element)
                        except:
                            logging.warning("could not retry click. whatever.")
                    else:
                        logging.info("popup seems legit. staying.")
                        return

    def download_mod(self, mod_id, main_window_handle):
        try:
            logging.info(f"--- processing mod: {mod_id} ---")
            self.driver.switch_to.window(main_window_handle)
            
            # search for the mod since we can't guess the url
            search_url = f"{self.base_url}/?s={mod_id}"
            logging.info(f"searching: {search_url}")
            self.driver.get(search_url)
            
            # click the first result
            try:
                # look for the first article link (smods usually creates a grid or list)
                # selector: article a
                result_link = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "article a")))
                target_url = result_link.get_attribute("href")
                logging.info(f"found mod page: {target_url}")
                # use js click because headless firefox is picky about scrolling
                self.driver.execute_script("arguments[0].click();", result_link)
            except Exception as e:
                logging.error(f"search failed. could not find result for {mod_id}. error: {e}")
                raise e

            # find the download button. it moves around to annoy me.
            try:
                # specific modsbase redirect link
                download_link_element = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, 'modsbase.com')]")))
                logging.info(f"found modsbase link: {download_link_element.get_attribute('href')}")
            except Exception:
                try:
                     # ck3 style
                    download_link_element = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "skymods-excerpt-btn")))
                except:
                     # desperation
                    download_link_element = self.wait.until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "Download")))

            logging.info("found initial download link. clicking...")
            self.safe_click(download_link_element, expected_domain="modsbase.com")
            time.sleep(3)

            # popups are the absolute worst thing on the internet.
            for handle in self.driver.window_handles:
                if handle != main_window_handle:
                    self.driver.switch_to.window(handle)
                    if "modsbase.com" in self.driver.current_url:
                        logging.info(f"switched to modsbase: {self.driver.current_url}")
                        break 
            
            # kill the cookie banner. die.
            try:
                cookie_button = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Accept')]")))
                cookie_button.click()
                time.sleep(1) 
            except Exception:
                pass

            # wait for the valid buttons. finding this id took me 2 hours.
            logging.info("waiting for timer...")
            # use presence_of_element_located so ad overlays don't block detection
            create_link_button = self.wait.until(EC.presence_of_element_located((By.ID, "downloadbtn")))
            # extra wait for safety
            time.sleep(6) 
            
            logging.info("clicking 'create download link'.")
            self.safe_click(create_link_button)
            
            final_download_link = self.wait.until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, ".zip")))
            logging.info(f"found final button. linking to: {final_download_link.get_attribute('href')}")
            logging.info("downloading...")
            self.safe_click(final_download_link)
            
            logging.info(f"success: download started for {mod_id}.")
            time.sleep(5)

        except Exception as e:
            logging.error(f"error processing {mod_id}: {e}")
            if self.driver:
                try:
                    self.driver.save_screenshot("error_screenshot.png")
                    logging.info("screenshot saved to error_screenshot.png")
                    with open("error_page_source.html", "w", encoding="utf-8") as f:
                        f.write(self.driver.page_source)
                except:
                    pass
        
        finally:
            # cleanup tabs
            if len(self.driver.window_handles) > 1:
                for handle in self.driver.window_handles:
                    if handle != main_window_handle:
                        self.driver.switch_to.window(handle)
                        self.driver.close()
                self.driver.switch_to.window(main_window_handle)

    def process_unzip(self):
        logging.info("scanning for files to extract...")
        # wait a bit for writers to close
        time.sleep(5) 
        
        count = 0
        for file_path in self.download_folder.glob("*.zip"):
            # check if file was modified after start time
            if file_path.stat().st_mtime > self.start_time:
                try:
                    logging.info(f"extracting: {file_path.name}")
                    with zipfile.ZipFile(file_path, 'r') as zip_ref:
                        zip_ref.extractall(self.download_folder)
                    logging.info(f"extracted {file_path.name}")
                    count += 1
                except zipfile.BadZipFile:
                    logging.error(f"failed to extract {file_path.name}: bad zip")
                except Exception as e:
                    logging.error(f"failed to extract {file_path.name}: {e}")
        
        if count == 0:
            logging.info("no new files extracted.")
        else:
            logging.info(f"extracted {count} archives.")

    def wait_for_downloads(self):
        logging.info("waiting for files. don't close me.")
        # wait up to 5 minutes
        timeout = 300
        start = time.time()
        while time.time() - start < timeout:
            # check for .part or .crdownload files (temp junk)
            temp_files = list(self.download_folder.glob("*.part")) + list(self.download_folder.glob("*.crdownload"))
            # check for completed zips
            zip_files = list(self.download_folder.glob("*.zip"))
            
            if temp_files:
                logging.info(f"still downloading... {len(temp_files)} files active.")
                time.sleep(2)
                continue
                
            if zip_files:
                # if size > 0 it's probably real. probably.
                if any(f.stat().st_size > 0 for f in zip_files):
                    logging.info("download looks done.")
                    time.sleep(1) # safety buffer
                    return
            
            time.sleep(1)
            
        logging.warning("download timed out. i gave it 5 minutes. it's not happening.")

    def run_single(self, url):
        # ensure folder exists
        if not self.download_folder.exists():
            self.download_folder.mkdir(parents=True, exist_ok=True)
            
        mod_id, app_id, base_url = self.resolve_steam_url(url)
        
        if not mod_id or not base_url:
            logging.error("could not resolve details. aborting.")
            if self.driver: self.driver.quit()
            return
 
        # update state with resolved info
        self.app_id = app_id
        self.base_url = base_url
        
        if not self.driver:
            self.setup_driver()
            
        try:
            self.download_mod(mod_id, self.driver.current_window_handle)
            self.wait_for_downloads()
            logging.info(f"--- check '{self.download_folder}' ---")
            
            if self.unzip:
                time.sleep(2)
                self.process_unzip()
        finally:
            if self.driver:
                self.driver.quit()

    def run_batch(self):
        # standard list processing
        if not self.download_folder.exists():
            self.download_folder.mkdir(parents=True, exist_ok=True)
            
        if not self.mod_file or not self.mod_file.exists():
            logging.error("mod list file not found.")
            return
 
        with open(self.mod_file, 'r') as f:
            mod_ids = [line.strip() for line in f if line.strip()]
            
        if not mod_ids:
            logging.error("no mod ids found.")
            return
 
        logging.info(f"found {len(mod_ids)} mods.")
        self.setup_driver()
        
        try:
            if not self.base_url:
                logging.error("no base url provided for batch mode. use -u.")
                return
 
            main_window_handle = self.driver.current_window_handle
            for mod_id in mod_ids:
                try:
                    self.download_mod(mod_id, main_window_handle)
                except Exception as e:
                    logging.error(f"failed to download {mod_id}: {e}")
            
            self.wait_for_downloads()
            logging.info("--- batch finished ---")
            
            if self.unzip:
                time.sleep(2)
                self.process_unzip()
            
        finally:
            if self.driver:
                self.driver.quit()

# --- main ---

def main():
    parser = argparse.ArgumentParser(description="downloads steam mods. no gui.")
    
    # allow a single url as a positional arg
    parser.add_argument('url', nargs='?', help="steam workshop url to download")
    
    # flags for advanced/batch usage
    parser.add_argument('-u', '--base_url', type=str, help="manually set base url")
    parser.add_argument('-a', '--app_id', type=str, help="manually set app id")
    parser.add_argument('-p', '--profile', type=str, help="firefox profile path")
    parser.add_argument('-f', '--file', type=str, default="mod_ids.txt", help="file with mod ids (batch mode)")
    parser.add_argument('-o', '--output', type=str, default="Mod_Downloads", help="where to put the files")
    parser.add_argument('--headless', action='store_true', help="run invisible")
    parser.add_argument('--unzip', action='store_true', help="auto-unzip stuff")
    
    args = parser.parse_args()

    # logic flow:
    # 1. if url is provided, run single mode (auto-detects app id if not provided)
    # 2. if no url, but flags provided, try batch mode
    # 3. otherwise, print help, because i deleted the menu.

    if args.url:
        harvester = ModHarvester(
            base_url=args.base_url,
            app_id=args.app_id,
            download_folder=args.output,
            profile_path=args.profile,
            headless=args.headless,
            unzip=args.unzip
        )
        harvester.run_single(args.url)
        return

    if args.base_url and args.app_id:
        harvester = ModHarvester(
            base_url=args.base_url,
            app_id=args.app_id,
            download_folder=args.output,
            mod_file=args.file,
            profile_path=args.profile,
            headless=args.headless,
            unzip=args.unzip
        )
        harvester.run_batch()
        return
        
    # if we got here, the user didn't do it right
    parser.print_help()

if __name__ == "__main__":
    main()