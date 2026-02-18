# Spain Eclipse Sites 🦕🌑

A comprehensive data collection and visualization tool for Spanish geological sites with 2026 solar eclipse visibility information. Combines data from multiple sources including IGME (Spanish Geological Survey), IGN (National Geographic Institute), EclipseFan, timeanddate.com, Shademap, and Google Maps.

## Overview

This project aggregates geological site information and eclipse planning data for the August 12, 2026 total solar eclipse. It provides:

- **54 geological sites** in Spain (IB200, IB200a-z, IB034, IB034a-z)
- **Eclipse visibility data** with profile diagrams
- **Cloud coverage statistics** for eclipse planning
- **Horizon visualizations** showing eclipse path
- **Sun/shadow maps** for lighting analysis
- **Interactive web viewer** with search, filtering, and routing
- **KML exports** for Google Earth/Maps visualization

## Features

### Data Collection
- ✅ Automated scraping of IGME IELIG database (sites, photos, coordinates)
- ✅ Tourist value ratings and route difficulty levels
- ✅ Eclipse visibility checking via IGN Eclipse 2026 viewer
- ✅ Automated profile diagram capture (IGN)
- ✅ Historical cloud coverage data (timeanddate.com)
- ✅ EclipseFan horizon image downloading
- ✅ Shademap sun/shadow visualization snapshots
- ✅ Google Maps Static API location thumbnails
- ✅ Image caching for improved performance

### Web Viewer
- 🔍 **Search** by site code or name (sticky controls)
- 🌑 **Filter** eclipse-visible sites
- 📊 **Sort** by code, name, or tourist value
- 📚 **Navigation panels** - Resources, About, and Help sections accessible from header
- 🔗 **Resources panel** - Quick links to eclipse websites and planning tools
- 🖼️ **Image gallery** with full-screen carousel (IGME photos cached locally)
- 🗺️ **Interactive maps** with Leaflet/OpenStreetMap
- 📍 **Google Maps thumbnails** - Satellite view for each site location
- 🌄 **Shademap thumbnails** - Sun/shadow visualization with hover preview
- 🚗 **Multi-site route planning** with Ctrl/Cmd+Click selection
- 🧭 **Turn-by-turn directions** for each route segment
- 📦 **Collapsible route summary** to minimize map obstruction
- 📍 **Export routes** to Google Maps or KML for GPS devices
- 📈 **Eclipse profile diagrams** with hover preview (IGN, EclipseFan)
- ☁️ **Cloud coverage data** for eclipse planning
- 🔢 **Site counter** showing filtered results
- 🦕 **Dinosaur emoji** favicon (because dinosaur footprints!)
### Standalone Viewer
- 📦 **No server required** - Self-contained version that works offline
- 🚀 **Easy deployment** - Can be hosted on any static file server
- 💾 **Embedded data** - All site information and images bundled
- 🌐 **Browser-friendly** - Open directly or serve locally
- 📖 **Full documentation** - See [STANDALONE_VIEWER.md](STANDALONE_VIEWER.md)


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

### Build Standalone Viewer

Create a self-contained version that works without a server:

```bash
python3 build_standalone_viewer.py
```

This creates a `standalone_viewer/` directory with:
- All site data embedded as JavaScript
- All cached images bundled locally
- Modified modules that work without server APIs
- Can be opened directly in browser or hosted anywhere

See [STANDALONE_VIEWER.md](STANDALONE_VIEWER.md) for detailed documentation.

```
## Usage

### Generate Data

The main script `generate_eclipse_site_data.py` collects all site data with multiple options:

#### Basic Usage

Collect all data (IGME sites + eclipse visibility + cloud coverage + horizon images):
```bash
python3 generate_eclipse_site_data.py
```

This will:
1. Scrape IGME site data (tourist values, coordinates, etc.)
2. Check eclipse visibility using IGN Eclipse 2026 viewer
3. Scrape cloud coverage data from timeanddate.com
4. Download horizon images from EclipseFan.org
5. Generate CSV and KML output files

#### Command-Line Options

**Skip specific operations** (faster):
```bash
# Skip eclipse checking (IGME data only)
python3 generate_eclipse_site_data.py --no-eclipse

# Check visibility without profile screenshots (faster)
python3 generate_eclipse_site_data.py --no-profile

# Skip cloud coverage scraping
python3 generate_eclipse_site_data.py --no-cloud

# Skip horizon image downloading
python3 generate_eclipse_site_data.py --no-horizon

# Combine multiple skips
python3 generate_eclipse_site_data.py --no-eclipse --no-cloud --no-horizon
```

**Update existing CSV with specific data** (no IGME re-scraping):
```bash
# Add cloud coverage to existing sites
python3 generate_eclipse_site_data.py --only-cloud

# Add horizon images to existing sites
python3 generate_eclipse_site_data.py --only-horizon

# Re-check eclipse visibility for existing sites
python3 generate_eclipse_site_data.py --only-eclipse

# Re-check visibility without downloading profile screenshots (faster)
python3 generate_eclipse_site_data.py --only-eclipse --no-profile

# Update specific site only
python3 generate_eclipse_site_data.py --only-cloud --code IB200a
python3 generate_eclipse_site_data.py --only-horizon --code IB200b

# Use custom CSV file
python3 generate_eclipse_site_data.py --only-cloud --csv data/my_sites.csv
```

**Process specific site** (full pipeline):
```bash
python3 generate_eclipse_site_data.py --code IB200a
```

#### Help

View all options:
```bash
python3 generate_eclipse_site_data.py --help
```

#### Output

The script generates:
- `data/eclipse_site_data.csv` - Complete dataset
- `data/sites.kml` - KML file with 6 organized folders
- `data/ign_visibility_profiles/*.png` - Eclipse profile diagrams (if --no-eclipse not used)
- `data/eclipsefan_visibility_profiles/*.png` - Horizon images (if --no-horizon not used)

**Note**: Eclipse azimuth lines (283.7753°, 50km length) are automatically included in the generated KML file, showing the direction toward the eclipse for each site.

#### Performance Tips

- **First run**: Collect complete data (~30-60 minutes)
  ```bash
  python3 generate_eclipse_site_data.py
  ```

- **Fast visibility check**: Check eclipse visibility without profile screenshots (~10-15 minutes)
  ```bash
  python3 generate_eclipse_site_data.py --no-profile --no-cloud --no-horizon
  ```

- **Add missing data**: Use `--only-*` flags to update existing CSV without re-scraping IGME
  ```bash
  python3 generate_eclipse_site_data.py --only-cloud
  python3 generate_eclipse_site_data.py --only-eclipse --no-profile
  ```

- **Update specific site**: Combine `--only-*` with `--code`
  ```bash
  python3 generate_eclipse_site_data.py --only-horizon --code IB200a
  ```

- **Testing**: Skip slow operations for quick IGME data only (~2-3 minutes)
  ```bash
  python3 generate_eclipse_site_data.py --no-eclipse --no-cloud --no-horizon
  ```

- **Recommended workflow**:
  1. Quick visibility check: `python3 generate_eclipse_site_data.py --no-profile --no-cloud --no-horizon`
  2. Add cloud data: `python3 generate_eclipse_site_data.py --only-cloud`
  3. Add horizon images: `python3 generate_eclipse_site_data.py --only-horizon`
  4. Add profile screenshots: `python3 generate_eclipse_site_data.py --only-eclipse`

### View Data

Start the web viewer:
```bash
python3 serve_viewer.py
```

### Utility Scripts

Additional utility scripts are available in the `tests/` directory:

- **Shademap automation**: `tests/download_shademap_export_playwright.py`
- **EclipseFan horizon images**: `tests/download_eclipsefan_horizon.py`
- **Cloud coverage data**: `tests/add_cloud_data_to_csv.py`
- **Screenshot tools**: Various screenshot utilities

See documentation in `tests/` directory for detailed usage:
- `tests/SHADEMAP_PLAYWRIGHT_README.md` - Shademap automation guide
- `tests/SCREENSHOT_README.md` - Screenshot tools documentation
- `tests/SERVER_SHUTDOWN.md` - Server shutdown options

This will:
- Start a local web server on port 8000
- Automatically open the viewer in your default browser
- Load data from `data/eclipse_site_data.csv`

## Project Structure

```
spain-eclipse-sites/
├── archive/                          # Legacy scripts
│   ├── scrape_igme_sites.py
│   ├── check_eclipse_visibility.py
│   ├── add_eclipse_azimuth.py       # Standalone azimuth tool (deprecated)
│   └── favicon.svg
├── data/                             # Generated data (gitignored)
│   ├── ign_visibility_profiles/      # IGN eclipse visibility diagrams
│   ├── eclipsefan_visibility_profiles/ # EclipseFan horizon profiles
│   ├── shademap_snapshot/            # Shademap visualizations
│   ├── eclipse_site_data.csv         # Main dataset
│   └── sites.kml                     # All sites organized in 6 folders
├── src/                              # Modular source code
│   ├── __init__.py
│   ├── cache.py                     # API response caching
│   ├── config.py                    # Configuration loader
│   ├── exceptions.py                # Custom exception classes
│   ├── logger.py                    # Logging configuration
│   ├── models.py                    # Data models (Site dataclass)
│   ├── igme_scraper.py              # IGME site scraping
│   ├── eclipse_checker.py           # Eclipse visibility checking
│   ├── cloud_coverage_scraper.py    # Cloud coverage data scraping
│   ├── eclipsefan_scraper.py        # EclipseFan horizon image downloading
│   └── output_generator.py          # CSV/KML generation with azimuth lines
├── static/                           # Web viewer assets
│   ├── app.js                       # Interactive viewer logic
│   └── styles.css                   # Viewer styling
├── tests/                            # Test and utility scripts
│   ├── __init__.py                  # Tests package
│   ├── test_models.py               # Unit tests for models
│   ├── test_config.py               # Unit tests for config
│   ├── test_cloud_integration.py    # Cloud coverage integration test
│   ├── test_server_shutdown.py      # Server shutdown test
│   ├── add_cloud_data_to_csv.py     # Add cloud data to existing CSV
│   ├── download_*.py                # Various download utilities
│   ├── scrape_*.py                  # Scraping utilities
│   ├── take_*.py                    # Screenshot utilities
│   ├── SHADEMAP_PLAYWRIGHT_README.md # Shademap automation docs
│   ├── SCREENSHOT_README.md         # Screenshot tools docs
│   └── SERVER_SHUTDOWN.md           # Server shutdown guide
├── config.yaml                       # Application configuration
├── .env.example                      # Environment variables template
├── Dockerfile                        # Docker container definition
├── docker-compose.yml                # Docker Compose configuration
├── .dockerignore                     # Docker build exclusions
├── generate_eclipse_site_data.py     # Main data generation script
├── serve_viewer.py                   # Web viewer server
├── run_tests.py                      # Test runner
├── viewer.html                       # Interactive web interface
├── requirements.txt                  # Python dependencies
├── README.md                         # This file
├── DOCKER.md                         # Docker deployment guide
├── REFACTORING_SUGGESTIONS.md        # Code improvement suggestions
├── CREDITS.md                        # Data attribution
├── LICENSE                           # MIT License
└── .gitignore                        # Git ignore rules
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

| Column | Description |
|--------|-------------|
| `code` | Site code (e.g., IB200a) |
| `denominacion` | Site name (cleaned) |
| `url` | IGME information page URL |
| `valor_turistico` | Tourist value rating (numeric) |
| `confidencialidad` | Privacy status (Public/Private) |
| `route_difficulty` | Route difficulty (Low/Medium/High/Very High) |
| `latitude` | Latitude in decimal degrees (WGS84) |
| `longitude` | Longitude in decimal degrees (WGS84) |
| `eclipse_visibility` | Eclipse visibility status |
| `status` | Scraping status |

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

**`data/ign_visibility_profiles/{code}_profile.png`** - Eclipse visibility profile diagrams from IGN showing the eclipse path and visibility details

### EclipseFan Visibility Profiles

**`data/eclipsefan_visibility_profiles/{code}_horizon.png`** - Horizon profile images from EclipseFan.org showing local topography and eclipse direction

### Shademap Snapshots

**`data/shademap_snapshot/{code}_shademap.jpg`** - Sun/shadow visualization snapshots from Shademap.app at eclipse time

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
- **Shademap Automation**: See `tests/SHADEMAP_PLAYWRIGHT_README.md` for Shademap.app export automation
- **Server Shutdown**: See `tests/SERVER_SHUTDOWN.md` for clean server shutdown options
- **Screenshot Tools**: See `tests/SCREENSHOT_README.md` for EclipseFan.org screenshot utilities
- **Utility Scripts**: Various tools in `tests/` directory for data processing and downloads

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

# Run specific test file
python3 -m unittest tests.test_models
```

Current test coverage:
- ✅ Site dataclass (15 tests)
- ✅ Configuration system (when PyYAML installed)
- ⚠️ Integration tests (legacy, needs update)

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
- playwright >= 1.40.0 (for Shademap automation)
- ChromeDriver (for eclipse visibility checking)

## Docker Deployment

See **[DOCKER.md](DOCKER.md)** for complete Docker deployment instructions.

Quick start:
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
- **EclipseFan.org** - Horizon visualizations
- **timeanddate.com** - Historical cloud coverage data

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