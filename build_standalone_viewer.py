#!/usr/bin/env python3
"""
Build a standalone version of the Eclipse Sites Viewer that doesn't require a server.
All data is embedded or bundled into a single directory that can be opened directly in a browser.
"""

import os
import json
import csv
import shutil
import base64
from pathlib import Path

def read_csv_as_json(csv_path):
    """Read CSV file and convert to JSON"""
    sites = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            sites.append(row)
    return sites

def read_cached_images_metadata():
    """Read cached image metadata from JSON files"""
    cache_dir = Path('data/cache/igme_html')
    image_metadata = {}
    
    for json_file in cache_dir.glob('*.json'):
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Extract site code from the cached data if possible
            # Store by hash for now
            hash_key = json_file.stem
            image_metadata[hash_key] = data
    
    return image_metadata

def copy_cached_images(output_dir):
    """Copy cached IGME images to standalone directory"""
    source_dir = Path('data/cache/igme_images')
    dest_dir = Path(output_dir) / 'images' / 'igme'
    dest_dir.mkdir(parents=True, exist_ok=True)
    
    if source_dir.exists():
        for img_file in source_dir.glob('*'):
            shutil.copy2(img_file, dest_dir / img_file.name)
        print(f"Copied {len(list(source_dir.glob('*')))} cached IGME images")
    
    # Also copy the other image cache directory
    source_dir2 = Path('data/igme_image_cache')
    if source_dir2.exists():
        for img_file in source_dir2.glob('*'):
            dest_file = dest_dir / img_file.name
            if not dest_file.exists():  # Don't overwrite
                shutil.copy2(img_file, dest_file)
        print(f"Copied additional images from igme_image_cache")

def copy_scraped_images(output_dir):
    """Copy scraped horizon, profile, and shademap images"""
    scrape_dir = Path('data/scrape')
    
    # Copy eclipsefan horizons
    if (scrape_dir / 'eclipsefan_horizons').exists():
        dest_dir = Path(output_dir) / 'images' / 'eclipsefan_horizons'
        dest_dir.mkdir(parents=True, exist_ok=True)
        for img in (scrape_dir / 'eclipsefan_horizons').glob('*'):
            shutil.copy2(img, dest_dir / img.name)
        print(f"Copied {len(list((scrape_dir / 'eclipsefan_horizons').glob('*')))} horizon images")
    
    # Copy IGN profiles
    if (scrape_dir / 'ign_profiles').exists():
        dest_dir = Path(output_dir) / 'images' / 'ign_profiles'
        dest_dir.mkdir(parents=True, exist_ok=True)
        for img in (scrape_dir / 'ign_profiles').glob('*'):
            shutil.copy2(img, dest_dir / img.name)
        print(f"Copied {len(list((scrape_dir / 'ign_profiles').glob('*')))} profile images")
    
    # Copy shademap snapshots
    if (scrape_dir / 'shademap_snapshots').exists():
        dest_dir = Path(output_dir) / 'images' / 'shademap_snapshots'
        dest_dir.mkdir(parents=True, exist_ok=True)
        for img in (scrape_dir / 'shademap_snapshots').glob('*'):
            shutil.copy2(img, dest_dir / img.name)
        print(f"Copied {len(list((scrape_dir / 'shademap_snapshots').glob('*')))} shademap images")

def build_image_index():
    """Build an index mapping site codes to their cached images"""
    cache_dir = Path('data/cache/igme_html')
    image_index = {}
    
    for json_file in cache_dir.glob('*.json'):
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if 'images' in data:
                hash_key = json_file.stem
                # Map hash to image list
                image_index[hash_key] = [
                    {
                        'src': img['src'],
                        'alt': img.get('alt', 'Site image'),
                        'hash': get_image_hash(img['src'])
                    }
                    for img in data['images']
                ]
    
    return image_index

def get_image_hash(url):
    """Get the hash that would be used for caching this image"""
    import hashlib
    return hashlib.md5(url.encode()).hexdigest()

def build_site_to_hash_mapping(csv_path):
    """Build mapping from site codes to their IGME URL hashes"""
    import hashlib
    site_to_hash = {}
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if 'url' in row and row['url']:
                url_hash = hashlib.md5(row['url'].encode()).hexdigest()
                site_to_hash[row['code']] = url_hash
    
    return site_to_hash

def main():
    print("Building standalone Eclipse Sites Viewer...")
    print("=" * 60)
    
    # Create output directory
    output_dir = Path('standalone_viewer')
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir()
    
    # Copy static files
    print("\nCopying static files...")
    shutil.copytree('static', output_dir / 'static')
    
    # Read and embed CSV data
    print("\nReading site data...")
    sites_data = read_csv_as_json('data/eclipse_site_data.csv')
    print(f"Loaded {len(sites_data)} sites")
    
    # Build image mappings
    print("\nBuilding image index...")
    image_index = build_image_index()
    site_to_hash = build_site_to_hash_mapping('data/eclipse_site_data.csv')
    
    # Create a mapping from site code to images
    site_images = {}
    for site_code, url_hash in site_to_hash.items():
        if url_hash in image_index:
            site_images[site_code] = image_index[url_hash]
    
    print(f"Indexed images for {len(site_images)} sites")
    
    # Copy all images
    print("\nCopying images...")
    copy_cached_images(output_dir)
    copy_scraped_images(output_dir)
    
    # Create embedded data file
    print("\nCreating embedded data file...")
    embedded_data = {
        'sites': sites_data,
        'siteImages': site_images
    }
    
    with open(output_dir / 'data.js', 'w', encoding='utf-8') as f:
        f.write('// Embedded site data - generated by build_standalone_viewer.py\n')
        f.write('window.EMBEDDED_SITE_DATA = ')
        json.dump(embedded_data, f, indent=2)
        f.write(';\n')
    
    # Copy and modify HTML file
    print("\nCreating standalone HTML...")
    with open('viewer.html', 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Modify HTML to load embedded data
    html_content = html_content.replace(
        '<!-- Modular ES6 JavaScript -->',
        '<!-- Embedded Data -->\n    <script src="data.js"></script>\n    <!-- Modular ES6 JavaScript -->'
    )
    
    with open(output_dir / 'index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    # Create standalone versions of JS modules
    print("\nCreating standalone JavaScript modules...")
    create_standalone_js_modules(output_dir)
    
    # Create README
    print("\nCreating README...")
    create_readme(output_dir)
    
    print("\n" + "=" * 60)
    print("✅ Standalone viewer built successfully!")
    print(f"📁 Output directory: {output_dir.absolute()}")
    print("\nTo use:")
    print(f"  1. Open {output_dir.absolute()}/index.html in your browser")
    print("  2. Or serve with: python -m http.server 8080 -d {output_dir}")
    print("=" * 60)

def create_standalone_js_modules(output_dir):
    """Create modified JS modules that work without a server"""
    
    # Create standalone config.js
    config_content = '''/**
 * Configuration Module - Standalone Version
 * Contains constants and configuration values
 */

export const CONFIG = {
    // Hotel coordinates (starting point for routes)
    HOTEL_COORDS: [42.2167, -2.2833],
    HOTEL_NAME: 'Hotel Parras Arnedillo',
    
    // Data is embedded in window.EMBEDDED_SITE_DATA
    CSV_PATH: null,
    
    // API endpoints - not used in standalone version
    API: {
        CONFIG: null,
        IMAGES: null,
        PROXY_IMAGE: null,
        SHUTDOWN: null
    },
    
    // Map configuration
    MAP: {
        DEFAULT_ZOOM: 10,
        TILE_LAYER: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
        ATTRIBUTION: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    },
    
    // Eclipse visibility values
    ECLIPSE: {
        VISIBLE: 'visible',
        NOT_VISIBLE: 'not_visible',
        UNKNOWN: 'unknown'
    },
    
    // Cloud coverage thresholds
    CLOUD: {
        LOW_THRESHOLD: 30,
        HIGH_THRESHOLD: 60
    }
};

// API keys - can be set manually if needed
export let googleMapsApiKey = '';
export let mapboxApiKey = '';

/**
 * Load configuration - standalone version (no-op)
 */
export async function loadConfig() {
    console.log('Standalone mode: No server configuration needed');
    return { google_maps_api_key: '', mapbox_api_key: '' };
}

// Made with Bob
'''
    
    with open(output_dir / 'static' / 'js' / 'config.js', 'w', encoding='utf-8') as f:
        f.write(config_content)
    
    # Create standalone data-loader.js
    data_loader_content = '''/**
 * Data Loader Module - Standalone Version
 * Loads data from embedded window.EMBEDDED_SITE_DATA
 */

import { parseCSVLine } from './utils.js';
import { appState } from './state.js';

/**
 * Load embedded site data
 * @returns {Promise<Array>} Array of site objects
 */
export async function loadCSV() {
    try {
        if (!window.EMBEDDED_SITE_DATA || !window.EMBEDDED_SITE_DATA.sites) {
            throw new Error('Embedded site data not found');
        }
        
        const sites = window.EMBEDDED_SITE_DATA.sites;
        appState.setSitesData(sites);
        
        console.log(`Loaded ${sites.length} sites from embedded data`);
        return sites;
    } catch (error) {
        console.error('Error loading embedded data:', error);
        throw error;
    }
}

/**
 * Parse CSV text into array of site objects (not used in standalone)
 * @param {string} text - CSV text content
 * @returns {Array} Array of site objects
 */
export function parseCSV(text) {
    const lines = text.trim().split('\\n');
    const headers = parseCSVLine(lines[0]);
    
    const sites = lines.slice(1).map(line => {
        const values = parseCSVLine(line);
        const site = {};
        headers.forEach((header, index) => {
            site[header.trim()] = values[index] ? values[index].trim() : '';
        });
        return site;
    });
    
    return sites;
}

/**
 * Filter and sort sites based on criteria
 * @param {Array} sites - Array of site objects
 * @param {Object} filters - Filter criteria
 * @returns {Array} Filtered and sorted sites
 */
export function filterAndSortSites(sites, filters) {
    const { searchTerm = '', eclipseOnly = false, sortBy = 'code' } = filters;
    
    // Filter
    let filtered = sites.filter(site => {
        const matchesSearch = site.code.toLowerCase().includes(searchTerm.toLowerCase()) ||
            (site.denominacion && site.denominacion.toLowerCase().includes(searchTerm.toLowerCase()));
        
        const matchesEclipse = !eclipseOnly || site.eclipse_visibility === 'visible';
        
        return matchesSearch && matchesEclipse;
    });
    
    // Sort
    filtered.sort((a, b) => {
        if (sortBy === 'name') {
            const nameA = (a.denominacion || a.code).toLowerCase();
            const nameB = (b.denominacion || b.code).toLowerCase();
            return nameA.localeCompare(nameB);
        } else if (sortBy === 'tourist_value') {
            const valueA = parseFloat(a.valor_turistico) || 0;
            const valueB = parseFloat(b.valor_turistico) || 0;
            return valueB - valueA; // Descending order
        } else {
            // Default: sort by code
            return a.code.localeCompare(b.code);
        }
    });
    
    return filtered;
}

// Made with Bob
'''
    
    with open(output_dir / 'static' / 'js' / 'data-loader.js', 'w', encoding='utf-8') as f:
        f.write(data_loader_content)
    
    # Create standalone image-loader.js
    image_loader_content = '''/**
 * Image Loader Module - Standalone Version
 * Loads images from embedded data and local files
 */

import { appState } from './state.js';
import { openImageModal } from './modal-handler.js';

/**
 * Load images for a site from embedded data
 * @param {Object} site - Site object with code
 * @returns {Promise<Array>} Array of image objects
 */
export async function loadSiteImages(site) {
    const container = document.getElementById('imagesContainer');
    
    if (!container) {
        console.warn('Images container not found');
        return [];
    }
    
    // Show loading state
    container.innerHTML = '<div class="loading">Loading images...</div>';
    
    try {
        // Get images from embedded data
        const siteImages = window.EMBEDDED_SITE_DATA?.siteImages?.[site.code] || [];
        
        if (siteImages.length > 0) {
            // Map to local image paths
            const imageUrls = siteImages.map(img => 
                `images/igme/${img.hash}.jpg`
            );
            appState.setCurrentImages(imageUrls);
            
            // Render image grid
            container.innerHTML = siteImages.map((img, index) => `
                <div class="image-card">
                    <img src="images/igme/${img.hash}.jpg"
                         alt="${img.alt || 'Site image'}"
                         data-index="${index}"
                         class="site-image"
                         onerror="this.parentElement.style.display='none'">
                    <div class="image-caption">${img.alt || 'Site image'}</div>
                </div>
            `).join('');
            
            // Add click listeners to images
            container.querySelectorAll('.site-image').forEach(img => {
                img.addEventListener('click', () => {
                    const index = parseInt(img.dataset.index);
                    openImageModal(index);
                });
            });
            
            return siteImages;
        } else {
            container.innerHTML = '<div class="no-images">No images available for this site</div>';
            appState.setCurrentImages([]);
            return [];
        }
    } catch (error) {
        console.error('Error loading images:', error);
        container.innerHTML = '<div class="no-images">Error loading images</div>';
        appState.setCurrentImages([]);
        return [];
    }
}

/**
 * Preload images for better performance
 * @param {Array<string>} imageUrls - Array of image URLs to preload
 */
export function preloadImages(imageUrls) {
    imageUrls.forEach(url => {
        const img = new Image();
        img.src = url;
    });
}

/**
 * Clear images container
 */
export function clearImages() {
    const container = document.getElementById('imagesContainer');
    if (container) {
        container.innerHTML = '';
    }
    appState.setCurrentImages([]);
}

// Made with Bob
'''
    
    with open(output_dir / 'static' / 'js' / 'image-loader.js', 'w', encoding='utf-8') as f:
        f.write(image_loader_content)

def create_readme(output_dir):
    """Create README for standalone viewer"""
    readme_content = '''# Spain Eclipse Sites Viewer - Standalone Version

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
'''
    
    with open(output_dir / 'README.md', 'w', encoding='utf-8') as f:
        f.write(readme_content)

if __name__ == '__main__':
    main()

# Made with Bob