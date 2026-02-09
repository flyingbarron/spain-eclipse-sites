#!/usr/bin/env python3
"""
Download shadow map export from Shademap.app for a specific location and time.
This script automates the process of opening Shademap, dismissing popups,
zooming in, and exporting the shadow visualization.

Requires: pip install selenium
Also requires: Chrome/Chromium browser and chromedriver
"""

import sys
import time
import os
import urllib.parse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

def download_shademap_export(url, output_dir="data", output_filename="shademap_export.jpg", headless=True):
    """
    Open Shademap, dismiss popup, zoom in, and export as JPG.
    
    Args:
        url: The Shademap URL with location and time parameters
        output_dir: Directory to save the exported file
        output_filename: Name for the output file
        headless: Whether to run in headless mode (default: True)
    """
    print(f"Opening Shademap (headless={headless}): {url}")
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Set up Chrome options
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # Set download directory
    download_dir = os.path.abspath(output_dir)
    prefs = {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    }
    chrome_options.add_experimental_option("prefs", prefs)
    
    # Initialize the driver
    try:
        driver = webdriver.Chrome(options=chrome_options)
        
        # Remove webdriver property
        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': '''
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            '''
        })
        
    except Exception as e:
        print(f"Error initializing Chrome driver: {e}")
        print("\nPlease ensure you have:")
        print("1. Chrome or Chromium browser installed")
        print("2. chromedriver installed (brew install chromedriver on macOS)")
        print("3. selenium installed (pip install selenium)")
        sys.exit(1)
    
    try:
        # Load the page
        print("Loading Shademap page...")
        print(f"URL: {url}")
        
        # URL is already properly formatted by Shademap, just use it directly
        # The special characters in the URL are intentional and part of Shademap's format
        driver.get(url)
        
        # Wait for page to load and check if it loaded correctly
        print("Waiting for page to load...")
        time.sleep(8)  # Increased wait time for complex page
        
        # Check if page loaded by looking for Shademap elements
        try:
            # Wait for the map canvas or container to load
            WebDriverWait(driver, 10).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            print("✓ Page loaded successfully")
        except:
            print("⚠️  Page may not have loaded completely")
            # Take a screenshot to see what's on the page
            debug_file = "shademap_load_debug.png"
            driver.save_screenshot(debug_file)
            print(f"Debug screenshot saved to: {debug_file}")
        
        # Step 1: Click "OK" to dismiss popup
        print("Looking for popup to dismiss...")
        popup_selectors = [
            (By.XPATH, "//button[contains(text(), 'OK')]"),
            (By.XPATH, "//button[contains(text(), 'Ok')]"),
            (By.XPATH, "//button[contains(text(), 'ok')]"),
            (By.CSS_SELECTOR, "button.ok"),
            (By.CSS_SELECTOR, "button[type='button']"),
            (By.XPATH, "//button[contains(@class, 'close')]"),
            (By.XPATH, "//*[contains(text(), 'OK')]"),
        ]
        
        popup_dismissed = False
        for by, selector in popup_selectors:
            try:
                element = WebDriverWait(driver, 3).until(
                    EC.element_to_be_clickable((by, selector))
                )
                print(f"Found popup button with selector: {selector}")
                element.click()
                popup_dismissed = True
                print("✓ Popup dismissed")
                time.sleep(1)
                break
            except:
                continue
        
        if not popup_dismissed:
            print("⚠️  No popup found (or already dismissed)")
        
        # Step 2: Zoom in 3 times using the + button
        print("\nZooming in 3 times...")
        zoom_selectors = [
            (By.CSS_SELECTOR, "button[aria-label*='Zoom in']"),
            (By.CSS_SELECTOR, "button.zoom-in"),
            (By.XPATH, "//button[contains(@aria-label, 'Zoom')]"),
            (By.XPATH, "//button[contains(text(), '+')]"),
            (By.CSS_SELECTOR, "button[title*='Zoom in']"),
        ]
        
        zoom_button = None
        for by, selector in zoom_selectors:
            try:
                zoom_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((by, selector))
                )
                print(f"Found zoom button with selector: {selector}")
                break
            except:
                continue
        
        if zoom_button:
            for i in range(3):
                zoom_button.click()
                print(f"  Zoom {i+1}/3")
                time.sleep(1)
            print("✓ Zoomed in 3 times")
        else:
            print("⚠️  Could not find zoom button")
        
        # Step 3: Click the export icon
        print("\nLooking for export button...")
        export_selectors = [
            (By.CSS_SELECTOR, "button[aria-label*='Export']"),
            (By.CSS_SELECTOR, "button[title*='Export']"),
            (By.XPATH, "//button[contains(@aria-label, 'Export')]"),
            (By.XPATH, "//button[contains(@title, 'Export')]"),
            (By.CSS_SELECTOR, "button.export"),
            (By.XPATH, "//*[contains(text(), 'Export')]"),
        ]
        
        export_clicked = False
        for by, selector in export_selectors:
            try:
                export_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((by, selector))
                )
                print(f"Found export button with selector: {selector}")
                export_button.click()
                export_clicked = True
                print("✓ Export button clicked")
                time.sleep(2)
                break
            except:
                continue
        
        if not export_clicked:
            print("⚠️  Could not find export button")
            # Take a screenshot for debugging
            debug_file = "shademap_debug.png"
            driver.save_screenshot(debug_file)
            print(f"Debug screenshot saved to: {debug_file}")
        
        # Step 4: Click JPG to save
        print("\nLooking for JPG export option...")
        jpg_selectors = [
            (By.XPATH, "//button[contains(text(), 'JPG')]"),
            (By.XPATH, "//button[contains(text(), 'jpg')]"),
            (By.XPATH, "//*[contains(text(), 'JPG')]"),
            (By.CSS_SELECTOR, "button[data-format='jpg']"),
            (By.CSS_SELECTOR, "button[data-format='jpeg']"),
        ]
        
        jpg_clicked = False
        for by, selector in jpg_selectors:
            try:
                jpg_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((by, selector))
                )
                print(f"Found JPG button with selector: {selector}")
                jpg_button.click()
                jpg_clicked = True
                print("✓ JPG export initiated")
                break
            except:
                continue
        
        if not jpg_clicked:
            print("⚠️  Could not find JPG button")
        
        # Wait for download to complete
        print("\nWaiting for download to complete...")
        time.sleep(5)
        
        print(f"\n✓ Export process completed!")
        print(f"Check the '{output_dir}' directory for the downloaded file")
        
        if not headless:
            print("\nBrowser window will close in 3 seconds...")
            time.sleep(3)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        
        # Take a screenshot for debugging
        debug_file = "shademap_error_debug.png"
        driver.save_screenshot(debug_file)
        print(f"\nDebug screenshot saved to: {debug_file}")
        sys.exit(1)
        
    finally:
        driver.quit()

def main():
    # Default URL for the eclipse location
    default_url = "https://shademap.app/@42.13096,-2.15972,20z,1786559455614t,0b,0p,0m!1786511647543!1786562164762,qDMKLwoxMyo5NTgsIC0zCi8KMTU5NzIw=!42.13096!-2.15972"
    
    # Allow custom URL from command line
    url = sys.argv[1] if len(sys.argv) > 1 else default_url
    output_filename = sys.argv[2] if len(sys.argv) > 2 else "shademap_export.jpg"
    
    download_shademap_export(url, output_filename=output_filename)

if __name__ == "__main__":
    main()

# Made with Bob
