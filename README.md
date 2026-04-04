# Spain Eclipse Sites 🦕🌑

**Version:** 1.3.0

A comprehensive data collection and visualization tool for Spanish geological sites with 2026 solar eclipse visibility information. Combines data from multiple sources including IGME (Spanish Geological Survey), IGN (National Geographic Institute), EclipseFan, timeanddate.com, Shademap, and Google Maps.

## 🌐 Live Demo

**View the live site:** [https://brobert.github.io/spain-eclipse-sites/](https://brobert.github.io/spain-eclipse-sites/)

The site is deployed on GitHub Pages and works entirely in the browser without requiring a backend server.

## Overview

This project aggregates geological site information and eclipse planning data for the August 12, 2026 total solar eclipse. It provides:

- **37 configured IGME-series and individual sites**, plus **2 custom test sites** (`T0001`, `T0002`) in `data/igme_sites_config.json`
- **Eclipse visibility data** with profile diagrams
- **Cloud coverage statistics** for eclipse planning
- **Horizon visualizations** showing eclipse path
- **Sun/shadow maps** for lighting analysis
- **Interactive web viewer** with search, filtering, and routing
- **Fully responsive design** - optimized for both desktop and mobile devices
- **GitHub Pages deployment** - works without a backend server
- **KML exports** for Google Earth/Maps visualization

## Deployment Options

This project supports two deployment modes:

### 1. GitHub Pages (Static Deployment) ⭐ Recommended
- **Live at:** [https://brobert.github.io/spain-eclipse-sites/](https://brobert.github.io/spain-eclipse-sites/)
- **Entry point:** `index.html`
- **No server required** - runs entirely in the browser
- **Pre-generated data** - all images and data committed to repository
- **See:** [GITHUB_PAGES.md](GITHUB_PAGES.md) for deployment details

### 2. Local Python Server (Development)
- **Entry point:** `viewer.html` served by `serve_viewer.py`
- **Dynamic features** - API endpoints for image proxying and config
- **Development mode** - for testing data pipeline changes
- **Run:** `python3 serve_viewer.py`

## Features

### Data Collection
- ✅ Automated scraping of IGME IELIG database data (sites, photos, coordinates)
- ✅ Tourist value ratings and route difficulty levels
- ✅ Eclipse visibility checking via IGN Eclipse 2026 viewer
- ✅ Automated profile diagram capture (IGN)
- ✅ Historical cloud coverage data (timeanddate.com)
- ✅ **Dark Sky Sites data** (SQM, Bortle scale, darkness percentage)
- ✅ **Horizon clearance data** - Sun's clearance above terrain at eclipse time (degrees)
- ✅ EclipseFan horizon image downloads
- ✅ Shademap sun/shadow visualization snapshots with retry handling and clearer status reporting
- ✅ Google Maps Static API location thumbnails
- ✅ Image caching for improved performance
- ✅ **Automatic CSV backup** before updates (timestamped)

### Web Viewer
- 🔍 **Search** by site code or name (sticky controls)
- 🌑 **Filter** eclipse-visible sites
- ⭐ **Favorites system** - Save favorite sites with localStorage persistence
- 📝 **Personal notes** - Add notes to sites with collapsible widget
- 🔗 **Share sites** - Generate shareable links to specific sites with URL parameters
- 🔧 **Advanced filtering** - Tourist value, cloud coverage, Bortle scale, route difficulty
- 📊 **Sort** by code, name, or darkness
- 📚 **Navigation panels** - Resources, About, and Help sections accessible from header
- 🔗 **Resources panel** - Quick links to eclipse websites and planning tools
- 🖼️ **Image gallery** with full-screen carousel (IGME photos cached locally)
- 🗺️ **Interactive maps** with Leaflet/OpenStreetMap
- 📍 **Google Maps thumbnails** - Satellite view for each site location
- 🌄 **Horizon profile images** - Local terrain horizon views with hover preview (from ./data/horizons/)
- 🌄 **Shademap thumbnails** - Sun/shadow visualization with hover preview
- 🚗 **Multi-site route planning** with Ctrl/Cmd+Click selection
- 🧭 **Turn-by-turn directions** for each route segment
- 📦 **Collapsible route summary** to minimize map obstruction
- 📍 **Export routes** to Google Maps or KML for GPS devices
- 📈 **Eclipse profile diagrams** with hover preview (IGN, EclipseFan)
- ☁️ **Cloud coverage data** for eclipse planning
- 🏔️ **Horizon clearance** - Shows if terrain blocks the sun during eclipse (color-coded: green=clear, red=blocked)
- 🌌 **Dark Sky Sites data** - SQM values, Bortle scale, darkness percentage
- 🔗 **Dark Sky Sites links** - Direct links to darkskysites.com for each location
- 🔢 **Site counter** showing filtered results
- 💾 **Import/Export** - Share favorites as JSON
- 🦕 **Dinosaur emoji** favicon (because dinosaur footprints!)


### Output Formats
- **CSV** - Complete dataset with all fields
- **KML** - Single file with 6 organized folders by tourist value and eclipse visibility
  - 🟢 High Tourist Value (>5.0) - Eclipse Visible/Not Visible
  - 🟡 Medium Tourist Value (4.0-5.0) - Eclipse Visible/Not Visible
  - 🔴 Lower Tourist Value (<4.0) - Eclipse Visible/Not Visible
  - 🧭 **Eclipse azimuth lines** automatically included (283.7753°, 50km length)
- **PNG** - Eclipse visibility profile diagrams

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/spain-eclipse-sites.git
cd spain-eclipse-sites
```

2. Create a virtual environment (recommended):
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install ChromeDriver (for eclipse visibility checking):
```bash
# macOS
brew install chromedriver

# Linux (Ubuntu/Debian)
sudo apt-get install chromium-chromedriver

# Or download from: https://chromedriver.chromium.org/

5. Optional: preinstall Playwright Chromium (used for Shademap exports)
```bash
python3 -m playwright install chromium
```

If skipped, the Shademap downloader will try to install Chromium automatically on first use.

Shademap behavior:
- Uses Playwright in headless mode
- Attempts automatic Chromium install if the browser binary is missing
- Retries page loads on timeout
- Uses less strict page readiness checks than `networkidle`
- Reports per-site Shademap status summaries in the main pipeline

## Architecture Overview

The repo is organized around a small data pipeline plus a lightweight viewer:

- [`generate_eclipse_site_data.py`](generate_eclipse_site_data.py) orchestrates the pipeline through a simplified CLI
- [`src/constants.py`](src/constants.py) defines canonical step names, schema fields, and output directories
- [`src/pipeline_utils.py`](src/pipeline_utils.py) provides shared helpers for CSV loading, skip-existing behavior, status summaries, and merging updated sites
- [`src/output_generator.py`](src/output_generator.py) writes canonical CSV and KML outputs
- [`serve_viewer.py`](serve_viewer.py) serves the browser viewer plus small JSON/image proxy APIs
- [`src/igme_image_service.py`](src/igme_image_service.py) handles IGME HTML/image caching used by the viewer server
- [`static/js/`](static/js/) contains the modular browser viewer
- [`tests/test_pipeline_utils.py`](tests/test_pipeline_utils.py) covers the shared pipeline helpers and IGME image service helpers
## Usage

### Generate Data

The main script [`generate_eclipse_site_data.py`](generate_eclipse_site_data.py) now uses a simpler CLI built around [`--mode`](generate_eclipse_site_data.py:1), [`--steps`](generate_eclipse_site_data.py:1), and [`--skip-steps`](generate_eclipse_site_data.py:1).

#### Basic Usage

Collect all configured data for new sites:
```bash
python3 generate_eclipse_site_data.py
```

This runs the full pipeline:
1. Scrape IGME site data
2. Run the selected enrichment steps
3. Save merged CSV and KML outputs
4. Create a timestamped CSV backup before overwriting

#### Command-Line Model

**Modes**
- [`--mode full`](generate_eclipse_site_data.py:1): scrape IGME data, then run selected enrichment steps
- [`--mode update`](generate_eclipse_site_data.py:1): load an existing CSV and run only the selected enrichment steps

**Steps**
- `eclipse`
- `cloud`
- `darksky`
- `horizon`
- `shademap`

#### Full Pipeline Examples

```bash
# Default full pipeline
python3 generate_eclipse_site_data.py

# Full pipeline with explicit steps
python3 generate_eclipse_site_data.py --mode full --steps eclipse,cloud,darksky,horizon,shademap

# Skip selected steps
python3 generate_eclipse_site_data.py --skip-steps cloud,shademap

# Visibility check without profile screenshots
python3 generate_eclipse_site_data.py --steps eclipse --no-profile

# Process one configured site only
python3 generate_eclipse_site_data.py --code IB200a

# Skip already-existing outputs/data where supported
python3 generate_eclipse_site_data.py --skip-existing
```

#### Update Existing CSV Examples

```bash
# Add cloud coverage to existing sites
python3 generate_eclipse_site_data.py --mode update --steps cloud

# Add Dark Sky data to existing sites
python3 generate_eclipse_site_data.py --mode update --steps darksky

# Add horizon or shademap assets
python3 generate_eclipse_site_data.py --mode update --steps horizon
python3 generate_eclipse_site_data.py --mode update --steps shademap

# Re-check eclipse visibility for existing sites
python3 generate_eclipse_site_data.py --mode update --steps eclipse

# Re-check eclipse visibility without profile screenshots
python3 generate_eclipse_site_data.py --mode update --steps eclipse --no-profile

# Update several steps at once
python3 generate_eclipse_site_data.py --mode update --steps cloud,darksky,horizon

# Update one site only
python3 generate_eclipse_site_data.py --mode update --steps cloud --code IB200a
python3 generate_eclipse_site_data.py --mode update --steps shademap --code IB200b

# Use a custom CSV file
python3 generate_eclipse_site_data.py --mode update --steps cloud --csv my_sites.csv
```

When [`--skip-existing`](generate_eclipse_site_data.py:1) is used, the pipeline applies the same shared skip/process/merge flow across eclipse, cloud, Dark Sky, horizon, and Shademap steps.

#### Help

View all options:
```bash
python3 generate_eclipse_site_data.py --help
```

#### Output

The script generates:
- [`data/eclipse_site_data.csv`](data/eclipse_site_data.csv) - Complete dataset
- [`data/sites.kml`](data/sites.kml) - KML file with 6 organized folders
- [`data/scrape/ign_profiles/`](data/scrape/ign_profiles/) - IGN eclipse profile diagrams
- [`data/scrape/eclipsefan_horizons/`](data/scrape/eclipsefan_horizons/) - downloaded EclipseFan horizon images
- [`data/scrape/shademap_snapshots/`](data/scrape/shademap_snapshots/) - downloaded Shademap exports
- [`data/brochures/`](data/brochures/) - downloaded site brochures
- [`data/cache/igme_html/`](src/constants.py:23) - cached IGME HTML and derived image JSON
- [`data/cache/igme_images/`](src/constants.py:24) - cached IGME image binaries for the viewer proxy

**Note**: Eclipse azimuth lines (283.7753°, 50km length) are automatically included in the generated KML file, showing the direction toward the eclipse for each site.

#### Performance Tips

- **First run**: collect complete data
  ```bash
  python3 generate_eclipse_site_data.py
  ```

- **Fast visibility-only pass**:
  ```bash
  python3 generate_eclipse_site_data.py --steps eclipse --no-profile
  ```

- **Update missing enrichment later**:
  ```bash
  python3 generate_eclipse_site_data.py --mode update --steps cloud
  python3 generate_eclipse_site_data.py --mode update --steps darksky
  python3 generate_eclipse_site_data.py --mode update --steps horizon
  ```

- **Quick testing**:
  ```bash
  python3 generate_eclipse_site_data.py --skip-steps cloud,darksky,horizon,shademap
  ```

- **Recommended workflow**:
  1. Quick visibility pass: `python3 generate_eclipse_site_data.py --steps eclipse --no-profile`
  2. Add cloud data: `python3 generate_eclipse_site_data.py --mode update --steps cloud`
  3. Add Dark Sky data: `python3 generate_eclipse_site_data.py --mode update --steps darksky`
  4. Add horizon images: `python3 generate_eclipse_site_data.py --mode update --steps horizon`
  5. Add Shademap exports: `python3 generate_eclipse_site_data.py --mode update --steps shademap`

### View Data

#### Option 1: GitHub Pages (Recommended)
Visit the live site: [https://brobert.github.io/spain-eclipse-sites/](https://brobert.github.io/spain-eclipse-sites/)

#### Option 2: Local Development Server
Start the Python web viewer for development:
```bash
python3 serve_viewer.py
```

The viewer server provides:
- Static file serving for the browser UI
- [`/api/config`](serve_viewer.py:76) for API-key configuration
- [`/api/horizon-files`](serve_viewer.py:79) for local horizon-file discovery under [`data/horizons/`](src/constants.py:21)
- [`/api/images`](serve_viewer.py:82) for cached IGME image metadata
- [`/api/proxy-image`](serve_viewer.py:85) for cached image proxying
- [`/api/shutdown`](serve_viewer.py:73) for local shutdown convenience

This will:
- Start a local web server on port 8000
- Automatically open the viewer in your default browser
- Load data from `data/eclipse_site_data.csv`

### Utility Scripts

Additional utility scripts are available in the `utilities/` directory:

- **Dark Sky Sites scraper**: `utilities/scrape_darkskysites_data.py` - Scrape SQM, Bortle, darkness data
- **Dark Sky Sites CSV updater**: `utilities/add_darksky_data_to_csv.py` - Add scraped data to CSV
- **Site deletion tool**: `utilities/delete_site.py` - Delete sites and associated files
- **Shademap automation**: `utilities/download_shademap_export_playwright.py` - auto-installs Playwright Chromium on first use if missing
- **EclipseFan horizon images**: `utilities/download_eclipsefan_horizon.py`

See documentation in `utilities/` directory for detailed usage:
- `utilities/DARKSKYSITES_SCRAPER_README.md` - Dark Sky Sites scraper guide
- `utilities/SHADEMAP_PLAYWRIGHT_README.md` - Shademap automation guide
- `utilities/SCREENSHOT_README.md` - Screenshot tools documentation

## Project Structure

```
spain-eclipse-sites/
├── index.html                        # GitHub Pages entry point
├── viewer.html                       # Local development entry point
├── gh-pages/                         # GitHub Pages specific modules
│   ├── config.js                     # Static config loader
│   ├── main.js                       # App initialization (no API calls)
│   ├── image-loader.js               # Static image loading with MD5 hashing
│   ├── site-details.js               # Site details (GitHub Pages compatible)
│   └── data-loader.js                # CSV data loader
├── archive/                          # Legacy scripts and old viewer experiments
├── data/                             # Generated data (committed for GitHub Pages)
│   ├── scrape/ign_profiles/          # IGN eclipse visibility diagrams
│   ├── scrape/eclipsefan_horizons/   # EclipseFan horizon profiles
│   ├── scrape/shademap_snapshots/    # Shademap visualizations
│   ├── scrape/darkskysites/          # Dark Sky utility outputs
│   ├── brochures/                    # Downloaded brochure PDFs
│   ├── cache/igme_html/              # Cached IGME HTML + image metadata JSON
│   ├── cache/igme_images/            # Cached IGME image binaries
│   ├── horizons/                     # Local horizon images used directly by the viewer
│   ├── eclipse_site_data.csv         # Main dataset (committed)
│   ├── sites.kml                     # Main KML output
│   ├── igme_sites_config.json        # Configured IGME and custom sites
│   ├── horizon_files.json            # Horizon image mappings (GitHub Pages)
│   └── google_maps_thumbnails/       # Pre-generated map thumbnails
├── src/                              # Modular pipeline and viewer-support code
│   ├── constants.py                  # Canonical schema, step names, and output paths
│   ├── pipeline_utils.py             # Shared CSV/merge/skip/status helpers
│   ├── igme_image_service.py         # Viewer-side IGME HTML/image caching helpers
│   ├── igme_scraper.py               # IGME site scraping
│   ├── eclipse_checker.py            # Eclipse visibility checking
│   ├── cloud_coverage_scraper.py     # Cloud coverage data scraping
│   ├── darksky_scraper.py            # Dark Sky pipeline integration
│   ├── eclipsefan_scraper.py         # EclipseFan horizon image downloading
│   ├── shademap_scraper.py           # Shademap visualization downloading
│   ├── output_generator.py           # CSV/KML generation and summaries
│   ├── config.py                     # Configuration loader
│   ├── models.py                     # Data models
│   ├── logger.py                     # Logging helpers
│   ├── cache.py                      # General cache helpers
│   └── exceptions.py                 # Custom exception classes
├── static/                           # Shared static assets
│   ├── styles.css                    # Viewer styling
│   └── js/                           # Modular browser viewer code (local dev)
├── tests/
│   ├── test_pipeline_utils.py        # Shared helper and IGME image service tests
│   ├── test_models.py                # Unit tests for models
│   ├── test_config.py                # Unit tests for config
│   └── test_cloud_integration.py     # Cloud coverage integration test
├── utilities/                        # One-off data utilities and helper docs
│   ├── download_google_maps_thumbnails.py  # Pre-generate map thumbnails
│   └── README.md                     # Utilities documentation
├── generate_eclipse_site_data.py     # Main data generation script
├── serve_viewer.py                   # Local development server
├── run_tests.py                      # Test runner
├── config.yaml                       # Application configuration
├── config.json                       # Static config for GitHub Pages
├── requirements.txt                  # Python dependencies
├── .env.example                      # Environment variables template
├── README.md                         # Main documentation (this file)
├── GITHUB_PAGES.md                   # GitHub Pages deployment guide
└── CONFIGURATION.md                  # Configuration reference
```

## Data Sources

### IGME (Instituto Geológico y Minero de España)
- **IELIG Database**: Spanish Inventory of Sites of Geological Interest
- **Site Information**: Names, tourist values, privacy status
- **MapServer API**: Precise GPS coordinates

### IGN (Instituto Geográfico Nacional)
- **Eclipse 2026 Viewer**: Official eclipse visibility calculator
- **Visibility Profiles**: Detailed eclipse path diagrams
- **Authoritative Data**: Based on precise astronomical calculations

## Output Files

### CSV File (`data/eclipse_site_data.csv`)

| Column | Description | Source |
|--------|-------------|--------|
| `code` | Site code (e.g., IB200a) | IGME IELIG Database |
| `denominacion` | Site name (cleaned) | IGME IELIG Database |
| `url` | IGME information page URL | IGME IELIG Database |
| `valor_turistico` | Tourist value rating (numeric) | IGME IELIG Database |
| `confidencialidad` | Privacy status (Public/Private) | IGME IELIG Database |
| `route_difficulty` | Route difficulty (Low/Medium/High/Very High) | IGME IELIG Database |
| `latitude` | Latitude in decimal degrees (WGS84) | IGME MapServer API |
| `longitude` | Longitude in decimal degrees (WGS84) | IGME MapServer API |
| `eclipse_visibility` | Eclipse visibility status | IGN Eclipse 2026 Viewer |
| `status` | Scraping status | Generated by script |
| `cloud_coverage` | Historical cloud coverage percentage | timeanddate.com |
| `cloud_status` | Cloud data scraping status | Generated by script |
| `cloud_url` | URL to cloud coverage data | timeanddate.com |
| `horizon_status` | EclipseFan horizon image status | Generated by script |
| `shademap_status` | Shademap visualization status | Generated by script |
| `darksky_sqm` | Sky Quality Meter value | darkskysites.com |
| `darksky_bortle` | Bortle scale value | darkskysites.com |
| `darksky_darkness` | Darkness percentage | darkskysites.com |
| `darksky_status` | Dark Sky Sites scraping status | Generated by script |

### Eclipse Visibility Values

- `visible` - Eclipse IS visible from this location
- `not_visible` - Eclipse IS NOT visible from this location
- `unknown` - Could not determine visibility
- `timeout` - Page took too long to load
- `error` - Error occurred while checking
- `no_coordinates` - Site has no coordinate data
- `not_checked` - Eclipse checking was skipped

### KML Files

**`data/sites.kml`** - All sites organized into 6 folders:
- 🟢 **High Tourist Value (>5.0)** - Eclipse Visible
- 🟢 **High Tourist Value (>5.0)** - Eclipse Not Visible
- 🟡 **Medium Tourist Value (4.0-5.0)** - Eclipse Visible
- 🟡 **Medium Tourist Value (4.0-5.0)** - Eclipse Not Visible
- 🔴 **Lower Tourist Value (<4.0)** - Eclipse Visible
- 🔴 **Lower Tourist Value (<4.0)** - Eclipse Not Visible

Each folder contains:
- Site markers with detailed information
- 🧭 **Eclipse azimuth lines** (yellow, 50km) pointing toward the eclipse direction (283.7753°)

### IGN Visibility Profiles

**`data/scrape/ign_profiles/{code}_profile.png`** - Eclipse visibility profile diagrams from IGN showing the eclipse path and visibility details

### EclipseFan Visibility Profiles

**`data/scrape/eclipsefan_horizons/{code}_horizon.png`** - Horizon profile images from EclipseFan.org showing local topography and eclipse direction

### Shademap Snapshots

**`data/scrape/shademap_snapshots/{code}_shademap.jpg`** - Sun/shadow visualization snapshots from Shademap.app at eclipse time

### Brochures

**`data/brochures/*.pdf`** - Downloaded brochures associated with matching sites and exposed in the viewer

## Technical Details

### Coordinate Systems

The project handles two coordinate systems:
- **WGS84 (EPSG:4326)**: Standard GPS coordinates (latitude/longitude)
- **Web Mercator (EPSG:3857)**: Used by IGME MapServer and IGN Eclipse viewer

Automatic conversion between systems is handled by the scripts.

### Web Scraping

- **BeautifulSoup**: HTML parsing for IGME pages
- **Selenium WebDriver**: JavaScript rendering for IGN Eclipse viewer
- **Rate Limiting**: 1-second delays between requests
- **Error Handling**: Graceful handling of network errors and missing data

### Eclipse Visibility Checking

The script uses Selenium to:
1. Navigate to IGN Eclipse 2026 viewer with site coordinates
2. Wait for JavaScript to render (up to 60 seconds)
3. Wait for visibility profile to load (up to 30 seconds)
4. Capture screenshot of profile diagram
5. Extract visibility text from rendered page

**Note**: The IGN viewer requires full browser rendering, so visible Chrome windows will open during the process.

## Viewer Features

### Search and Filter
- **Text search**: Filter by site code or name
- **Eclipse filter**: Show only eclipse-visible sites
- **Sort options**: By code, name, or tourist value
- **Sticky controls**: Search and filters stay visible while scrolling

### Site Details
- Site information (code, name, tourist value, privacy)
- GPS coordinates
- Eclipse visibility status
- **Eclipse profile diagram** (hover to preview, click to enlarge)
- **Shademap thumbnail** (hover to preview, click to enlarge) - shows sun/shadow visualization at eclipse time
- **EclipseFan horizon view** - shows local horizon profile
- Image gallery from IGME website
- Direct links to:
  - 🪨 IGME information page
  - 📍 Google Maps location
  - 🌄 Shademap.app (sun/shadow visualization)
  - 🕐 timeanddate.com (cloud coverage data)
  - 🌌 Dark Sky Sites (SQM, Bortle, darkness data)
  - 🌒 EclipseFan.org (horizon views)
  - 🌑 IGN Eclipse 2026 viewer

### Interactive Maps
- **Single-site view**: Map with route from Hotel Parras Arnedillo
- **Multi-site planning**: Select multiple sites (Ctrl/Cmd+Click)
- **Route visualization**: Color-coded segments with distance/time
- **Collapsible summary**: Minimize route summary to see more of the map
- **Turn-by-turn directions**: Click route segments for detailed navigation
- **Export options**:
  - 📍 Open complete route in Google Maps
  - 💾 Download as KML file for GPS devices/Google Earth

### Route Planning
1. **Select sites**: Ctrl/Cmd+Click multiple sites in the sidebar
2. **View route**: Switch to Map tab to see the route
3. **Collapse summary**: Click arrow to minimize route summary panel
4. **Get directions**: Click route segments for turn-by-turn instructions
5. **Export**: Use buttons to open in Google Maps or download KML

### Image Carousel
- Full-screen image viewing
- Keyboard navigation (← → arrows)
- Image counter (e.g., "3 / 8")
- ESC to close

### Additional Tools
- **Shademap Automation**: See [`utilities/SCREENSHOT_README.md`](utilities/SCREENSHOT_README.md) and the related Playwright/download utilities in [`utilities/`](utilities/)
- **Server Shutdown**: See [`utilities/SERVER_SHUTDOWN.md`](utilities/SERVER_SHUTDOWN.md) for clean server shutdown options
- **Brochure Downloading**: See [`utilities/download_brochures.py`](utilities/download_brochures.py)
- **Utility Scripts**: Supporting tools live under [`utilities/`](utilities/)

## Configuration

The application uses a YAML-based configuration system. See **[CONFIGURATION.md](CONFIGURATION.md)** for complete documentation.

Quick configuration:
- Edit `config.yaml` for application settings
- Use environment variables for container deployment (see `.env.example`)
- Override settings with `ECLIPSE_SITES_*` environment variables

Example:
```bash
export ECLIPSE_SITES_LOGGING_LEVEL=DEBUG
export ECLIPSE_SITES_SCRAPING_RATE_LIMIT_DELAY=2.0
python3 generate_eclipse_site_data.py
```

## Testing

Run the test suite:
```bash
# Install dependencies first
pip install -r requirements.txt

# Run all tests
python3 run_tests.py

# Run focused helper coverage
python3 -m unittest tests.test_pipeline_utils

# Run a specific test module
python3 -m unittest tests.test_models
```

Current test coverage includes:
- ✅ [`tests/test_pipeline_utils.py`](tests/test_pipeline_utils.py) for shared pipeline helpers and IGME image service caching/extraction helpers
- ✅ [`tests/test_models.py`](tests/test_models.py) for the site data model
- ✅ [`tests/test_config.py`](tests/test_config.py) for the configuration system
- ⚠️ Some tests require optional dependencies such as PyYAML or BeautifulSoup

## New Features (2026-02-09 Refactoring)

### 🎯 Type Safety
- **Type hints** added to all Python modules
- Improved code documentation and IDE support
- Better error detection during development

### ⚙️ Configuration System
- **YAML-based configuration** (`config.yaml`)
- Environment variable overrides for containers
- Centralized settings management
- See `.env.example` for available options

### 📦 Data Models
- **Site dataclass** with type-safe properties
- Helper methods for data conversion
- Convenient property accessors (e.g., `is_eclipse_visible`, `has_low_cloud_coverage`)

### 📝 Logging
- **Structured logging** with file rotation
- Configurable log levels
- EmojiLogger for better console output
- Replaces print statements throughout

### 🚨 Error Handling
- **Custom exception classes** for different error types
- Better error messages and debugging
- Retry logic for network errors

### 🧪 Testing
- **Unit tests** for models and configuration
- Test runner script (`run_tests.py`)
- Foundation for comprehensive test coverage

### 💾 Caching
- **File-based API response caching**
- Configurable TTL (time to live)
- Reduces API calls and improves performance
- `@cached` decorator for easy function caching

### 🐳 Docker Support
- **Dockerfile** for containerized deployment
- **docker-compose.yml** for easy setup
- Health checks and volume mounts
- See `DOCKER.md` for deployment guide

## Requirements

- Python 3.11+ (3.7+ for non-Docker)
- requests >= 2.31.0
- beautifulsoup4 >= 4.12.0
- selenium >= 4.0.0
- pyyaml >= 6.0.0
- playwright >= 1.40.0 (Python package for Shademap and Dark Sky automation)
- Playwright Chromium browser binary (auto-installed on first Shademap use, or manually via `python3 -m playwright install chromium`)
- ChromeDriver (for eclipse visibility checking)

## Deployment

### GitHub Pages (Production)
The site is automatically deployed to GitHub Pages when changes are pushed to the main branch.

**Live URL:** [https://brobert.github.io/spain-eclipse-sites/](https://brobert.github.io/spain-eclipse-sites/)

See **[GITHUB_PAGES.md](GITHUB_PAGES.md)** for deployment details and **[DEPLOY_TO_GITHUB_PAGES.md](DEPLOY_TO_GITHUB_PAGES.md)** for step-by-step instructions.

### Docker (Optional)
For containerized local development, see **[DOCKER.md](DOCKER.md)** for complete Docker deployment instructions.

```bash
# Using Docker Compose
docker-compose up -d

# Access at http://localhost:8000
```

## License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

**Important Notes**:
- **Code**: Open source under MIT License
- **Data**: Subject to original providers' terms of service (see [CREDITS.md](CREDITS.md))
- **Intended Use**: Educational and non-commercial purposes
- **Commercial Use**: May require additional permissions from data providers

The MIT License applies to the software code. All data remains the property of respective sources and is subject to their terms of service.

## Data Attribution

This project uses data from multiple sources. See **[CREDITS.md](CREDITS.md)** for complete attribution and terms of use.

**Primary Sources**:
- **IGME** (Instituto Geológico y Minero de España) - IELIG Database
- **IGN** (Instituto Geográfico Nacional) - Eclipse 2026 Viewer
- **Dark Sky Sites** (darkskysites.com) - SQM, Bortle scale, darkness data
- **EclipseFan.org** - Horizon visualizations
- **timeanddate.com** - Historical cloud coverage data
- **Shademap.app** - Sun/shadow visualizations

**Important**: This project is for educational and non-commercial use only. Please respect all data providers' terms of service.

## Contributing

Contributions are welcome! The modular structure makes it easy to:
- Add new data sources
- Enhance the viewer
- Improve scraping reliability
- Add new output formats

## Author

**Robert Barron**

Created with assistance from Bob 🤖

---

**Note**: The 2026 solar eclipse will be visible from northern Spain on August 12, 2026. This tool helps identify which geological sites will have visibility of this rare astronomical event.