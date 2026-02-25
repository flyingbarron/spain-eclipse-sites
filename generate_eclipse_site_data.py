#!/usr/bin/env python3
"""
Generate Eclipse Site Data - Main Script
Combines IGME site scraping with eclipse visibility checking.
Generates a single CSV with all data and three KML files.
"""

import argparse
import csv
import os
import sys
from typing import List, Dict, Any
from src.igme_scraper import scrape_all_sites
from src.eclipse_checker import check_sites_eclipse_visibility
from src.cloud_coverage_scraper import scrape_cloud_coverage_for_sites
from src.eclipsefan_scraper import download_horizon_images_for_sites
from src.shademap_scraper import download_shademap_for_sites
from src.output_generator import save_to_csv, save_to_kml, print_summary


def load_sites_from_csv(csv_filename: str = 'eclipse_site_data.csv') -> List[Dict[str, Any]]:
    """Load sites from existing CSV file
    
    Args:
        csv_filename: CSV filename (will be looked for in data/ directory)
    
    Returns:
        List of site dictionaries
    """
    # Construct full path - check if filename already includes data/ prefix
    if csv_filename.startswith('data/'):
        csv_path = csv_filename
    else:
        csv_path = os.path.join('data', csv_filename)
    
    sites = []
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                sites.append(row)
        print(f"✓ Loaded {len(sites)} sites from {csv_path}")
        return sites
    except FileNotFoundError:
        print(f"✗ Error: {csv_path} not found!")
        print("  Run without --only-* flags first to create the base data.")
        sys.exit(1)


def get_next_t_code(csv_filename: str = 'eclipse_site_data.csv') -> str:
    """Get the next available Txxxx code
    
    Args:
        csv_filename: CSV filename to check for existing codes
    
    Returns:
        Next available code in format Txxxx (e.g., T0001, T0002, etc.)
    """
    # Construct full path
    if csv_filename.startswith('data/'):
        csv_path = csv_filename
    else:
        csv_path = os.path.join('data', csv_filename)
    
    max_num = 0
    
    # Check if file exists
    if os.path.exists(csv_path):
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    code = row.get('code', '')
                    # Check if code matches Txxxx pattern
                    if code.startswith('T') and len(code) == 5:
                        try:
                            num = int(code[1:])
                            max_num = max(max_num, num)
                        except ValueError:
                            continue
        except Exception as e:
            print(f"Warning: Could not read existing CSV: {e}")
    
    # Return next number
    return f"T{max_num + 1:04d}"


def check_data_exists(site_code: str, data_type: str) -> bool:
    """Check if data already exists for a site
    
    Args:
        site_code: Site code (e.g., IB200a)
        data_type: Type of data to check ('eclipse', 'cloud', 'darksky', 'horizon', 'shademap')
    
    Returns:
        True if data exists, False otherwise
    """
    if data_type == 'eclipse':
        # Check if profile image exists
        profile_path = os.path.join('data', 'ign_visibility_profiles', f'{site_code}_profile.png')
        return os.path.exists(profile_path)
    
    elif data_type == 'horizon':
        # Check if horizon image exists
        horizon_path = os.path.join('data', 'eclipsefan_visibility_profiles', f'{site_code}_horizon.png')
        return os.path.exists(horizon_path)
    
    elif data_type == 'shademap':
        # Check if shademap image exists
        shademap_path = os.path.join('data', 'shademap_snapshot', f'{site_code}_shademap.jpg')
        return os.path.exists(shademap_path)
    
    elif data_type == 'cloud':
        # Check CSV for cloud data
        csv_path = os.path.join('data', 'eclipse_site_data.csv')
        if not os.path.exists(csv_path):
            return False
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get('code') == site_code:
                        return row.get('cloud_coverage') not in [None, '', 'N/A']
        except Exception:
            return False
        return False
    
    elif data_type == 'darksky':
        # Check CSV for darksky data
        csv_path = os.path.join('data', 'eclipse_site_data.csv')
        if not os.path.exists(csv_path):
            return False
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get('code') == site_code:
                        return row.get('darksky_sqm') not in [None, '', 'N/A']
        except Exception:
            return False
        return False
    
    return False


def add_site_manually(args) -> None:
    """Add a new site manually to the CSV
    
    Args:
        args: Command-line arguments
    """
    # Validate required arguments
    if not args.name:
        print("✗ Error: --name is required when using --add-site")
        sys.exit(1)
    if args.lat is None:
        print("✗ Error: --lat is required when using --add-site")
        sys.exit(1)
    if args.lon is None:
        print("✗ Error: --lon is required when using --add-site")
        sys.exit(1)
    if not args.visibility:
        print("✗ Error: --visibility is required when using --add-site")
        sys.exit(1)
    
    # Generate or use provided code
    if args.site_code:
        code = args.site_code
    else:
        code = get_next_t_code(args.csv)
        print(f"Auto-generated code: {code}")
    
    # Create new site entry
    new_site = {
        'code': code,
        'denominacion': args.name,
        'url': 'N/A',
        'valor_turistico': '5',
        'confidencialidad': 'N/A',
        'route_difficulty': 'low',
        'latitude': str(args.lat),
        'longitude': str(args.lon),
        'eclipse_visibility': args.visibility,
        'status': 'manual',
        'cloud_coverage': None,
        'cloud_status': 'not_checked',
        'cloud_url': None,
        'darksky_sqm': None,
        'darksky_bortle': None,
        'darksky_darkness': None,
        'darksky_status': 'not_checked',
        'horizon_status': 'not_checked',
        'shademap_status': 'not_checked'
    }
    
    print("\n" + "=" * 60)
    print("Adding new site manually")
    print("=" * 60)
    print(f"Code: {code}")
    print(f"Name: {args.name}")
    print(f"Coordinates: {args.lat}, {args.lon}")
    print(f"Eclipse Visibility: {args.visibility}")
    print(f"Tourist Value: 5 (default)")
    print(f"Route Difficulty: low (default)")
    print(f"IGME URL: N/A")
    
    # Load existing sites
    results = []
    csv_path = os.path.join('data', args.csv) if not args.csv.startswith('data/') else args.csv
    if os.path.exists(csv_path):
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                results = list(reader)
            print(f"\nLoaded {len(results)} existing sites from CSV")
        except Exception as e:
            print(f"Warning: Could not load existing CSV: {e}")
    
    # Check if code already exists
    if any(s.get('code') == code for s in results):
        print(f"\n✗ Error: Site code {code} already exists in CSV")
        print("  Use --site-code to specify a different code")
        sys.exit(1)
    
    # Add new site
    results.append(new_site)
    
    # Save to CSV
    print("\n" + "=" * 60)
    print("Saving to CSV...")
    print("=" * 60)
    save_to_csv(results, args.csv)
    print(f"✓ Site {code} added successfully!")
    print(f"\nYou can now run operations on this site:")
    print(f"  python3 generate_eclipse_site_data.py --only-cloud --code {code}")
    print(f"  python3 generate_eclipse_site_data.py --only-horizon --code {code}")
    print(f"  python3 generate_eclipse_site_data.py --only-shademap --code {code}")


def main():
    """Main entry point for the script"""
    parser = argparse.ArgumentParser(
        description='Generate comprehensive eclipse site data from IGME and IGN Eclipse viewer',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate all data (IGME + eclipse + cloud + horizon + shademap)
  # By default, only processes NEW sites not in CSV
  python3 generate_eclipse_site_data.py
  
  # Force re-scrape all sites (including existing ones)
  python3 generate_eclipse_site_data.py --force
  
  # Skip specific operations (faster)
  python3 generate_eclipse_site_data.py --no-eclipse-view-scrape --no-cloud --no-shademap
  
  # Check visibility without profile screenshots (faster)
  python3 generate_eclipse_site_data.py --no-profile
  
  # Check specific site only
  python3 generate_eclipse_site_data.py --code IB200a
  
  # Only perform specific operations on existing CSV
  python3 generate_eclipse_site_data.py --only-cloud
  python3 generate_eclipse_site_data.py --only-horizon
  python3 generate_eclipse_site_data.py --only-shademap
  python3 generate_eclipse_site_data.py --only-eclipse --no-profile
  
  # Combine multiple --only-* operations
  python3 generate_eclipse_site_data.py --only-cloud --only-horizon --only-shademap
  python3 generate_eclipse_site_data.py --only-eclipse --only-cloud --code IB200a
  
  # Only update specific site from existing CSV
  python3 generate_eclipse_site_data.py --only-cloud --code IB200a
  python3 generate_eclipse_site_data.py --only-shademap --code IB200b
  
  # Add a new site manually (auto-generates code T0001, T0002, etc.)
  python3 generate_eclipse_site_data.py --add-site --name "My Site" --lat 42.5 --lon -2.3 --visibility visible
  
  # Add a new site with custom code
  python3 generate_eclipse_site_data.py --add-site --name "Custom Site" --lat 42.5 --lon -2.3 --visibility visible --site-code CUSTOM01
        """
    )
    parser.add_argument('--code', '-c',
                       help='Process only a specific site code (e.g., IB200a)')
    parser.add_argument('--csv', default='eclipse_site_data.csv',
                       help='CSV file to read from (default: data/eclipse_site_data.csv)')
    parser.add_argument('--force', action='store_true',
                       help='Force re-scrape all sites, even if they exist in CSV')
    
    # Add site manually
    parser.add_argument('--add-site', action='store_true',
                       help='Add a new site manually to the CSV')
    parser.add_argument('--name', help='Site name (required with --add-site)')
    parser.add_argument('--lat', type=float, help='Latitude in decimal degrees (required with --add-site)')
    parser.add_argument('--lon', type=float, help='Longitude in decimal degrees (required with --add-site)')
    parser.add_argument('--visibility', choices=['visible', 'not_visible', 'unknown'],
                       help='Eclipse visibility status (required with --add-site)')
    parser.add_argument('--site-code', help='Site code (optional, auto-generates Txxxx if not provided)')
    
    # Skip flags (for full pipeline)
    parser.add_argument('--no-eclipse-view-scrape', action='store_true',
                       help='Skip eclipse view profile image scraping (still checks visibility)')
    parser.add_argument('--no-cloud', action='store_true',
                       help='Skip cloud coverage scraping')
    parser.add_argument('--no-darksky', action='store_true',
                       help='Skip Dark Sky Sites data scraping (SQM, Bortle, darkness)')
    parser.add_argument('--no-horizon', action='store_true',
                       help='Skip EclipseFan horizon image downloading')
    parser.add_argument('--no-shademap', action='store_true',
                       help='Skip Shademap shadow visualization downloading')
    parser.add_argument('--no-profile', action='store_true',
                       help='Skip profile diagram screenshots (check visibility only)')
    
    # Smart skip flag
    parser.add_argument('--skip-existing', action='store_true',
                       help='Skip scraping if data already exists (checks CSV fields and files)')
    
    # Only flags (for updating existing CSV)
    parser.add_argument('--only-eclipse', action='store_true',
                       help='Only check eclipse visibility (reads from existing CSV)')
    parser.add_argument('--only-cloud', action='store_true',
                       help='Only scrape cloud coverage (reads from existing CSV)')
    parser.add_argument('--only-darksky', action='store_true',
                       help='Only scrape Dark Sky Sites data (reads from existing CSV)')
    parser.add_argument('--only-horizon', action='store_true',
                       help='Only download horizon images (reads from existing CSV)')
    parser.add_argument('--only-shademap', action='store_true',
                       help='Only download shademap visualizations (reads from existing CSV)')
    
    args = parser.parse_args()
    
    # Validate arguments
    only_flags = [args.only_eclipse, args.only_cloud, args.only_darksky, args.only_horizon, args.only_shademap]
    no_flags = [args.no_eclipse_view_scrape, args.no_cloud, args.no_darksky, args.no_horizon, args.no_shademap]
    
    if any(only_flags) and any(no_flags):
        print("✗ Error: Cannot use --only-* and --no-* flags together")
        sys.exit(1)
    
    print("=" * 60)
    print("Eclipse Site Data Generator")
    print("=" * 60)
    print()
    
    # Handle --add-site mode
    if args.add_site:
        add_site_manually(args)
        return
    
    # Handle --only-* modes (update existing CSV)
    if any(only_flags):
        print("MODE: Update existing CSV with specific data")
        print("=" * 60)
        
        # Load existing sites from CSV
        results = load_sites_from_csv(args.csv)
        
        # Filter to specific site if requested
        if args.code:
            filtered_results = [s for s in results if s.get('code') == args.code]
            if not filtered_results:
                # Site not found in CSV - scrape it from IGME first
                print(f"⚠️  Site {args.code} not found in {args.csv}")
                print(f"Scraping site {args.code} from IGME first...")
                print("=" * 60)
                new_site = scrape_all_sites(specific_code=args.code)
                if not new_site:
                    print(f"✗ Error: Could not scrape site {args.code} from IGME")
                    sys.exit(1)
                print(f"✓ Successfully scraped site {args.code} from IGME")
                results = new_site
            else:
                print(f"✓ Filtering to site: {args.code}")
                results = filtered_results
        
        # Perform the requested operations (can be multiple)
        if args.only_eclipse:
            print("\nChecking eclipse visibility...")
            print("=" * 60)
            save_profiles = not args.no_profile
            if args.no_profile:
                print("Profile screenshots will be skipped (--no-profile flag)")
            results = check_sites_eclipse_visibility(results, save_profiles=save_profiles)
            print(f"\n✓ Eclipse visibility checked for {len(results)} site(s)")
        
        if args.only_cloud:
            print("\nScraping cloud coverage data...")
            print("=" * 60)
            print("This will take a while (2 second delay between requests)...")
            results = scrape_cloud_coverage_for_sites(results, delay=2.0)
            print(f"\n✓ Cloud coverage scraped for {len(results)} site(s)")
        
        if args.only_darksky:
            print("\nScraping Dark Sky Sites data...")
            print("=" * 60)
            print("This will scrape SQM, Bortle scale, and darkness data from darkskysites.com")
            print("This will take a while (3 second delay between requests)...")
            # Import scraper dynamically to avoid Playwright dependency if not used
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'utilities'))
            from scrape_darkskysites_data import scrape_darkskysites_data, parse_darksky_data
            
            for i, site in enumerate(results, 1):
                code = site.get('code', 'Unknown')
                lat_str = site.get('latitude', 'N/A')
                lon_str = site.get('longitude', 'N/A')
                
                if lat_str == 'N/A' or lon_str == 'N/A':
                    print(f"[{i}/{len(results)}] {code}: No coordinates, skipping")
                    site['darksky_sqm'] = None
                    site['darksky_bortle'] = None
                    site['darksky_darkness'] = None
                    site['darksky_status'] = 'no_coordinates'
                    continue
                
                try:
                    lat = float(lat_str)
                    lon = float(lon_str)
                except (ValueError, TypeError):
                    print(f"[{i}/{len(results)}] {code}: Invalid coordinates, skipping")
                    site['darksky_sqm'] = None
                    site['darksky_bortle'] = None
                    site['darksky_darkness'] = None
                    site['darksky_status'] = 'invalid_coordinates'
                    continue
                
                print(f"[{i}/{len(results)}] {code}: Scraping Dark Sky Sites data...")
                
                try:
                    result = scrape_darkskysites_data(lat, lon, site_code=code, headless=True)
                    
                    if result['status'] == 'success' and result.get('parsed_data'):
                        parsed = result['parsed_data']
                        site['darksky_sqm'] = parsed.get('sqm')
                        site['darksky_bortle'] = parsed.get('bortle')
                        site['darksky_darkness'] = parsed.get('darkness')
                        site['darksky_status'] = 'success'
                        print(f"  ✓ SQM={parsed.get('sqm')}, Bortle={parsed.get('bortle')}, Darkness={parsed.get('darkness')}%")
                    else:
                        site['darksky_sqm'] = None
                        site['darksky_bortle'] = None
                        site['darksky_darkness'] = None
                        site['darksky_status'] = result['status']
                        print(f"  ✗ Failed: {result['status']}")
                except Exception as e:
                    print(f"  ✗ Error: {e}")
                    site['darksky_sqm'] = None
                    site['darksky_bortle'] = None
                    site['darksky_darkness'] = None
                    site['darksky_status'] = 'error'
                
                # Rate limiting
                if i < len(results):
                    import time
                    time.sleep(3.0)
            
            print(f"\n✓ Dark Sky Sites data scraped for {len(results)} site(s)")
        
        if args.only_horizon:
            print("\nDownloading EclipseFan horizon images...")
            print("=" * 60)
            print("This will take a while (2 second delay between requests)...")
            results = download_horizon_images_for_sites(results, delay=2.0)
            print(f"\n✓ Horizon images downloaded for {len(results)} site(s)")
        
        if args.only_shademap:
            print("\nDownloading Shademap visualizations...")
            print("=" * 60)
            print("This will take a while (2 second delay between requests)...")
            results = download_shademap_for_sites(results, delay=2.0)
            print(f"\n✓ Shademap visualizations downloaded for {len(results)} site(s)")
        
        # If updating specific site, merge back into full dataset
        if args.code:
            print(f"\nMerging updated site {args.code} back into CSV...")
            all_sites = load_sites_from_csv(args.csv)
            for i, site in enumerate(all_sites):
                if site.get('code') == args.code:
                    all_sites[i] = results[0]
                    break
            results = all_sites
        
        # Save updated CSV
        print("\n" + "=" * 60)
        print("Saving updated data...")
        print("=" * 60)
        save_to_csv(results, args.csv)
        print(f"✓ Updated {args.csv}")
        
        print("\n✓ All done!")
        return
    
    # Normal mode: Full pipeline
    print("MODE: Full pipeline (scrape IGME + optional checks)")
    print("=" * 60)
    
    # Load existing CSV to check for already-scraped sites
    csv_path = os.path.join('data', args.csv) if not args.csv.startswith('data/') else args.csv
    existing_sites = []
    existing_codes = set()
    
    if os.path.exists(csv_path) and not args.force:
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                existing_sites = list(reader)
                existing_codes = {site.get('code') for site in existing_sites}
            print(f"\n✓ Found existing CSV with {len(existing_sites)} sites")
            if not args.code:
                print(f"  Will only scrape NEW sites not in CSV (use --force to re-scrape all)")
        except Exception as e:
            print(f"⚠️  Could not load existing CSV: {e}")
    
    # Step 1: Scrape IGME sites
    print("\nSTEP 1: Scraping IGME site data...")
    print("=" * 60)
    
    if args.code:
        # Specific site requested - always scrape it
        results = scrape_all_sites(specific_code=args.code)
    else:
        # Scrape all sites from config
        from src.igme_scraper import generate_urls
        all_urls = generate_urls()
        
        if not args.force and existing_codes:
            # Filter out sites that already exist in CSV
            new_urls = [(code, url, custom_data) for code, url, custom_data in all_urls
                       if code not in existing_codes]
            print(f"  Found {len(all_urls)} total sites in config")
            print(f"  Skipping {len(all_urls) - len(new_urls)} existing sites")
            print(f"  Will scrape {len(new_urls)} new sites")
            
            if not new_urls:
                print("\n✓ No new sites to scrape!")
                print("  All sites in config already exist in CSV")
                print("  Use --force to re-scrape all sites")
                print("  Or use --only-* flags to update specific data")
                return
            
            # Scrape only new sites
            results = []
            for code, url, custom_data in new_urls:
                from src.igme_scraper import scrape_site
                print(f"\n[{code}] Scraping...")
                site_data = scrape_site(code, url, custom_data)
                if site_data:
                    results.append(site_data)
                    print(f"  ✓ Success")
                else:
                    print(f"  ✗ Failed")
        else:
            # Force mode or no existing CSV - scrape all
            if args.force:
                print("  --force flag set: will re-scrape all sites")
            results = scrape_all_sites(specific_code=args.code)
    
    if not results:
        print("\n⚠️  No data collected!")
        sys.exit(1)
    
    print(f"\n✓ Collected {len(results)} sites from IGME")
    
    # Step 2: Check eclipse visibility
    print("\n" + "=" * 60)
    print("STEP 2: Checking eclipse visibility...")
    print("=" * 60)
    
    # Determine if we should save profile images
    save_profiles = not args.no_profile and not args.no_eclipse_view_scrape
    
    if args.no_eclipse_view_scrape:
        print("Profile image scraping will be skipped (--no-eclipse-view-scrape flag)")
        print("Visibility will still be checked")
    elif args.no_profile:
        print("Profile screenshots will be skipped (--no-profile flag)")
    
    # Filter sites if --skip-existing is set
    if args.skip_existing and save_profiles:
        sites_to_check = []
        skipped_count = 0
        for site in results:
            if check_data_exists(site.get('code'), 'eclipse'):
                print(f"  Skipping {site.get('code')}: eclipse profile already exists")
                skipped_count += 1
            else:
                sites_to_check.append(site)
        if skipped_count > 0:
            print(f"  Skipped {skipped_count} sites with existing eclipse data")
        results = check_sites_eclipse_visibility(sites_to_check, save_profiles=save_profiles) + \
                  [s for s in results if s not in sites_to_check]
    else:
        results = check_sites_eclipse_visibility(results, save_profiles=save_profiles)
    
    print(f"\n✓ Eclipse visibility checked for all sites")
    
    # Step 2.5: Scrape cloud coverage (if enabled)
    if not args.no_cloud:
        print("\n" + "=" * 60)
        print("STEP 2.5: Scraping cloud coverage data...")
        print("=" * 60)
        print("This will take a while (2 second delay between requests)...")
        
        # Filter sites if --skip-existing is set
        if args.skip_existing:
            sites_to_scrape = []
            skipped_count = 0
            for site in results:
                if check_data_exists(site.get('code', ''), 'cloud'):
                    print(f"  Skipping {site.get('code')}: cloud data already exists")
                    skipped_count += 1
                else:
                    sites_to_scrape.append(site)
            if skipped_count > 0:
                print(f"  Skipped {skipped_count} sites with existing cloud data")
            scraped_sites = scrape_cloud_coverage_for_sites(sites_to_scrape, delay=2.0)
            # Merge results
            for site in results:
                for scraped in scraped_sites:
                    if site.get('code') == scraped.get('code'):
                        site.update(scraped)
                        break
        else:
            results = scrape_cloud_coverage_for_sites(results, delay=2.0)
        
        print(f"\n✓ Cloud coverage scraped for all sites")
    else:
        print("\n⚠️  Skipping cloud coverage scraping (--no-cloud flag)")
        for site in results:
            site['cloud_coverage'] = None
            site['cloud_status'] = 'not_checked'
            site['cloud_url'] = None
    
    # Step 2.6: Scrape Dark Sky Sites data (if enabled)
    if not args.no_darksky:
        print("\n" + "=" * 60)
        print("STEP 2.6: Scraping Dark Sky Sites data...")
        print("=" * 60)
        print("This will scrape SQM, Bortle scale, and darkness data from darkskysites.com")
        print("This will take a while (3 second delay between requests)...")
        
        # Import scraper dynamically to avoid Playwright dependency if not used
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'utilities'))
        from scrape_darkskysites_data import scrape_darkskysites_data, parse_darksky_data
        
        for i, site in enumerate(results, 1):
            code = site.get('code', 'Unknown')
            lat_str = site.get('latitude', 'N/A')
            lon_str = site.get('longitude', 'N/A')
            
            if lat_str == 'N/A' or lon_str == 'N/A':
                print(f"[{i}/{len(results)}] {code}: No coordinates, skipping")
                site['darksky_sqm'] = None
                site['darksky_bortle'] = None
                site['darksky_darkness'] = None
                site['darksky_status'] = 'no_coordinates'
                continue
            
            try:
                lat = float(lat_str)
                lon = float(lon_str)
            except (ValueError, TypeError):
                print(f"[{i}/{len(results)}] {code}: Invalid coordinates, skipping")
                site['darksky_sqm'] = None
                site['darksky_bortle'] = None
                site['darksky_darkness'] = None
                site['darksky_status'] = 'invalid_coordinates'
                continue
            
            # Skip if data exists and --skip-existing is set
            if args.skip_existing and check_data_exists(code, 'darksky'):
                print(f"[{i}/{len(results)}] {code}: Skipping - Dark Sky data already exists")
                continue
            
            print(f"[{i}/{len(results)}] {code}: Scraping Dark Sky Sites data...")
            
            try:
                result = scrape_darkskysites_data(lat, lon, site_code=code, headless=True)
                
                if result['status'] == 'success' and result.get('parsed_data'):
                    parsed = result['parsed_data']
                    site['darksky_sqm'] = parsed.get('sqm')
                    site['darksky_bortle'] = parsed.get('bortle')
                    site['darksky_darkness'] = parsed.get('darkness')
                    site['darksky_status'] = 'success'
                    print(f"  ✓ SQM={parsed.get('sqm')}, Bortle={parsed.get('bortle')}, Darkness={parsed.get('darkness')}%")
                else:
                    site['darksky_sqm'] = None
                    site['darksky_bortle'] = None
                    site['darksky_darkness'] = None
                    site['darksky_status'] = result['status']
                    print(f"  ✗ Failed: {result['status']}")
            except Exception as e:
                print(f"  ✗ Error: {e}")
                site['darksky_sqm'] = None
                site['darksky_bortle'] = None
                site['darksky_darkness'] = None
                site['darksky_status'] = 'error'
            
            # Rate limiting
            if i < len(results):
                import time
                time.sleep(3.0)
        
        print(f"\n✓ Dark Sky Sites data scraped for all sites")
    else:
        print("\n⚠️  Skipping Dark Sky Sites data scraping (--no-darksky flag)")
        for site in results:
            site['darksky_sqm'] = None
            site['darksky_bortle'] = None
            site['darksky_darkness'] = None
            site['darksky_status'] = 'not_checked'
    
    # Step 2.7: Download EclipseFan horizon images (if enabled)
    if not args.no_horizon:
        print("\n" + "=" * 60)
        print("STEP 2.7: Downloading EclipseFan horizon images...")
        print("=" * 60)
        print("This will take a while (2 second delay between requests)...")
        
        # Filter sites if --skip-existing is set
        if args.skip_existing:
            sites_to_download = []
            skipped_count = 0
            for site in results:
                if check_data_exists(site.get('code', ''), 'horizon'):
                    print(f"  Skipping {site.get('code')}: horizon image already exists")
                    skipped_count += 1
                else:
                    sites_to_download.append(site)
            if skipped_count > 0:
                print(f"  Skipped {skipped_count} sites with existing horizon images")
            downloaded_sites = download_horizon_images_for_sites(sites_to_download, delay=2.0)
            # Merge results
            for site in results:
                for downloaded in downloaded_sites:
                    if site.get('code') == downloaded.get('code'):
                        site.update(downloaded)
                        break
        else:
            results = download_horizon_images_for_sites(results, delay=2.0)
        
        print(f"\n✓ Horizon images downloaded for all sites")
    else:
        print("\n⚠️  Skipping horizon image downloading (--no-horizon flag)")
        for site in results:
            site['horizon_status'] = 'not_checked'
    
    # Step 2.8: Download Shademap visualizations (if enabled)
    if not args.no_shademap:
        print("\n" + "=" * 60)
        print("STEP 2.8: Downloading Shademap shadow visualizations...")
        print("=" * 60)
        print("This will take a while (2 second delay between requests)...")
        
        # Filter sites if --skip-existing is set
        if args.skip_existing:
            sites_to_download = []
            skipped_count = 0
            for site in results:
                if check_data_exists(site.get('code', ''), 'shademap'):
                    print(f"  Skipping {site.get('code')}: shademap already exists")
                    skipped_count += 1
                else:
                    sites_to_download.append(site)
            if skipped_count > 0:
                print(f"  Skipped {skipped_count} sites with existing shademap visualizations")
            downloaded_sites = download_shademap_for_sites(sites_to_download, delay=2.0)
            # Merge results
            for site in results:
                for downloaded in downloaded_sites:
                    if site.get('code') == downloaded.get('code'):
                        site.update(downloaded)
                        break
        else:
            results = download_shademap_for_sites(results, delay=2.0)
        
        print(f"\n✓ Shademap visualizations downloaded for all sites")
    else:
        print("\n⚠️  Skipping shademap downloading (--no-shademap flag)")
        for site in results:
            site['shademap_status'] = 'not_checked'
    
    # Step 3: Merge with existing sites and generate outputs
    print("\n" + "=" * 60)
    print("STEP 3: Generating output files...")
    print("=" * 60)
    
    # Merge new results with existing sites
    if existing_sites and not args.force:
        print(f"Merging {len(results)} new sites with {len(existing_sites)} existing sites...")
        # Create a dict of existing sites by code for easy lookup
        existing_dict = {site['code']: site for site in existing_sites}
        # Update with new results
        for site in results:
            existing_dict[site['code']] = site
        # Convert back to list
        all_results = list(existing_dict.values())
        print(f"✓ Total sites in output: {len(all_results)}")
    else:
        all_results = results
    
    save_to_csv(all_results, 'eclipse_site_data.csv')
    save_to_kml(all_results, 'sites.kml')
    
    # Print summary
    print_summary(all_results)
    
    print("\n✓ All done!")


if __name__ == "__main__":
    main()

# Made with Bob