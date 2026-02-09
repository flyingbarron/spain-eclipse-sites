# Spain Eclipse Sites 🦕🌑

A comprehensive data collection and visualization tool for Spanish geological sites with 2026 solar eclipse visibility information. Combines data from IGME (Spanish Geological Survey) with eclipse visibility calculations from IGN (National Geographic Institute).

## Overview

This project scrapes geological site information from IGME's IELIG database and checks eclipse visibility for the August 12, 2026 total solar eclipse. It provides:

- **54 geological sites** in Spain (IB200, IB200a-z, IB034, IB034a-z)
- **Eclipse visibility data** for each site
- **Interactive web viewer** with search, filtering, and sorting
- **KML exports** for Google Earth/Maps visualization
- **Eclipse visibility profile diagrams**

## Features

### Data Collection
- ✅ Automated scraping of IGME IELIG database
- ✅ Tourist value ratings and site information
- ✅ Route difficulty levels (translated from Spanish)
- ✅ Precise GPS coordinates from MapServer API
- ✅ Eclipse visibility checking via IGN Eclipse 2026 viewer
- ✅ Automated profile diagram capture
- ✅ EclipseFan horizon image downloading

### Web Viewer
- 🔍 **Search** by site code or name (sticky controls)
- 🌑 **Filter** eclipse-visible sites
- 📊 **Sort** by code, name, or tourist value
- 📚 **Navigation panels** - Resources, About, and Help sections accessible from header
- 🔗 **Resources panel** - Quick links to eclipse websites and planning tools
- 🖼️ **Image gallery** with full-screen carousel
- 🗺️ **Interactive maps** with routing from Hotel Parras Arnedillo
- 🚗 **Multi-site route planning** with Ctrl/Cmd+Click selection
- 🧭 **Turn-by-turn directions** for each route segment
- 📦 **Collapsible route summary** to minimize map obstruction
- 📍 **Export routes** to Google Maps or KML for GPS devices
- 📈 **Eclipse profile diagrams** with hover preview
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
```
## Usage

### Generate Data

Collect all data (IGME sites + eclipse visibility):
```bash
python3 generate_eclipse_site_data.py
```

Skip eclipse checking (faster, IGME data only):
```bash
python3 generate_eclipse_site_data.py --no-eclipse
```

Skip cloud coverage scraping (faster):
```bash
python3 generate_eclipse_site_data.py --no-cloud
```

Skip horizon image downloading (faster):
```bash
python3 generate_eclipse_site_data.py --no-horizon
```

Check specific site only:
```bash
python3 generate_eclipse_site_data.py --code IB200a
```

**Note**: Eclipse azimuth lines (283.7753°, 50km length) are automatically included in the generated KML file, showing the direction toward the eclipse for each site.

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
│   ├── eclipse_profiles/             # Profile diagram images
│   ├── eclipsefan_horizon/           # EclipseFan horizon images
│   ├── shademap/                     # Shademap visualizations
│   ├── eclipse_site_data.csv         # Main dataset
│   └── sites.kml                     # All sites organized in 6 folders
├── src/                              # Modular source code
│   ├── __init__.py
│   ├── igme_scraper.py              # IGME site scraping
│   ├── eclipse_checker.py           # Eclipse visibility checking
│   ├── cloud_coverage_scraper.py    # Cloud coverage data scraping
│   ├── eclipsefan_scraper.py        # EclipseFan horizon image downloading
│   └── output_generator.py          # CSV/KML generation with azimuth lines
├── static/                           # Web viewer assets
│   ├── app.js                       # Interactive viewer logic
│   └── styles.css                   # Viewer styling
├── tests/                            # Test and utility scripts
│   ├── test_cloud_integration.py    # Cloud coverage integration test
│   ├── test_server_shutdown.py      # Server shutdown test
│   ├── add_cloud_data_to_csv.py     # Add cloud data to existing CSV
│   ├── download_*.py                # Various download utilities
│   ├── scrape_*.py                  # Scraping utilities
│   ├── take_*.py                    # Screenshot utilities
│   ├── SHADEMAP_PLAYWRIGHT_README.md # Shademap automation docs
│   ├── SCREENSHOT_README.md         # Screenshot tools docs
│   └── SERVER_SHUTDOWN.md           # Server shutdown guide
├── generate_eclipse_site_data.py     # Main data generation script
├── serve_viewer.py                   # Web viewer server
├── viewer.html                       # Interactive web interface
├── requirements.txt                  # Python dependencies
├── README.md                         # This file
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

### Profile Diagrams

**`data/eclipse_profiles/{code}_profile.png`** - Eclipse visibility profile for each site showing the eclipse path and visibility details

### Horizon Images

**`data/eclipsefan_horizon/{code}_horizon.png`** - Horizon profile images from EclipseFan.org showing local topography and eclipse direction

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

## Requirements

- Python 3.7+
- requests >= 2.31.0
- beautifulsoup4 >= 4.12.0
- selenium >= 4.0.0
- playwright >= 1.40.0 (for Shademap automation)
- ChromeDriver (for eclipse visibility checking)

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