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
import csv
import argparse
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

def download_shademap_export(url, output_dir="../data/shademap_snapshot", output_filename="shademap_export.jpg", headless=False):
    """
    Open Shademap, dismiss popup, zoom in, and export as JPG.
    
    Args:
        url: The Shademap URL with location and time parameters
        output_dir: Directory to save the exported file
        output_filename: Name for the output file
        headless: Whether to run in headless mode (default: False - visible browser)
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
            
            # Step 2: Skip zooming - use default zoom level
            print("\nSkipping zoom (using default zoom level)...")
            
            # Step 3: Click settings cog to configure shadow display
            print("\nLooking for settings button...")
            settings_selectors = [
                'button[aria-label*="Settings"]',
                'button[aria-label*="settings"]',
                'button[title*="Settings"]',
                'button.settings',
                'button:has-text("Settings")',
                # SVG or icon-based buttons
                'button svg[class*="cog"]',
                'button svg[class*="gear"]',
                'button svg[class*="settings"]',
            ]
            
            settings_clicked = False
            for selector in settings_selectors:
                try:
                    button = page.locator(selector).first
                    if button.is_visible(timeout=5000):
                        print(f"Found settings button with selector: {selector}")
                        button.click()
                        settings_clicked = True
                        print("✓ Settings button clicked")
                        time.sleep(2)
                        break
                except:
                    continue
            
            if not settings_clicked:
                print("⚠️  Could not find settings button")
                # Take a screenshot for debugging
                debug_file = "shademap_settings_debug.png"
                page.screenshot(path=debug_file)
                print(f"Debug screenshot saved to: {debug_file}")
            else:
                # Step 3a: Select "current time" option
                print("\nLooking for 'current time' option...")
                current_time_selectors = [
                    'input[value*="current"]',
                    'input[id*="current"]',
                    'label:has-text("Current time")',
                    'label:has-text("current time")',
                    ':text("Current time")',
                    ':text("current time")',
                ]
                
                current_time_clicked = False
                for selector in current_time_selectors:
                    try:
                        element = page.locator(selector).first
                        if element.is_visible(timeout=3000):
                            print(f"Found 'current time' with selector: {selector}")
                            element.click()
                            current_time_clicked = True
                            print("✓ 'Current time' selected")
                            time.sleep(1)
                            break
                    except:
                        continue
                
                if not current_time_clicked:
                    print("⚠️  Could not find 'current time' option")
                
                # Step 3b: Select "sunset" option
                print("\nLooking for 'sunset' option...")
                sunset_selectors = [
                    'input[value*="sunset"]',
                    'input[id*="sunset"]',
                    'label:has-text("Sunset")',
                    'label:has-text("sunset")',
                    ':text("Sunset")',
                    ':text("sunset")',
                ]
                
                sunset_clicked = False
                for selector in sunset_selectors:
                    try:
                        element = page.locator(selector).first
                        if element.is_visible(timeout=3000):
                            print(f"Found 'sunset' with selector: {selector}")
                            element.click()
                            sunset_clicked = True
                            print("✓ 'Sunset' selected")
                            time.sleep(1)
                            break
                    except:
                        continue
                
                if not sunset_clicked:
                    print("⚠️  Could not find 'sunset' option")
                
                # Step 3c: Close the settings modal by clicking X button with "close" tooltip
                print("\nLooking for close button (has 'close' tooltip)...")
                
                close_selectors = [
                    # Button with title="close" (mouseover tooltip)
                    'button[title="close"]',
                    'button[title="Close"]',
                    # ARIA label
                    'button[aria-label="close"]',
                    'button[aria-label="Close"]',
                    # Try finding by the tooltip text using Playwright's getByTitle
                ]
                
                close_clicked = False
                
                # First try using Playwright's getByTitle which matches tooltip/title attribute
                try:
                    button = page.get_by_title("close", exact=False)
                    if button.is_visible(timeout=3000):
                        print("Found close button using getByTitle('close')")
                        button.click()
                        close_clicked = True
                        print("✓ Settings modal closed")
                        time.sleep(1)
                except Exception as e:
                    print(f"getByTitle failed: {e}")
                
                # If that didn't work, try the selectors
                if not close_clicked:
                    for selector in close_selectors:
                        try:
                            button = page.locator(selector).first
                            if button.is_visible(timeout=3000):
                                print(f"Found close button with selector: {selector}")
                                button.click()
                                close_clicked = True
                                print("✓ Settings modal closed")
                                time.sleep(1)
                                break
                        except:
                            continue
                
                if not close_clicked:
                    print("⚠️  Could not find close button")
                    # Take a screenshot for debugging
                    debug_file = "shademap_modal_close_debug.png"
                    page.screenshot(path=debug_file)
                    print(f"Debug screenshot saved to: {debug_file}")
            
            # Step 4: Click the export icon
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

def load_site_from_csv(site_code, csv_file="../data/eclipse_site_data.csv"):
    """Load a specific site from CSV by code
    
    Args:
        site_code: Site code to look for (e.g., 'IB200a')
        csv_file: Path to CSV file
    
    Returns:
        Dictionary with site data or None if not found
    """
    if not os.path.exists(csv_file):
        print(f"Error: {csv_file} not found")
        print("Please run generate_eclipse_site_data.py first")
        sys.exit(1)
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['code'] == site_code:
                lat = row.get('latitude', '').strip()
                lon = row.get('longitude', '').strip()
                
                if not lat or not lon or lat == 'N/A' or lon == 'N/A':
                    print(f"Error: Site {site_code} has no valid coordinates")
                    return None
                
                try:
                    return {
                        'code': row['code'],
                        'name': row.get('denominacion', row['code']),
                        'lat': float(lat),
                        'lon': float(lon)
                    }
                except ValueError:
                    print(f"Error: Site {site_code} has invalid coordinates: {lat}, {lon}")
                    return None
    
    print(f"Error: Site {site_code} not found in CSV")
    return None


def process_all_sites(csv_file="../data/eclipse_site_data.csv", zoom_level=19):
    """Process all sites from eclipse_site_data.csv
    
    Args:
        csv_file: Path to CSV file with site data
        zoom_level: Zoom level for Shademap (default: 19)
    """
    
    # Check if CSV file exists
    if not os.path.exists(csv_file):
        print(f"Error: {csv_file} not found")
        print("Please run generate_eclipse_site_data.py first")
        sys.exit(1)
    
    # Read sites from CSV
    sites = []
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            lat = row.get('latitude', '').strip()
            lon = row.get('longitude', '').strip()
            
            # Skip sites without valid coordinates
            if not lat or not lon or lat == 'N/A' or lon == 'N/A':
                continue
            
            try:
                sites.append({
                    'code': row['code'],
                    'name': row.get('denominacion', row['code']),
                    'lat': float(lat),
                    'lon': float(lon)
                })
            except ValueError:
                print(f"Warning: Skipping {row['code']} - invalid coordinates: {lat}, {lon}")
                continue
    
    print(f"Found {len(sites)} sites with coordinates")
    print("=" * 60)
    
    # Eclipse time in milliseconds (August 12, 2026)
    eclipse_time = "1786559455614"
    
    # Process each site
    for i, site in enumerate(sites, 1):
        print(f"\n[{i}/{len(sites)}] Processing {site['code']} - {site['name']}")
        print("-" * 60)
        
        # Build Shademap URL
        lat = site['lat']
        lon = site['lon']
        coords_base64 = btoa(f"{lat}, {lon}")
        url = f"https://shademap.app/@{lat},{lon},{zoom_level}z,{eclipse_time}t,0b,0p,0m!1786511647543!1786562164762,{coords_base64}!{lat}!{lon}"
        
        # Output filename
        output_filename = f"{site['code']}_shademap.jpg"
        
        try:
            download_shademap_export(url, output_dir="../data/shademap_snapshot", output_filename=output_filename, headless=False)
            print(f"✓ Successfully exported {output_filename}")
        except Exception as e:
            print(f"✗ Failed to export {site['code']}: {e}")
            # Continue with next site instead of stopping
            continue
        
        # Small delay between sites to avoid overwhelming the server
        if i < len(sites):
            print("\nWaiting 2 seconds before next site...")
            time.sleep(2)
    
    print("\n" + "=" * 60)
    print(f"Completed processing {len(sites)} sites")
    print(f"Shademap exports saved to: ../data/shademap_snapshot/")

def btoa(s):
    """Base64 encode a string (like JavaScript's btoa)"""
    import base64
    return base64.b64encode(s.encode()).decode()

def main():
    parser = argparse.ArgumentParser(
        description='Download Shademap export for eclipse sites',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Download shademap for specific site (reads from CSV)
  python3 download_shademap_export_playwright.py --code IB200a
  
  # Download shademap for all sites
  python3 download_shademap_export_playwright.py --all
  
  # Use custom CSV file
  python3 download_shademap_export_playwright.py --code IB200a --csv ../data/my_sites.csv
  
  # Download from custom URL
  python3 download_shademap_export_playwright.py --url "https://shademap.app/@42.13,-2.16,20z,..."
        """
    )
    
    parser.add_argument('--code', '-c',
                       help='Site code to download shademap for (e.g., IB200a)')
    parser.add_argument('--all', action='store_true',
                       help='Download shademaps for all sites in CSV')
    parser.add_argument('--csv', default='../data/eclipse_site_data.csv',
                       help='CSV file to read site data from (default: ../data/eclipse_site_data.csv)')
    parser.add_argument('--url',
                       help='Custom Shademap URL to download')
    parser.add_argument('--output', '-o',
                       help='Output filename (default: based on site code or shademap_export.jpg)')
    parser.add_argument('--headless', action='store_true',
                       help='Run browser in headless mode')
    parser.add_argument('--zoom', '-z', type=int, default=19,
                       help='Zoom level for Shademap (default: 19, range: 1-20)')
    
    args = parser.parse_args()
    
    # Eclipse time in milliseconds (August 12, 2026)
    eclipse_time = "1786559455614"
    
    # Validate zoom level
    if args.zoom < 1 or args.zoom > 20:
        print(f"Error: Zoom level must be between 1 and 20 (got {args.zoom})")
        sys.exit(1)
    
    # Process all sites
    if args.all:
        print(f"Using zoom level: {args.zoom}z")
        process_all_sites(csv_file=args.csv, zoom_level=args.zoom)
        return
    
    # Process specific site by code
    if args.code:
        site = load_site_from_csv(args.code, csv_file=args.csv)
        if not site:
            sys.exit(1)
        
        print(f"Processing {site['code']} - {site['name']}")
        print(f"Coordinates: {site['lat']}, {site['lon']}")
        print("=" * 60)
        
        # Build Shademap URL
        lat = site['lat']
        lon = site['lon']
        coords_base64 = btoa(f"{lat}, {lon}")
        url = f"https://shademap.app/@{lat},{lon},{args.zoom}z,{eclipse_time}t"
        
        # Output filename
        output_filename = args.output or f"{site['code']}_shademap.jpg"
        
        download_shademap_export(url, output_dir="../data/shademap_snapshot", output_filename=output_filename, headless=args.headless)
        print(f"\n✓ Successfully exported to: ../data/shademap_snapshot/{output_filename}")
        return
    
    # Process custom URL
    if args.url:
        output_filename = args.output or "shademap_export.jpg"
        download_shademap_export(args.url, output_filename=output_filename, headless=args.headless)
        return
    
    # No arguments provided - show help
    parser.print_help()

if __name__ == "__main__":
    main()

# Made with Bob