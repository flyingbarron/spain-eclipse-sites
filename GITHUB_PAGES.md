# GitHub Pages Deployment Guide

This project includes a GitHub Pages compatible version that works without the Python backend.

## Files Overview

### GitHub Pages Specific Files

- **`index.html`** - Main entry point for GitHub Pages (uses gh-pages modules)
- **`config.json`** - Static configuration file for API keys
- **`gh-pages/`** - Modified JavaScript modules that work without Python backend
  - `config.js` - Loads config from static JSON file
  - `main.js` - Initializes app without API calls
  - `image-loader.js` - Loads images from static cache

### Shared Files (Used by Both Versions)

- **`viewer.html`** - Local development version (uses Python backend via `serve_viewer.py`)
- **`static/`** - All CSS, JS modules, and assets
- **`data/`** - CSV data, images, and other static content

## Setup Instructions

### 1. Generate All Data Locally

Before deploying to GitHub Pages, run the data pipeline locally to generate all necessary files:

```bash
# Generate site data and download all images
python generate_eclipse_site_data.py

# This will create:
# - data/eclipse_site_data.csv
# - data/igme_images/ (cached IGME photos)
# - data/horizons/ (horizon profile images)
# - data/shademap/ (sun/shadow visualizations)
# - data/google_maps/ (location thumbnails)
```

### 2. Configure API Keys (Optional)

Edit `config.json` to add your API keys:

```json
{
  "google_maps_api_key": "YOUR_KEY_HERE",
  "mapbox_api_key": "YOUR_KEY_HERE"
}
```

**Important:** If you add real API keys, add `config.json` to `.gitignore` to keep them private.

### 3. Commit Generated Files

Ensure all generated data is committed to the repository:

```bash
git add data/eclipse_site_data.csv
git add data/igme_images/
git add data/horizons/
git add data/shademap/
git add data/brochures/
git commit -m "Add generated data for GitHub Pages"
```

### 4. Enable GitHub Pages

1. Go to your repository settings on GitHub
2. Navigate to "Pages" section
3. Under "Source", select the branch (usually `main` or `master`)
4. Select root directory `/` as the source
5. Click "Save"

Your site will be available at: `https://[username].github.io/[repository-name]/`

## How It Works

### Local Development (Python Backend)

```
viewer.html → static/js/main.js → API endpoints (/api/*)
                                 ↓
                          serve_viewer.py (Python server)
                                 ↓
                          Dynamic image proxy, config loading
```

### GitHub Pages (Static)

```
index.html → gh-pages/main.js → Static files (config.json, data/*)
                               ↓
                        Direct file access, no server needed
```

## Key Differences

| Feature | Local (viewer.html) | GitHub Pages (index.html) |
|---------|-------------------|--------------------------|
| Entry Point | `viewer.html` | `index.html` |
| JavaScript | `static/js/main.js` | `gh-pages/main.js` |
| Config Loading | `/api/config` endpoint | `config.json` file |
| Image Loading | `/api/images` proxy | Direct file paths |
| IGME Images | Dynamic proxy | Pre-cached in `data/igme_images/` |
| Documentation | `/api/readme`, `/api/credits` | `readme.html`, `credits.html` |

## Limitations on GitHub Pages

1. **No Dynamic Image Proxy** - IGME images must be pre-downloaded and cached
2. **No Server-Side Processing** - All data must be pre-generated
3. **API Keys in Config** - Must be in static file (use environment-specific configs)
4. **CORS Restrictions** - Some external resources may not load

## Testing Locally

You can test the GitHub Pages version locally:

```bash
# Using Python's built-in server
python -m http.server 8080

# Or using Node.js http-server
npx http-server -p 8080

# Then open: http://localhost:8080/
```

## Updating Data

To update the site with new data:

1. Run data generation scripts locally
2. Commit updated files in `data/` directory
3. Push to GitHub
4. GitHub Pages will automatically rebuild

## Troubleshooting

### Images Not Loading

- Ensure all images are committed to the repository
- Check browser console for 404 errors
- Verify image paths in `data/` directory

### API Keys Not Working

- Check `config.json` format
- Ensure file is accessible (not in `.gitignore` if needed publicly)
- Verify keys are valid

### Site Not Updating

- Check GitHub Actions tab for build status
- Clear browser cache
- Wait a few minutes for GitHub Pages to rebuild

## Security Notes

- **Never commit real API keys** to public repositories
- Use environment-specific config files
- Consider using GitHub Secrets for sensitive data
- The example `config.json` has empty strings for keys

## Maintenance

The GitHub Pages version requires:
- Regular data updates (run pipeline locally)
- Committing generated files
- Keeping dependencies (Leaflet, Mapbox) up to date

For development with live data updates, use the local Python version (`viewer.html` + `serve_viewer.py`).