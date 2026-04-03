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
from typing import Any, Dict, List, Set

from src.constants import CSV_FIELDS, STATUS_FIELDS, NOT_CHECKED_STATUS, resolve_data_csv_path
from src.igme_scraper import scrape_all_sites
from src.eclipse_checker import check_sites_eclipse_visibility
from src.cloud_coverage_scraper import scrape_cloud_coverage_for_sites
from src.eclipsefan_scraper import download_horizon_images_for_sites
from src.shademap_scraper import download_shademap_for_sites
from src.darksky_scraper import scrape_darksky_for_sites
from src.output_generator import save_to_csv, save_to_kml, print_summary
from src.pipeline_utils import (
    check_data_exists,
    load_sites_from_csv,
    print_status_summary,
    process_sites_with_skip,
)

STEP_ECLIPSE = 'eclipse'
STEP_CLOUD = 'cloud'
STEP_DARKSKY = 'darksky'
STEP_HORIZON = 'horizon'
STEP_SHADEMAP = 'shademap'
VALID_STEPS = [STEP_ECLIPSE, STEP_CLOUD, STEP_DARKSKY, STEP_HORIZON, STEP_SHADEMAP]
MODE_FULL = 'full'
MODE_UPDATE = 'update'


def parse_steps(value: str) -> List[str]:
    """Parse a comma-separated step list and validate supported step names."""
    steps = [step.strip().lower() for step in value.split(',') if step.strip()]
    invalid_steps = [step for step in steps if step not in VALID_STEPS]
    if invalid_steps:
        raise argparse.ArgumentTypeError(
            f"Invalid step(s): {', '.join(invalid_steps)}. Valid steps: {', '.join(VALID_STEPS)}"
        )
    return steps


def normalize_cli_mode_and_steps(args: argparse.Namespace) -> None:
    """Normalize new and legacy CLI flags into a single mode/steps model."""
    legacy_only_map = {
        STEP_ECLIPSE: args.only_eclipse,
        STEP_CLOUD: args.only_cloud,
        STEP_DARKSKY: args.only_darksky,
        STEP_HORIZON: args.only_horizon,
        STEP_SHADEMAP: args.only_shademap,
    }
    legacy_skip_map = {
        STEP_CLOUD: args.no_cloud,
        STEP_DARKSKY: args.no_darksky,
        STEP_HORIZON: args.no_horizon,
        STEP_SHADEMAP: args.no_shademap,
    }

    legacy_only_steps = [step for step, enabled in legacy_only_map.items() if enabled]
    legacy_skipped_steps = {step for step, enabled in legacy_skip_map.items() if enabled}

    if legacy_only_steps and args.mode == MODE_FULL:
        print(f"⚠️  Legacy --only-* flags detected; using --mode {MODE_UPDATE}")
        args.mode = MODE_UPDATE

    if legacy_only_steps and args.steps:
        print("✗ Error: Cannot combine legacy --only-* flags with --steps")
        sys.exit(1)

    if args.mode == MODE_UPDATE and legacy_skipped_steps:
        print("✗ Error: Cannot use legacy --no-* flags in update mode")
        sys.exit(1)

    if args.mode == MODE_UPDATE and args.skip_steps:
        print("✗ Error: Use --steps with --mode update instead of --skip-steps")
        sys.exit(1)

    if legacy_only_steps:
        args.steps = legacy_only_steps

    if args.mode == MODE_UPDATE and not args.steps:
        args.steps = VALID_STEPS.copy()

    if args.mode == MODE_FULL and not args.steps:
        selected_steps = VALID_STEPS.copy()
        for skipped_step in legacy_skipped_steps:
            if skipped_step in selected_steps:
                selected_steps.remove(skipped_step)
        args.steps = selected_steps

    if args.skip_steps:
        args.steps = [step for step in args.steps if step not in set(args.skip_steps)]

    deduped_steps: List[str] = []
    seen: Set[str] = set()
    for step in args.steps:
        if step not in seen:
            deduped_steps.append(step)
            seen.add(step)
    args.steps = deduped_steps

    if not args.steps and not args.add_site:
        print("✗ Error: No steps selected")
        sys.exit(1)


def get_next_t_code(csv_filename: str = 'eclipse_site_data.csv') -> str:
    """Get the next available Txxxx code."""
    csv_path = resolve_data_csv_path(csv_filename)

    max_num = 0

    if os.path.exists(csv_path):
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    code = row.get('code', '')
                    if code.startswith('T') and len(code) == 5:
                        try:
                            num = int(code[1:])
                            max_num = max(max_num, num)
                        except ValueError:
                            continue
        except Exception as e:
            print(f"Warning: Could not read existing CSV: {e}")

    return f"T{max_num + 1:04d}"


def add_site_manually(args: argparse.Namespace) -> None:
    """Add a new site manually to the CSV."""
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

    if args.site_code:
        code = args.site_code
    else:
        code = get_next_t_code(args.csv)
        print(f"Auto-generated code: {code}")

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
        'cloud_status': NOT_CHECKED_STATUS,
        'cloud_url': None,
        'darksky_sqm': None,
        'darksky_bortle': None,
        'darksky_darkness': None,
        'darksky_status': NOT_CHECKED_STATUS,
        'horizon_status': NOT_CHECKED_STATUS,
        'shademap_status': NOT_CHECKED_STATUS,
        'brochure_file': '',
        'brochure_title': '',
        'brochure_url': '',
        'brochure_source_url': '',
    }

    for field in CSV_FIELDS:
        new_site.setdefault(field, '')
    for field in STATUS_FIELDS.values():
        if not new_site.get(field):
            new_site[field] = NOT_CHECKED_STATUS

    print("\n" + "=" * 60)
    print("Adding new site manually")
    print("=" * 60)
    print(f"Code: {code}")
    print(f"Name: {args.name}")
    print(f"Coordinates: {args.lat}, {args.lon}")
    print(f"Eclipse Visibility: {args.visibility}")
    print("Tourist Value: 5 (default)")
    print("Route Difficulty: low (default)")
    print("IGME URL: N/A")

    results: List[Dict[str, Any]] = []
    csv_path = resolve_data_csv_path(args.csv)
    if os.path.exists(csv_path):
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                results = list(reader)
            print(f"\nLoaded {len(results)} existing sites from CSV")
        except Exception as e:
            print(f"Warning: Could not load existing CSV: {e}")

    if any(site.get('code') == code for site in results):
        print(f"\n✗ Error: Site code {code} already exists in CSV")
        print("  Use --site-code to specify a different code")
        sys.exit(1)

    results.append(new_site)

    print("\n" + "=" * 60)
    print("Saving to CSV...")
    print("=" * 60)
    save_to_csv(results, args.csv)
    print(f"✓ Site {code} added successfully!")
    print("\nYou can now run operations on this site:")
    print(f"  python3 generate_eclipse_site_data.py --mode update --steps cloud --code {code}")
    print(f"  python3 generate_eclipse_site_data.py --mode update --steps horizon --code {code}")
    print(f"  python3 generate_eclipse_site_data.py --mode update --steps shademap --code {code}")


def apply_selected_steps(args: argparse.Namespace, results: List[Dict[str, Any]], update_mode: bool) -> List[Dict[str, Any]]:
    """Run the selected processing steps for either full or update mode."""
    selected_steps = set(args.steps)

    if STEP_ECLIPSE in selected_steps:
        print("\nChecking eclipse visibility..." if update_mode else "\n" + "=" * 60)
        if not update_mode:
            print("STEP 2: Checking eclipse visibility...")
            print("=" * 60)

        save_profiles = not args.no_profile and (update_mode or STEP_ECLIPSE in selected_steps)

        if not update_mode and args.no_eclipse_view_scrape:
            print("Profile image downloading will be skipped (--no-eclipse-view-scrape flag)")
            print("Visibility will still be checked")
        elif args.no_profile:
            print("Profile screenshots will be skipped (--no-profile flag)")

        if args.skip_existing and save_profiles:
            results = process_sites_with_skip(
                results,
                STEP_ECLIPSE,
                lambda sites: check_sites_eclipse_visibility(sites, save_profiles=save_profiles),
                "  Skipping {code}: eclipse profile already exists",
                csv_filename=args.csv,
            )
        else:
            results = check_sites_eclipse_visibility(results, save_profiles=save_profiles)

        if update_mode:
            print(f"\n✓ Eclipse visibility checked for {len(results)} site(s)")
        else:
            print("\n✓ Eclipse visibility checked for all sites")

    if STEP_CLOUD in selected_steps:
        print("\nScraping cloud coverage data..." if update_mode else "\n" + "=" * 60)
        if not update_mode:
            print("STEP 2.5: Scraping cloud coverage data...")
            print("=" * 60)
        print("This will take a while (2 second delay between requests)...")

        if args.skip_existing:
            results = process_sites_with_skip(
                results,
                STEP_CLOUD,
                lambda sites: scrape_cloud_coverage_for_sites(sites, delay=2.0),
                "  Skipping {code}: cloud data already exists",
                csv_filename=args.csv,
            )
        else:
            results = scrape_cloud_coverage_for_sites(results, delay=2.0)

        if update_mode:
            print(f"\n✓ Cloud coverage data scraped for {len(results)} site(s)")
        else:
            print("\n✓ Cloud coverage data scraped for all sites")
    elif not update_mode:
        print("\n⚠️  Skipping cloud coverage data scraping")
        for site in results:
            site['cloud_coverage'] = None
            site['cloud_status'] = NOT_CHECKED_STATUS
            site['cloud_url'] = None

    if STEP_DARKSKY in selected_steps:
        print("\nScraping Dark Sky data..." if update_mode else "\n" + "=" * 60)
        if not update_mode:
            print("STEP 2.6: Scraping Dark Sky data...")
            print("=" * 60)
        print("This will scrape SQM, Bortle scale, and darkness data from darkskysites.com")
        print("This will take a while (3 second delay between requests)...")

        results = scrape_darksky_for_sites(
            results,
            delay=3.0,
            skip_existing=args.skip_existing,
            data_exists_checker=lambda code, kind: check_data_exists(code, kind, args.csv),
        )
        label = (
            f"Dark Sky data scraped for {len(results)} site(s)"
            if update_mode else
            "Dark Sky data scraped for all sites"
        )
        print_status_summary(results, 'darksky_status', label)
    elif not update_mode:
        print("\n⚠️  Skipping Dark Sky data scraping")
        for site in results:
            site['darksky_sqm'] = None
            site['darksky_bortle'] = None
            site['darksky_darkness'] = None
            site['darksky_status'] = NOT_CHECKED_STATUS

    if STEP_HORIZON in selected_steps:
        print("\nDownloading EclipseFan horizon images..." if update_mode else "\n" + "=" * 60)
        if not update_mode:
            print("STEP 2.7: Downloading EclipseFan horizon images...")
            print("=" * 60)
        print("This will take a while (2 second delay between requests)...")

        if args.skip_existing:
            results = process_sites_with_skip(
                results,
                STEP_HORIZON,
                lambda sites: download_horizon_images_for_sites(sites, delay=2.0),
                "  Skipping {code}: horizon image already exists",
                csv_filename=args.csv,
            )
        else:
            results = download_horizon_images_for_sites(results, delay=2.0)

        if update_mode:
            print(f"\n✓ Horizon images downloaded for {len(results)} site(s)")
        else:
            print("\n✓ Horizon images downloaded for all sites")
    elif not update_mode:
        print("\n⚠️  Skipping horizon image downloads")
        for site in results:
            site['horizon_status'] = NOT_CHECKED_STATUS

    if STEP_SHADEMAP in selected_steps:
        print("\nDownloading Shademap visualizations..." if update_mode else "\n" + "=" * 60)
        if not update_mode:
            print("STEP 2.8: Downloading Shademap shadow visualizations...")
            print("=" * 60)
        print("This will take a while (2 second delay between requests)...")

        if args.skip_existing:
            results = process_sites_with_skip(
                results,
                STEP_SHADEMAP,
                lambda sites: download_shademap_for_sites(sites, delay=2.0),
                "  Skipping {code}: shademap already exists",
                skipped_status_field='shademap_status',
                csv_filename=args.csv,
            )
        else:
            results = download_shademap_for_sites(results, delay=2.0)

        label = (
            f"Shademap step complete for {len(results)} site(s)"
            if update_mode else
            "Shademap step complete"
        )
        print_status_summary(results, 'shademap_status', label)
    elif not update_mode:
        print("\n⚠️  Skipping Shademap asset downloading")
        for site in results:
            site['shademap_status'] = NOT_CHECKED_STATUS

    return results


def main() -> None:
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description='Generate comprehensive eclipse site data from IGME and IGN Eclipse viewer',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Full pipeline with all enrichment steps
  python3 generate_eclipse_site_data.py
  python3 generate_eclipse_site_data.py --mode full --steps eclipse,cloud,darksky,horizon,shademap

  # Full pipeline, skipping some steps
  python3 generate_eclipse_site_data.py --skip-steps cloud,shademap
  python3 generate_eclipse_site_data.py --no-profile

  # Update existing CSV only
  python3 generate_eclipse_site_data.py --mode update --steps cloud
  python3 generate_eclipse_site_data.py --mode update --steps eclipse,cloud --code IB200a

  # Add a new site manually
  python3 generate_eclipse_site_data.py --add-site --name "My Site" --lat 42.5 --lon -2.3 --visibility visible
        """
    )
    parser.add_argument('--code', '-c', help='Process only a specific site code (e.g., IB200a)')
    parser.add_argument('--csv', default='eclipse_site_data.csv', help='CSV file to read from (default: data/eclipse_site_data.csv)')
    parser.add_argument('--force', action='store_true', help='Force re-scrape all sites, even if they exist in CSV')

    parser.add_argument('--mode', choices=[MODE_FULL, MODE_UPDATE], default=MODE_FULL, help='Processing mode: full pipeline or update existing CSV')
    parser.add_argument(
        '--steps',
        type=parse_steps,
        default=None,
        help='Comma-separated steps to run: eclipse,cloud,darksky,horizon,shademap',
    )
    parser.add_argument(
        '--skip-steps',
        type=parse_steps,
        default=None,
        help='Comma-separated steps to skip in full mode',
    )

    parser.add_argument('--add-site', action='store_true', help='Add a new site manually to the CSV')
    parser.add_argument('--name', help='Site name (required with --add-site)')
    parser.add_argument('--lat', type=float, help='Latitude in decimal degrees (required with --add-site)')
    parser.add_argument('--lon', type=float, help='Longitude in decimal degrees (required with --add-site)')
    parser.add_argument('--visibility', choices=['visible', 'not_visible', 'unknown'], help='Eclipse visibility status (required with --add-site)')
    parser.add_argument('--site-code', help='Site code (optional, auto-generates Txxxx if not provided)')

    parser.add_argument('--no-eclipse-view-scrape', action='store_true', help='Legacy compatibility: skip eclipse profile image downloads in full mode')
    parser.add_argument('--no-cloud', action='store_true', help='Legacy compatibility: skip cloud coverage data scraping in full mode')
    parser.add_argument('--no-darksky', action='store_true', help='Legacy compatibility: skip Dark Sky data scraping in full mode')
    parser.add_argument('--no-horizon', action='store_true', help='Legacy compatibility: skip EclipseFan horizon image downloads in full mode')
    parser.add_argument('--no-shademap', action='store_true', help='Legacy compatibility: skip Shademap shadow visualization downloads in full mode')
    parser.add_argument('--no-profile', action='store_true', help='Skip profile diagram screenshots (check visibility only)')
    parser.add_argument('--skip-existing', action='store_true', help='Skip step processing if data already exists (checks CSV fields and files)')

    parser.add_argument('--only-eclipse', action='store_true', help='Legacy compatibility: update mode for eclipse step')
    parser.add_argument('--only-cloud', action='store_true', help='Legacy compatibility: update mode for cloud step')
    parser.add_argument('--only-darksky', action='store_true', help='Legacy compatibility: update mode for darksky step')
    parser.add_argument('--only-horizon', action='store_true', help='Legacy compatibility: update mode for horizon step')
    parser.add_argument('--only-shademap', action='store_true', help='Legacy compatibility: update mode for shademap step')

    args = parser.parse_args()
    args.steps = args.steps or []
    args.skip_steps = args.skip_steps or []

    normalize_cli_mode_and_steps(args)

    print("=" * 60)
    print("Eclipse Site Data Generator")
    print("=" * 60)
    print()

    if args.add_site:
        add_site_manually(args)
        return

    if args.mode == MODE_UPDATE:
        print("MODE: Update existing CSV with selected steps")
        print("=" * 60)

        results = load_sites_from_csv(args.csv)

        if args.code:
            filtered_results = [site for site in results if site.get('code') == args.code]
            if not filtered_results:
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

        results = apply_selected_steps(args, results, update_mode=True)

        if args.code:
            print(f"\nMerging updated site {args.code} back into CSV...")
            all_sites = load_sites_from_csv(args.csv)
            for i, site in enumerate(all_sites):
                if site.get('code') == args.code and results:
                    all_sites[i] = results[0]
                    break
            results = all_sites

        print("\n" + "=" * 60)
        print("Saving updated data...")
        print("=" * 60)
        save_to_csv(results, args.csv)
        print(f"✓ Updated {args.csv}")
        print("\n✓ All done!")
        return

    print("MODE: Full pipeline (scrape IGME + selected enrichment steps)")
    print("=" * 60)
    print(f"Selected steps: {', '.join(args.steps)}")

    csv_path = resolve_data_csv_path(args.csv)
    existing_sites: List[Dict[str, Any]] = []
    existing_codes = set()

    if os.path.exists(csv_path) and not args.force:
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                existing_sites = list(reader)
                existing_codes = {site.get('code') for site in existing_sites}
            print(f"\n✓ Found existing CSV with {len(existing_sites)} sites")
            if not args.code:
                print("  Will only scrape NEW sites not in CSV (use --force to re-scrape all)")
        except Exception as e:
            print(f"⚠️  Could not load existing CSV: {e}")

    print("\nSTEP 1: Scraping IGME site data...")
    print("=" * 60)

    if args.code:
        results = scrape_all_sites(specific_code=args.code)
    else:
        from src.igme_scraper import generate_urls, scrape_site

        all_urls = generate_urls()

        if not args.force and existing_codes:
            new_urls = [
                (code, url, custom_data)
                for code, url, custom_data in all_urls
                if code not in existing_codes
            ]
            print(f"  Found {len(all_urls)} total sites in config")
            print(f"  Skipping {len(all_urls) - len(new_urls)} existing sites")
            print(f"  Will scrape {len(new_urls)} new sites")

            if not new_urls:
                print("\n✓ No new sites to scrape!")
                print("  All sites in config already exist in CSV")
                print("  Use --force to re-scrape all sites")
                print("  Or use --mode update --steps ... to update specific data")
                return

            results = []
            for code, url, custom_data in new_urls:
                print(f"\n[{code}] Scraping...")
                site_data = scrape_site(code, url, custom_data)
                if site_data:
                    results.append(site_data)
                    print("  ✓ Success")
                else:
                    print("  ✗ Failed")
        else:
            if args.force:
                print("  --force flag set: will re-scrape all sites")
            results = scrape_all_sites(specific_code=args.code)

    if not results:
        print("\n⚠️  No data collected!")
        sys.exit(1)

    print(f"\n✓ Collected {len(results)} sites from IGME")

    results = apply_selected_steps(args, results, update_mode=False)

    print("\n" + "=" * 60)
    print("STEP 3: Generating output files...")
    print("=" * 60)

    if existing_sites and not args.force:
        print(f"Merging {len(results)} new sites with {len(existing_sites)} existing sites...")
        existing_dict = {site['code']: site for site in existing_sites}
        for site in results:
            existing_dict[site['code']] = site
        all_results = list(existing_dict.values())
        print(f"✓ Total sites in output: {len(all_results)}")
    else:
        all_results = results

    save_to_csv(all_results, 'eclipse_site_data.csv')
    save_to_kml(all_results, 'sites.kml')
    print_summary(all_results)

    print("\n✓ All done!")


if __name__ == "__main__":
    main()

# Made with Bob