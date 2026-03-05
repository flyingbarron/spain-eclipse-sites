#!/usr/bin/env python3
"""
Extract terrain clearance data from tmp.data and add it to the main CSV file.
"""

import csv
import re
from pathlib import Path


def parse_clearance_data(tmp_data_path):
    """
    Parse the tmp.data file to extract terrain clearance for each site.
    
    Returns:
        dict: Mapping of site code to clearance value (float)
    """
    clearance_map = {}
    
    with open(tmp_data_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Find lines that match the table format
    # Example: " 1   La Pellejera (IB200v)             1003   1m42.9s     2.20    +5.53     2.20    +5.53     full     YES"
    # We want to extract: (IB200v) and +5.53 (the first +/- value)
    
    for line in lines:
        # Look for site code in parentheses
        code_match = re.search(r'\(([A-Za-z0-9]+)\)', line)
        if not code_match:
            continue
        
        site_code = code_match.group(1)
        
        # Look for the clearance value (first +/- number after the code)
        # Split the line after the code and find +/- values
        after_code = line[code_match.end():]
        clearance_match = re.search(r'([\+\-]\d+\.\d+)', after_code)
        
        if clearance_match:
            clearance = float(clearance_match.group(1))
            
            # Only store the first occurrence (avoid duplicates)
            if site_code not in clearance_map:
                clearance_map[site_code] = clearance
                print(f"Found: {site_code} -> {clearance:+.2f} deg")
    
    return clearance_map


def add_clearance_to_csv(csv_path, clearance_map):
    """
    Add terrain_clearance column to the CSV file.
    
    Args:
        csv_path: Path to the CSV file
        clearance_map: Dictionary mapping site codes to clearance values
    """
    # Read existing CSV
    rows = []
    with open(csv_path, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        
        # Add terrain_clearance column if not present
        if 'terrain_clearance' not in fieldnames:
            fieldnames = list(fieldnames)
            # Insert after eclipse_visibility column
            idx = fieldnames.index('eclipse_visibility') + 1
            fieldnames.insert(idx, 'terrain_clearance')
        
        for row in reader:
            code = row['code']
            if code in clearance_map:
                row['terrain_clearance'] = f"{clearance_map[code]:+.2f}"
            else:
                row['terrain_clearance'] = ''
            rows.append(row)
    
    # Write updated CSV
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"\n✓ Updated {csv_path}")
    print(f"  Added terrain_clearance data for {len([r for r in rows if r['terrain_clearance']])} sites")


def main():
    """Main function."""
    # Paths
    tmp_data_path = Path('tmp.data')
    csv_path = Path('data/eclipse_site_data.csv')
    
    if not tmp_data_path.exists():
        print(f"Error: {tmp_data_path} not found")
        return
    
    if not csv_path.exists():
        print(f"Error: {csv_path} not found")
        return
    
    print("Parsing clearance data from tmp.data...")
    clearance_map = parse_clearance_data(tmp_data_path)
    
    print(f"\nFound clearance data for {len(clearance_map)} sites")
    
    print("\nAdding clearance data to CSV...")
    add_clearance_to_csv(csv_path, clearance_map)
    
    print("\n✓ Done!")


if __name__ == '__main__':
    main()

# Made with Bob
