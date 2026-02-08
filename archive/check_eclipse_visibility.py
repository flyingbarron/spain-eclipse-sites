#!/usr/bin/env python3
"""
Check eclipse visibility for all sites in the CSV file.
Queries the IGN Eclipse 2026 viewer for each site and determines visibility.
Requires Selenium and a web driver (Chrome/Firefox) to render JavaScript.
"""

import csv
import time
import math
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException

def wgs84_to_web_mercator(lat, lon):
    """Convert WGS84 (lat/lon) to Web Mercator (EPSG:3857) coordinates"""
    x = lon * 20037508.34 / 180
    y = math.log(math.tan((90 + lat) * math.pi / 360)) / (math.pi / 180)
    y_mercator = y * 20037508.34 / 180
    return x, y_mercator

def check_eclipse_visibility(driver, lat, lon, code):
    """Check if eclipse is visible from the given coordinates using Selenium"""
    try:
        # Convert coordinates to Web Mercator
        x, y_mercator = wgs84_to_web_mercator(lat, lon)
        
        # Construct the IGN Eclipse viewer URL
        url = f"https://visualizadores.ign.es/eclipses/2026?center={x},{y_mercator}&zoom=16&srs=EPSG:3857"
        
        print(f"Checking {code} ({lat}, {lon})...")
        print(f"  URL: {url}")
        
        # Load the page
        driver.get(url)
        
        # Wait for BOTH loading spinners to disappear
        # The page shows two loading spinners:
        # 1. Main page loader: "block-loader-container"
        # 2. Visibility profile loader: "loader-overlay-profile"
        try:
            print(f"  Waiting for page to load...")
            
            # Wait for the main loading container to disappear (up to 60 seconds)
            WebDriverWait(driver, 60).until_not(
                EC.presence_of_element_located((By.CLASS_NAME, "block-loader-container"))
            )
            
            print(f"  Main page loaded, waiting for visibility profile...")
            
            # Wait for the visibility profile loader to disappear (up to 30 seconds)
            WebDriverWait(driver, 30).until_not(
                EC.presence_of_element_located((By.CLASS_NAME, "loader-overlay-profile"))
            )
            
            print(f"  All loading complete, waiting for profile diagram to render...")
            
            # Wait for the profile diagram SVG/canvas to be present and fully rendered
            try:
                # Wait for SVG or canvas element to appear (up to 10 seconds)
                WebDriverWait(driver, 10).until(
                    lambda d: d.find_element(By.CSS_SELECTOR, ".profile-container svg") or
                              d.find_element(By.CSS_SELECTOR, ".profile-container canvas")
                )
                print(f"  Profile diagram element found, waiting for render...")
                
                # Give extra time for the diagram to fully render (SVG paths, etc.)
                time.sleep(3)
                
            except TimeoutException:
                print(f"  ⚠️  Profile diagram element not found, proceeding anyway...")
                time.sleep(2)
            
            # Take a screenshot of the visibility profile
            try:
                # Try to find the SVG element inside the profile container
                # This should contain just the diagram without the text
                try:
                    # First try to find the SVG directly
                    profile_element = driver.find_element(By.CSS_SELECTOR, ".profile-container svg")
                    print(f"  Found SVG element for profile")
                except:
                    # Fallback to the canvas if SVG not found
                    try:
                        profile_element = driver.find_element(By.CSS_SELECTOR, ".profile-container canvas")
                        print(f"  Found canvas element for profile")
                    except:
                        # Last resort: use the profile-container but try to crop better
                        profile_element = driver.find_element(By.CLASS_NAME, "profile-container")
                        print(f"  Using profile-container (may include text)")
                
                # Create eclipse_profiles directory if it doesn't exist
                os.makedirs("eclipse_profiles", exist_ok=True)
                
                # Save screenshot of the profile
                profile_path = f"eclipse_profiles/{code}_profile.png"
                profile_element.screenshot(profile_path)
                print(f"  📊 Saved visibility profile to {profile_path}")
            except Exception as e:
                print(f"  ⚠️  Could not capture profile diagram: {e}")
            
            # Get the page source
            page_source = driver.page_source
            
            # Look for the visibility text in the page
            # The IGN viewer displays: "The eclipse IS NOT visible from the observation point"
            # or "The eclipse IS visible from the observation point"
            
            page_lower = page_source.lower()
            
            # Check for the specific visibility messages
            if "is not" in page_lower and "visible from the observation point" in page_lower:
                print(f"  ✗ Eclipse NOT visible")
                return "not_visible"
            elif "is visible from the observation point" in page_lower or "is</strong> visible from the observation point" in page_lower:
                print(f"  ✓ Eclipse IS visible")
                return "visible"
            else:
                # Couldn't find the expected text
                print(f"  ? Could not determine visibility")
                with open(f"debug_{code}.html", "w", encoding="utf-8") as f:
                    f.write(page_source)
                print(f"  Saved page to debug_{code}.html for inspection")
                return "unknown"
                
        except TimeoutException:
            print(f"  ✗ Timeout: Loading spinner didn't disappear after 60 seconds")
            # Save the page for debugging
            with open(f"debug_{code}_timeout.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            return "timeout"
            
    except Exception as e:
        print(f"  ✗ Error: {str(e)}")
        return "error"

def main():
    print("=" * 60)
    print("Eclipse Visibility Checker for IGME Sites")
    print("=" * 60)
    print()
    
    # Setup Selenium WebDriver
    print("Setting up Chrome WebDriver...")
    chrome_options = Options()
    # Note: Headless mode doesn't work with this IGN viewer - the JavaScript doesn't execute properly
    # The script will open visible Chrome windows, but this is necessary for the viewer to work
    # chrome_options.add_argument('--headless=new')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--window-size=1920,1080')
    # Add user agent to avoid detection
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
    except Exception as e:
        print(f"Error: Could not start Chrome WebDriver: {e}")
        print("\nPlease install Selenium and ChromeDriver:")
        print("  pip install selenium")
        print("  brew install chromedriver  # On macOS")
        return
    
    print("✓ WebDriver ready")
    print()
    
    # Read the CSV file
    sites = []
    try:
        with open('igme_tourist_values.csv', 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                sites.append(row)
    except FileNotFoundError:
        print("Error: igme_tourist_values.csv not found!")
        print("Please run scrape_igme_sites.py first to generate the CSV file.")
        driver.quit()
        return
    
    print(f"Found {len(sites)} sites in CSV")
    print("-" * 60)
    print()
    
    # Check each site
    results = []
    try:
        for site in sites:
            code = site['code']
            lat_str = site['latitude']
            lon_str = site['longitude']
            
            # Skip sites without coordinates
            if lat_str == 'N/A' or lon_str == 'N/A':
                print(f"Skipping {code} - no coordinates")
                results.append({
                    'code': code,
                    'denominacion': site['denominacion'],
                    'latitude': lat_str,
                    'longitude': lon_str,
                    'eclipse_visibility': 'no_coordinates'
                })
                continue
            
            try:
                lat = float(lat_str)
                lon = float(lon_str)
                
                visibility = check_eclipse_visibility(driver, lat, lon, code)
                
                results.append({
                    'code': code,
                    'denominacion': site['denominacion'],
                    'latitude': lat_str,
                    'longitude': lon_str,
                    'eclipse_visibility': visibility
                })
                
                # Small delay between sites
                time.sleep(1)
                
            except ValueError:
                print(f"Skipping {code} - invalid coordinates")
                results.append({
                    'code': code,
                    'denominacion': site['denominacion'],
                    'latitude': lat_str,
                    'longitude': lon_str,
                    'eclipse_visibility': 'invalid_coordinates'
                })
    finally:
        # Always close the browser
        driver.quit()
        print()
        print("✓ Browser closed")
    
    # Save results to new CSV
    output_file = 'eclipse_visibility_results.csv'
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['code', 'denominacion', 'latitude', 'longitude', 'eclipse_visibility']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for result in results:
            writer.writerow(result)
    
    # Print summary
    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    visible = sum(1 for r in results if r['eclipse_visibility'] == 'visible')
    partial = sum(1 for r in results if r['eclipse_visibility'] == 'partial')
    not_visible = sum(1 for r in results if r['eclipse_visibility'] == 'not_visible')
    errors = sum(1 for r in results if r['eclipse_visibility'] == 'error')
    no_coords = sum(1 for r in results if r['eclipse_visibility'] in ['no_coordinates', 'invalid_coordinates'])
    
    print(f"Total sites checked: {len(results)}")
    print(f"Eclipse visible (in path): {visible}")
    print(f"Eclipse partial (near path): {partial}")
    print(f"Eclipse NOT visible: {not_visible}")
    print(f"Errors: {errors}")
    print(f"No/invalid coordinates: {no_coords}")
    print()
    print("Note: Visibility determined by geographic location relative to")
    print("      the 2026 eclipse path across northern Spain (41°N-44°N)")
    print()
    print(f"✓ Results saved to {output_file}")

if __name__ == "__main__":
    main()

# Made with Bob
