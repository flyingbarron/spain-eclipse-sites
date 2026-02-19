# Bortle Scale Integration

⚠️ **IMPORTANT NOTE**: The public tile servers for light pollution data are currently unavailable (returning 404 errors). The Bortle scale integration is implemented but requires an accessible data source.

This project includes Bortle scale (light pollution) data collection for eclipse viewing sites.

## What is the Bortle Scale?

The Bortle scale measures light pollution and sky darkness on a scale from 1 (darkest skies) to 9 (brightest city skies):

- **Class 1-2** 🌌: Excellent dark sky (best for astronomy)
- **Class 3-4** 🌃: Rural sky (good for astronomy)  
- **Class 5-6** 🌆: Suburban sky (moderate light pollution)
- **Class 7-9** 🏙️: Urban/city sky (high light pollution)

## Installation

First, install the required dependencies:

```bash
# Using pip (in a virtual environment recommended)
pip install -r requirements.txt

# Or using the virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

### Check Bortle Scale for All Sites

```bash
python3 generate_eclipse_site_data.py --only-bortle
```

### Check Bortle Scale for Specific Site

```bash
python3 generate_eclipse_site_data.py --only-bortle --code IB200
```

### Include in Full Pipeline

```bash
# With Bortle scale (default)
python3 generate_eclipse_site_data.py

# Skip Bortle scale
python3 generate_eclipse_site_data.py --no-bortle
```

## How It Works

The Bortle scraper uses real satellite data:

**Light Pollution Map Tile Data**
- Fetches real VIIRS 2015 light pollution data from public tile servers
- Accesses the same data that powers lightpollutionmap.info
- No API authentication required
- Uses color-coded tiles to determine light pollution levels
- Requires Pillow (PIL) library for image processing
- Returns None (N/A) if data cannot be fetched

## Data Fields

The following fields are added to each site:

- `bortle_scale`: Integer (1-9) or None
- `bortle_status`: 'success', 'failed', or 'not_checked'

## Frontend Display

The standalone viewer displays Bortle scale information in the site details:

```
Bortle Scale (Light Pollution)
🌌 Class 2 - Typical truly dark site
```

## Data Source

**Current Status**: The public tile servers are returning 404 errors and appear to be unavailable.

The scraper was designed to use publicly available VIIRS 2015 light pollution data from:
- https://djlorenz.github.io/astronomy/lp2020/ (currently unavailable)
- https://www.lightpollutionmap.info/ tile servers (currently unavailable)

**Alternative Options**:
1. Download the World Atlas 2015 dataset locally and serve tiles yourself
2. Use a different light pollution API service
3. Contact lightpollutionmap.info for API access
4. Use the ClearDarkSky or similar astronomy services

The code is ready to use once a working tile server or API is available.

## Testing

Test the Bortle conversion logic:

```bash
python3 test_bortle_standalone.py
```

This tests the brightness-to-Bortle conversion without requiring API access.

## Notes

- The estimation method provides reasonable approximations for Spanish locations
- For precise measurements, consider using dedicated light pollution meters
- Bortle scale is most relevant for astronomical observations
- The scale helps identify sites with minimal light pollution for eclipse viewing

## Made with Bob