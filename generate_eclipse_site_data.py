#!/usr/bin/env python3
"""
Generate Eclipse Site Data - Main Script
Combines IGME site scraping with eclipse visibility checking.
Generates a single CSV with all data and three KML files.
"""

import argparse
import sys
from src.igme_scraper import scrape_all_sites
from src.eclipse_checker import check_sites_eclipse_visibility
from src.cloud_coverage_scraper import scrape_cloud_coverage_for_sites
from src.eclipsefan_scraper import download_horizon_images_for_sites
from src.output_generator import save_to_csv, save_to_kml, print_summary


def main():
    """Main entry point for the script"""
    parser = argparse.ArgumentParser(
        description='Generate comprehensive eclipse site data from IGME and IGN Eclipse viewer',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate all data (IGME + eclipse visibility + cloud coverage)
  python3 generate_eclipse_site_data.py
  
  # Skip eclipse checking (faster, IGME data only)
  python3 generate_eclipse_site_data.py --no-eclipse
  
  # Skip cloud coverage scraping (faster)
  python3 generate_eclipse_site_data.py --no-cloud
  
  # Skip horizon image downloading (faster)
  python3 generate_eclipse_site_data.py --no-horizon
  
  # Check specific site only
  python3 generate_eclipse_site_data.py --code IB200a
        """
    )
    parser.add_argument('--code', '-c',
                       help='Scrape only a specific site code (e.g., IB200a)')
    parser.add_argument('--no-eclipse', action='store_true',
                       help='Skip eclipse visibility checking')
    parser.add_argument('--no-cloud', action='store_true',
                       help='Skip cloud coverage scraping')
    parser.add_argument('--no-horizon', action='store_true',
                       help='Skip EclipseFan horizon image downloading')
    args = parser.parse_args()
    
    print("=" * 60)
    print("Eclipse Site Data Generator")
    print("=" * 60)
    print()
    
    # Step 1: Scrape IGME sites
    print("STEP 1: Scraping IGME site data...")
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
        results = check_sites_eclipse_visibility(results)
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