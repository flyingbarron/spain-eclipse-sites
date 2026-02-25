#!/usr/bin/env python3
"""
Add Dark Sky Sites data to eclipse_site_data.csv

Reads the scraped Dark Sky Sites JSON files and adds the parsed data
(SQM, Bortle, Darkness) to the CSV file.

Usage:
    python3 utilities/add_darksky_data_to_csv.py
"""

import csv
import json
import os
import sys
from pathlib import Path


def load_darksky_data(darksky_dir="../data/scrape/darkskysites"):
    """
    Load all Dark Sky Sites data from JSON files.
    
    Args:
        darksky_dir: Directory containing the scraped JSON files
    
    Returns:
        Dictionary mapping site codes to parsed data
    """
    darksky_data = {}
    
    if not os.path.exists(darksky_dir):
        print(f"Warning: Dark Sky Sites data directory not found: {darksky_dir}")
        return darksky_data
    
    # Find all JSON data files (not the summary)
    json_files = [f for f in os.listdir(darksky_dir) 
                  if f.endswith('_data.json') and f != 'scrape_summary.json']
    
    print(f"Found {len(json_files)} Dark Sky Sites data files")
    
    for filename in json_files:
        filepath = os.path.join(darksky_dir, filename)
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            site_code = data.get('site_code')
            if not site_code:
                print(f"Warning: No site code in {filename}")
                continue
            
            # Extract parsed data
            parsed = data.get('parsed_data', {})
            if parsed and data.get('status') == 'success':
                darksky_data[site_code] = {
                    'sqm': parsed.get('sqm'),
                    'bortle': parsed.get('bortle'),
                    'darkness': parsed.get('darkness'),
                    'coordinates': parsed.get('coordinates'),
                    'status': 'success'
                }
                print(f"  ✓ {site_code}: SQM={parsed.get('sqm')}, Bortle={parsed.get('bortle')}, Darkness={parsed.get('darkness')}%")
            else:
                darksky_data[site_code] = {
                    'sqm': None,
                    'bortle': None,
                    'darkness': None,
                    'coordinates': None,
                    'status': data.get('status', 'failed')
                }
                print(f"  ✗ {site_code}: No data (status: {data.get('status')})")
                
        except Exception as e:
            print(f"Error reading {filename}: {e}")
            continue
    
    return darksky_data


def update_csv_with_darksky_data(csv_file="../data/eclipse_site_data.csv", 
                                  darksky_dir="../data/scrape/darkskysites"):
    """
    Update the CSV file with Dark Sky Sites data.
    
    Args:
        csv_file: Path to the eclipse site data CSV
        darksky_dir: Directory containing scraped Dark Sky Sites data
    """
    
    if not os.path.exists(csv_file):
        print(f"Error: CSV file not found: {csv_file}")
        sys.exit(1)
    
    # Load Dark Sky Sites data
    print("\nLoading Dark Sky Sites data...")
    print("=" * 60)
    darksky_data = load_darksky_data(darksky_dir)
    
    if not darksky_data:
        print("\nNo Dark Sky Sites data found. Please run the scraper first:")
        print("  python3 utilities/scrape_darkskysites_data.py --all")
        sys.exit(1)
    
    # Read CSV
    print(f"\nReading CSV file: {csv_file}")
    rows = []
    fieldnames = []
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames) if reader.fieldnames else []
        rows = list(reader)
    
    # Add new columns if they don't exist
    new_columns = ['darksky_sqm', 'darksky_bortle', 'darksky_darkness', 'darksky_status']
    for col in new_columns:
        if col not in fieldnames:
            fieldnames.append(col)
            print(f"  Adding column: {col}")
    
    # Update rows with Dark Sky Sites data
    print("\nUpdating rows with Dark Sky Sites data...")
    print("=" * 60)
    
    updated_count = 0
    no_data_count = 0
    
    for row in rows:
        code = row['code']
        
        if code in darksky_data:
            data = darksky_data[code]
            
            # Update the row
            row['darksky_sqm'] = str(data['sqm']) if data['sqm'] is not None else ''
            row['darksky_bortle'] = str(data['bortle']) if data['bortle'] is not None else ''
            row['darksky_darkness'] = str(data['darkness']) if data['darkness'] is not None else ''
            row['darksky_status'] = data['status']
            
            if data['status'] == 'success':
                updated_count += 1
                print(f"  ✓ {code}: Updated with Dark Sky Sites data")
            else:
                no_data_count += 1
                print(f"  ⚠ {code}: No data available (status: {data['status']})")
        else:
            # No Dark Sky Sites data for this site
            row['darksky_sqm'] = ''
            row['darksky_bortle'] = ''
            row['darksky_darkness'] = ''
            row['darksky_status'] = 'not_scraped'
            no_data_count += 1
    
    # Write updated CSV
    print(f"\nWriting updated CSV to: {csv_file}")
    with open(csv_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    # Summary
    print("\n" + "=" * 60)
    print("Summary:")
    print(f"  Total sites: {len(rows)}")
    print(f"  Updated with data: {updated_count}")
    print(f"  No data available: {no_data_count}")
    print(f"  Not scraped: {len(rows) - updated_count - no_data_count}")
    print("\n✓ CSV file updated successfully!")
    print("\nNext steps:")
    print("  1. Review the updated CSV file")
    print("  2. Rebuild the standalone viewer:")
    print("     python3 build_standalone_viewer.py")


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Add Dark Sky Sites data to eclipse_site_data.csv',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Update CSV with default paths
  python3 utilities/add_darksky_data_to_csv.py
  
  # Use custom paths
  python3 utilities/add_darksky_data_to_csv.py --csv data/my_sites.csv --darksky-dir data/scrape/darkskysites
        """
    )
    
    parser.add_argument('--csv', default='../data/eclipse_site_data.csv',
                       help='Path to CSV file (default: ../data/eclipse_site_data.csv)')
    parser.add_argument('--darksky-dir', default='../data/scrape/darkskysites',
                       help='Directory with Dark Sky Sites data (default: ../data/scrape/darkskysites)')
    
    args = parser.parse_args()
    
    update_csv_with_darksky_data(args.csv, args.darksky_dir)


if __name__ == '__main__':
    main()

# Made with Bob