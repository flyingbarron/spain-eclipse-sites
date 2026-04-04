/**
 * Configuration Module
 * Contains constants and configuration values
 */

export const CONFIG = {
    // Hotel coordinates (starting point for routes)
    HOTEL_COORDS: [42.2167, -2.2833],
    HOTEL_NAME: 'Hotel Parras Arnedillo',
    
    // Data file path
    CSV_PATH: 'data/eclipse_site_data.csv',
    
    // API endpoints
    API: {
        CONFIG: '/api/config',
        IMAGES: '/api/images',
        PROXY_IMAGE: '/api/proxy-image',
        README: '/api/readme',
        CREDITS: '/api/credits',
        SHUTDOWN: '/api/shutdown'
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

// API keys (loaded from server)
export let googleMapsApiKey = '';
export let mapboxApiKey = '';

/**
 * Load configuration from server or static file
 * Tries static config.json first (GitHub Pages), then falls back to API endpoint (local dev)
 */
export async function loadConfig() {
    // Try static config.json first (GitHub Pages mode)
    try {
        const response = await fetch('config.json');
        if (response.ok) {
            const config = await response.json();
            googleMapsApiKey = config.google_maps_api_key || '';
            mapboxApiKey = config.mapbox_api_key || '';
            console.log('[Static Config] Google Maps API key loaded:', googleMapsApiKey ? 'Yes' : 'No');
            console.log('[Static Config] Mapbox API key loaded:', mapboxApiKey ? 'Yes' : 'No');
            return config;
        }
    } catch (error) {
        console.log('Static config.json not found, trying API endpoint...');
    }
    
    // Fall back to API endpoint (local development mode)
    try {
        const response = await fetch(CONFIG.API.CONFIG);
        const config = await response.json();
        googleMapsApiKey = config.google_maps_api_key || '';
        mapboxApiKey = config.mapbox_api_key || '';
        console.log('[API Config] Google Maps API key loaded:', googleMapsApiKey ? 'Yes' : 'No');
        console.log('[API Config] Mapbox API key loaded:', mapboxApiKey ? 'Yes' : 'No');
        return config;
    } catch (error) {
        console.warn('Could not load config from API or static file:', error);
        return null;
    }
}

// Made with Bob
