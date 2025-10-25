# Filename: mod_harvester.py
import time
import os
import argparse
import geckodriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options as FirefoxOptions

def download_mods_with_firefox(base_url, app_id, profile_path, mod_file, download_folder):
    """
    Automates downloading Steam Workshop mods from a specified Skymods-style site.
    """
    # --- SETUP ---
    geckodriver_autoinstaller.install() 

    if not os.path.exists(download_folder):
        os.makedirs(download_folder)

    print("--- Setting up Firefox WebDriver ---")
    options = FirefoxOptions()
    options.add_argument("--headless")
    
    if profile_path:
        print(f"Using Firefox profile: {profile_path}")
        options.add_argument("-profile")
        options.add_argument(profile_path)
    else:
        print("WARNING: No Firefox profile provided. Ad-blocking will be disabled, which may cause errors.")

    options.set_preference("browser.download.folderList", 2)
    options.set_preference("browser.download.dir", os.path.abspath(download_folder))
    options.set_preference("browser.download.useDownloadDir", True)
    options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/zip, application/octet-stream")

    driver = webdriver.Firefox(options=options)
    wait = WebDriverWait(driver, 20)

    try:
        with open(mod_file, 'r') as f:
            mod_ids = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"!!! ERROR: Mod ID file '{mod_file}' not found.")
        driver.quit()
        return

    print(f"Found {len(mod_ids)} mods for App ID {app_id} to download from {base_url}\n")
    main_window_handle = driver.current_window_handle

    # --- MAIN DOWNLOAD LOOP ---
    for mod_id in mod_ids:
        try:
            print(f"--- Processing Mod ID: {mod_id} ---")
            driver.switch_to.window(main_window_handle)
            
            # --- ======================================== ---
            # --- DYNAMIC URL CONSTRUCTION (THE FINAL FIX) ---
            # --- ======================================== ---
            # Construct the URL using the provided base URL template
            target_url = base_url.format(mod_id=mod_id, app_id=app_id)
            print(f"Navigating to: {target_url}")
            driver.get(target_url)
            # --- ======================================== ---

            # Find the download button. We will make this more robust.
            # It could be a button or a direct link. We'll try both.
            try:
                # Try the button class first (like for CK3)
                download_link_element = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "skymods-excerpt-btn")))
            except Exception:
                # If that fails, try looking for a generic download link (like for HOI4)
                download_link_element = wait.until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "Download")))

            print("Found initial download link. Clicking...")
            download_link_element.click()
            time.sleep(3)

            # Handle popup windows and switch to modsbase.com tab
            for handle in driver.window_handles:
                if handle != main_window_handle:
                    driver.switch_to.window(handle)
                    if "modsbase.com" in driver.current_url:
                        print(f"Switched to Modsbase tab: {driver.current_url}")
                        break 
            
            # Handle cookie banner
            try:
                print("Looking for cookie banner...")
                cookie_button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Accept')]")))
                print("Cookie banner found. Clicking 'Accept'...")
                cookie_button.click()
                time.sleep(2) 
            except Exception:
                print("No cookie banner found, or already accepted. Continuing...")

            # Wait for timer and click download button on modsbase.com
            print("Waiting for 5-second timer on Modsbase...")
            create_link_button = wait.until(EC.element_to_be_clickable((By.ID, "downloadbtn")))
            time.sleep(6)
            driver.execute_script("arguments[0].click();", create_link_button) 
            print("Clicked 'Create download link'.")

            final_download_link = wait.until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, ".zip")))
            print(f"Found final download button. Initiating download...")
            driver.execute_script("arguments[0].click();", final_download_link) 
            
            print(f"SUCCESS: Download initiated for Mod ID: {mod_id}.")
            time.sleep(10)

        except Exception as e:
            print(f"!!! ERROR processing {mod_id}: {e}")
            print("This mod may need to be downloaded manually or the file may not exist on the server.")
        
        finally:
            # Close any extra tabs that might have opened
            while len(driver.window_handles) > 1:
                driver.switch_to.window(driver.window_handles[-1])
                driver.close()
            driver.switch_to.window(main_window_handle)

    print(f"\n--- All mods for App ID {app_id} have been processed. ---")
    print(f"Check your '{download_folder}' folder.")
    input("Downloads may still be in progress. Press Enter to close the browser...")
    driver.quit()

if __name__ == "__main__":
    # Add a new required argument for the base URL
    parser = argparse.ArgumentParser(description="Universal downloader for Skymods network sites.")
    parser.add_argument('-u', '--base_url', type=str, required=True, help="The base URL template for the game's mod page. Use {mod_id} and {app_id} as placeholders.")
    parser.add_argument('-a', '--app_id', type=str, required=True, help="The Steam App ID of the game.")
    parser.add_argument('-p', '--profile', type=str, help="Full path to the Firefox profile directory for ad-blocking.")
    parser.add_argument('-f', '--file', type=str, default="mod_ids.txt", help="Name of the text file containing Workshop IDs (default: mod_ids.txt).")
    parser.add_argument('-o', '--output', type=str, default="Mod_Downloads", help="Name of the folder to download mods into (default: Mod_Downloads).")
    args = parser.parse_args()
    
    download_mods_with_firefox(args.base_url, args.app_id, args.profile, args.file, args.output)