#!/usr/bin/env python3
"""
Download shadow map export from Shademap.app with specific time set via JavaScript.
This version loads the page first, then sets the time programmatically.

Requires: pip install selenium
Works with Safari (built-in WebDriver on macOS)
"""

import sys
import time
import os
from selenium import webdriver
from selenium.webdriver.safari.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def download_shademap_export(lat, lon, timestamp_ms, output_dir="data", output_filename="shademap_export.jpg"):
    """
    Open Shademap, set time via JavaScript, dismiss popup, zoom in, and export as JPG.
    
    Args:
        lat: Latitude
        lon: Longitude
        timestamp_ms: Unix timestamp in milliseconds
        output_dir: Directory to save the exported file
        output_filename: Name for the output file
    """
    # Construct base URL without timestamp (Shademap will use current time)
    base_url = f"https://shademap.app/@{lat},{lon},20z"
    
    print(f"Opening Shademap at coordinates: {lat}, {lon}")
    print(f"Will set time to: {timestamp_ms} ms (August 12, 2026 eclipse)")
    print("\nNote: Make sure 'Allow Remote Automation' is enabled in Safari > Develop menu")
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    safari_options = Options()
    
    # Initialize the driver
    try:
        driver = webdriver.Safari(options=safari_options)
        driver.set_window_size(1920, 1080)
        
    except Exception as e:
        print(f"Error initializing Safari driver: {e}")
        print("\nPlease ensure 'Allow Remote Automation' is enabled in Safari > Develop menu")
        sys.exit(1)
    
    try:
        # Load the page
        print("\nLoading Shademap page...")
        driver.get(base_url)
        
        # Wait for page to load
        print("Waiting for page to load...")
        time.sleep(10)
        
        # Try to set the time via JavaScript
        print(f"\nAttempting to set time to {timestamp_ms}...")
        try:
            # Shademap might store time in a global variable or state
            # Try different approaches to set the time
            
            # Approach 1: Try to find and manipulate time controls
            js_set_time = f"""
            // Try to set time via Shademap's internal state
            if (window.shademap) {{
                window.shademap.setTime({timestamp_ms});
            }}
            // Or try setting via URL hash
            window.location.hash = window.location.hash.replace(/,\\d+t/, ',{timestamp_ms}t');
            """
            driver.execute_script(js_set_time)
            time.sleep(2)
            print("✓ Time set via JavaScript")
            
        except Exception as e:
            print(f"⚠️  Could not set time via JavaScript: {e}")
            print("Continuing with current time...")
        
        # Take a screenshot to see current state
        initial_screenshot = os.path.join(output_dir, "shademap_with_time_initial.png")
        driver.save_screenshot(initial_screenshot)
        print(f"Initial screenshot saved to: {initial_screenshot}")
        
        # Step 1: Click "OK" to dismiss popup
        print("\nLooking for popup to dismiss...")
        popup_selectors = [
            (By.XPATH, "//button[contains(text(), 'OK')]"),
            (By.XPATH, "//button[contains(text(), 'Ok')]"),
            (By.XPATH, "//button"),
        ]
        
        popup_dismissed = False
        for by, selector in popup_selectors:
            try:
                elements = driver.find_elements(by, selector)
                for element in elements:
                    try:
                        text = element.text.strip().upper()
                        if 'OK' in text or element.is_displayed():
                            element.click()
                            popup_dismissed = True
                            print("✓ Popup dismissed")
                            time.sleep(2)
                            break
                    except:
                        continue
                if popup_dismissed:
                    break
            except:
                continue
        
        # Step 2: Zoom in 3 times
        print("\nZooming in 3 times...")
        zoom_selectors = [
            (By.CSS_SELECTOR, "button[aria-label*='Zoom in']"),
            (By.XPATH, "//button[contains(text(), '+')]"),
        ]
        
        zoom_button = None
        for by, selector in zoom_selectors:
            try:
                zoom_button = driver.find_element(by, selector)
                if zoom_button and zoom_button.is_displayed():
                    print(f"Found zoom button")
                    break
            except:
                continue
        
        if zoom_button:
            for i in range(3):
                try:
                    zoom_button.click()
                    print(f"  Zoom {i+1}/3")
                    time.sleep(1.5)
                except:
                    pass
        
        # Step 3: Click export
        print("\nLooking for export button...")
        export_selectors = [
            (By.CSS_SELECTOR, "button[aria-label*='Export']"),
            (By.XPATH, "//*[contains(text(), 'Export')]"),
        ]
        
        for by, selector in export_selectors:
            try:
                export_button = driver.find_element(by, selector)
                if export_button and export_button.is_displayed():
                    export_button.click()
                    print("✓ Export button clicked")
                    time.sleep(3)
                    break
            except:
                continue
        
        # Step 4: Click JPG
        print("\nLooking for JPG option...")
        jpg_selectors = [
            (By.XPATH, "//button[contains(text(), 'JPG')]"),
            (By.XPATH, "//*[contains(text(), 'JPG')]"),
        ]
        
        for by, selector in jpg_selectors:
            try:
                jpg_button = driver.find_element(by, selector)
                if jpg_button:
                    jpg_button.click()
                    print("✓ JPG export initiated")
                    break
            except:
                continue
        
        # Wait for download
        print("\nWaiting for download...")
        time.sleep(5)
        
        # Take final screenshot
        final_screenshot = os.path.join(output_dir, "shademap_with_time_final.png")
        driver.save_screenshot(final_screenshot)
        print(f"Final screenshot saved to: {final_screenshot}")
        
        print(f"\n✓ Export process completed!")
        print(f"Check your Downloads folder for the exported file")
        
        print("\nBrowser window will close in 5 seconds...")
        time.sleep(5)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        
        debug_file = os.path.join(output_dir, "shademap_time_error.png")
        driver.save_screenshot(debug_file)
        print(f"\nDebug screenshot saved to: {debug_file}")
        sys.exit(1)
        
    finally:
        driver.quit()

def main():
    # Eclipse location and time
    lat = 42.13096
    lon = -2.15972
    timestamp_ms = 1786559455614  # August 12, 2026, 18:30:55 UTC (eclipse time)
    
    # Allow custom values from command line
    if len(sys.argv) > 1:
        lat = float(sys.argv[1])
    if len(sys.argv) > 2:
        lon = float(sys.argv[2])
    if len(sys.argv) > 3:
        timestamp_ms = int(sys.argv[3])
    
    download_shademap_export(lat, lon, timestamp_ms)

if __name__ == "__main__":
    main()

# Made with Bob
