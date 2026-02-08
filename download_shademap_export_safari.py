#!/usr/bin/env python3
"""
Download shadow map export from Shademap.app using Safari.
Safari has built-in WebDriver support on macOS.

Requires: pip install selenium
Also requires: Enable "Allow Remote Automation" in Safari's Develop menu
"""

import sys
import time
import os
from selenium import webdriver
from selenium.webdriver.safari.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def download_shademap_export(url, output_dir="data", output_filename="shademap_export.jpg"):
    """
    Open Shademap with Safari, dismiss popup, zoom in, and export as JPG.
    
    Args:
        url: The Shademap URL with location and time parameters
        output_dir: Directory to save the exported file
        output_filename: Name for the output file
    """
    print(f"Opening Shademap with Safari: {url}")
    print("\nNote: Make sure 'Allow Remote Automation' is enabled in Safari > Develop menu")
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Safari doesn't support headless mode
    # Safari options are limited compared to Chrome/Firefox
    safari_options = Options()
    
    # Initialize the driver
    try:
        driver = webdriver.Safari(options=safari_options)
        driver.set_window_size(1920, 1080)
        
    except Exception as e:
        print(f"Error initializing Safari driver: {e}")
        print("\nPlease ensure you have:")
        print("1. Safari browser (comes with macOS)")
        print("2. Enabled 'Allow Remote Automation' in Safari > Develop menu")
        print("   (If you don't see Develop menu, enable it in Safari > Preferences > Advanced)")
        print("3. selenium installed (pip install selenium)")
        sys.exit(1)
    
    try:
        # Load the page
        print("\nLoading Shademap page...")
        print(f"URL: {url}")
        driver.get(url)
        
        # Wait for page to load
        print("Waiting for page to load...")
        time.sleep(12)  # Safari may need more time
        
        # Check if page loaded
        try:
            WebDriverWait(driver, 15).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            print("✓ Page loaded successfully")
        except:
            print("⚠️  Page may not have loaded completely")
        
        # Take a screenshot to see what loaded
        initial_screenshot = os.path.join(output_dir, "shademap_safari_initial.png")
        driver.save_screenshot(initial_screenshot)
        print(f"Initial screenshot saved to: {initial_screenshot}")
        
        # Step 1: Click "OK" to dismiss popup
        print("\nLooking for popup to dismiss...")
        popup_selectors = [
            (By.XPATH, "//button[contains(text(), 'OK')]"),
            (By.XPATH, "//button[contains(text(), 'Ok')]"),
            (By.XPATH, "//button[contains(text(), 'ok')]"),
            (By.CSS_SELECTOR, "button.ok"),
            (By.XPATH, "//button"),
            (By.XPATH, "//*[contains(text(), 'OK')]"),
        ]
        
        popup_dismissed = False
        for by, selector in popup_selectors:
            try:
                elements = driver.find_elements(by, selector)
                for element in elements:
                    try:
                        text = element.text.strip().upper()
                        if 'OK' in text or element.is_displayed():
                            print(f"Found button: '{element.text}' with selector: {selector}")
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
        
        if not popup_dismissed:
            print("⚠️  No popup found (or already dismissed)")
        
        # Step 2: Zoom in 3 times using the + button
        print("\nZooming in 3 times...")
        zoom_selectors = [
            (By.CSS_SELECTOR, "button[aria-label*='Zoom in']"),
            (By.CSS_SELECTOR, "button[title*='Zoom in']"),
            (By.XPATH, "//button[contains(@aria-label, 'Zoom')]"),
            (By.XPATH, "//button[contains(text(), '+')]"),
        ]
        
        zoom_button = None
        for by, selector in zoom_selectors:
            try:
                zoom_button = driver.find_element(by, selector)
                if zoom_button and zoom_button.is_displayed():
                    print(f"Found zoom button with selector: {selector}")
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
                    print(f"  Failed to click zoom button on attempt {i+1}")
            print("✓ Zoom attempts completed")
        else:
            print("⚠️  Could not find zoom button")
        
        # Step 3: Click the export icon
        print("\nLooking for export button...")
        export_selectors = [
            (By.CSS_SELECTOR, "button[aria-label*='Export']"),
            (By.CSS_SELECTOR, "button[title*='Export']"),
            (By.XPATH, "//button[contains(@aria-label, 'Export')]"),
            (By.XPATH, "//button[contains(@title, 'Export')]"),
            (By.XPATH, "//*[contains(text(), 'Export')]"),
        ]
        
        export_clicked = False
        for by, selector in export_selectors:
            try:
                export_button = driver.find_element(by, selector)
                if export_button and export_button.is_displayed():
                    print(f"Found export button with selector: {selector}")
                    export_button.click()
                    export_clicked = True
                    print("✓ Export button clicked")
                    time.sleep(3)
                    break
            except:
                continue
        
        if not export_clicked:
            print("⚠️  Could not find export button")
            # List all buttons for debugging
            all_buttons = driver.find_elements(By.TAG_NAME, "button")
            print(f"\nFound {len(all_buttons)} buttons on page:")
            for i, btn in enumerate(all_buttons[:10]):
                try:
                    print(f"  {i+1}. Text: '{btn.text}', aria-label: '{btn.get_attribute('aria-label')}'")
                except:
                    pass
        
        # Step 4: Click JPG to save
        print("\nLooking for JPG export option...")
        jpg_selectors = [
            (By.XPATH, "//button[contains(text(), 'JPG')]"),
            (By.XPATH, "//button[contains(text(), 'jpg')]"),
            (By.XPATH, "//*[contains(text(), 'JPG')]"),
            (By.XPATH, "//*[contains(text(), 'JPEG')]"),
        ]
        
        jpg_clicked = False
        for by, selector in jpg_selectors:
            try:
                jpg_button = driver.find_element(by, selector)
                if jpg_button:
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
        print("Note: Safari will download to your Downloads folder by default")
        time.sleep(5)
        
        # Take final screenshot
        final_screenshot = os.path.join(output_dir, "shademap_safari_final.png")
        driver.save_screenshot(final_screenshot)
        print(f"Final screenshot saved to: {final_screenshot}")
        
        print(f"\n✓ Export process completed!")
        print(f"Check your Downloads folder for the exported file")
        print(f"(Safari doesn't allow custom download directories)")
        
        print("\nBrowser window will close in 5 seconds...")
        time.sleep(5)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        
        # Take a screenshot for debugging
        debug_file = os.path.join(output_dir, "shademap_safari_error.png")
        driver.save_screenshot(debug_file)
        print(f"\nDebug screenshot saved to: {debug_file}")
        sys.exit(1)
        
    finally:
        driver.quit()

def main():
    # Default URL for the eclipse location (simplified)
    default_url = "https://shademap.app/@42.13096,-2.15972,20z,1786559455614t,0b,0p,0m"
    
    # Allow custom URL from command line
    url = sys.argv[1] if len(sys.argv) > 1 else default_url
    output_filename = sys.argv[2] if len(sys.argv) > 2 else "shademap_export.jpg"
    
    download_shademap_export(url, output_filename=output_filename)

if __name__ == "__main__":
    main()

# Made with Bob
