/**
 * Favorites Manager Module
 * Handles user favorites with localStorage persistence
 */

import { appState } from './state.js';

const STORAGE_KEY = 'eclipse_sites_favorites';

export class FavoritesManager {
    constructor() {
        this.favorites = this.loadFavorites();
    }
    
    /**
     * Load favorites from localStorage
     * @returns {Array} Array of favorite site codes
     */
    loadFavorites() {
        try {
            const stored = localStorage.getItem(STORAGE_KEY);
            return stored ? JSON.parse(stored) : [];
        } catch (error) {
            console.error('Error loading favorites:', error);
            return [];
        }
    }
    
    /**
     * Save favorites to localStorage
     */
    saveFavorites() {
        try {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(this.favorites));
        } catch (error) {
            console.error('Error saving favorites:', error);
        }
    }
    
    /**
     * Add site to favorites
     * @param {string} siteCode - Site code to add
     * @returns {boolean} True if added, false if already exists
     */
    addFavorite(siteCode) {
        if (!this.isFavorite(siteCode)) {
            this.favorites.push(siteCode);
            this.saveFavorites();
            appState.notify('favorites', this.favorites);
            return true;
        }
        return false;
    }
    
    /**
     * Remove site from favorites
     * @param {string} siteCode - Site code to remove
     * @returns {boolean} True if removed, false if not found
     */
    removeFavorite(siteCode) {
        const index = this.favorites.indexOf(siteCode);
        if (index > -1) {
            this.favorites.splice(index, 1);
            this.saveFavorites();
            appState.notify('favorites', this.favorites);
            return true;
        }
        return false;
    }
    
    /**
     * Toggle favorite status
     * @param {string} siteCode - Site code to toggle
     * @returns {boolean} True if now favorite, false if removed
     */
    toggleFavorite(siteCode) {
        if (this.isFavorite(siteCode)) {
            this.removeFavorite(siteCode);
            return false;
        } else {
            this.addFavorite(siteCode);
            return true;
        }
    }
    
    /**
     * Check if site is favorite
     * @param {string} siteCode - Site code to check
     * @returns {boolean} True if favorite
     */
    isFavorite(siteCode) {
        return this.favorites.includes(siteCode);
    }
    
    /**
     * Get all favorite sites
     * @returns {Array} Array of site objects
     */
    getFavoriteSites() {
        return this.favorites
            .map(code => appState.getSiteByCode(code))
            .filter(site => site !== null);
    }
    
    /**
     * Clear all favorites
     */
    clearAll() {
        this.favorites = [];
        this.saveFavorites();
        appState.notify('favorites', this.favorites);
    }
    
    /**
     * Export favorites as JSON
     * @returns {string} JSON string of favorites
     */
    exportFavorites() {
        const favoriteSites = this.getFavoriteSites();
        const exportData = {
            version: '1.0',
            exportDate: new Date().toISOString(),
            favorites: favoriteSites.map(site => ({
                code: site.code,
                denominacion: site.denominacion,
                latitude: site.latitude,
                longitude: site.longitude
            }))
        };
        return JSON.stringify(exportData, null, 2);
    }
    
    /**
     * Import favorites from JSON
     * @param {string} jsonString - JSON string to import
     * @returns {Object} Result with success status and message
     */
    importFavorites(jsonString) {
        try {
            const data = JSON.parse(jsonString);
            if (!data.favorites || !Array.isArray(data.favorites)) {
                return { success: false, message: 'Invalid format' };
            }
            
            const imported = [];
            data.favorites.forEach(fav => {
                if (fav.code && !this.isFavorite(fav.code)) {
                    this.favorites.push(fav.code);
                    imported.push(fav.code);
                }
            });
            
            this.saveFavorites();
            appState.notify('favorites', this.favorites);
            
            return {
                success: true,
                message: `Imported ${imported.length} favorites`,
                imported: imported
            };
        } catch (error) {
            return { success: false, message: 'Error parsing JSON: ' + error.message };
        }
    }
    
    /**
     * Get favorites count
     * @returns {number} Number of favorites
     */
    getCount() {
        return this.favorites.length;
    }
}

// Create and export singleton instance
export const favoritesManager = new FavoritesManager();

// Made with Bob