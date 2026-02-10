# Frontend JavaScript Modules

This directory contains the modularized ES6 JavaScript code for the Spain Eclipse Sites Viewer.

## Module Structure

### Core Modules

- **`config.js`** - Application configuration and constants
  - Hotel coordinates, API endpoints, map settings
  - Loads Google Maps API key from server
  - Eclipse and cloud coverage thresholds

- **`state.js`** - Application state management
  - Centralized state container with reactive updates
  - Manages sites data, current site, selections, UI state
  - Provides subscriber pattern for state changes

- **`utils.js`** - Utility functions
  - Coordinate conversion (decimal to DMS)
  - CSV parsing helpers
  - Cloud coverage and eclipse info formatters

- **`data-loader.js`** - Data loading and processing
  - CSV file loading and parsing
  - Site filtering and sorting logic
  - Data transformation utilities

- **`site-display.js`** - Site list rendering
  - Sidebar site list display
  - Filter and search functionality
  - Site counter updates

- **`main.js`** - Application initialization
  - Coordinates all modules
  - Sets up event listeners
  - Handles application lifecycle

## Migration Status

### ✅ Completed (Phase 1)
- Configuration management
- State management pattern
- Data loading and parsing
- Site list display and filtering
- Basic site details view

### 🚧 To Be Implemented (Phase 2)
- **`site-details.js`** - Full site details rendering
  - Tabs (Details, Map, Images)
  - Eclipse profile diagrams
  - Cloud coverage display
  - External links

- **`map-handler.js`** - Map and routing functionality
  - Leaflet map initialization
  - Single-site and multi-site routing
  - Route export (Google Maps, KML)
  - Turn-by-turn directions

- **`modal-handler.js`** - Modal dialogs
  - Image carousel
  - Resources panel
  - About panel
  - Help panel

- **`image-loader.js`** - Image handling
  - IGME image scraping
  - Image proxy for CORS
  - Lazy loading
  - Caching

## Usage

The modules use ES6 import/export syntax and are loaded as a module in `viewer.html`:

```html
<script type="module" src="static/js/main.js"></script>
```

All modules are automatically loaded through the dependency chain starting from `main.js`.

## Development Notes

### Adding New Modules

1. Create new `.js` file in `static/js/`
2. Use ES6 export syntax for public functions/classes
3. Import dependencies at the top of the file
4. Import and use in `main.js` or other modules

Example:
```javascript
// new-module.js
import { appState } from './state.js';
import { CONFIG } from './config.js';

export function myFunction() {
    // Implementation
}
```

### State Management

Use the `appState` singleton for shared state:

```javascript
import { appState } from './state.js';

// Get data
const sites = appState.sitesData;
const currentSite = appState.currentSite;

// Update state
appState.setCurrentSite(site);
appState.toggleSiteSelection(code);

// Subscribe to changes
appState.subscribe((property, value) => {
    console.log(`${property} changed to:`, value);
});
```

### Configuration

Access configuration through the `CONFIG` object:

```javascript
import { CONFIG } from './config.js';

const hotelCoords = CONFIG.HOTEL_COORDS;
const apiEndpoint = CONFIG.API.CONFIG;
```

## Browser Compatibility

Requires modern browser with ES6 module support:
- Chrome 61+
- Firefox 60+
- Safari 11+
- Edge 16+

## Original Code

The original monolithic `app.js` (1505 lines) has been backed up as `static/app.js.backup` for reference during the migration.

## Testing

To test the modular version:

1. Start the server: `python3 serve_viewer.py`
2. Open browser to `http://localhost:8000/viewer.html`
3. Check browser console for any module loading errors
4. Test site list, filtering, and basic site selection

## Future Improvements

- Add unit tests for each module
- Implement lazy loading for heavy modules
- Add TypeScript definitions
- Bundle and minify for production
- Add service worker for offline support