"""
Shademap Scraper Module
Functions for downloading shadow map exports from Shademap.app
"""

import os
import time
import base64
from typing import List, Dict, Any, Optional

# Try to import playwright, but make it optional
try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

# Data directory for outputs
DATA_DIR = "data"
SHADEMAP_DIR = os.path.join(DATA_DIR, "scrape", "shademap_snapshots")

# Eclipse time in milliseconds (August 12, 2026, 18:30 UTC)
ECLIPSE_TIME = "1786559455614"


def btoa(s: str) -> str:
    """Base64 encode a string (like JavaScript's btoa)"""
    return base64.b64encode(s.encode()).decode()


def download_shademap_export(lat: float, lon: float, code: str, zoom_level: int = 19) -> str:
    """Download shadow map export from Shademap.app
    
    Args:
        lat: Latitude in decimal degrees
        lon: Longitude in decimal degrees
        code: Site code for saving image
        zoom_level: Zoom level for Shademap (default: 19)
    
    Returns:
        String indicating status: 'success', 'not_found', 'timeout', or 'error'
    """
    if not PLAYWRIGHT_AVAILABLE:
        print(f"  ⚠️  Playwright not available - skipping shademap")
        return 'playwright_not_installed'
    
    try:
        # Build Shademap URL
        url = f"https://shademap.app/@{lat},{lon},{zoom_level}z,{ECLIPSE_TIME}t"
        
        print(f"  Loading Shademap page...")
        
        with sync_playwright() as p:
            # Launch browser
            browser = p.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-blink-features=AutomationControlled'
                ]
            )
            
            # Create context
            context = browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                accept_downloads=True
            )
            
            # Create page
            page = context.new_page()
            
            try:
                # Load the page
                page.goto(url, wait_until='networkidle', timeout=30000)
                
                # Wait for page to be fully loaded
                time.sleep(8)
                
                # Dismiss popup if present
                popup_selectors = [
                    'button:has-text("OK")',
                    'button:has-text("Ok")',
                    'button.ok',
                ]
                
                for selector in popup_selectors:
                    try:
                        button = page.locator(selector).first
                        if button.is_visible(timeout=3000):
                            button.click()
                            time.sleep(1)
                            break
                    except:
                        continue
                
                # Click settings button
                settings_selectors = [
                    'button[aria-label*="Settings"]',
                    'button[title*="Settings"]',
                ]
                
                settings_clicked = False
                for selector in settings_selectors:
                    try:
                        button = page.locator(selector).first
                        if button.is_visible(timeout=5000):
                            button.click()
                            settings_clicked = True
                            time.sleep(2)
                            break
                    except:
                        continue
                
                if settings_clicked:
                    # Select sunset option
                    sunset_selectors = [
                        'input[value*="sunset"]',
                        'label:has-text("Sunset")',
                    ]
                    
                    for selector in sunset_selectors:
                        try:
                            element = page.locator(selector).first
                            if element.is_visible(timeout=3000):
                                element.click()
                                time.sleep(1)
                                break
                        except:
                            continue
                    
                    # Close settings modal
                    try:
                        button = page.get_by_title("close", exact=False)
                        if button.is_visible(timeout=3000):
                            button.click()
                            time.sleep(1)
                    except:
                        pass
                
                # Click export button
                export_selectors = [
                    'button[aria-label*="Export"]',
                    'button[title*="Export"]',
                ]
                
                export_clicked = False
                for selector in export_selectors:
                    try:
                        button = page.locator(selector).first
                        if button.is_visible(timeout=5000):
                            button.click()
                            export_clicked = True
                            time.sleep(2)
                            break
                    except:
                        continue
                
                if not export_clicked:
                    print(f"  ✗ Could not find export button")
                    return 'not_found'
                
                # Click JPG to save
                jpg_selectors = [
                    'button:has-text("JPG")',
                    'button:has-text("jpg")',
                ]
                
                jpg_clicked = False
                for selector in jpg_selectors:
                    try:
                        button = page.locator(selector).first
                        if button.is_visible(timeout=5000):
                            # Set up download handler
                            with page.expect_download(timeout=10000) as download_info:
                                button.click()
                            
                            download = download_info.value
                            jpg_clicked = True
                            
                            # Save the download
                            os.makedirs(SHADEMAP_DIR, exist_ok=True)
                            output_path = os.path.join(SHADEMAP_DIR, f"{code}_shademap.jpg")
                            download.save_as(output_path)
                            print(f"  ✓ Saved shademap to {output_path}")
                            return 'success'
                    except Exception as e:
                        continue
                
                if not jpg_clicked:
                    print(f"  ✗ Could not find JPG button")
                    return 'not_found'
                
            except PlaywrightTimeout:
                print(f"  ✗ Timeout loading page")
                return 'timeout'
            except Exception as e:
                print(f"  ✗ Error: {str(e)}")
                return 'error'
            finally:
                browser.close()
                
    except Exception as e:
        print(f"  ✗ Error downloading shademap: {str(e)}")
        return 'error'


def download_shademap_for_sites(sites: List[Dict[str, Any]], delay: float = 2.0, zoom_level: int = 19) -> List[Dict[str, Any]]:
    """Download shademap exports for multiple sites
    
    Args:
        sites: List of site dictionaries with 'code', 'latitude', 'longitude'
        delay: Delay in seconds between requests (default 2.0 for respectful scraping)
        zoom_level: Zoom level for Shademap (default: 19)
    
    Returns:
        List of site dictionaries with added 'shademap_status' field
    """
    if not PLAYWRIGHT_AVAILABLE:
        print("⚠️  Playwright not installed. Skipping shademap downloads.")
        print("    Install with: pip install playwright && playwright install chromium")
        for site in sites:
            site['shademap_status'] = 'playwright_not_installed'
        return sites
    
    for site in sites:
        code = site['code']
        lat_str = site.get('latitude', 'N/A')
        lon_str = site.get('longitude', 'N/A')
        
        # Skip sites without coordinates
        if lat_str == 'N/A' or lon_str == 'N/A':
            print(f"\n[{code}] Skipping - no coordinates")
            site['shademap_status'] = 'no_coordinates'
            continue
        
        try:
            lat = float(lat_str)
            lon = float(lon_str)
            
            print(f"\n[{code}] Downloading shademap...")
            status = download_shademap_export(lat, lon, code, zoom_level)
            site['shademap_status'] = status
            
            # Respectful delay between sites
            if delay > 0:
                time.sleep(delay)
            
        except ValueError:
            print(f"\n[{code}] Skipping - invalid coordinates")
            site['shademap_status'] = 'invalid_coordinates'
    
    return sites


# Made with Bob