# Standalone Eclipse Sites Viewer

This document explains how to build and use the standalone version of the Spain Eclipse Sites Viewer that works without a server.

## Overview

The standalone viewer is a self-contained version that:
- ✅ Works offline (after initial load)
- ✅ Has all site data embedded as JavaScript
- ✅ Includes all cached images locally
- ✅ Requires no server-side processing
- ✅ Can be opened directly in a browser or hosted on any static file server

## Building the Standalone Version

### Prerequisites

- Python 3.x
- All data files cached (run the main application first to cache images)

### Build Command

```bash
python3 build_standalone_viewer.py
```

This will:
1. Copy all static files (CSS, JavaScript)
2. Read the CSV data and convert it to embedded JavaScript
3. Build an image index mapping sites to their cached images
4. Copy all cached IGME images
5. Copy all scraped images (horizons, profiles, shademaps)
6. Create modified JavaScript modules that work without server APIs
7. Generate a standalone HTML file
8. Create a README with usage instructions

### Output

The build process creates a `standalone_viewer/` directory with this structure:

```
standalone_viewer/
├── index.html              # Main HTML file
├── data.js                 # Embedded site data (JSON)
├── README.md               # Usage instructions
├── static/                 # CSS and JavaScript
│   ├── styles.css
│   └── js/
│       ├── config.js       # Modified for standalone
│       ├── data-loader.js  # Modified for standalone
│       ├── image-loader.js # Modified for standalone
│       ├── site-details.js # Modified for standalone
│       └── ...             # Other modules (unchanged)
└── images/                 # All cached images
    ├── igme/              # IGME site photos
    ├── eclipsefan_horizons/  # Horizon views
    ├── ign_profiles/      # Eclipse profiles
    └── shademap_snapshots/   # Shademap visualizations
```

## Using the Standalone Viewer

### Option 1: Open Directly in Browser

Simply open `standalone_viewer/index.html` in your web browser.

**Note:** Some browsers (especially Chrome) have security restrictions on loading local files. If you encounter issues, use Option 2 or 3.

### Option 2: Local Web Server (Recommended)

Using Python:
```bash
cd standalone_viewer
python3 -m http.server 8080
```

Then open http://localhost:8080 in your browser.

Using Node.js:
```bash
cd standalone_viewer
npx http-server -p 8080
```

### Option 3: Deploy to Static Hosting

The standalone viewer can be deployed to any static hosting service:

- **GitHub Pages**: Push to a `gh-pages` branch
- **Netlify**: Drag and drop the `standalone_viewer` folder
- **Vercel**: Deploy with `vercel deploy`
- **AWS S3**: Upload as a static website
- **Any web server**: Copy files to your web root

## Key Differences from Server Version

### What Works the Same

- ✅ All site browsing and filtering
- ✅ Site details and information
- ✅ Map display and navigation
- ✅ Image viewing and galleries
- ✅ Route planning
- ✅ Export to Google Maps and KML
- ✅ All external links (IGME, EclipseFan, etc.)

### What's Different

- ⚠️ Uses pre-cached images only (no dynamic scraping)
- ⚠️ No server-side image proxy (images loaded directly)
- ⚠️ No API configuration endpoint (API keys must be set manually)
- ⚠️ Data is embedded in JavaScript (not loaded from CSV)

### Limitations

1. **No Dynamic Image Scraping**: The viewer only shows images that were cached when the standalone version was built. To update images, rebuild the standalone version.

2. **API Keys**: If you want to use Google Maps or Mapbox features, you need to manually edit `static/js/config.js` and add your API keys:

```javascript
export let googleMapsApiKey = 'YOUR_GOOGLE_MAPS_KEY';
export let mapboxApiKey = 'YOUR_MAPBOX_KEY';
```

3. **Browser Compatibility**: Modern browsers required (ES6 modules support needed).

## Updating the Standalone Version

To update the standalone viewer with new data or images:

1. Run the main application to cache new data:
   ```bash
   python3 serve_viewer.py
   ```

2. Browse sites to cache their images

3. Rebuild the standalone version:
   ```bash
   python3 build_standalone_viewer.py
   ```

## File Size Considerations

The standalone viewer includes all cached images, which can result in a large directory size:

- **IGME images**: ~50-100 MB (varies by number of cached sites)
- **Horizon images**: ~5-10 MB
- **Profile images**: ~3-5 MB
- **Shademap images**: ~10-15 MB
- **Total**: ~70-130 MB

If deploying to a hosting service with size limits, consider:
- Only caching images for sites you need
- Compressing images before building
- Using a CDN for image hosting

## Troubleshooting

### Images Not Loading

**Problem**: Images show as broken or don't load.

**Solutions**:
1. Check browser console for errors
2. Verify images exist in the `images/` directory
3. Check file paths in `site-details.js` (should be `images/...` not `data/scrape/...`)
4. Ensure you're using a web server (not file:// protocol)

### Site Data Not Loading

**Problem**: Site list is empty or shows "Loading..."

**Solutions**:
1. Check browser console for JavaScript errors
2. Verify `data.js` exists and contains `window.EMBEDDED_SITE_DATA`
3. Check that all JavaScript modules are loading correctly
4. Try clearing browser cache

### Map Not Displaying

**Problem**: Map area is blank or shows errors.

**Solutions**:
1. Check internet connection (map tiles require internet)
2. Verify Leaflet CSS and JS are loading from CDN
3. Check browser console for errors
4. Try a different browser

### CORS Errors

**Problem**: Browser shows CORS errors in console.

**Solutions**:
1. Use a local web server instead of opening files directly
2. If using Chrome, try Firefox or Safari
3. Ensure all resources are served from the same origin

## Advanced Customization

### Changing Map Tiles

Edit `static/js/config.js`:

```javascript
MAP: {
    DEFAULT_ZOOM: 10,
    TILE_LAYER: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
    ATTRIBUTION: '&copy; OpenStreetMap contributors'
}
```

### Adding Custom Styles

Edit `static/styles.css` to customize the appearance.

### Modifying Site Data

The site data is embedded in `data.js`. To modify:

1. Edit the source CSV file: `data/eclipse_site_data.csv`
2. Rebuild the standalone version: `python3 build_standalone_viewer.py`

## Performance Tips

1. **Lazy Load Images**: Images are loaded on-demand when viewing site details
2. **Browser Caching**: The browser will cache images after first load
3. **Preload Critical Images**: Consider preloading images for frequently viewed sites
4. **Compress Images**: Use image compression tools before building

## Security Considerations

1. **API Keys**: Don't commit API keys to public repositories
2. **HTTPS**: Use HTTPS when deploying to production
3. **Content Security Policy**: Consider adding CSP headers when hosting
4. **Input Validation**: The viewer doesn't accept user input, minimizing XSS risks

## Support

For issues or questions:
1. Check this documentation
2. Review the main README.md
3. Check browser console for errors
4. Open an issue on GitHub

## Credits

Created by Robert Barron • Made with Bob 🤖

See [CREDITS.md](CREDITS.md) for full attribution and data sources.