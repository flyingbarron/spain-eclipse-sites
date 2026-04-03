"""
Shared pipeline utility helpers for loading, merging, status counting,
skip-existing processing, and CSV-backed existence checks.
"""

import csv
import os
import sys
from typing import Any, Callable, Dict, List, Optional

from src.constants import (
    DATA_PRESENCE_FIELDS,
    MODE_FULL,
    SKIPPED_EXISTING_STATUS,
    get_output_file_path,
    resolve_data_csv_path,
)


def load_sites_from_csv(csv_filename: str = 'eclipse_site_data.csv') -> List[Dict[str, Any]]:
    """Load sites from an existing CSV file."""
    csv_path = resolve_data_csv_path(csv_filename)

    sites: List[Dict[str, Any]] = []
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                sites.append(row)
        print(f"✓ Loaded {len(sites)} sites from {csv_path}")
        return sites
    except FileNotFoundError:
        print(f"✗ Error: {csv_path} not found!")
        print(f"  Run the full pipeline first, or use [`--mode {MODE_FULL}`](generate_eclipse_site_data.py:1) to create the base data.")
        sys.exit(1)


def check_data_exists(site_code: str, data_type: str, csv_filename: str = 'eclipse_site_data.csv') -> bool:
    """Check whether a site's output/file-backed data already exists."""
    if data_type in {'eclipse', 'horizon', 'shademap'}:
        output_path = get_output_file_path(data_type, site_code)
        return os.path.exists(output_path)

    data_field = DATA_PRESENCE_FIELDS.get(data_type)
    if not data_field:
        return False

    csv_path = resolve_data_csv_path(csv_filename)
    if not os.path.exists(csv_path):
        return False

    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('code') == site_code:
                    return row.get(data_field) not in [None, '', 'N/A']
    except Exception:
        return False

    return False


def merge_sites_by_code(
    base_sites: List[Dict[str, Any]],
    updated_sites: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Merge updated site dictionaries into a base list by site code."""
    updated_by_code = {site.get('code'): site for site in updated_sites}
    return [updated_by_code.get(site.get('code'), site) for site in base_sites]


def count_statuses(sites: List[Dict[str, Any]], status_field: str) -> Dict[str, int]:
    """Count sites by a given status field."""
    counts: Dict[str, int] = {}
    for site in sites:
        status = str(site.get(status_field, 'unknown'))
        counts[status] = counts.get(status, 0) + 1
    return counts


def print_status_summary(sites: List[Dict[str, Any]], status_field: str, label: str) -> None:
    """Print a sorted status summary for a processing step."""
    counts = count_statuses(sites, status_field)
    summary = ", ".join(f"{status}={count}" for status, count in sorted(counts.items()))
    print(f"\n✓ {label}: {summary}")


def process_sites_with_skip(
    sites: List[Dict[str, Any]],
    data_type: str,
    processor: Callable[[List[Dict[str, Any]]], List[Dict[str, Any]]],
    skip_message: str,
    skipped_status_field: Optional[str] = None,
    skipped_status_value: str = SKIPPED_EXISTING_STATUS,
    csv_filename: str = 'eclipse_site_data.csv',
    data_exists_checker: Optional[Callable[[str, str], bool]] = None,
) -> List[Dict[str, Any]]:
    """Apply skip-existing filtering, run a processor, and merge results back."""
    sites_to_process: List[Dict[str, Any]] = []
    skipped_count = 0
    checker = data_exists_checker or (lambda code, kind: check_data_exists(code, kind, csv_filename))

    for site in sites:
        code = str(site.get('code', ''))
        if checker(code, data_type):
            print(skip_message.format(code=code))
            skipped_count += 1
            if skipped_status_field:
                site[skipped_status_field] = skipped_status_value
        else:
            sites_to_process.append(site)

    if skipped_count > 0:
        print(f"  Skipped {skipped_count} sites with existing {data_type} data")

    processed_sites = processor(sites_to_process)
    return merge_sites_by_code(sites, processed_sites)

def merge_updated_site(base_sites: List[Dict[str, Any]], updated_site: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Merge one updated site dictionary into a base list by site code."""
    return merge_sites_by_code(base_sites, [updated_site])


# Made with Bob