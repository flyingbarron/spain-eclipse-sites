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
from src.output_generator import save_to_csv, save_to_kml, print_summary


def main():
    """Main entry point for the script"""
    parser = argparse.ArgumentParser(
        description='Generate comprehensive eclipse site data from IGME and IGN Eclipse viewer',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate all data (IGME + eclipse visibility)
  python3 generate_eclipse_site_data.py
  
  # Skip eclipse checking (faster, IGME data only)
  python3 generate_eclipse_site_data.py --no-eclipse
  
  # Check specific site only
  python3 generate_eclipse_site_data.py --code IB200a
        """
    )
    parser.add_argument('--code', '-c', 
                       help='Scrape only a specific site code (e.g., IB200a)')
    parser.add_argument('--no-eclipse', action='store_true',
                       help='Skip eclipse visibility checking')
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