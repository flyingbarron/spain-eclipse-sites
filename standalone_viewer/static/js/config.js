/**
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
