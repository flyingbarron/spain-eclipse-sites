#!/usr/bin/env python3
"""
Test cloud coverage integration with existing data
"""

import csv
import sys
import os

# Add parent directory to path so we can import from src
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.cloud_coverage_scraper import scrape_cloud_coverage_for_sites
from src.output_generator import save_to_csv, print_summary

# Read first 3 sites from existing CSV
sites = []
with open('../data/eclipse_site_data.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for i, row in enumerate(reader):
        if i >= 3:  # Only test with 3 sites
            break
        sites.append(row)

print(f"Testing cloud coverage with {len(sites)} sites...")
print("=" * 60)

# Add cloud coverage data
sites = scrape_cloud_coverage_for_sites(sites, delay=2.0)

print("\n" + "=" * 60)
print("Results:")
print("=" * 60)

for site in sites:
    print(f"\n{site['code']} - {site['denominacion']}")
    print(f"  Cloud Coverage: {site.get('cloud_coverage', 'N/A')}%")
    print(f"  Cloud Status: {site.get('cloud_status', 'N/A')}")
    if site.get('cloud_url'):
        print(f"  URL: {site['cloud_url']}")

# Save test output
save_to_csv(sites, 'test_cloud_data.csv')
print_summary(sites)

# Made with Bob
