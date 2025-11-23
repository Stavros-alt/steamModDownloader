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

# Setup logging
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
        
        # Grab all links. We're looking for game pages, usually subdomains or /game/ paths.
        links = driver.find_elements(By.TAG_NAME, "a")
        game_links = []
        for link in links:
            href = link.get_attribute("href")
            text = link.text.strip()
            if href and "smods.ru" in href and text:
                # Skip the boring stuff
                if text in ["Home", "About Us", "Privacy Policy", "Cookie Policy", "How To Install Mods", "Catalogue"]:
                    continue
                if "archives" in href: # specific mods, not games
                    continue
                game_links.append((text, href))
        
        # Unique links only
        game_links = list(set(game_links))
        logging.info(f"Found {len(game_links)} potential game links.")

        # Just checking the big ones for now so we don't sit here all day.
        target_games = [
            "Cities: Skylines", "Stellaris", "Hearts of Iron IV", "RimWorld", 
            "Crusader Kings III", "Europa Universalis IV", "Darkest Dungeon", 
            "Barotrauma", "Teardown", "Total War: WARHAMMER III", "Garry's Mod", 
            "XCOM 2", "Sid Meier's Civilization VI", "Terraria", "Project Zomboid"
        ]
        
        verified_count = 0
        
        for name, url in game_links:
            # Fuzzy match to see if it's one of the games we care about
            is_target = any(t.lower() in name.lower() for t in target_games)
            
            if not is_target:
                 continue

            logging.info(f"Checking {name} at {url}...")
            try:
                driver.get(url)
                
                # Grab the first mod we see to figure out the URL pattern
                try:
                    article_link = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "article h2 a")))
                    mod_url = article_link.get_attribute("href")
                    
                    # Pattern should be something like https://subdomain.smods.ru/archives/12345
                    match = re.search(r'/(\d+)/?$', mod_url)
                    if match:
                        mod_id = match.group(1)
                        base_url = mod_url.replace(mod_id, "{mod_id}")
                        
                        # Try to snag the App ID if it's lying around in the URL params
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

    # Save to file
    with open("verified_presets.json", "w") as f:
        json.dump(presets, f, indent=4)
    
    logging.info(f"Saved {len(presets)} verified presets to verified_presets.json")

if __name__ == "__main__":
    scrape_presets()
