# Bortle Scale Integration

✅ **Working with real satellite data!**

This project includes Bortle scale (light pollution) data collection for eclipse viewing sites using VIIRS 2024 satellite data.

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

**Binary Tile Data (VIIRS 2024)**
- Fetches real VIIRS 2024 light pollution data from djlorenz's binary tiles
- Publicly accessible without authentication
- Uses gzip-compressed binary tiles (one byte per pixel)
- No external dependencies beyond standard Python libraries
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

The scraper uses publicly available VIIRS 2024 light pollution data from:
- https://djlorenz.github.io/astronomy/binary_tiles/2024/
- Binary tiles in gzip-compressed format
- No API key or authentication required
- Data represents the latest satellite measurements of artificial sky brightness

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