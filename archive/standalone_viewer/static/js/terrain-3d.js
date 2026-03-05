/**
 * 3D Terrain Visualization Module
 * Provides Mapbox GL JS 3D terrain visualization for eclipse sites
 */

import { mapboxApiKey } from './config.js';
import { CONFIG } from './config.js';

// Global 3D map instance
let terrain3DMap = null;

/**
 * Initialize 3D terrain map
 * @param {Array} sites - Array of site objects to display
 */
export function initialize3DMap(sites) {
    if (!mapboxApiKey) {
        console.error('Mapbox API key not available');
        const container = document.getElementById('map3DContainer');
        if (container) {
            container.innerHTML = '<div class="loading">Mapbox API key required for 3D terrain view. Please add ECLIPSE_SITES_API_KEYS_MAPBOX to your .env file.</div>';
        }
        return;
    }
    
    // Set Mapbox access token
    mapboxgl.accessToken = mapboxApiKey;
    
    // Calculate center point
    const allCoords = [CONFIG.HOTEL_COORDS, ...sites.map(s => [parseFloat(s.latitude), parseFloat(s.longitude)])];
    const centerLat = allCoords.reduce((sum, coord) => sum + coord[0], 0) / allCoords.length;
    const centerLon = allCoords.reduce((sum, coord) => sum + coord[1], 0) / allCoords.length;
    
    // Remove existing map
    if (terrain3DMap) {
        terrain3DMap.remove();
        terrain3DMap = null;
    }
    
    // Create 3D map
    terrain3DMap = new mapboxgl.Map({
        container: 'map3DContainer',
        style: 'mapbox://styles/mapbox/satellite-streets-v12',
        center: [centerLon, centerLat],
        zoom: 10,
        pitch: 60,
        bearing: 0,
        antialias: true
    });
    
    terrain3DMap.on('load', () => {
        // Add 3D terrain
        terrain3DMap.addSource('mapbox-dem', {
            'type': 'raster-dem',
            'url': 'mapbox://mapbox.mapbox-terrain-dem-v1',
            'tileSize': 512,
            'maxzoom': 14
        });
        
        terrain3DMap.setTerrain({ 'source': 'mapbox-dem', 'exaggeration': 1.5 });
        
        // Add sky layer
        terrain3DMap.addLayer({
            'id': 'sky',
            'type': 'sky',
            'paint': {
                'sky-type': 'atmosphere',
                'sky-atmosphere-sun': [0.0, 90.0],
                'sky-atmosphere-sun-intensity': 15
            }
        });
        
        // Add hotel marker
        const hotelEl = document.createElement('div');
        hotelEl.className = 'marker-3d';
        hotelEl.innerHTML = '🏨';
        hotelEl.style.fontSize = '32px';
        
        new mapboxgl.Marker(hotelEl)
            .setLngLat([CONFIG.HOTEL_COORDS[1], CONFIG.HOTEL_COORDS[0]])
            .setPopup(new mapboxgl.Popup().setHTML(`<b>${CONFIG.HOTEL_NAME}</b><br>Starting point`))
            .addTo(terrain3DMap);
        
        // Add site markers
        sites.forEach((site, index) => {
            const lat = parseFloat(site.latitude);
            const lon = parseFloat(site.longitude);
            
            const siteEl = document.createElement('div');
            siteEl.className = 'marker-3d site-marker-3d';
            siteEl.innerHTML = sites.length > 1 ? (index + 1) : '📍';
            siteEl.style.fontSize = '24px';
            siteEl.style.background = sites.length > 1 ? '#007bff' : 'transparent';
            siteEl.style.color = 'white';
            siteEl.style.borderRadius = '50%';
            siteEl.style.width = '30px';
            siteEl.style.height = '30px';
            siteEl.style.display = 'flex';
            siteEl.style.alignItems = 'center';
            siteEl.style.justifyContent = 'center';
            siteEl.style.fontWeight = 'bold';
            
            new mapboxgl.Marker(siteEl)
                .setLngLat([lon, lat])
                .setPopup(new mapboxgl.Popup().setHTML(`
                    <b>${site.denominacion || site.code}</b><br>
                    ${site.tourist_value ? `Tourist Value: ${site.tourist_value}` : ''}
                `))
                .addTo(terrain3DMap);
        });
        
        // Add navigation controls
        terrain3DMap.addControl(new mapboxgl.NavigationControl());
        terrain3DMap.addControl(new mapboxgl.FullscreenControl());
        
        // Add terrain toggle control
        addTerrainToggle();
    });
}

/**
 * Add terrain exaggeration toggle control
 */
function addTerrainToggle() {
    const toggleContainer = document.createElement('div');
    toggleContainer.className = 'mapboxgl-ctrl mapboxgl-ctrl-group';
    toggleContainer.style.position = 'absolute';
    toggleContainer.style.top = '10px';
    toggleContainer.style.right = '10px';
    
    const toggleButton = document.createElement('button');
    toggleButton.className = 'mapboxgl-ctrl-icon';
    toggleButton.innerHTML = '⛰️';
    toggleButton.title = 'Toggle terrain exaggeration';
    toggleButton.style.fontSize = '20px';
    
    let exaggeration = 1.5;
    toggleButton.onclick = () => {
        exaggeration = exaggeration === 1.5 ? 3.0 : exaggeration === 3.0 ? 0 : 1.5;
        if (exaggeration === 0) {
            terrain3DMap.setTerrain(null);
            toggleButton.style.opacity = '0.5';
        } else {
            terrain3DMap.setTerrain({ 'source': 'mapbox-dem', 'exaggeration': exaggeration });
            toggleButton.style.opacity = '1.0';
        }
    };
    
    toggleContainer.appendChild(toggleButton);
    document.getElementById('map3DContainer').appendChild(toggleContainer);
}

/**
 * Cleanup 3D map
 */
export function cleanup3DMap() {
    if (terrain3DMap) {
        terrain3DMap.remove();
        terrain3DMap = null;
    }
}

// Made with Bob
