"""
Shared project constants for schema, status fields, data files, and output paths.
"""

import os
from typing import Dict, Tuple

DATA_DIR = 'data'
SCRAPE_DIR = os.path.join(DATA_DIR, 'scrape')
CACHE_DIR = os.path.join(DATA_DIR, 'cache')

DEFAULT_CSV_FILENAME = 'eclipse_site_data.csv'
DEFAULT_KML_FILENAME = 'sites.kml'
IGME_SITES_CONFIG_PATH = os.path.join(DATA_DIR, 'igme_sites_config.json')

IGN_PROFILES_DIR = os.path.join(SCRAPE_DIR, 'ign_profiles')
ECLIPSEFAN_HORIZONS_DIR = os.path.join(SCRAPE_DIR, 'eclipsefan_horizons')
SHADEMAP_SNAPSHOTS_DIR = os.path.join(SCRAPE_DIR, 'shademap_snapshots')
DARKSKY_SCRAPE_DIR = os.path.join(SCRAPE_DIR, 'darkskysites')
BROCHURES_DIR = os.path.join(DATA_DIR, 'brochures')
HORIZON_FILES_DIR = os.path.join(DATA_DIR, 'horizons')

IGME_HTML_CACHE_DIR = os.path.join(CACHE_DIR, 'igme_html')
IGME_IMAGE_CACHE_DIR = os.path.join(CACHE_DIR, 'igme_images')

STEP_ECLIPSE = 'eclipse'
STEP_CLOUD = 'cloud'
STEP_DARKSKY = 'darksky'
STEP_HORIZON = 'horizon'
STEP_SHADEMAP = 'shademap'
VALID_STEPS = [STEP_ECLIPSE, STEP_CLOUD, STEP_DARKSKY, STEP_HORIZON, STEP_SHADEMAP]

MODE_FULL = 'full'
MODE_UPDATE = 'update'

CSV_FIELDS = [
    'code',
    'denominacion',
    'url',
    'valor_turistico',
    'confidencialidad',
    'route_difficulty',
    'latitude',
    'longitude',
    'eclipse_visibility',
    'status',
    'cloud_coverage',
    'cloud_status',
    'cloud_url',
    'horizon_status',
    'shademap_status',
    'darksky_sqm',
    'darksky_bortle',
    'darksky_darkness',
    'darksky_status',
    'brochure_file',
    'brochure_title',
    'brochure_url',
    'brochure_source_url',
]

STATUS_FIELDS = {
    'cloud': 'cloud_status',
    'darksky': 'darksky_status',
    'horizon': 'horizon_status',
    'shademap': 'shademap_status',
}

DATA_PRESENCE_FIELDS = {
    'cloud': 'cloud_coverage',
    'darksky': 'darksky_sqm',
}

NOT_CHECKED_STATUS = 'not_checked'
SKIPPED_EXISTING_STATUS = 'skipped_existing'
NO_COORDINATES_STATUS = 'no_coordinates'
INVALID_COORDINATES_STATUS = 'invalid_coordinates'
SUCCESS_STATUS = 'success'

FILE_OUTPUT_PATHS: Dict[str, Tuple[str, str]] = {
    STEP_ECLIPSE: (IGN_PROFILES_DIR, '{site_code}_profile.png'),
    STEP_HORIZON: (ECLIPSEFAN_HORIZONS_DIR, '{site_code}_horizon.png'),
    STEP_SHADEMAP: (SHADEMAP_SNAPSHOTS_DIR, '{site_code}_shademap.jpg'),
}

SUMMARY_OUTPUT_LABELS: Dict[str, str] = {
    STEP_ECLIPSE: 'data/scrape/ign_profiles/*.png - IGN visibility profile diagrams',
    STEP_HORIZON: 'data/scrape/eclipsefan_horizons/*.png - EclipseFan horizon profiles',
    STEP_SHADEMAP: 'data/scrape/shademap_snapshots/*.jpg - Shademap shadow visualizations',
}


def data_file_path(filename: str) -> str:
    """Return a path under the data directory."""
    return os.path.join(DATA_DIR, filename)


def resolve_data_csv_path(csv_filename: str = DEFAULT_CSV_FILENAME) -> str:
    """Return CSV path under data/ unless already prefixed."""
    return csv_filename if csv_filename.startswith(f'{DATA_DIR}/') else data_file_path(csv_filename)


def get_output_file_path(data_type: str, site_code: str) -> str:
    """Return the canonical output file path for a site and data type."""
    directory, pattern = FILE_OUTPUT_PATHS[data_type]
    return os.path.join(directory, pattern.format(site_code=site_code))

# Made with Bob
