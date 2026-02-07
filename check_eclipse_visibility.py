#!/usr/bin/env python3
"""
Check eclipse visibility for all sites in the CSV file.
Queries the IGN Eclipse 2026 viewer for each site and determines visibility.
"""

import csv
import requests
from bs4 import BeautifulSoup
import time
import math

def wgs84_to_web_mercator(lat, lon):
    """Convert WGS84 (lat/lon) to Web Mercator (EPSG:3857) coordinates"""
    x = lon * 20037508.34 / 180
    y = math.log(math.tan((90 + lat) * math.pi / 360)) / (math.pi / 180)
    y_mercator = y * 20037508.34 / 180
    return x, y_mercator

def check_eclipse_visibility(lat, lon, code):
    """Check if eclipse is visible from the given coordinates"""
    try:
        # Convert coordinates to Web Mercator
        x, y_mercator = wgs84_to_web_mercator(lat, lon)
        
        # Construct the IGN Eclipse viewer URL
        url = f"https://visualizadores.ign.es/eclipses/2026?center={x},{y_mercator}&zoom=16&srs=EPSG:3857"
        
        print(f"Checking {code} ({lat}, {lon})...")
        
        # Add headers to mimic a browser request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        # Parse the HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for visibility text in the page
        page_text = soup.get_text()
        
        if "The eclipse is visible from the observation point" in page_text:
            print(f"  ✓ Eclipse IS visible")
            return "visible"
        elif "The eclipse IS NOT visible from the observation point" in page_text:
            print(f"  ✗ Eclipse NOT visible")
            return "not_visible"
        else:
            print(f"  ? Could not determine visibility")
            return "unknown"
            
    except Exception as e:
        print(f"  ✗ Error: {str(e)}")
        return "error"

def main():
    print("=" * 60)
    print("Eclipse Visibility Checker for IGME Sites")
    print("=" * 60)
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
        return
    
    print(f"Found {len(sites)} sites in CSV")
    print("-" * 60)
    print()
    
    # Check each site
    results = []
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
            
            visibility = check_eclipse_visibility(lat, lon, code)
            
            results.append({
                'code': code,
                'denominacion': site['denominacion'],
                'latitude': lat_str,
                'longitude': lon_str,
                'eclipse_visibility': visibility
            })
            
            # Be polite - add delay between requests
            time.sleep(2)
            
        except ValueError:
            print(f"Skipping {code} - invalid coordinates")
            results.append({
                'code': code,
                'denominacion': site['denominacion'],
                'latitude': lat_str,
                'longitude': lon_str,
                'eclipse_visibility': 'invalid_coordinates'
            })
    
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
    not_visible = sum(1 for r in results if r['eclipse_visibility'] == 'not_visible')
    unknown = sum(1 for r in results if r['eclipse_visibility'] == 'unknown')
    errors = sum(1 for r in results if r['eclipse_visibility'] == 'error')
    no_coords = sum(1 for r in results if r['eclipse_visibility'] in ['no_coordinates', 'invalid_coordinates'])
    
    print(f"Total sites checked: {len(results)}")
    print(f"Eclipse visible: {visible}")
    print(f"Eclipse NOT visible: {not_visible}")
    print(f"Unknown: {unknown}")
    print(f"Errors: {errors}")
    print(f"No/invalid coordinates: {no_coords}")
    print()
    print(f"✓ Results saved to {output_file}")

if __name__ == "__main__":
    main()

# Made with Bob
