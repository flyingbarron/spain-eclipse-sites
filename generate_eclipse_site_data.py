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


def main():
    """Main entry point for the script"""
    parser = argparse.ArgumentParser(
        description='Generate comprehensive eclipse site data from IGME and IGN Eclipse viewer',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate all data (IGME + eclipse + cloud + horizon + shademap)
  python3 generate_eclipse_site_data.py
  
  # Skip specific operations (faster)
  python3 generate_eclipse_site_data.py --no-eclipse --no-cloud --no-shademap
  
  # Check visibility without profile screenshots (faster)
  python3 generate_eclipse_site_data.py --no-profile
  
  # Check specific site only
  python3 generate_eclipse_site_data.py --code IB200a
  
  # Only perform specific operations on existing CSV
  python3 generate_eclipse_site_data.py --only-cloud
  python3 generate_eclipse_site_data.py --only-horizon
  python3 generate_eclipse_site_data.py --only-shademap
  python3 generate_eclipse_site_data.py --only-eclipse --no-profile
  
  # Only update specific site from existing CSV
  python3 generate_eclipse_site_data.py --only-cloud --code IB200a
  python3 generate_eclipse_site_data.py --only-shademap --code IB200b
        """
    )
    parser.add_argument('--code', '-c',
                       help='Process only a specific site code (e.g., IB200a)')
    parser.add_argument('--csv', default='eclipse_site_data.csv',
                       help='CSV file to read from (default: data/eclipse_site_data.csv)')
    
    # Skip flags (for full pipeline)
    parser.add_argument('--no-eclipse', action='store_true',
                       help='Skip eclipse visibility checking')
    parser.add_argument('--no-cloud', action='store_true',
                       help='Skip cloud coverage scraping')
    parser.add_argument('--no-horizon', action='store_true',
                       help='Skip EclipseFan horizon image downloading')
    parser.add_argument('--no-shademap', action='store_true',
                       help='Skip Shademap shadow visualization downloading')
    parser.add_argument('--no-profile', action='store_true',
                       help='Skip profile diagram screenshots (check visibility only)')
    
    # Only flags (for updating existing CSV)
    parser.add_argument('--only-eclipse', action='store_true',
                       help='Only check eclipse visibility (reads from existing CSV)')
    parser.add_argument('--only-cloud', action='store_true',
                       help='Only scrape cloud coverage (reads from existing CSV)')
    parser.add_argument('--only-horizon', action='store_true',
                       help='Only download horizon images (reads from existing CSV)')
    parser.add_argument('--only-shademap', action='store_true',
                       help='Only download shademap visualizations (reads from existing CSV)')
    
    args = parser.parse_args()
    
    # Validate arguments
    only_flags = [args.only_eclipse, args.only_cloud, args.only_horizon]
    no_flags = [args.no_eclipse, args.no_cloud, args.no_horizon]
    
    if any(only_flags) and any(no_flags):
        print("✗ Error: Cannot use --only-* and --no-* flags together")
        sys.exit(1)
    
    if sum(only_flags) > 1:
        print("✗ Error: Can only use one --only-* flag at a time")
        sys.exit(1)
    
    print("=" * 60)
    print("Eclipse Site Data Generator")
    print("=" * 60)
    print()
    
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
        
        # Perform the requested operation
        if args.only_eclipse:
            print("\nChecking eclipse visibility...")
            print("=" * 60)
            save_profiles = not args.no_profile
            if args.no_profile:
                print("Profile screenshots will be skipped (--no-profile flag)")
            results = check_sites_eclipse_visibility(results, save_profiles=save_profiles)
            print(f"\n✓ Eclipse visibility checked for {len(results)} site(s)")
        
        elif args.only_cloud:
            print("\nScraping cloud coverage data...")
            print("=" * 60)
            print("This will take a while (2 second delay between requests)...")
            results = scrape_cloud_coverage_for_sites(results, delay=2.0)
            print(f"\n✓ Cloud coverage scraped for {len(results)} site(s)")
        
        elif args.only_horizon:
            print("\nDownloading EclipseFan horizon images...")
            print("=" * 60)
            print("This will take a while (2 second delay between requests)...")
            results = download_horizon_images_for_sites(results, delay=2.0)
            print(f"\n✓ Horizon images downloaded for {len(results)} site(s)")
        
        elif args.only_shademap:
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
    
    # Step 1: Scrape IGME sites
    print("\nSTEP 1: Scraping IGME site data...")
    print("=" * 60)
    results = scrape_all_sites(specific_code=args.code)
    
    if not results:
        print("\n⚠️  No data collected!")
        sys.exit(1)
    
    print(f"\n✓ Collected {len(results)} sites from IGME")
    
    # Step 2: Check eclipse visibility (if enabled)
    if not args.no_eclipse:
        print("\n" + "=" * 60)
        print("STEP 2: Checking eclipse visibility...")
        print("=" * 60)
        save_profiles = not args.no_profile
        if args.no_profile:
            print("Profile screenshots will be skipped (--no-profile flag)")
        results = check_sites_eclipse_visibility(results, save_profiles=save_profiles)
        print(f"\n✓ Eclipse visibility checked for all sites")
    else:
        print("\n⚠️  Skipping eclipse visibility checking (--no-eclipse flag)")
        for site in results:
            site['eclipse_visibility'] = 'not_checked'
    
    # Step 2.5: Scrape cloud coverage (if enabled)
    if not args.no_cloud:
        print("\n" + "=" * 60)
        print("STEP 2.5: Scraping cloud coverage data...")
        print("=" * 60)
        print("This will take a while (2 second delay between requests)...")
        results = scrape_cloud_coverage_for_sites(results, delay=2.0)
        print(f"\n✓ Cloud coverage scraped for all sites")
    else:
        print("\n⚠️  Skipping cloud coverage scraping (--no-cloud flag)")
        for site in results:
            site['cloud_coverage'] = None
            site['cloud_status'] = 'not_checked'
            site['cloud_url'] = None
    
    # Step 2.7: Download EclipseFan horizon images (if enabled)
    if not args.no_horizon:
        print("\n" + "=" * 60)
        print("STEP 2.7: Downloading EclipseFan horizon images...")
        print("=" * 60)
        print("This will take a while (2 second delay between requests)...")
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
        results = download_shademap_for_sites(results, delay=2.0)
        print(f"\n✓ Shademap visualizations downloaded for all sites")
    else:
        print("\n⚠️  Skipping shademap downloading (--no-shademap flag)")
        for site in results:
            site['shademap_status'] = 'not_checked'
    
    # Step 3: Generate outputs
    print("\n" + "=" * 60)
    print("STEP 3: Generating output files...")
    print("=" * 60)
    
    save_to_csv(results, 'eclipse_site_data.csv')
    save_to_kml(results, 'sites.kml')
    
    # Print summary
    print_summary(results)
    
    print("\n✓ All done!")


if __name__ == "__main__":
    main()

# Made with Bob