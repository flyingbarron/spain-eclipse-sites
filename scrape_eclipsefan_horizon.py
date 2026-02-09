#!/usr/bin/env python3
"""
Scrape eclipse horizon profile image from EclipseFan.org
Uses Selenium to render the JavaScript-generated horizon image
"""

import csv
import sys
import os
import time
from urllib.parse import urlencode

def read_site_coordinates(site_code, csv_file='data/eclipse_site_data_with_cloud.csv'):
    """Read site coordinates from CSV file"""
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['code'].upper() == site_code.upper():
                    return {
                        'code': row['code'],
                        'name': row['denominacion'],
                        'latitude': float(row['latitude']),
                        'longitude': float(row['longitude'])
                    }
    except FileNotFoundError:
        print(f"Error: CSV file not found: {csv_file}")
        return None
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return None
    
    return None

def scrape_eclipsefan_horizon(site_code):
    """Scrape horizon profile image from EclipseFan.org using Selenium"""
    
    # Check if selenium is installed
    try:
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.chrome.options import Options
    except ImportError:
        print("Error: Selenium is not installed")
        print("Install it with: pip install selenium")
        print("\nYou may also need to install ChromeDriver:")
        print("  brew install chromedriver  (macOS)")
        print("  Or download from: https://chromedriver.chromium.org/")
        return False
    
    # Read site coordinates
    site = read_site_coordinates(site_code)
    if not site:
        print(f"Error: Site code '{site_code}' not found in CSV")
        return False
    
    print(f"Found site: {site['name']} ({site['code']})")
    print(f"Coordinates: {site['latitude']}, {site['longitude']}")
    
    # Build EclipseFan URL
    params = {
        'lat': site['latitude'],
        'lng': site['longitude'],
        'zoom': 6,
        'oz': 5,
        'lang': 'en'
    }
    eclipsefan_url = f"https://www.eclipsefan.org/?{urlencode(params)}"
    print(f"\nEclipseFan URL: {eclipsefan_url}")
    
    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # Run in background
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--window-size=1920,1080')
    
    driver = None
    try:
        print("\nLaunching Chrome browser...")
        driver = webdriver.Chrome(options=chrome_options)
        
        print("Loading EclipseFan page...")
        driver.get(eclipsefan_url)
        
        # Wait for initial page load
        print("Waiting for initial page load...")
        time.sleep(2)
        
        # Fill in the modal form and submit
        print("Filling in coordinates in modal...")
        form_result = driver.execute_script("""
            const latInput = document.getElementById('modal-lat');
            const lngInput = document.getElementById('modal-lng');
            const okButton = document.getElementById('modal-ok');
            
            if (latInput && lngInput && okButton) {
                latInput.value = arguments[0];
                lngInput.value = arguments[1];
                
                // Trigger input events
                latInput.dispatchEvent(new Event('input', { bubbles: true }));
                lngInput.dispatchEvent(new Event('input', { bubbles: true }));
                
                // Click OK
                okButton.click();
                return 'Form submitted';
            }
            return 'Form not found';
        """, site['latitude'], site['longitude'])
        
        print(f"Form result: {form_result}")
        
        if "submitted" in form_result:
            print("Waiting for eclipse data to load...")
            time.sleep(8)
        else:
            print("Could not submit form, trying to proceed anyway...")
            time.sleep(3)
        
        # Now try to find and click the Horizon tab
        print("\nLooking for Horizon tab...")
        
        # Get page text to see what's available
        all_text = driver.execute_script("return document.body.innerText;")
        
        if "Horizon" in all_text or "horizon" in all_text.lower():
            print("Found 'Horizon' text on page")
            
            # Try to click it using JavaScript
            click_result = driver.execute_script("""
                // Look for elements containing "Horizon"
                const elements = Array.from(document.querySelectorAll('*'));
                for (let el of elements) {
                    const text = el.textContent ? el.textContent.trim() : '';
                    if (text === 'Horizon' || text.toLowerCase() === 'horizon') {
                        // Make sure it's clickable (button, link, or has click handler)
                        if (el.tagName === 'BUTTON' || el.tagName === 'A' ||
                            el.onclick || el.getAttribute('role') === 'tab') {
                            console.log('Found Horizon element:', el.tagName, el.className);
                            el.click();
                            return 'Clicked: ' + el.tagName + ' ' + el.className;
                        }
                    }
                }
                return 'Not found';
            """)
            print(f"Click result: {click_result}")
            
            if "Clicked" in click_result:
                print("Waiting for horizon content to load...")
                time.sleep(5)
            else:
                print("Could not click Horizon tab")
        else:
            print("'Horizon' text not found on page")
            print(f"Page text preview: {all_text[:300]}")
        
        # Look for canvas or image elements
        print("\nSearching for horizon image...")
        
        # Create output directory
        output_dir = 'data/eclipsefan_horizons'
        os.makedirs(output_dir, exist_ok=True)
        
        # Save page source for inspection
        html_file = os.path.join(output_dir, f'{site["code"]}_page_rendered.html')
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print(f"Saved rendered HTML to: {html_file}")
        
        # Try to find canvas elements
        canvases = driver.find_elements(By.TAG_NAME, "canvas")
        if canvases:
            print(f"\nFound {len(canvases)} canvas element(s)")
            for i, canvas in enumerate(canvases):
                try:
                    # Get canvas as PNG
                    canvas_base64 = driver.execute_script(
                        "return arguments[0].toDataURL('image/png').substring(21);", 
                        canvas
                    )
                    
                    # Save canvas image
                    import base64
                    canvas_file = os.path.join(output_dir, f'{site["code"]}_canvas_{i}.png')
                    with open(canvas_file, 'wb') as f:
                        f.write(base64.b64decode(canvas_base64))
                    print(f"  Saved canvas {i+1} to: {canvas_file}")
                except Exception as e:
                    print(f"  Could not save canvas {i+1}: {e}")
        
        # Try to find img elements
        images = driver.find_elements(By.TAG_NAME, "img")
        if images:
            print(f"\nFound {len(images)} img element(s)")
            for i, img in enumerate(images):
                try:
                    src = img.get_attribute('src')
                    if src and ('horizon' in src.lower() or 'profile' in src.lower() or 'eclipse' in src.lower()):
                        print(f"  Image {i+1}: {src[:100]}...")
                except:
                    pass
        
        # Take a full page screenshot
        screenshot_file = os.path.join(output_dir, f'{site["code"]}_screenshot.png')
        driver.save_screenshot(screenshot_file)
        print(f"\nSaved full page screenshot to: {screenshot_file}")
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if driver:
            driver.quit()

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 scrape_eclipsefan_horizon.py <SITE_CODE>")
        print("Example: python3 scrape_eclipsefan_horizon.py IB200")
        print("\nNote: Requires Selenium and ChromeDriver to be installed")
        sys.exit(1)
    
    site_code = sys.argv[1]
    print("=" * 60)
    print("EclipseFan Horizon Profile Scraper")
    print("=" * 60)
    print()
    
    success = scrape_eclipsefan_horizon(site_code)
    
    if success:
        print("\n✓ Scraping completed")
        print("  Check the output directory for images")
    else:
        print("\n✗ Failed to scrape horizon profile")
        sys.exit(1)

if __name__ == "__main__":
    main()

# Made with Bob
