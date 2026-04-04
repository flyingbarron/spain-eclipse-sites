#!/usr/bin/env python3
"""
Apply brochure mappings to existing CSV data.
Reads data/brochure_mappings.json and updates data/eclipse_site_data.csv
"""

import csv
import json
import os
import sys

def apply_brochure_mappings():
    """Apply brochure mappings from JSON to CSV."""
    
    csv_file = 'data/eclipse_site_data.csv'
    mappings_file = 'data/brochure_mappings.json'
    
    if not os.path.exists(csv_file):
        print(f"Error: CSV file not found: {csv_file}")
        sys.exit(1)
    
    if not os.path.exists(mappings_file):
        print(f"Error: Mappings file not found: {mappings_file}")
        sys.exit(1)
    
    # Load brochure mappings
    with open(mappings_file, 'r', encoding='utf-8') as f:
        mappings_data = json.load(f)
    
    brochures = mappings_data.get('brochures', [])
    download_dir = mappings_data.get('download_dir', 'data/brochures')
    
    # Create mapping from site code to brochure info
    code_to_brochure = {}
    for brochure in brochures:
        site_codes = brochure.get('site_codes', [])
        for code in site_codes:
            code_to_brochure[code] = {
                'title': brochure.get('title', ''),
                'filename': brochure.get('filename', ''),
                'source_url': brochure.get('source_url', '')
            }
    
    print(f"Loaded {len(code_to_brochure)} brochure mappings")
    
    # Read CSV
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        sites = list(reader)
    
    # Add brochure fields if they don't exist
    brochure_fields = ['brochure_file', 'brochure_title', 'brochure_url', 'brochure_source_url']
    for field in brochure_fields:
        if field not in fieldnames:
            fieldnames.append(field)
    
    # Apply brochure mappings
    updated_count = 0
    for site in sites:
        code = site.get('code', '')
        
        # Initialize brochure fields if they don't exist
        for field in brochure_fields:
            if field not in site:
                site[field] = ''
        
        # Apply mapping if exists
        if code in code_to_brochure:
            brochure = code_to_brochure[code]
            site['brochure_file'] = brochure['filename']
            site['brochure_title'] = brochure['title']
            site['brochure_url'] = f"{download_dir}/{brochure['filename']}"
            site['brochure_source_url'] = brochure['source_url']
            updated_count += 1
            print(f"  ✓ {code}: {brochure['title']}")
    
    # Write updated CSV
    with open(csv_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(sites)
    
    print(f"\n✓ Applied brochure mappings to {updated_count} sites")
    print(f"✓ Updated {csv_file}")

if __name__ == '__main__':
    apply_brochure_mappings()

# Made with Bob
