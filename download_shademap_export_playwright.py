#!/usr/bin/env python3
"""
Download shadow map export from Shademap.app using Playwright.
This script automates the process of opening Shademap, dismissing popups,
zooming in, and exporting the shadow visualization.

Requires: pip install playwright
Also requires: playwright install chromium

Playwright is more reliable than Selenium for modern web apps.
"""

import sys
import time
import os
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

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
    
    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(
            headless=headless,
            args=[
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-blink-features=AutomationControlled'
            ]
        )
        
        # Create context with download path
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            accept_downloads=True
        )
        
        # Create page
        page = context.new_page()
        
        try:
            # Load the page
            print("Loading Shademap page...")
            print(f"URL: {url}")
            
            page.goto(url, wait_until='networkidle', timeout=30000)
            
            # Wait for page to be fully loaded
            print("Waiting for page to load...")
            time.sleep(8)
            
            print("✓ Page loaded successfully")
            
            # Step 1: Click "OK" to dismiss popup
            print("\nLooking for popup to dismiss...")
            popup_selectors = [
                'button:has-text("OK")',
                'button:has-text("Ok")',
                'button:has-text("ok")',
                'button.ok',
                'button[type="button"]',
                'button:has-text("Close")',
            ]
            
            popup_dismissed = False
            for selector in popup_selectors:
                try:
                    button = page.locator(selector).first
                    if button.is_visible(timeout=3000):
                        print(f"Found popup button with selector: {selector}")
                        button.click()
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
                'button[aria-label*="Zoom in"]',
                'button.zoom-in',
                'button[title*="Zoom in"]',
                'button:has-text("+")',
            ]
            
            zoom_button = None
            for selector in zoom_selectors:
                try:
                    button = page.locator(selector).first
                    if button.is_visible(timeout=5000):
                        zoom_button = button
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
                'button[aria-label*="Export"]',
                'button[title*="Export"]',
                'button.export',
                'button:has-text("Export")',
            ]
            
            export_clicked = False
            for selector in export_selectors:
                try:
                    button = page.locator(selector).first
                    if button.is_visible(timeout=5000):
                        print(f"Found export button with selector: {selector}")
                        button.click()
                        export_clicked = True
                        print("✓ Export button clicked")
                        time.sleep(2)
                        break
                except:
                    continue
            
            if not export_clicked:
                print("⚠️  Could not find export button")
                # Take a screenshot for debugging
                debug_file = "shademap_playwright_debug.png"
                page.screenshot(path=debug_file)
                print(f"Debug screenshot saved to: {debug_file}")
            
            # Step 4: Click JPG to save
            print("\nLooking for JPG export option...")
            jpg_selectors = [
                'button:has-text("JPG")',
                'button:has-text("jpg")',
                'button[data-format="jpg"]',
                'button[data-format="jpeg"]',
            ]
            
            jpg_clicked = False
            for selector in jpg_selectors:
                try:
                    button = page.locator(selector).first
                    if button.is_visible(timeout=5000):
                        print(f"Found JPG button with selector: {selector}")
                        
                        # Set up download handler
                        with page.expect_download(timeout=10000) as download_info:
                            button.click()
                        
                        download = download_info.value
                        jpg_clicked = True
                        print("✓ JPG export initiated")
                        
                        # Save the download
                        output_path = os.path.join(output_dir, output_filename)
                        download.save_as(output_path)
                        print(f"✓ File saved to: {output_path}")
                        break
                except Exception as e:
                    print(f"Error with selector {selector}: {e}")
                    continue
            
            if not jpg_clicked:
                print("⚠️  Could not find JPG button")
                # Wait a bit in case download started anyway
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
            debug_file = "shademap_playwright_error_debug.png"
            page.screenshot(path=debug_file)
            print(f"\nDebug screenshot saved to: {debug_file}")
            sys.exit(1)
            
        finally:
            browser.close()

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