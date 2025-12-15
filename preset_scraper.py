import json
import time
import re
import logging
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options as FirefoxOptions
import geckodriver_autoinstaller

# setup logging. if it crashes, i want to know why.
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def setup_driver():
    geckodriver_autoinstaller.install()
    options = FirefoxOptions()
    options.add_argument("--headless")
    driver = webdriver.Firefox(options=options)
    return driver

def scrape_presets():
    driver = setup_driver()
    wait = WebDriverWait(driver, 10)
    presets = {}

    try:
        logging.info("Navigating to catalogue...")
        driver.get("https://catalogue.smods.ru/")
        
        # grab every link. yes, all of them. efficiency is for people with time.
        links = driver.find_elements(By.TAG_NAME, "a")
        game_links = []
        for link in links:
            href = link.get_attribute("href")
            text = link.text.strip()
            if href and "smods.ru" in href and text:
                # ignore the useless pages
                if text in ["Home", "About Us", "Privacy Policy", "Cookie Policy", "How To Install Mods", "Catalogue"]:
                    continue
                if "archives" in href: # specific mods. not what i'm looking for.
                    continue
                game_links.append((text, href))
        
        # remove duplicates. clearly.
        game_links = list(set(game_links))
        logging.info(f"Found {len(game_links)} potential game links.")

        # checking the popular ones. i don't care about your indie gem right now.
        target_games = [
            "Cities: Skylines", "Stellaris", "Hearts of Iron IV", "RimWorld", 
            "Crusader Kings III", "Europa Universalis IV", "Darkest Dungeon", 
            "Barotrauma", "Teardown", "Total War: WARHAMMER III", "Garry's Mod", 
            "XCOM 2", "Sid Meier's Civilization VI", "Terraria", "Project Zomboid"
        ]
        
        verified_count = 0
        
        for name, url in game_links:
            # close enough match.
            is_target = any(t.lower() in name.lower() for t in target_games)
            
            if not is_target:
                 continue

            logging.info(f"Checking {name} at {url}...")
            try:
                driver.get(url)
                
                # click the first thing i see to guess the pattern.
                try:
                    article_link = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "article h2 a")))
                    mod_url = article_link.get_attribute("href")
                    
                    # guessing the url pattern. regex is a nightmare.
                    match = re.search(r'/(\d+)/?$', mod_url)
                    if match:
                        mod_id = match.group(1)
                        base_url = mod_url.replace(mod_id, "{mod_id}")
                        
                        # stealing the app id from url params.
                        app_id = ""
                        app_match = re.search(r'app=(\d+)', url) or re.search(r'app=(\d+)', mod_url)
                        if app_match:
                            app_id = app_match.group(1)
                        
                        presets[name] = {
                            "app_id": app_id, 
                            "base_url": base_url
                        }
                        logging.info(f"VERIFIED: {name} -> {base_url}")
                        verified_count += 1
                    else:
                        logging.warning(f"Could not parse ID from {mod_url}")
                except Exception as e:
                    logging.warning(f"No articles found for {name}: {e}")

            except Exception as e:
                logging.error(f"Error visiting {url}: {e}")
            
            if verified_count >= 20: # Safety limit for this run
                break

    finally:
        driver.quit()

    # dump it all into a file and hope it works.
    with open("verified_presets.json", "w") as f:
        json.dump(presets, f, indent=4)
    
    logging.info(f"Saved {len(presets)} verified presets to verified_presets.json")

if __name__ == "__main__":
    scrape_presets()
