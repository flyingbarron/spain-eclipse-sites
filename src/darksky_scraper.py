"""
Dark Sky data scraping helpers.

Wraps the utility scraper so the main pipeline can call a single function
instead of inlining import, coordinate parsing, delay, and status mapping.
"""

import os
import sys
import time
from typing import Any, Dict, List
from src.constants import (
    INVALID_COORDINATES_STATUS,
    NO_COORDINATES_STATUS,
    SKIPPED_EXISTING_STATUS,
    SUCCESS_STATUS,
)


def _load_darksky_utility():
    """Dynamically import the Dark Sky utility data scraper."""
    utilities_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'utilities')
    if utilities_dir not in sys.path:
        sys.path.insert(0, utilities_dir)

    from scrape_darkskysites_data import scrape_darkskysites_data  # pyright: ignore[reportMissingImports]
    return scrape_darkskysites_data


def _set_darksky_failure(site: Dict[str, Any], status: str) -> None:
    """Set dark sky fields consistently for non-success outcomes."""
    site['darksky_sqm'] = None
    site['darksky_bortle'] = None
    site['darksky_darkness'] = None
    site['darksky_status'] = status


def scrape_darksky_for_sites(
    sites: List[Dict[str, Any]],
    delay: float = 3.0,
    skip_existing: bool = False,
    data_exists_checker=None,
) -> List[Dict[str, Any]]:
    """Scrape Dark Sky data for a list of site dictionaries."""
    scrape_darkskysites_data = _load_darksky_utility()

    for i, site in enumerate(sites, 1):
        code = site.get('code', 'Unknown')
        lat_str = site.get('latitude', 'N/A')
        lon_str = site.get('longitude', 'N/A')

        if lat_str == 'N/A' or lon_str == 'N/A':
            print(f"[{i}/{len(sites)}] {code}: No coordinates, skipping")
            _set_darksky_failure(site, NO_COORDINATES_STATUS)
            continue

        try:
            lat = float(lat_str)
            lon = float(lon_str)
        except (ValueError, TypeError):
            print(f"[{i}/{len(sites)}] {code}: Invalid coordinates, skipping")
            _set_darksky_failure(site, INVALID_COORDINATES_STATUS)
            continue

        if skip_existing and data_exists_checker and data_exists_checker(str(code), 'darksky'):
            print(f"[{i}/{len(sites)}] {code}: Skipping - Dark Sky data already exists")
            site['darksky_status'] = SKIPPED_EXISTING_STATUS
            continue

        print(f"[{i}/{len(sites)}] {code}: Scraping Dark Sky Sites data...")

        try:
            result = scrape_darkskysites_data(lat, lon, site_code=code, headless=True)

            if result['status'] == SUCCESS_STATUS and result.get('parsed_data'):
                parsed = result['parsed_data']
                site['darksky_sqm'] = parsed.get('sqm')
                site['darksky_bortle'] = parsed.get('bortle')
                site['darksky_darkness'] = parsed.get('darkness')
                site['darksky_status'] = SUCCESS_STATUS
                print(
                    f"  ✓ SQM={parsed.get('sqm')}, "
                    f"Bortle={parsed.get('bortle')}, "
                    f"Darkness={parsed.get('darkness')}%"
                )
            else:
                _set_darksky_failure(site, result['status'])
                print(f"  ✗ Failed: {result['status']}")
        except Exception as e:
            print(f"  ✗ Error: {e}")
            _set_darksky_failure(site, 'error')

        if i < len(sites) and delay > 0:
            time.sleep(delay)

    return sites

# Made with Bob
