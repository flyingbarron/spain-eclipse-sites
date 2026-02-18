# Bortle Scale Integration

This project now includes Bortle scale (light pollution) data for eclipse viewing sites.

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

The Bortle scraper uses two methods:

1. **Primary Method**: Light Pollution Map Tile Data
   - Fetches real VIIRS 2015 light pollution data from public tile servers
   - Accesses the same data that powers lightpollutionmap.info
   - No API authentication required
   - Uses color-coded tiles to determine light pollution levels
   - Requires Pillow (PIL) library for image processing

2. **Fallback Method**: Location-based Estimation
   - Used if tile data is unavailable or Pillow is not installed
   - Estimates Bortle scale based on distance from major Spanish cities
   - Uses geographic heuristics:
     - < 10km from major city: Urban (Bortle 7-8)
     - 10-30km: Suburban (Bortle 5-6)
     - 30-60km: Rural/suburban transition (Bortle 4)
     - 60-100km: Rural (Bortle 3)
     - > 100km: Dark rural (Bortle 2)

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

The scraper uses publicly available VIIRS 2015 light pollution data from:
- https://djlorenz.github.io/astronomy/lp2020/
- This is the same data used by lightpollutionmap.info
- No API key or authentication required
- Data is accessed via map tiles (PNG images)

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