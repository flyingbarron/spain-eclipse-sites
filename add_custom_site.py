#!/usr/bin/env python3
"""
Add Custom Site Utility
Adds a custom site to both the config file and the CSV data file
"""

import argparse
import json
import csv
import os
import sys
from typing import Dict, Any


def load_config(config_path: str = "data/igme_sites_config.json") -> Dict[str, Any]:
    """Load the config file"""
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_config(config: Dict[str, Any], config_path: str = "data/igme_sites_config.json") -> None:
    """Save the config file"""
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
        f.write('\n')  # Add trailing newline


def add_site_to_config(code: str, name: str, latitude: float, longitude: float, 
                       description: str = "", config_path: str = "data/igme_sites_config.json") -> bool:
    """Add a custom site to the config file"""
    try:
        config = load_config(config_path)
        
        # Check if site already exists
        custom_sites = config.get('custom_sites', [])
        for site in custom_sites:
            if site['code'].upper() == code.upper():
                print(f"Error: Site with code '{code}' already exists in config")
                return False
        
        # Add new site
        new_site = {
            "code": code,
            "name": name,
            "latitude": latitude,
            "longitude": longitude,
            "description": description if description else f"Custom site: {name}"
        }
        
        custom_sites.append(new_site)
        config['custom_sites'] = custom_sites
        
        save_config(config, config_path)
        print(f"✓ Added '{code}' to config file")
        return True
        
    except Exception as e:
        print(f"Error updating config: {e}")
        return False


def add_site_to_csv(code: str, name: str, latitude: float, longitude: float,
                    csv_path: str = "data/eclipse_site_data.csv") -> bool:
    """Add a custom site to the CSV file"""
    try:
        # Check if CSV exists and read existing data
        if not os.path.exists(csv_path):
            print(f"Error: CSV file not found: {csv_path}")
            return False
        
        # Read existing data to check for duplicates
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['code'].upper() == code.upper():
                    print(f"Error: Site with code '{code}' already exists in CSV")
                    return False
        
        # Get default values from config
        try:
            config = load_config()
            defaults = config.get('default_values', {})
            valor_turistico = defaults.get('valor_turistico', '5.0')
            confidencialidad = defaults.get('confidencialidad', 'Public')
            route_difficulty = defaults.get('route_difficulty', 'Medium')
        except:
            valor_turistico = '5.0'
            confidencialidad = 'Public'
            route_difficulty = 'Medium'
        
        # Prepare new row
        new_row = {
            'code': code,
            'denominacion': name,
            'url': 'N/A',  # Custom sites don't have IGME URLs
            'valor_turistico': valor_turistico,
            'confidencialidad': confidencialidad,
            'route_difficulty': route_difficulty,
            'latitude': f"{latitude:.6f}",
            'longitude': f"{longitude:.6f}",
            'eclipse_visibility': 'not_checked',
            'status': 'custom',
            'cloud_coverage': 'N/A',
            'cloud_status': 'not_checked',
            'cloud_url': 'N/A',
            'bortle_scale': 'N/A',
            'bortle_status': 'not_checked',
            'horizon_status': 'not_checked',
            'shademap_status': 'not_checked'
        }
        
        # Append to CSV
        with open(csv_path, 'a', encoding='utf-8', newline='') as f:
            # Read header from existing file
            with open(csv_path, 'r', encoding='utf-8') as rf:
                reader = csv.DictReader(rf)
                fieldnames = reader.fieldnames
            
            if not fieldnames:
                print("Error: Could not read CSV headers")
                return False
            
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writerow(new_row)
        
        print(f"✓ Added '{code}' to CSV file")
        return True
        
    except Exception as e:
        print(f"Error updating CSV: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Add a custom site to the IGME config and CSV data files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Add a site with minimal info
  python add_custom_site.py CUSTOM001 "My Site" 40.4168 -3.7038
  
  # Add a site with description
  python add_custom_site.py CUSTOM002 "Another Site" 41.3851 2.1734 -d "Near Barcelona"
  
  # Add to custom paths
  python add_custom_site.py TEST001 "Test Site" 40.0 -3.0 --config custom_config.json --csv custom_data.csv
        """
    )
    
    parser.add_argument('code', help='Site code (e.g., CUSTOM001)')
    parser.add_argument('name', help='Site name')
    parser.add_argument('latitude', type=float, help='Latitude (decimal degrees)')
    parser.add_argument('longitude', type=float, help='Longitude (decimal degrees)')
    parser.add_argument('-d', '--description', default='', help='Site description (optional)')
    parser.add_argument('--config', default='data/igme_sites_config.json', 
                       help='Path to config file (default: data/igme_sites_config.json)')
    parser.add_argument('--csv', default='data/eclipse_site_data.csv',
                       help='Path to CSV file (default: data/eclipse_site_data.csv)')
    parser.add_argument('--config-only', action='store_true',
                       help='Only add to config file, not CSV')
    parser.add_argument('--csv-only', action='store_true',
                       help='Only add to CSV file, not config')
    
    args = parser.parse_args()
    
    # Validate coordinates
    if not -90 <= args.latitude <= 90:
        print(f"Error: Latitude must be between -90 and 90 (got {args.latitude})")
        sys.exit(1)
    
    if not -180 <= args.longitude <= 180:
        print(f"Error: Longitude must be between -180 and 180 (got {args.longitude})")
        sys.exit(1)
    
    print(f"\nAdding custom site:")
    print(f"  Code: {args.code}")
    print(f"  Name: {args.name}")
    print(f"  Coordinates: {args.latitude}, {args.longitude}")
    if args.description:
        print(f"  Description: {args.description}")
    print()
    
    success = True
    
    # Add to config unless --csv-only
    if not args.csv_only:
        if not add_site_to_config(args.code, args.name, args.latitude, args.longitude, 
                                   args.description, args.config):
            success = False
    
    # Add to CSV unless --config-only
    if not args.config_only:
        if not add_site_to_csv(args.code, args.name, args.latitude, args.longitude, args.csv):
            success = False
    
    if success:
        print("\n✓ Custom site added successfully!")
        if not args.config_only:
            print(f"\nThe site has been added to the CSV with basic data.")
            print(f"To update it with eclipse visibility, cloud coverage, etc., run:")
            print(f"  python generate_eclipse_site_data.py --mode update --steps eclipse,cloud --code {args.code}")
            print(f"\nOr update specific data:")
            print(f"  python generate_eclipse_site_data.py --mode update --steps cloud --code {args.code}")
            print(f"  python generate_eclipse_site_data.py --mode update --steps horizon --code {args.code}")
        else:
            print(f"\nTo collect this site and add it to CSV, run:")
            print(f"  python generate_eclipse_site_data.py")
    else:
        print("\n✗ Failed to add custom site")
        sys.exit(1)


if __name__ == '__main__':
    main()

# Made with Bob
