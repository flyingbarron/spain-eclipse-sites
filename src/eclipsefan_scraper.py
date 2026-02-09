"""
EclipseFan Horizon Scraper Module
Functions for downloading horizon profile images from EclipseFan.org
"""

import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Data directory for outputs
DATA_DIR = "data"
HORIZON_DIR = os.path.join(DATA_DIR, "eclipsefan_horizon")


def setup_webdriver(headless=True):
    """Setup and return a Chrome WebDriver instance for EclipseFan
    
    Args:
        headless: Whether to run in headless mode
    
    Returns:
        WebDriver instance or None if setup fails
    """
    print("Setting up Chrome WebDriver for EclipseFan...")
    chrome_options = Options()
    
    if headless:
        chrome_options.add_argument('--headless')
    
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
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
        
        print("✓ WebDriver ready")
        return driver
    except Exception as e:
        print(f"⚠️  Could not start WebDriver: {e}")
        return None


def download_horizon_image(driver, lat, lon, code):
    """Download horizon profile image from EclipseFan.org
    
    Args:
        driver: Selenium WebDriver instance
        lat: Latitude in decimal degrees
        lon: Longitude in decimal degrees
        code: Site code for saving image
    
    Returns:
        String indicating status: 'success', 'not_found', 'timeout', or 'error'
    """
    try:
        # Build EclipseFan URL
        url = f"https://www.eclipsefan.org/?lat={lat}&lng={lon}&zoom=6&oz=5&lang=en"
        
        print(f"  Loading EclipseFan page...")
        driver.get(url)
        
        # Wait for page to initialize
        time.sleep(3)
        
        # Look for and click the Horizon tab
        print(f"  Looking for Horizon tab...")
        horizon_clicked = False
        
        # Try to find Horizon tab by text
        try:
            elements = driver.find_elements(By.XPATH, "//*[contains(translate(text(), 'HORIZON', 'horizon'), 'horizon')]")
            for elem in elements:
                if 'horizon' in elem.text.lower():
                    elem.click()
                    horizon_clicked = True
                    print(f"  ✓ Clicked Horizon tab")
                    break
        except Exception as e:
            print(f"  ⚠️  Could not find Horizon tab: {e}")
            return 'not_found'
        
        if not horizon_clicked:
            print(f"  ✗ Horizon tab not found")
            return 'not_found'
        
        # Wait for horizon image to generate
        print(f"  Waiting for horizon image to render...")
        time.sleep(5)
        
        # Look for the skyline canvas
        try:
            canvas = driver.find_element(By.ID, 'skyline-canvas-v2')
            
            if canvas and canvas.is_displayed():
                # Create output directory
                os.makedirs(HORIZON_DIR, exist_ok=True)
                
                # Save canvas screenshot
                output_path = os.path.join(HORIZON_DIR, f"{code}_horizon.png")
                canvas.screenshot(output_path)
                print(f"  ✓ Saved horizon image to {output_path}")
                return 'success'
            else:
                print(f"  ✗ Canvas found but not displayed")
                return 'not_found'
                
        except NoSuchElementException:
            # Try fallback: look for any canvas in left sidebar
            try:
                canvases = driver.find_elements(By.TAG_NAME, 'canvas')
                for canvas in canvases:
                    if canvas.is_displayed():
                        location = canvas.location
                        width = canvas.size.get('width', 0)
                        height = canvas.size.get('height', 0)
                        x_pos = location.get('x', 0)
                        
                        # Look for canvas in left sidebar with reasonable size
                        if x_pos < 500 and width > 200 and height > 200:
                            os.makedirs(HORIZON_DIR, exist_ok=True)
                            output_path = os.path.join(HORIZON_DIR, f"{code}_horizon.png")
                            canvas.screenshot(output_path)
                            print(f"  ✓ Saved horizon image (fallback) to {output_path}")
                            return 'success'
                
                print(f"  ✗ No suitable canvas found")
                return 'not_found'
                
            except Exception as e:
                print(f"  ✗ Error in fallback: {e}")
                return 'error'
        
    except TimeoutException:
        print(f"  ✗ Timeout loading page")
        return 'timeout'
    except Exception as e:
        print(f"  ✗ Error downloading horizon: {str(e)}")
        return 'error'


def download_horizon_images_for_sites(sites, delay=2.0):
    """Download horizon images for multiple sites
    
    Args:
        sites: List of site dictionaries with 'code', 'latitude', 'longitude'
        delay: Delay in seconds between requests (default 2.0 for respectful scraping)
    
    Returns:
        List of site dictionaries with added 'horizon_status' field
    """
    driver = setup_webdriver(headless=True)
    if not driver:
        print("⚠️  Continuing without horizon image downloading...")
        for site in sites:
            site['horizon_status'] = 'not_checked'
        return sites
    
    try:
        for site in sites:
            code = site['code']
            lat_str = site.get('latitude', 'N/A')
            lon_str = site.get('longitude', 'N/A')
            
            # Skip sites without coordinates
            if lat_str == 'N/A' or lon_str == 'N/A':
                print(f"\n[{code}] Skipping - no coordinates")
                site['horizon_status'] = 'no_coordinates'
                continue
            
            try:
                lat = float(lat_str)
                lon = float(lon_str)
                
                print(f"\n[{code}] Downloading horizon image...")
                status = download_horizon_image(driver, lat, lon, code)
                site['horizon_status'] = status
                
                # Respectful delay between sites
                if delay > 0:
                    time.sleep(delay)
                
            except ValueError:
                print(f"\n[{code}] Skipping - invalid coordinates")
                site['horizon_status'] = 'invalid_coordinates'
    
    finally:
        driver.quit()
        print("\n✓ Browser closed")
    
    return sites


# Made with Bob