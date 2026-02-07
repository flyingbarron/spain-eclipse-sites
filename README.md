# IGME Tourist Value Scraper

A Python web scraper that extracts tourist value (Valor Turístico) data and geographic coordinates from the Spanish Geological Survey (IGME) IELIG database for geological sites. Generates both CSV and KML outputs for data analysis and map visualization.

## Overview

This script scrapes geological site information from IGME's IELIG (Spanish Inventory of Sites of Geological Interest) database, specifically targeting sites with codes:
- **IB200** (1 site)
- **IB200a** through **IB200z** (26 sites)
- **IB034** (1 site)
- **IB034a** through **IB034z** (26 sites)

**Total: 54 sites**

For each site, it extracts:
- Site code
- Site name (Denominación) - with automatic cleaning of repeated prefixes
- Tourist value (Valor Turístico/VT) rating
- Geographic coordinates (latitude/longitude) from IGME's MapServer API
- URL to the site's information page

The script outputs data in two formats:
- **CSV file** for data analysis and spreadsheet applications
- **KML file** for visualization in Google Earth, Google Maps, and other mapping applications

## Features

- **Automated URL Generation**: Generates URLs for all 54 sites (IB200, IB200a-z, IB034, IB034a-z)
- **Web Scraping**: Extracts site names and tourist values from HTML pages
- **Coordinate Extraction**: Retrieves precise coordinates via IGME MapServer REST API
- **Coordinate Conversion**: Converts Web Mercator (EPSG:3857) to WGS84 (EPSG:4326) lat/lon
- **Polygon Centroid Calculation**: Calculates centroids for polygon geometries
- **Name Cleaning**: Removes redundant prefixes from site names (e.g., "Icnitas de dinosaurio del Weald de Cameros")
- **CSV Export**: Saves all results to a structured CSV file
- **KML Export**: Generates color-coded KML file for map visualization
  - **Green markers** (>5.0): High tourist value sites
  - **Yellow markers** (4.0-5.0): Medium tourist value sites
  - **Red markers** (<4.0): Lower tourist value sites
  - **Gray markers**: Sites with missing/invalid tourist values
- **Error Handling**: Gracefully handles network errors and missing data
- **Rate Limiting**: Includes 1-second delays between requests to be respectful to the server
- **Progress Tracking**: Real-time console output showing scraping progress

## Requirements

- Python 3.7+
- requests >= 2.31.0
- beautifulsoup4 >= 4.12.0

## Installation

1. Clone this repository or download the script
2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Run the script:

```bash
python scrape_igme_sites.py
```

The script will:
1. Generate URLs for all 54 sites
2. Scrape each site's information page
3. Extract tourist values and site names
4. Fetch coordinates from the MapServer API
5. Save results to `igme_tourist_values.csv`
6. Generate color-coded KML file `igme_tourist_values.kml`
7. Display a summary of the scraping operation

### Sample Output

```
============================================================
IGME Tourist Value Scraper
============================================================
Starting to scrape 54 websites...
------------------------------------------------------------
Scraping IB200: https://info.igme.es/ielig/LIGInfo.aspx?codigo=IB200
  ✓ Found VT: 4.2
  ✓ Found coordinates: 39.123456, 2.654321
Scraping IB200a: https://info.igme.es/ielig/LIGInfo.aspx?codigo=IB200a
  ✓ Found VT: 3.5
  ✓ Found coordinates: 39.123456, 2.654321
Scraping IB200b: https://info.igme.es/ielig/LIGInfo.aspx?codigo=IB200b
  ✗ VT not found
...

✓ Results saved to igme_tourist_values.csv
✓ KML file saved to igme_tourist_values.kml

============================================================
SUMMARY
============================================================
Total sites scraped: 54
Successfully extracted: 47
VT not found: 5
Errors: 2
Sites with coordinates: 50

✓ Check 'igme_tourist_values.csv' for results
✓ Check 'igme_tourist_values.kml' for map visualization
```

## Output Formats

### CSV File

The script generates a CSV file (`igme_tourist_values.csv`) with the following columns:

| Column | Description |
|--------|-------------|
| `code` | Site code (e.g., IB200a, IB034b) |
| `denominacion` | Site name (cleaned) |
| `url` | URL to the site's information page |
| `valor_turistico` | Tourist value rating (numeric) |
| `latitude` | Latitude in decimal degrees (WGS84) |
| `longitude` | Longitude in decimal degrees (WGS84) |
| `status` | Scraping status (success/not_found/error) |

#### Status Values

- `success`: Tourist value and coordinates successfully extracted
- `not_found`: Page exists but tourist value not found
- `error: [message]`: Request failed with error message

### KML File

The script also generates a KML file (`igme_tourist_values.kml`) for visualization in mapping applications like Google Earth and Google Maps. The KML file includes:

- **Color-coded markers** based on tourist value:
  - 🟢 **Green** (>5.0): High tourist value sites
  - 🟡 **Yellow** (4.0-5.0): Medium tourist value sites
  - 🔴 **Red** (<4.0): Lower tourist value sites
  - ⚪ **Gray**: Sites with missing or invalid tourist values

- **Rich descriptions** for each site including:
  - Site name (Denominación)
  - Site code
  - Tourist value rating
  - Clickable URL link to the IGME information page

- **Precise coordinates**: Only sites with valid coordinates are included in the KML file

#### Using the KML File

1. **Google Earth**: Open the KML file directly in Google Earth Desktop or Google Earth Pro
2. **Google Maps**:
   - Go to [Google My Maps](https://www.google.com/maps/d/u/0/)
   - Create a new map
   - Import the KML file
3. **Other GIS Software**: Most GIS applications support KML import (QGIS, ArcGIS, etc.)

## Technical Details

### Data Sources

1. **Web Pages**: `https://info.igme.es/ielig/LIGInfo.aspx?codigo=[CODE]`
   - Extracts site names and tourist values from HTML
   
2. **MapServer API**: `https://mapas.igme.es/gis/rest/services/BasesDatos/IGME_IELIG/MapServer/0/query`
   - Retrieves polygon geometries in Web Mercator projection
   - Calculates centroids for coordinate representation

### Coordinate System Conversion

The script converts coordinates from Web Mercator (EPSG:3857) to WGS84 (EPSG:4326):
- Web Mercator is used by the IGME MapServer API
- WGS84 lat/lon is the standard for GPS and mapping applications

### Name Cleaning

The script automatically removes redundant prefixes from site names, including:
- "Icnitas de dinosaurio del Weald de Cameros (La Rioja). Yacimiento de "
- "Icnitas de dinosaurio del Weald de Cameros (Soria). "
- And other variations

This makes the site names more concise and readable.

## Error Handling

The script handles various error scenarios:
- Network timeouts (10-second timeout per request)
- HTTP errors (404, 500, etc.)
- Missing data fields
- Invalid coordinate data
- API failures

All errors are logged in the CSV with appropriate status messages.

## Rate Limiting

The script includes a 1-second delay between requests to avoid overwhelming the IGME servers and to be a good web citizen.

## License

This script is provided as-is for educational and research purposes.

## Data Attribution

Data sourced from:
- **IGME (Instituto Geológico y Minero de España)**
- IELIG Database (Inventario Español de Lugares de Interés Geológico)

Please respect IGME's terms of service when using this data.

## Version Control

This project uses Git for version control. All changes are tracked and committed with descriptive messages.

### Repository Structure
```
scrape_igme/
├── .gitignore              # Git ignore rules
├── README.md               # This file
├── requirements.txt        # Python dependencies
├── scrape_igme_sites.py   # Main scraper script
├── igme_tourist_values.csv # Generated output (not tracked)
└── igme_tourist_values.kml # Generated output (not tracked)
```

### Contributing

When making changes:
1. Make your modifications
2. Test the changes
3. Update the README if functionality changes
4. Commit with a descriptive message

Example commit:
```bash
git add .
git commit -m "Add feature: description of what changed"
```

## Author

Made with Bob