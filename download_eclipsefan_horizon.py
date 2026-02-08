#!/usr/bin/env python3
"""
Download the horizon image from EclipseFan.org for a specific location.
This script clicks the Horizon tab and downloads the generated image.
Requires: pip install selenium
Also requires: Chrome/Chromium browser and chromedriver
"""

import sys
import time
import os
import base64
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def download_horizon_image(url, output_file="horizon_image.png", headless=False):
    """
    Navigate to EclipseFan, click Horizon tab, and download the image.
    
    Args:
        url: The EclipseFan URL with location parameters
        output_file: Output filename for the horizon image
        headless: Whether to run in headless mode
    """
    print(f"Loading EclipseFan page: {url}")
    
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
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    # Initialize the driver
    try:
        driver = webdriver.Chrome(options=chrome_options)
        
        # Remove webdriver property to avoid detection
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
        print("Loading page...")
        driver.get(url)
        
        # Wait for page to initialize
        print("Waiting for page to initialize...")
        time.sleep(3)
        
        # Look for and click the Horizon tab
        print("Looking for Horizon tab...")
        
        horizon_selectors = [
            (By.XPATH, "//*[contains(text(), 'Horizon')]"),
            (By.LINK_TEXT, "Horizon"),
            (By.PARTIAL_LINK_TEXT, "Horizon"),
            (By.CSS_SELECTOR, "button:contains('Horizon')"),
            (By.CSS_SELECTOR, "a:contains('Horizon')"),
        ]
        
        horizon_clicked = False
        for by, selector in horizon_selectors:
            try:
                element = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((by, selector))
                )
                if element:
                    print(f"Found Horizon tab with selector: {selector}")
                    element.click()
                    horizon_clicked = True
                    break
            except:
                continue
        
        if not horizon_clicked:
            print("Could not find Horizon tab. Available text on page:")
            print(driver.find_element(By.TAG_NAME, "body").text[:500])
            raise Exception("Horizon tab not found")
        
        print("Clicked Horizon tab, waiting for image to load...")
        time.sleep(5)  # Wait for horizon image to generate
        
        # Look for the horizon image
        print("Looking for horizon image...")
        
        image_selectors = [
            (By.CSS_SELECTOR, 'img[src*="horizon"]'),
            (By.CSS_SELECTOR, 'img[alt*="horizon"]'),
            (By.CSS_SELECTOR, 'img[alt*="Horizon"]'),
            (By.CSS_SELECTOR, '.horizon-image img'),
            (By.CSS_SELECTOR, '#horizon img'),
            (By.TAG_NAME, 'canvas'),
        ]
        
        image_element = None
        for by, selector in image_selectors:
            try:
                element = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((by, selector))
                )
                if element:
                    tag_name = element.tag_name.lower()
                    if tag_name == 'img':
                        image_element = element
                        print(f"Found image with selector: {selector}")
                        break
                    elif tag_name == 'canvas':
                        # If it's a canvas, take a screenshot of it
                        print("Horizon is rendered on canvas, taking screenshot...")
                        element.screenshot(output_file)
                        print(f"✓ Canvas screenshot saved to: {output_file}")
                        return
            except:
                continue
        
        if not image_element:
            # Try to find any images loaded after clicking
            print("Searching for any images in the page...")
            all_images = driver.find_elements(By.TAG_NAME, 'img')
            print(f"Found {len(all_images)} images on page")
            
            for img in all_images:
                src = img.get_attribute('src')
                alt = img.get_attribute('alt') or ''
                print(f"  - {src} (alt: {alt})")
            
            raise Exception("Could not find horizon image")
        
        # Get the image source
        image_url = image_element.get_attribute('src')
        print(f"Image URL: {image_url}")
        
        # Download the image
        print(f"Downloading image...")
        
        # If it's a data URL, save it directly
        if image_url.startswith('data:'):
            print("Image is a data URL, extracting...")
            header, encoded = image_url.split(',', 1)
            data = base64.b64decode(encoded)
            with open(output_file, 'wb') as f:
                f.write(data)
        else:
            # Make URL absolute if needed
            if image_url.startswith('/'):
                image_url = 'https://www.eclipsefan.org' + image_url
            elif not image_url.startswith('http'):
                image_url = 'https://www.eclipsefan.org/' + image_url
            
            # Download using requests with the same session cookies
            import urllib.request
            req = urllib.request.Request(image_url, headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            })
            
            with urllib.request.urlopen(req) as response:
                image_data = response.read()
            
            with open(output_file, 'wb') as f:
                f.write(image_data)
        
        print(f"✓ Horizon image saved to: {output_file}")
        
        if not headless:
            print("\nBrowser window will close in 3 seconds...")
            time.sleep(3)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        
        # Take a screenshot for debugging
        debug_file = "debug_screenshot.png"
        driver.save_screenshot(debug_file)
        print(f"\nDebug screenshot saved to: {debug_file}")
        sys.exit(1)
        
    finally:
        driver.quit()

def main():
    # Default URL for Spain eclipse location
    default_url = "https://www.eclipsefan.org/?lat=42.083378&lng=-2.085237&zoom=6&oz=5&lang=en"
    
    # Allow custom URL from command line
    url = sys.argv[1] if len(sys.argv) > 1 else default_url
    output_file = sys.argv[2] if len(sys.argv) > 2 else "horizon_image.png"
    
    download_horizon_image(url, output_file)

if __name__ == "__main__":
    main()

# Made with Bob
