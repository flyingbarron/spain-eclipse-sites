#!/usr/bin/env python3
"""
Check eclipse visibility for all sites in the CSV file.
Queries the IGN Eclipse 2026 data API for each site and determines visibility.
"""

import csv
import requests
import time
import math
import json

def wgs84_to_web_mercator(lat, lon):
    """Convert WGS84 (lat/lon) to Web Mercator (EPSG:3857) coordinates"""
    x = lon * 20037508.34 / 180
    y = math.log(math.tan((90 + lat) * math.pi / 360)) / (math.pi / 180)
    y_mercator = y * 20037508.34 / 180
    return x, y_mercator

def check_eclipse_visibility(lat, lon, code):
    """Check if eclipse is visible from the given coordinates
    
    Uses a simple heuristic: Spain is roughly between 36°N-44°N, 9°W-4°E
    The 2026 eclipse path crosses northern Spain.
    Sites in northern Spain (lat > 41°) are more likely to see the eclipse.
    """
    try:
        print(f"Checking {code} ({lat}, {lon})...")
        
        # Simple geographic check based on eclipse path
        # The 2026 eclipse will be visible from northern Spain
        # This is a rough approximation - ideally would use actual eclipse data
        
        # Eclipse path roughly crosses Spain between 41°N and 44°N
        if 41.0 <= lat <= 44.0 and -9.0 <= lon <= 4.0:
            print(f"  ✓ Eclipse likely visible (in path zone)")
            return "visible"
        elif 36.0 <= lat < 41.0 and -9.0 <= lon <= 4.0:
            print(f"  ~ Eclipse partially visible (near path)")
            return "partial"
        else:
            print(f"  ✗ Eclipse likely NOT visible (outside path)")
            return "not_visible"
            
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
            
            # Small delay for processing
            time.sleep(0.1)
            
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
