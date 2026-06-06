/**
 * Celestial Lines Module
 * Draws directional lines showing Sun, Milky Way, and Perseid radiant directions
 * on the map when a location is clicked
 */

// Constants for celestial objects
const ECLIPSE_SUN_AZIMUTH = 283.7753; // Degrees, from config
const LINE_LENGTH_KM = 100; // Length of direction lines in kilometers
const EARTH_RADIUS_KM = 6371.0;

// Celestial coordinates (J2000)
const MILKY_WAY_CENTER = {
    ra: 17.76, // Right Ascension in hours (17h 45m)
    dec: -29.0  // Declination in degrees
};

const PERSEID_RADIANT = {
    ra: 3.07,   // Right Ascension in hours (3h 4m)
    dec: 58.0   // Declination in degrees
};

// Eclipse date and time for calculations
const ECLIPSE_DATE = new Date('2026-08-12T19:30:00Z'); // Approximate eclipse time
const MILKY_WAY_TIME = new Date('2026-08-12T20:00:00Z'); // 10pm local time (approx 8pm UTC)
const PERSEID_TIME = new Date('2026-08-13T00:00:00Z'); // Midnight

// Line styles
const LINE_STYLES = {
    sun: {
        color: '#FF8C00',
        weight: 3,
        opacity: 0.7,
        dashArray: null,
        label: '☀️ Sun (Eclipse Peak)',
        icon: '☀️'
    },
    milkyWay: {
        color: '#9370DB',
        weight: 2.5,
        opacity: 0.7,
        dashArray: '10, 5',
        label: '🌌 Milky Way Center (10pm)',
        icon: '🌌'
    },
    perseid: {
        color: '#00CED1',
        weight: 2.5,
        opacity: 0.7,
        dashArray: '2, 4',
        label: '☄️ Perseid Radiant',
        icon: '☄️'
    }
};

// Store current lines for cleanup
let currentLines = [];
let currentMarkers = [];

/**
 * Calculate endpoint coordinates given start point, azimuth, and distance
 * @param {number} lat - Starting latitude in decimal degrees
 * @param {number} lon - Starting longitude in decimal degrees
 * @param {number} azimuth - Bearing in degrees (0=North, 90=East, 180=South, 270=West)
 * @param {number} distanceKm - Distance in kilometers
 * @returns {Array} [endLat, endLon]
 */
function calculateEndpoint(lat, lon, azimuth, distanceKm) {
    const latRad = lat * Math.PI / 180;
    const lonRad = lon * Math.PI / 180;
    const azimuthRad = azimuth * Math.PI / 180;
    
    const angularDistance = distanceKm / EARTH_RADIUS_KM;
    
    const endLatRad = Math.asin(
        Math.sin(latRad) * Math.cos(angularDistance) +
        Math.cos(latRad) * Math.sin(angularDistance) * Math.cos(azimuthRad)
    );
    
    const endLonRad = lonRad + Math.atan2(
        Math.sin(azimuthRad) * Math.sin(angularDistance) * Math.cos(latRad),
        Math.cos(angularDistance) - Math.sin(latRad) * Math.sin(endLatRad)
    );
    
    return [
        endLatRad * 180 / Math.PI,
        endLonRad * 180 / Math.PI
    ];
}

/**
 * Calculate Local Sidereal Time
 * @param {Date} date - Date and time
 * @param {number} longitude - Observer's longitude in degrees
 * @returns {number} LST in hours
 */
function calculateLST(date, longitude) {
    // Julian Date
    const jd = date.getTime() / 86400000 + 2440587.5;
    
    // Days since J2000.0
    const d = jd - 2451545.0;
    
    // Greenwich Mean Sidereal Time (GMST) in hours
    const gmst = (18.697374558 + 24.06570982441908 * d) % 24;
    
    // Local Sidereal Time
    const lst = (gmst + longitude / 15) % 24;
    
    return lst < 0 ? lst + 24 : lst;
}

/**
 * Convert equatorial coordinates (RA/Dec) to horizontal coordinates (Az/Alt)
 * @param {number} ra - Right Ascension in hours
 * @param {number} dec - Declination in degrees
 * @param {number} lat - Observer's latitude in degrees
 * @param {number} lon - Observer's longitude in degrees
 * @param {Date} date - Date and time of observation
 * @returns {Object} {azimuth, altitude} in degrees
 */
function equatorialToHorizontal(ra, dec, lat, lon, date) {
    const lst = calculateLST(date, lon);
    
    // Hour Angle in hours
    const ha = lst - ra;
    
    // Convert to radians
    const haRad = ha * 15 * Math.PI / 180; // 15 degrees per hour
    const decRad = dec * Math.PI / 180;
    const latRad = lat * Math.PI / 180;
    
    // Calculate altitude
    const sinAlt = Math.sin(decRad) * Math.sin(latRad) +
                   Math.cos(decRad) * Math.cos(latRad) * Math.cos(haRad);
    const altitude = Math.asin(sinAlt) * 180 / Math.PI;
    
    // Calculate azimuth
    const cosAz = (Math.sin(decRad) - Math.sin(latRad) * sinAlt) /
                  (Math.cos(latRad) * Math.cos(Math.asin(sinAlt)));
    let azimuth = Math.acos(Math.max(-1, Math.min(1, cosAz))) * 180 / Math.PI;
    
    // Adjust azimuth based on hour angle
    if (Math.sin(haRad) > 0) {
        azimuth = 360 - azimuth;
    }
    
    return { azimuth, altitude };
}

/**
 * Draw a directional line on the map
 * @param {L.Map} map - Leaflet map instance
 * @param {number} lat - Starting latitude
 * @param {number} lon - Starting longitude
 * @param {number} azimuth - Direction in degrees
 * @param {Object} style - Line style configuration
 * @returns {L.Polyline} The created line
 */
function drawDirectionLine(map, lat, lon, azimuth, style) {
    const [endLat, endLon] = calculateEndpoint(lat, lon, azimuth, LINE_LENGTH_KM);
    
    const line = L.polyline(
        [[lat, lon], [endLat, endLon]],
        {
            color: style.color,
            weight: style.weight,
            opacity: style.opacity,
            dashArray: style.dashArray
        }
    ).addTo(map);
    
    // Add label at the end of the line
    const labelIcon = L.divIcon({
        html: `<div style="
            background: white;
            padding: 4px 8px;
            border-radius: 4px;
            border: 2px solid ${style.color};
            font-size: 11px;
            font-weight: bold;
            white-space: nowrap;
            box-shadow: 0 2px 4px rgba(0,0,0,0.3);
        ">${style.icon} ${style.label.split('(')[0].trim()}</div>`,
        className: 'celestial-label',
        iconSize: null,
        iconAnchor: [0, 0]
    });
    
    const marker = L.marker([endLat, endLon], { icon: labelIcon }).addTo(map);
    
    return { line, marker };
}

/**
 * Clear all celestial lines from the map
 * @param {L.Map} map - Leaflet map instance
 */
export function clearCelestialLines(map) {
    currentLines.forEach(({ line, marker }) => {
        map.removeLayer(line);
        map.removeLayer(marker);
    });
    currentLines = [];
    currentMarkers = [];
}

/**
 * Draw all three celestial direction lines on the map
 * @param {L.Map} map - Leaflet map instance
 * @param {number} lat - Click location latitude
 * @param {number} lon - Click location longitude
 */
export function drawCelestialLines(map, lat, lon) {
    // Clear any existing lines
    clearCelestialLines(map);
    
    // 1. Sun direction (eclipse azimuth)
    const sunLine = drawDirectionLine(map, lat, lon, ECLIPSE_SUN_AZIMUTH, LINE_STYLES.sun);
    currentLines.push(sunLine);
    
    // 2. Milky Way center direction at 10pm
    const milkyWayCoords = equatorialToHorizontal(
        MILKY_WAY_CENTER.ra,
        MILKY_WAY_CENTER.dec,
        lat,
        lon,
        MILKY_WAY_TIME
    );
    
    if (milkyWayCoords.altitude > 0) {
        const milkyWayLine = drawDirectionLine(
            map, lat, lon, milkyWayCoords.azimuth, LINE_STYLES.milkyWay
        );
        currentLines.push(milkyWayLine);
    }
    
    // 3. Perseid radiant direction at midnight
    const perseidCoords = equatorialToHorizontal(
        PERSEID_RADIANT.ra,
        PERSEID_RADIANT.dec,
        lat,
        lon,
        PERSEID_TIME
    );
    
    if (perseidCoords.altitude > 0) {
        const perseidLine = drawDirectionLine(
            map, lat, lon, perseidCoords.azimuth, LINE_STYLES.perseid
        );
        currentLines.push(perseidLine);
    }
    
    console.log(`Celestial lines drawn at ${lat.toFixed(4)}, ${lon.toFixed(4)}`);
    console.log(`  Sun: ${ECLIPSE_SUN_AZIMUTH.toFixed(1)}°`);
    console.log(`  Milky Way: ${milkyWayCoords.azimuth.toFixed(1)}° (alt: ${milkyWayCoords.altitude.toFixed(1)}°)`);
    console.log(`  Perseid: ${perseidCoords.azimuth.toFixed(1)}° (alt: ${perseidCoords.altitude.toFixed(1)}°)`);
}

/**
 * Create a legend control for the celestial lines
 * @param {L.Map} map - Leaflet map instance
 * @returns {L.Control} The legend control
 */
export function createCelestialLegend(map) {
    const legend = L.control({ position: 'bottomright' });
    
    legend.onAdd = function() {
        const div = L.DomUtil.create('div', 'celestial-legend');
        div.style.cssText = `
            background: white;
            padding: 10px;
            border-radius: 5px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.3);
            font-size: 12px;
            line-height: 1.6;
        `;
        
        div.innerHTML = `
            <div style="font-weight: bold; margin-bottom: 5px;">Celestial Directions</div>
            <div style="display: flex; align-items: center; margin-bottom: 3px;">
                <div style="width: 30px; height: 3px; background: ${LINE_STYLES.sun.color}; margin-right: 8px;"></div>
                <span>${LINE_STYLES.sun.label}</span>
            </div>
            <div style="display: flex; align-items: center; margin-bottom: 3px;">
                <div style="width: 30px; height: 2.5px; background: ${LINE_STYLES.milkyWay.color}; margin-right: 8px; background-image: repeating-linear-gradient(to right, ${LINE_STYLES.milkyWay.color} 0, ${LINE_STYLES.milkyWay.color} 10px, transparent 10px, transparent 15px);"></div>
                <span>${LINE_STYLES.milkyWay.label}</span>
            </div>
            <div style="display: flex; align-items: center;">
                <div style="width: 30px; height: 2.5px; background: ${LINE_STYLES.perseid.color}; margin-right: 8px; background-image: repeating-linear-gradient(to right, ${LINE_STYLES.perseid.color} 0, ${LINE_STYLES.perseid.color} 2px, transparent 2px, transparent 6px);"></div>
                <span>${LINE_STYLES.perseid.label}</span>
            </div>
            <div style="margin-top: 8px; font-size: 10px; color: #666;">
                Click any location on the map to show directions
            </div>
        `;
        
        return div;
    };
    
    return legend;
}

// Made with Bob