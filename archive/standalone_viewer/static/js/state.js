/**
 * Application State Management Module
 * Manages global application state and provides reactive updates
 */

export class AppState {
    constructor() {
        // Site data
        this.sitesData = [];
        this.currentSite = null;
        
        // Image carousel state
        this.currentImages = [];
        this.currentImageIndex = 0;
        
        // UI state
        this.activeTab = 'details';
        this.selectedSites = []; // Array to maintain order for multi-select
        this.returnToHotel = false;
        
        // Map state
        this.currentRouteControl = null;
        this.routeSegments = [];
        
        // Subscribers for state changes
        this.subscribers = [];
    }
    
    /**
     * Subscribe to state changes
     * @param {Function} callback - Function to call when state changes
     */
    subscribe(callback) {
        this.subscribers.push(callback);
    }
    
    /**
     * Notify all subscribers of state change
     * @param {string} property - Property that changed
     * @param {*} value - New value
     */
    notify(property, value) {
        this.subscribers.forEach(callback => callback(property, value));
    }
    
    /**
     * Set sites data
     * @param {Array} sites - Array of site objects
     */
    setSitesData(sites) {
        this.sitesData = sites;
        this.notify('sitesData', sites);
    }
    
    /**
     * Set current site
     * @param {Object} site - Site object
     */
    setCurrentSite(site) {
        this.currentSite = site;
        this.notify('currentSite', site);
    }
    
    /**
     * Set current images
     * @param {Array} images - Array of image objects
     */
    setCurrentImages(images) {
        this.currentImages = images;
        this.currentImageIndex = 0;
        this.notify('currentImages', images);
    }
    
    /**
     * Set current image index
     * @param {number} index - Image index
     */
    setCurrentImageIndex(index) {
        this.currentImageIndex = index;
        this.notify('currentImageIndex', index);
    }
    
    /**
     * Set active tab
     * @param {string} tab - Tab name ('details', 'map', 'images')
     */
    setActiveTab(tab) {
        this.activeTab = tab;
        this.notify('activeTab', tab);
    }
    
    /**
     * Toggle site selection for multi-select
     * @param {string} siteCode - Site code to toggle
     */
    toggleSiteSelection(siteCode) {
        const index = this.selectedSites.indexOf(siteCode);
        if (index > -1) {
            this.selectedSites.splice(index, 1);
        } else {
            this.selectedSites.push(siteCode);
        }
        this.notify('selectedSites', this.selectedSites);
    }
    
    /**
     * Clear all selected sites
     */
    clearSelectedSites() {
        this.selectedSites = [];
        this.notify('selectedSites', this.selectedSites);
    }
    
    /**
     * Set return to hotel flag
     * @param {boolean} value - Whether to return to hotel
     */
    setReturnToHotel(value) {
        this.returnToHotel = value;
        this.notify('returnToHotel', value);
    }
    
    /**
     * Set current route control
     * @param {Object} control - Leaflet routing control
     */
    setCurrentRouteControl(control) {
        this.currentRouteControl = control;
        this.notify('currentRouteControl', control);
    }
    
    /**
     * Set route segments
     * @param {Array} segments - Array of route segment data
     */
    setRouteSegments(segments) {
        this.routeSegments = segments;
        this.notify('routeSegments', segments);
    }
    
    /**
     * Get site by code
     * @param {string} code - Site code
     * @returns {Object|null} Site object or null
     */
    getSiteByCode(code) {
        return this.sitesData.find(site => site.code === code) || null;
    }
    
    /**
     * Check if site is selected
     * @param {string} code - Site code
     * @returns {boolean} True if selected
     */
    isSiteSelected(code) {
        return this.selectedSites.includes(code);
    }
}

// Create and export singleton instance
export const appState = new AppState();

// Made with Bob
