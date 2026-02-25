#!/usr/bin/env python3
"""
Delete Site from CSV and Clean Up Associated Files

This script removes a site entry from the CSV and deletes all associated
scraped data including screenshots, images, and other generated files.

Usage:
    python3 utilities/delete_site.py --code IB200a
    python3 utilities/delete_site.py --code IB200a --dry-run
"""

import argparse
import csv
import os
import sys
from pathlib import Path


def find_site_files(site_code, base_dir='data'):
    """
    Find all files associated with a site code.
    
    Args:
        site_code: Site code to search for
        base_dir: Base directory to search in
    
    Returns:
        List of file paths
    """
    files_to_delete = []
    
    # Directories to search
    search_dirs = [
        'data/scrape/eclipsefan_horizons',
        'data/scrape/ign_profiles',
        'data/scrape/shademap_snapshots',
        'data/scrape/darkskysites',
        'data/scrape/igme_images',
        'standalone_viewer/images/eclipsefan_horizons',
        'standalone_viewer/images/ign_profiles',
        'standalone_viewer/images/shademap_snapshots',
        'standalone_viewer/images/igme',
    ]
    
    for search_dir in search_dirs:
        if not os.path.exists(search_dir):
            continue
        
        # Find files that start with the site code
        for filename in os.listdir(search_dir):
            if filename.startswith(site_code):
                filepath = os.path.join(search_dir, filename)
                files_to_delete.append(filepath)
    
    return files_to_delete


def delete_site_from_csv(site_code, csv_file='data/eclipse_site_data.csv', dry_run=False):
    """
    Delete a site from the CSV file.
    
    Args:
        site_code: Site code to delete
        csv_file: Path to CSV file
        dry_run: If True, don't actually delete, just show what would be deleted
    
    Returns:
        True if site was found and deleted, False otherwise
    """
    
    if not os.path.exists(csv_file):
        print(f"✗ Error: CSV file not found: {csv_file}")
        return False
    
    # Read CSV
    rows = []
    fieldnames = []
    site_found = False
    site_data = None
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames) if reader.fieldnames else []
        
        for row in reader:
            if row.get('code') == site_code:
                site_found = True
                site_data = row
                print(f"\n✓ Found site in CSV: {site_code}")
                print(f"  Name: {row.get('denominacion', 'N/A')}")
                print(f"  Coordinates: {row.get('latitude', 'N/A')}, {row.get('longitude', 'N/A')}")
                # Don't add to rows - this deletes it
            else:
                rows.append(row)
    
    if not site_found:
        print(f"\n✗ Site {site_code} not found in CSV")
        return False
    
    if dry_run:
        print(f"\n[DRY RUN] Would delete site {site_code} from CSV")
        print(f"[DRY RUN] CSV would have {len(rows)} sites (currently {len(rows) + 1})")
    else:
        # Write updated CSV
        with open(csv_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        
        print(f"\n✓ Deleted site {site_code} from CSV")
        print(f"  CSV now has {len(rows)} sites (was {len(rows) + 1})")
    
    return True


def delete_site_files(site_code, dry_run=False):
    """
    Delete all files associated with a site.
    
    Args:
        site_code: Site code
        dry_run: If True, don't actually delete, just show what would be deleted
    
    Returns:
        Number of files deleted
    """
    files = find_site_files(site_code)
    
    if not files:
        print(f"\n✓ No associated files found for {site_code}")
        return 0
    
    print(f"\n{'[DRY RUN] Would delete' if dry_run else 'Deleting'} {len(files)} associated file(s):")
    
    deleted_count = 0
    for filepath in files:
        print(f"  {'[DRY RUN]' if dry_run else '✓'} {filepath}")
        if not dry_run:
            try:
                os.remove(filepath)
                deleted_count += 1
            except Exception as e:
                print(f"    ✗ Error deleting: {e}")
    
    if not dry_run:
        print(f"\n✓ Deleted {deleted_count} file(s)")
    
    return deleted_count if not dry_run else len(files)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Delete a site from CSV and clean up all associated files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Delete a site (with confirmation)
  python3 utilities/delete_site.py --code IB200a
  
  # Dry run - see what would be deleted without actually deleting
  python3 utilities/delete_site.py --code IB200a --dry-run
  
  # Force delete without confirmation
  python3 utilities/delete_site.py --code IB200a --force
  
  # Use custom CSV file
  python3 utilities/delete_site.py --code IB200a --csv data/my_sites.csv

Note: This will delete:
  - Site entry from CSV
  - EclipseFan horizon images
  - IGN profile screenshots
  - Shademap snapshots
  - Dark Sky Sites data
  - IGME images
  - All corresponding files in standalone_viewer/images/
        """
    )
    
    parser.add_argument('--code', '-c', required=True,
                       help='Site code to delete (e.g., IB200a)')
    parser.add_argument('--csv', default='data/eclipse_site_data.csv',
                       help='CSV file path (default: data/eclipse_site_data.csv)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be deleted without actually deleting')
    parser.add_argument('--force', '-f', action='store_true',
                       help='Skip confirmation prompt')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Delete Site and Associated Files")
    print("=" * 60)
    print(f"\nSite code: {args.code}")
    print(f"CSV file: {args.csv}")
    
    if args.dry_run:
        print("\n⚠️  DRY RUN MODE - No files will be deleted")
    
    # Find all files first
    files = find_site_files(args.code)
    
    print(f"\nFound {len(files)} associated file(s)")
    
    # Check if site exists in CSV
    csv_path = args.csv
    site_exists = False
    
    if os.path.exists(csv_path):
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('code') == args.code:
                    site_exists = True
                    break
    
    if not site_exists and not files:
        print(f"\n✗ Site {args.code} not found in CSV and no associated files found")
        print("  Nothing to delete")
        sys.exit(1)
    
    # Confirmation prompt (unless --force or --dry-run)
    if not args.force and not args.dry_run:
        print("\n" + "=" * 60)
        print("⚠️  WARNING: This will permanently delete:")
        if site_exists:
            print(f"  - Site {args.code} from CSV")
        if files:
            print(f"  - {len(files)} associated file(s)")
        print("=" * 60)
        
        response = input("\nAre you sure you want to continue? (yes/no): ")
        if response.lower() not in ['yes', 'y']:
            print("\n✗ Deletion cancelled")
            sys.exit(0)
    
    # Delete from CSV
    if site_exists:
        delete_site_from_csv(args.code, csv_path, dry_run=args.dry_run)
    
    # Delete associated files
    if files:
        delete_site_files(args.code, dry_run=args.dry_run)
    
    # Summary
    print("\n" + "=" * 60)
    if args.dry_run:
        print("DRY RUN COMPLETE")
        print(f"Would delete site {args.code} and {len(files)} file(s)")
        print("\nRun without --dry-run to actually delete")
    else:
        print("DELETION COMPLETE")
        print(f"✓ Site {args.code} and all associated files have been deleted")
        print("\nNext steps:")
        print("  1. Rebuild standalone viewer: python3 build_standalone_viewer.py")
        print("  2. Commit changes to git")
    print("=" * 60)


if __name__ == '__main__':
    main()

# Made with Bob