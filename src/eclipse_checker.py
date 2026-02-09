"""
Eclipse Visibility Checker Module
Functions for checking eclipse visibility using IGN Eclipse 2026 viewer
"""

import math
import time
import os
from typing import List, Dict, Any, Tuple, Optional

# Data directory for outputs
DATA_DIR = "data"
PROFILES_DIR = os.path.join(DATA_DIR, "ign_visibility_profiles")
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException


def wgs84_to_web_mercator(lat: float, lon: float) -> Tuple[float, float]:
    """Convert WGS84 (lat/lon) to Web Mercator (EPSG:3857) coordinates
    
    Args:
        lat: Latitude in decimal degrees
        lon: Longitude in decimal degrees
    
    Returns:
        Tuple of (x, y) in Web Mercator
    """
    x = lon * 20037508.34 / 180
    y = math.log(math.tan((90 + lat) * math.pi / 360)) / (math.pi / 180)
    y_mercator = y * 20037508.34 / 180
    return x, y_mercator


def setup_webdriver() -> Optional[webdriver.Chrome]:
    """Setup and return a Chrome WebDriver instance
    
    Returns:
        WebDriver instance or None if setup fails
    """
    print("Setting up Chrome WebDriver...")
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        print("✓ WebDriver ready")
        return driver
    except Exception as e:
        print(f"⚠️  Could not start WebDriver: {e}")
        return None


def check_eclipse_visibility(driver: webdriver.Chrome, lat: float, lon: float, code: str, save_profile: bool = True) -> str:
    """Check if eclipse is visible from given coordinates
    
    Args:
        driver: Selenium WebDriver instance
        lat: Latitude in decimal degrees
        lon: Longitude in decimal degrees
        code: Site code for saving profile image
        save_profile: Whether to save the profile diagram screenshot (default: True)
    
    Returns:
        String indicating visibility status: 'visible', 'not_visible', 'unknown', 'timeout', or 'error'
    """
    try:
        x, y_mercator = wgs84_to_web_mercator(lat, lon)
        url = f"https://visualizadores.ign.es/eclipses/2026?center={x},{y_mercator}&zoom=16&srs=EPSG:3857"
        
        print(f"  Checking eclipse visibility...")
        driver.get(url)
        
        try:
            # Wait for main loading container to disappear
            WebDriverWait(driver, 60).until_not(
                EC.presence_of_element_located((By.CLASS_NAME, "block-loader-container"))
            )
            
            # Wait for visibility profile loader to disappear
            WebDriverWait(driver, 30).until_not(
                EC.presence_of_element_located((By.CLASS_NAME, "loader-overlay-profile"))
            )
            
            print(f"  Page loaded, waiting for profile diagram...")
            
            # Wait for profile diagram to render
            try:
                WebDriverWait(driver, 10).until(
                    lambda d: d.find_element(By.CSS_SELECTOR, ".profile-container svg") or 
                              d.find_element(By.CSS_SELECTOR, ".profile-container canvas")
                )
                time.sleep(3)  # Extra time for full render
            except TimeoutException:
                time.sleep(2)
            
            # Capture profile diagram screenshot (if enabled)
            if save_profile:
                try:
                    try:
                        profile_element = driver.find_element(By.CSS_SELECTOR, ".profile-container svg")
                    except:
                        try:
                            profile_element = driver.find_element(By.CSS_SELECTOR, ".profile-container canvas")
                        except:
                            profile_element = driver.find_element(By.CLASS_NAME, "profile-container")
                    
                    os.makedirs(PROFILES_DIR, exist_ok=True)
                    profile_path = os.path.join(PROFILES_DIR, f"{code}_profile.png")
                    profile_element.screenshot(profile_path)
                    print(f"  📊 Saved profile to {profile_path}")
                except Exception as e:
                    print(f"  ⚠️  Could not capture profile: {e}")
            else:
                print(f"  ⏭️  Skipping profile screenshot (--no-profile flag)")
            
            # Check visibility text
            page_source = driver.page_source
            page_lower = page_source.lower()
            
            if "is not" in page_lower and "visible from the observation point" in page_lower:
                print(f"  ✗ Eclipse NOT visible")
                return "not_visible"
            elif "is visible from the observation point" in page_lower or "is</strong> visible from the observation point" in page_lower:
                print(f"  ✓ Eclipse IS visible")
                return "visible"
            else:
                print(f"  ? Could not determine visibility")
                return "unknown"
                
        except TimeoutException:
            print(f"  ✗ Timeout waiting for page to load")
            return "timeout"
            
    except Exception as e:
        print(f"  ✗ Error checking eclipse: {str(e)}")
        return "error"


def check_sites_eclipse_visibility(sites: List[Dict[str, Any]], save_profiles: bool = True) -> List[Dict[str, Any]]:
    """Check eclipse visibility for multiple sites
    
    Args:
        sites: List of site dictionaries with 'code', 'latitude', 'longitude'
        save_profiles: Whether to save profile diagram screenshots (default: True)
    
    Returns:
        List of site dictionaries with added 'eclipse_visibility' field
    """
    driver = setup_webdriver()
    if not driver:
        print("⚠️  Continuing without eclipse visibility checking...")
        for site in sites:
            site['eclipse_visibility'] = 'not_checked'
        return sites
    
    try:
        for site in sites:
            code = site['code']
            lat_str = site.get('latitude', 'N/A')
            lon_str = site.get('longitude', 'N/A')
            
            # Skip sites without coordinates
            if lat_str == 'N/A' or lon_str == 'N/A':
                print(f"\n[{code}] Skipping - no coordinates")
                site['eclipse_visibility'] = 'no_coordinates'
                continue
            
            try:
                lat = float(lat_str)
                lon = float(lon_str)
                
                print(f"\n[{code}] Checking eclipse visibility...")
                visibility = check_eclipse_visibility(driver, lat, lon, code, save_profile=save_profiles)
                site['eclipse_visibility'] = visibility
                
                time.sleep(1)  # Small delay between sites
                
            except ValueError:
                print(f"\n[{code}] Skipping - invalid coordinates")
                site['eclipse_visibility'] = 'invalid_coordinates'
    
    finally:
        driver.quit()
        print("\n✓ Browser closed")
    
    return sites

# Made with Bob
