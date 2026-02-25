#!/usr/bin/env python3
"""
Scrape Dark Sky Sites data including the mouseover popup information.
This script automates opening darkskysites.com at specific coordinates
and capturing the popup data that appears when hovering over the location.

Requires: pip install playwright
Also requires: playwright install chromium
"""

import sys
import time
import os
import csv
import json
import argparse
import re
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout


def parse_darksky_data(text):
    """
    Parse the Dark Sky Sites tooltip text to extract structured data.
    
    Expected format:
    SQM:
    21.56
    Bortle:
    3~
    Darkness:
    85.0%
    Observing Quality (visual bar - not extracted)
    42.12°N, 2.19°W
    
    Args:
        text: Raw text from tooltip
    
    Returns:
        Dictionary with parsed data
    
    Note:
        "Observing Quality" appears as a visual bar/indicator in the tooltip
        and cannot be extracted from text. It would require image analysis
        or DOM inspection of the bar element.
    """
    parsed = {
        'sqm': None,
        'bortle': None,
        'darkness': None,
        'coordinates': None,
        'raw_text': text
    }
    
    try:
        # Extract SQM value
        sqm_match = re.search(r'SQM[:\s]*\n?\s*([\d.]+)', text, re.IGNORECASE)
        if sqm_match:
            parsed['sqm'] = float(sqm_match.group(1))
        
        # Extract Bortle value
        bortle_match = re.search(r'Bortle[:\s]*\n?\s*(\d+)[~]?', text, re.IGNORECASE)
        if bortle_match:
            parsed['bortle'] = int(bortle_match.group(1))
        
        # Extract Darkness percentage
        darkness_match = re.search(r'Darkness[:\s]*\n?\s*([\d.]+)%', text, re.IGNORECASE)
        if darkness_match:
            parsed['darkness'] = float(darkness_match.group(1))
        
        # Extract coordinates (if present in text)
        coord_match = re.search(r'([\d.]+)°[NS],?\s*([\d.]+)°[EW]', text)
        if coord_match:
            parsed['coordinates'] = coord_match.group(0)
        
    except Exception as e:
        print(f"Warning: Error parsing data: {e}")
    
    return parsed


def scrape_darkskysites_data(lat, lon, output_dir="../data/scrape/darkskysites", site_code=None, headless=False):
    """
    Open Dark Sky Sites at coordinates and capture popup data.
    
    Args:
        lat: Latitude in decimal degrees
        lon: Longitude in decimal degrees
        output_dir: Directory to save the scraped data
        site_code: Optional site code for filename
        headless: Whether to run in headless mode (default: False)
    
    Returns:
        Dictionary with scraped data or None if failed
    """
    url = f"https://www.darkskysites.com/?lat={lat}&lng={lon}&zoom=8"
    print(f"Opening Dark Sky Sites (headless={headless}): {url}")
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    scraped_data = {
        'site_code': site_code,
        'latitude': lat,
        'longitude': lon,
        'url': url,
        'popup_data': None,
        'status': 'failed'
    }
    
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
        
        # Create context
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        # Create page
        page = context.new_page()
        
        try:
            # Load the page
            print("Loading Dark Sky Sites page...")
            page.goto(url, wait_until='networkidle', timeout=30000)
            
            # Wait for page to be fully loaded
            print("Waiting for page to load...")
            time.sleep(5)
            
            print("✓ Page loaded successfully")
            
            # Step 1: Close the automatic popup
            print("\nStep 1: Looking for automatic popup to close...")
            close_selectors = [
                'button:has-text("Close")',
                'button:has-text("close")',
                'button[aria-label*="close"]',
                'button[aria-label*="Close"]',
                'button.close',
                '[class*="close-button"]',
                '[class*="closeButton"]',
                'button[title*="close"]',
                'button[title*="Close"]',
                '.modal-close',
                '.popup-close',
            ]
            
            popup_closed = False
            for selector in close_selectors:
                try:
                    close_button = page.locator(selector).first
                    if close_button.is_visible(timeout=3000):
                        print(f"Found close button with selector: {selector}")
                        close_button.click()
                        popup_closed = True
                        print("✓ Automatic popup closed")
                        time.sleep(1)
                        break
                except:
                    continue
            
            if not popup_closed:
                print("⚠️  No automatic popup found (or already closed)")
            
            # Take a screenshot after closing popup
            if site_code:
                screenshot_path = os.path.join(output_dir, f"{site_code}_screenshot.png")
            else:
                screenshot_path = os.path.join(output_dir, f"darksky_{lat}_{lon}_screenshot.png")
            page.screenshot(path=screenshot_path)
            print(f"✓ Screenshot saved: {screenshot_path}")
            
            # Step 2: Find and hover over the blue dot marker
            print("\nStep 2: Looking for blue dot marker...")
            
            # Wait for map to be fully loaded
            time.sleep(2)
            
            # Try to find the marker/blue dot
            marker_selectors = [
                '.leaflet-marker-icon',
                '.marker',
                '[class*="marker"]',
                'img[src*="marker"]',
                'svg circle[fill*="blue"]',
                'svg circle',
                '.mapboxgl-marker',
            ]
            
            marker_found = False
            tooltip_text = None
            
            # Try each selector
            for selector in marker_selectors:
                try:
                    markers = page.locator(selector).all()
                    if markers:
                        print(f"Found {len(markers)} marker(s) with selector: {selector}")
                        
                        # Try hovering over the first marker
                        marker = markers[0]
                        if marker.is_visible(timeout=2000):
                            print("Hovering over marker...")
                            marker.hover()
                            time.sleep(2)  # Wait for tooltip to appear
                            
                            # Look for tooltip/mouseover content
                            tooltip_selectors = [
                                '.leaflet-tooltip',
                                '.tooltip',
                                '[class*="tooltip"]',
                                '[role="tooltip"]',
                                '.leaflet-popup-content',
                                '.mapboxgl-popup-content',
                                '[class*="popup"]',
                            ]
                            
                            for tooltip_selector in tooltip_selectors:
                                try:
                                    tooltip = page.locator(tooltip_selector).first
                                    if tooltip.is_visible(timeout=2000):
                                        print(f"Found tooltip with selector: {tooltip_selector}")
                                        tooltip_text = tooltip.inner_text()
                                        marker_found = True
                                        print(f"✓ Tooltip text captured: {tooltip_text[:200]}...")
                                        break
                                except:
                                    continue
                            
                            if marker_found:
                                break
                except Exception as e:
                    print(f"Error with selector {selector}: {e}")
                    continue
            
            # If marker not found by selector, try clicking at map center
            if not marker_found:
                print("\nMarker not found by selector, trying to hover at map center...")
                try:
                    # Hover at the center of the viewport where the marker should be
                    page.mouse.move(960, 540)
                    time.sleep(2)
                    
                    # Look for tooltip again
                    tooltip_selectors = [
                        '.leaflet-tooltip',
                        '.tooltip',
                        '[class*="tooltip"]',
                        '[role="tooltip"]',
                        '.leaflet-popup-content',
                        '.mapboxgl-popup-content',
                    ]
                    
                    for tooltip_selector in tooltip_selectors:
                        try:
                            tooltip = page.locator(tooltip_selector).first
                            if tooltip.is_visible(timeout=2000):
                                print(f"Found tooltip with selector: {tooltip_selector}")
                                tooltip_text = tooltip.inner_text()
                                marker_found = True
                                print(f"✓ Tooltip text captured: {tooltip_text[:200]}...")
                                break
                        except:
                            continue
                except Exception as e:
                    print(f"Could not hover at map center: {e}")
            
            # If still not found, try a comprehensive search for floating boxes/divs
            if not marker_found:
                print("\nSearching for floating box/tooltip by various methods...")
                try:
                    # Save HTML for debugging
                    html_path = os.path.join(output_dir, f"{site_code or 'debug'}_page.html")
                    with open(html_path, 'w', encoding='utf-8') as f:
                        f.write(page.content())
                    print(f"Saved page HTML to: {html_path}")
                    
                    # Method 1: Look for any div/span that contains our keywords and is visible
                    print("\nMethod 1: Searching for visible elements with keywords...")
                    search_strings = ['SQM', 'Bortle', 'darkness', 'Observing Quality']
                    
                    for search_str in search_strings:
                        try:
                            elements = page.get_by_text(search_str, exact=False).all()
                            print(f"  Found {len(elements)} element(s) with '{search_str}'")
                            
                            for element in elements:
                                try:
                                    if element.is_visible(timeout=500):
                                        # Get the element's bounding box to see if it's a floating box
                                        box = element.bounding_box()
                                        if box:
                                            print(f"    Element at position: x={box['x']}, y={box['y']}, w={box['width']}, h={box['height']}")
                                        
                                        # Try to get parent container
                                        parent_selectors = [
                                            'xpath=ancestor::div[1]',
                                            'xpath=ancestor::div[2]',
                                            'xpath=ancestor::div[3]',
                                            'xpath=..',
                                        ]
                                        
                                        for parent_sel in parent_selectors:
                                            try:
                                                parent = element.locator(parent_sel).first
                                                parent_text = parent.inner_text(timeout=500)
                                                
                                                # Check if this parent contains multiple keywords (likely the full tooltip)
                                                keyword_count = sum(1 for kw in ['sqm', 'bortle', 'darkness', 'observing']
                                                                   if kw in parent_text.lower())
                                                
                                                if keyword_count >= 2:
                                                    tooltip_text = parent_text
                                                    marker_found = True
                                                    print(f"✓ Found tooltip container with {keyword_count} keywords: {tooltip_text[:200]}...")
                                                    break
                                            except:
                                                continue
                                        
                                        if marker_found:
                                            break
                                        
                                        # If parent didn't work, just use the element itself
                                        if not marker_found:
                                            elem_text = element.inner_text(timeout=500)
                                            if len(elem_text) > 10:  # Make sure it's not just the keyword
                                                tooltip_text = elem_text
                                                marker_found = True
                                                print(f"✓ Using element text: {tooltip_text[:200]}...")
                                                break
                                except:
                                    continue
                            
                            if marker_found:
                                break
                        except:
                            continue
                    
                    # Method 2: Get all divs and filter by content
                    if not marker_found:
                        print("\nMethod 2: Checking all visible divs...")
                        all_divs = page.locator('div').all()
                        print(f"  Found {len(all_divs)} div elements")
                        
                        for div in all_divs:
                            try:
                                if div.is_visible(timeout=100):
                                    div_text = div.inner_text(timeout=500)
                                    
                                    # Check if contains our keywords
                                    keyword_count = sum(1 for kw in ['sqm', 'bortle', 'darkness', 'observing']
                                                       if kw in div_text.lower())
                                    
                                    if keyword_count >= 2 and len(div_text) < 500:  # Likely a tooltip, not the whole page
                                        tooltip_text = div_text
                                        marker_found = True
                                        print(f"✓ Found div with {keyword_count} keywords: {tooltip_text[:200]}...")
                                        break
                            except:
                                continue
                    
                    # Method 3: Extract from page text using regex
                    if not marker_found:
                        print("\nMethod 3: Extracting from page text with regex...")
                        import re
                        
                        all_text = page.inner_text('body')
                        
                        # Try to find a block of text with multiple keywords close together
                        # Look for text that has SQM, Bortle, and other keywords within ~200 characters
                        pattern = r'(.{0,50}(?:SQM|Bortle|darkness|Observing Quality).{0,200}(?:SQM|Bortle|darkness|Observing Quality).{0,50})'
                        matches = re.findall(pattern, all_text, re.IGNORECASE | re.DOTALL)
                        
                        if matches:
                            # Find the match with the most keywords
                            best_match = max(matches, key=lambda m: sum(1 for kw in ['sqm', 'bortle', 'darkness', 'observing']
                                                                        if kw in m.lower()))
                            tooltip_text = best_match.strip()
                            marker_found = True
                            print(f"✓ Extracted via regex: {tooltip_text[:200]}...")
                        
                except Exception as e:
                    print(f"Error during comprehensive search: {e}")
                    import traceback
                    traceback.print_exc()
            
            # Store the results
            if marker_found and tooltip_text:
                # Parse the tooltip data
                parsed_data = parse_darksky_data(tooltip_text)
                
                scraped_data['popup_data'] = tooltip_text
                scraped_data['parsed_data'] = parsed_data
                scraped_data['status'] = 'success'
                
                print(f"\n✓ Successfully scraped tooltip data for {site_code or 'location'}")
                print(f"  Parsed data:")
                print(f"    SQM: {parsed_data.get('sqm')}")
                print(f"    Bortle: {parsed_data.get('bortle')}")
                print(f"    Darkness: {parsed_data.get('darkness')}%")
                print(f"    Coordinates: {parsed_data.get('coordinates')}")
            else:
                print(f"\n⚠️  Could not find tooltip data for {site_code or 'location'}")
                scraped_data['status'] = 'no_tooltip_found'
                
                # Take a debug screenshot
                debug_path = os.path.join(output_dir, f"{site_code or 'debug'}_no_tooltip.png")
                page.screenshot(path=debug_path)
                print(f"Debug screenshot saved: {debug_path}")
            
            # Save data to JSON file
            if site_code:
                json_path = os.path.join(output_dir, f"{site_code}_data.json")
            else:
                json_path = os.path.join(output_dir, f"darksky_{lat}_{lon}_data.json")
            
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(scraped_data, f, indent=2, ensure_ascii=False)
            print(f"✓ Data saved to: {json_path}")
            
            if not headless:
                print("\nBrowser window will close in 3 seconds...")
                time.sleep(3)
            
            return scraped_data
            
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            
            # Take a screenshot for debugging
            debug_file = os.path.join(output_dir, "darkskysites_error_debug.png")
            page.screenshot(path=debug_file)
            print(f"\nDebug screenshot saved to: {debug_file}")
            
            scraped_data['status'] = 'error'
            scraped_data['error'] = str(e)
            return scraped_data
            
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


def process_all_sites(csv_file="../data/eclipse_site_data.csv", headless=False, delay=3.0):
    """Process all sites from eclipse_site_data.csv
    
    Args:
        csv_file: Path to CSV file with site data
        headless: Whether to run in headless mode
        delay: Delay between sites in seconds
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
    
    results = []
    
    # Process each site
    for i, site in enumerate(sites, 1):
        print(f"\n[{i}/{len(sites)}] Processing {site['code']} - {site['name']}")
        print("-" * 60)
        
        try:
            result = scrape_darkskysites_data(
                site['lat'], 
                site['lon'], 
                site_code=site['code'],
                headless=headless
            )
            results.append(result)
            
            if result['status'] == 'success':
                print(f"✓ Successfully scraped {site['code']}")
            else:
                print(f"⚠️  Partial or no data for {site['code']}")
                
        except Exception as e:
            print(f"✗ Failed to scrape {site['code']}: {e}")
            results.append({
                'site_code': site['code'],
                'latitude': site['lat'],
                'longitude': site['lon'],
                'status': 'error',
                'error': str(e)
            })
        
        # Delay between sites
        if i < len(sites):
            print(f"\nWaiting {delay} seconds before next site...")
            time.sleep(delay)
    
    # Save summary
    summary_path = "../data/scrape/darkskysites/scrape_summary.json"
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print("\n" + "=" * 60)
    print(f"Completed processing {len(sites)} sites")
    success_count = sum(1 for r in results if r['status'] == 'success')
    print(f"Success: {success_count}/{len(sites)}")
    print(f"Data saved to: ../data/scrape/darkskysites/")
    print(f"Summary saved to: {summary_path}")


def main():
    parser = argparse.ArgumentParser(
        description='Scrape Dark Sky Sites data including mouseover popup information',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scrape data for specific site (reads from CSV)
  python3 scrape_darkskysites_data.py --code IB200a
  
  # Scrape data for all sites
  python3 scrape_darkskysites_data.py --all
  
  # Use custom CSV file
  python3 scrape_darkskysites_data.py --code IB200a --csv ../data/my_sites.csv
  
  # Scrape specific coordinates
  python3 scrape_darkskysites_data.py --lat 40.6941 --lon -2.01107
  
  # Run in headless mode (faster, no browser window)
  python3 scrape_darkskysites_data.py --all --headless
        """
    )
    
    parser.add_argument('--code', '-c',
                       help='Site code to scrape data for (e.g., IB200a)')
    parser.add_argument('--all', action='store_true',
                       help='Scrape data for all sites in CSV')
    parser.add_argument('--csv', default='../data/eclipse_site_data.csv',
                       help='CSV file to read site data from (default: ../data/eclipse_site_data.csv)')
    parser.add_argument('--lat', type=float,
                       help='Latitude for custom location')
    parser.add_argument('--lon', type=float,
                       help='Longitude for custom location')
    parser.add_argument('--headless', action='store_true',
                       help='Run browser in headless mode')
    parser.add_argument('--delay', type=float, default=3.0,
                       help='Delay between sites in seconds (default: 3.0)')
    
    args = parser.parse_args()
    
    # Process all sites
    if args.all:
        process_all_sites(csv_file=args.csv, headless=args.headless, delay=args.delay)
        return
    
    # Process specific site by code
    if args.code:
        site = load_site_from_csv(args.code, csv_file=args.csv)
        if not site:
            sys.exit(1)
        
        print(f"Processing {site['code']} - {site['name']}")
        print(f"Coordinates: {site['lat']}, {site['lon']}")
        print("=" * 60)
        
        result = scrape_darkskysites_data(
            site['lat'], 
            site['lon'], 
            site_code=site['code'],
            headless=args.headless
        )
        
        if result['status'] == 'success':
            print(f"\n✓ Successfully scraped data for {site['code']}")
            print(f"Data saved to: ../data/scrape/darkskysites/{site['code']}_data.json")
        else:
            print(f"\n⚠️  Could not fully scrape data for {site['code']}")
        return
    
    # Process custom coordinates
    if args.lat is not None and args.lon is not None:
        print(f"Processing custom coordinates: {args.lat}, {args.lon}")
        print("=" * 60)
        
        result = scrape_darkskysites_data(
            args.lat, 
            args.lon,
            headless=args.headless
        )
        
        if result['status'] == 'success':
            print(f"\n✓ Successfully scraped data")
        else:
            print(f"\n⚠️  Could not fully scrape data")
        return
    
    # No arguments provided - show help
    parser.print_help()


if __name__ == "__main__":
    main()

# Made with Bob