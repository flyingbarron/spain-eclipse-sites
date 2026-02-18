# Spain Eclipse Sites Viewer - Standalone Version

This is a standalone version of the Eclipse Sites Viewer that works without a server.

## Features

- ✅ Works offline (after initial load)
- ✅ All site data embedded
- ✅ All cached images included
- ✅ No server required
- ✅ Can be hosted on any static file server

## Usage

### Option 1: Open Directly in Browser

Simply open `index.html` in your web browser. Most modern browsers support this.

**Note:** Some browsers (like Chrome) may have restrictions on loading local files. If you encounter issues, use Option 2.

### Option 2: Use a Local Web Server

```bash
# Python 3
python -m http.server 8080

# Python 2
python -m SimpleHTTPServer 8080

# Node.js (if you have http-server installed)
npx http-server -p 8080
```

Then open http://localhost:8080 in your browser.

### Option 3: Deploy to Static Hosting

You can deploy this entire directory to any static hosting service:
- GitHub Pages
- Netlify
- Vercel
- AWS S3
- Any web server

## Directory Structure

```
standalone_viewer/
├── index.html              # Main HTML file
├── data.js                 # Embedded site data
├── static/                 # CSS and JavaScript
│   ├── styles.css
│   └── js/
│       ├── config.js       # Configuration (standalone version)
│       ├── data-loader.js  # Data loading (standalone version)
│       ├── image-loader.js # Image loading (standalone version)
│       └── ...             # Other modules
└── images/                 # All cached images
    ├── igme/              # IGME site photos
    ├── eclipsefan_horizons/  # Horizon views
    ├── ign_profiles/      # Eclipse profiles
    └── shademap_snapshots/   # Shademap visualizations
```

## API Keys (Optional)

If you want to use Google Maps or Mapbox features, you can add your API keys by editing `static/js/config.js`:

```javascript
export let googleMapsApiKey = 'YOUR_GOOGLE_MAPS_KEY';
export let mapboxApiKey = 'YOUR_MAPBOX_KEY';
```

## Limitations

Compared to the server version:
- Cannot dynamically scrape new images from IGME
- Uses pre-cached images only
- No server-side image proxy

## Building

This standalone version was built using:
```bash
python build_standalone_viewer.py
```

## Credits

Created by Robert Barron • Made with Bob 🤖

See the main repository for full credits and data sources.
