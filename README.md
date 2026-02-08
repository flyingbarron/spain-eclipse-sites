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

### Web Viewer
- 🔍 **Search** by site code or name
- 🌑 **Filter** eclipse-visible sites
- 📊 **Sort** by code, name, or tourist value
- 🖼️ **Image gallery** with full-screen carousel
- 🗺️ **Direct links** to Google Maps, Shademap, and IGN Eclipse viewer
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
│   ├── eclipse_site_data.csv         # Main dataset
│   └── sites.kml                     # All sites organized in 6 folders
├── src/                              # Modular source code
│   ├── __init__.py
│   ├── igme_scraper.py              # IGME site scraping
│   ├── eclipse_checker.py           # Eclipse visibility checking
│   └── output_generator.py          # CSV/KML generation with azimuth lines
├── generate_eclipse_site_data.py     # Main data generation script
├── serve_viewer.py                   # Web viewer server
├── viewer.html                       # Interactive web interface
├── requirements.txt                  # Python dependencies
├── README.md                         # This file
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

### Site Details
- Site information (code, name, tourist value, privacy)
- GPS coordinates
- Eclipse visibility status
- Eclipse profile diagram (hover to preview, click to enlarge)
- Image gallery from IGME website
- Direct links to:
  - IGME information page
  - Google Maps location
  - Shademap.app (sun/shadow visualization)
  - IGN Eclipse 2026 viewer

### Image Carousel
- Full-screen image viewing
- Keyboard navigation (← → arrows)
- Image counter (e.g., "3 / 8")
- ESC to close

## Requirements

- Python 3.7+
- requests >= 2.31.0
- beautifulsoup4 >= 4.12.0
- selenium >= 4.0.0
- ChromeDriver (for eclipse visibility checking)

## License

This project is provided as-is for educational and research purposes.

## Data Attribution

Data sourced from:
- **IGME** (Instituto Geológico y Minero de España) - IELIG Database
- **IGN** (Instituto Geográfico Nacional) - Eclipse 2026 Viewer

Please respect IGME and IGN terms of service when using this data.

## Contributing

Contributions are welcome! The modular structure makes it easy to:
- Add new data sources
- Enhance the viewer
- Improve scraping reliability
- Add new output formats

## Author

Made with Bob 🤖

---

**Note**: The 2026 solar eclipse will be visible from northern Spain on August 12, 2026. This tool helps identify which geological sites will have visibility of this rare astronomical event.