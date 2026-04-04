/**
 * Configuration Module - GitHub Pages Version
 * Contains constants and configuration values
 * Loads API keys from static config.json instead of server API
 */

export const CONFIG = {
    // Hotel coordinates (starting point for routes)
    HOTEL_COORDS: [42.2167, -2.2833],
    HOTEL_NAME: 'Hotel Parras Arnedillo',
    
    // Data file path
    CSV_PATH: 'data/eclipse_site_data.csv',
    
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
    },
    
    // Image directories (static paths for GitHub Pages)
    IMAGES: {
        IGME_CACHE: 'data/igme_images/',
        HORIZONS: 'data/horizons/',
        SHADEMAPS: 'data/shademap/',
        GOOGLE_MAPS: 'data/google_maps/'
    }
};

// API keys (loaded from static config.json)
export let googleMapsApiKey = '';
export let mapboxApiKey = '';

/**
 * Load configuration from static config.json file
 */
export async function loadConfig() {
    try {
        const response = await fetch('config.json');
        const config = await response.json();
        googleMapsApiKey = config.google_maps_api_key || '';
        mapboxApiKey = config.mapbox_api_key || '';
        console.log('Google Maps API key loaded:', googleMapsApiKey ? 'Yes' : 'No');
        console.log('Mapbox API key loaded:', mapboxApiKey ? 'Yes' : 'No');
        return config;
    } catch (error) {
        console.warn('Could not load config.json, using defaults:', error);
        return null;
    }
}

// Made with Bob