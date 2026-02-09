#!/usr/bin/env python3
"""
Add cloud coverage data to existing eclipse_site_data.csv
Reads the CSV, scrapes cloud data for all sites, and saves updated CSV
Saves progress after every 5 sites to allow resuming if interrupted
"""

import csv
import sys
import os

# Add parent directory to path so we can import from src
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.cloud_coverage_scraper import get_cloud_coverage
from src.output_generator import save_to_csv, print_summary

def main():
    input_file = '../data/eclipse_site_data.csv'
    output_file = '../data/eclipse_site_data_with_cloud.csv'
    progress_file = '../data/.cloud_progress.csv'
    
    print("=" * 60)
    print("Add Cloud Coverage Data to Existing Sites")
    print("=" * 60)
    print()
    
    # Check for existing progress
    start_index = 0
    if os.path.exists(progress_file):
        print(f"Found progress file: {progress_file}")
        response = input("Resume from previous progress? (y/n): ").strip().lower()
        if response == 'y':
            input_file = progress_file
            print("✓ Resuming from progress file")
        else:
            print("✓ Starting fresh")
    
    # Read existing sites from CSV
    print(f"Reading sites from {input_file}...")
    sites = []
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                sites.append(row)
        print(f"✓ Loaded {len(sites)} sites")
    except FileNotFoundError:
        print(f"✗ Error: {input_file} not found!")
        print("  Run generate_eclipse_site_data.py first to create the base data.")
        sys.exit(1)
    
    if not sites:
        print("✗ No sites found in CSV!")
        sys.exit(1)
    
    # Count sites that need cloud data
    sites_needing_data = [s for s in sites if not s.get('cloud_coverage')]
    if not sites_needing_data:
        print("\n✓ All sites already have cloud coverage data!")
        print(f"  Output file: {output_file if os.path.exists(output_file) else progress_file}")
        return
    
    # Scrape cloud coverage data
    print("\n" + "=" * 60)
    print("Scraping cloud coverage data...")
    print("=" * 60)
    print(f"Sites needing data: {len(sites_needing_data)}/{len(sites)}")
    print(f"Estimated time: ~{len(sites_needing_data) * 2} seconds (2 sec delay per site)")
    print("Progress will be saved every 5 sites")
    print()
    
    # Process sites individually with progress saving
    import time
    processed = 0
    for i, site in enumerate(sites):
        # Skip if already has cloud data
        if site.get('cloud_coverage'):
            continue
        
        processed += 1
        print(f"[{processed}/{len(sites_needing_data)}] Checking {site['code']}...")
        
        # Get cloud coverage for this site
        try:
            lat = float(site['latitude'])
            lon = float(site['longitude'])
            result = get_cloud_coverage(lat, lon, '2026-08-12')
            
            site['cloud_coverage'] = result.get('cloud_percentage')
            site['cloud_status'] = result.get('status', 'unknown')
            site['cloud_url'] = result.get('url', '')
            
            if result.get('status') == 'success':
                print(f"  → Cloud coverage: {result['cloud_percentage']}%")
            else:
                print(f"  → {result.get('message', 'No data')}")
        except (ValueError, TypeError) as e:
            print(f"  → Error: Invalid coordinates")
            site['cloud_coverage'] = None
            site['cloud_status'] = 'error'
            site['cloud_url'] = ''
        except Exception as e:
            print(f"  → Error: {e}")
            site['cloud_coverage'] = None
            site['cloud_status'] = 'error'
            site['cloud_url'] = ''
        
        # Save progress every 5 sites
        if processed % 5 == 0:
            print(f"\n  💾 Saving progress ({processed}/{len(sites_needing_data)})...")
            save_to_csv(sites, progress_file.replace('data/', ''))
            print()
        
        # Delay between requests
        if processed < len(sites_needing_data):
            time.sleep(2.0)
    
    # Save final output
    print("\n" + "=" * 60)
    print("Saving final data...")
    print("=" * 60)
    save_to_csv(sites, output_file.replace('data/', ''))
    
    # Clean up progress file
    if os.path.exists(progress_file):
        os.remove(progress_file)
        print("✓ Progress file cleaned up")
    
    # Print summary
    print_summary(sites)
    
    print("\n✓ Cloud coverage data added successfully!")
    print(f"  Updated file: {output_file}")
    print(f"  Original file: {input_file} (unchanged)")

if __name__ == "__main__":
    main()

# Made with Bob
