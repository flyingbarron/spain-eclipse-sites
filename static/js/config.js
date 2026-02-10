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

// Google Maps API key (loaded from server)
export let googleMapsApiKey = '';

/**
 * Load configuration from server
 */
export async function loadConfig() {
    try {
        const response = await fetch(CONFIG.API.CONFIG);
        const config = await response.json();
        googleMapsApiKey = config.google_maps_api_key || '';
        console.log('Google Maps API key loaded:', googleMapsApiKey ? 'Yes' : 'No');
        return config;
    } catch (error) {
        console.error('Error loading config:', error);
        return null;
    }
}

// Made with Bob
