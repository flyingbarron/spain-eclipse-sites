#!/usr/bin/env python3
"""
Take a screenshot of the EclipseFan.org map for a specific location.
Requires: pip install selenium
Also requires: Chrome/Chromium browser and chromedriver
"""

import sys
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def take_screenshot(url, output_file="eclipsefan_screenshot.png", wait_time=5):
    """
    Take a screenshot of the given URL.
    
    Args:
        url: The URL to screenshot
        output_file: Output filename for the screenshot
        wait_time: Time to wait for page to load (seconds)
    """
    print(f"Taking screenshot of: {url}")
    
    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in background
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")  # Set window size
    chrome_options.add_argument("--disable-gpu")
    
    # Initialize the driver
    try:
        driver = webdriver.Chrome(options=chrome_options)
    except Exception as e:
        print(f"Error initializing Chrome driver: {e}")
        print("\nPlease ensure you have:")
        print("1. Chrome or Chromium browser installed")
        print("2. chromedriver installed (brew install chromedriver on macOS)")
        print("3. selenium installed (pip install selenium)")
        sys.exit(1)
    
    try:
        # Load the page
        print("Loading page...")
        driver.get(url)
        
        # Wait for the page to load
        print(f"Waiting {wait_time} seconds for page to fully load...")
        time.sleep(wait_time)
        
        # Optional: Wait for specific element (map container)
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "map"))
            )
            print("Map element detected")
        except:
            print("Map element not found, but continuing anyway...")
        
        # Take screenshot
        print(f"Taking screenshot and saving to: {output_file}")
        driver.save_screenshot(output_file)
        
        print(f"✓ Screenshot saved successfully!")
        
    except Exception as e:
        print(f"Error taking screenshot: {e}")
        sys.exit(1)
        
    finally:
        driver.quit()

def main():
    # Default URL for Spain eclipse location
    default_url = "https://www.eclipsefan.org/?lat=42.083378&lng=-2.085237&zoom=6&oz=5&lang=en"
    
    # Allow custom URL from command line
    url = sys.argv[1] if len(sys.argv) > 1 else default_url
    output_file = sys.argv[2] if len(sys.argv) > 2 else "eclipsefan_screenshot.png"
    
    take_screenshot(url, output_file)

if __name__ == "__main__":
    main()

# Made with Bob
