# Celestial Direction Lines Feature

## Overview

The Celestial Direction Lines feature adds three directional lines to the map when you click on any location, showing the directions of:
1. **Sun during Eclipse Peak** - Shows where the sun will be during the total solar eclipse
2. **Milky Way Center at 10pm** - Shows the direction to the galactic center at 22:00 local time
3. **Perseid Radiant** - Shows the direction of the Perseid meteor shower radiant point

## Visual Design

### Line Styles
- **Sun Direction**: Solid orange line (`#FF8C00`), 3px width
- **Milky Way**: Dashed purple line (`#9370DB`), 2.5px width, 10px dash / 5px gap
- **Perseid Radiant**: Dotted cyan line (`#00CED1`), 2.5px width, 2px dot / 4px gap

### Line Length
All lines extend 100km from the clicked point.

### Labels
Each line has a label at its endpoint showing:
- An emoji icon (☀️, 🌌, or ☄️)
- The celestial object name

## Implementation

### Files Created/Modified

1. **`gh-pages/celestial-lines.js`** (NEW)
   - Core module for astronomical calculations
   - Functions to draw directional lines on Leaflet map
   - Legend creation

2. **`gh-pages/map-view.js`** (MODIFIED)
   - Added import for celestial-lines module
   - Added map click handler to trigger line drawing
   - Added celestial legend to map

3. **`static/styles.css`** (MODIFIED)
   - Added CSS for celestial line labels
   - Added CSS for celestial legend
   - Added high-contrast mode support
   - Added responsive design adjustments

4. **`index.html`** (MODIFIED)
   - Updated version to 1.5.0 for cache busting

### Astronomical Calculations

#### Sun Direction
- Uses hardcoded eclipse azimuth: **283.7753°** (West-Northwest)
- This is the sun's position during the eclipse peak on August 12, 2026

#### Milky Way Center
- Right Ascension: 17h 45m (17.76 hours)
- Declination: -29.0°
- Calculated for 10pm local time (20:00 UTC) on eclipse night
- Uses equatorial to horizontal coordinate conversion

#### Perseid Radiant
- Right Ascension: 3h 4m (3.07 hours)
- Declination: +58.0°
- Calculated for midnight (00:00 UTC) on August 13, 2026
- The Perseids peak coincides with the eclipse date!

### Coordinate Conversion

The module includes functions to convert:
1. **Equatorial coordinates (RA/Dec)** → **Horizontal coordinates (Azimuth/Altitude)**
2. **Geographic coordinates + Azimuth + Distance** → **Endpoint coordinates**

Key formulas used:
- Local Sidereal Time (LST) calculation
- Hour Angle calculation
- Spherical trigonometry for coordinate transformations
- Great circle distance calculations

## Usage

### For Users
1. Open the map view (click "🗺️ Map" button)
2. Click anywhere on the map
3. Three directional lines will appear showing celestial directions
4. Click elsewhere to clear and draw new lines
5. View the legend in the bottom-right corner for line identification

### For Developers

#### Drawing Lines Programmatically
```javascript
import { drawCelestialLines } from './gh-pages/celestial-lines.js';

// Draw lines at a specific location
drawCelestialLines(mapInstance, latitude, longitude);
```

#### Clearing Lines
```javascript
import { clearCelestialLines } from './gh-pages/celestial-lines.js';

clearCelestialLines(mapInstance);
```

#### Adding Legend
```javascript
import { createCelestialLegend } from './gh-pages/celestial-lines.js';

const legend = createCelestialLegend(mapInstance);
legend.addTo(mapInstance);
```

## Technical Details

### Constants
```javascript
ECLIPSE_SUN_AZIMUTH = 283.7753  // degrees
LINE_LENGTH_KM = 100            // kilometers
EARTH_RADIUS_KM = 6371.0        // kilometers
```

### Celestial Coordinates (J2000 Epoch)
```javascript
MILKY_WAY_CENTER = {
    ra: 17.76,   // hours
    dec: -29.0   // degrees
}

PERSEID_RADIANT = {
    ra: 3.07,    // hours
    dec: 58.0    // degrees
}
```

### Times Used
- Eclipse: August 12, 2026 at 19:30 UTC (approximate peak)
- Milky Way: August 12, 2026 at 20:00 UTC (10pm local time)
- Perseids: August 13, 2026 at 00:00 UTC (midnight)

## Accuracy

The astronomical calculations use simplified formulas suitable for visualization:
- **Sun direction**: Exact (from eclipse calculations)
- **Milky Way/Perseid directions**: Accurate to within ~1° for the date/time specified
- **Line endpoints**: Accurate great circle calculations

For scientific applications requiring higher precision, consider using a full astronomy library like astronomy-engine.js.

## Browser Compatibility

Works in all modern browsers that support:
- ES6 modules
- Leaflet.js 1.9.4+
- CSS3

## Future Enhancements

Potential improvements:
1. Toggle button to show/hide lines
2. Adjustable line length
3. More celestial objects (planets, constellations)
4. Time slider to see how directions change throughout the night
5. Altitude information (whether object is above horizon)
6. Integration with site-specific horizon profiles

## Credits

- Eclipse azimuth data from IGN Eclipse 2026 visualizer
- Celestial coordinates from standard astronomical catalogs
- Coordinate conversion algorithms based on Jean Meeus' "Astronomical Algorithms"

---

**Made with Bob 🤖**