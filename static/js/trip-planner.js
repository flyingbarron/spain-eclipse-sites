/**
 * Trip Planner Module
 * Manages trip itineraries with localStorage persistence
 */

import { appState } from './state.js';
import { favoritesManager } from './favorites-manager.js';

const STORAGE_KEY = 'eclipse_sites_trips';

export class TripPlanner {
    constructor() {
        this.trips = this.loadTrips();
        this.currentTrip = null;
    }
    
    /**
     * Load trips from localStorage
     * @returns {Array} Array of trip objects
     */
    loadTrips() {
        try {
            const stored = localStorage.getItem(STORAGE_KEY);
            return stored ? JSON.parse(stored) : [];
        } catch (error) {
            console.error('Error loading trips:', error);
            return [];
        }
    }
    
    /**
     * Save trips to localStorage
     */
    saveTrips() {
        try {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(this.trips));
        } catch (error) {
            console.error('Error saving trips:', error);
        }
    }
    
    /**
     * Create a new trip
     * @param {string} name - Trip name
     * @param {string} description - Trip description
     * @returns {Object} Created trip object
     */
    createTrip(name, description = '') {
        const trip = {
            id: Date.now().toString(),
            name: name,
            description: description,
            created: new Date().toISOString(),
            modified: new Date().toISOString(),
            days: []
        };
        
        this.trips.push(trip);
        this.saveTrips();
        appState.notify('trips', this.trips);
        return trip;
    }
    
    /**
     * Update trip details
     * @param {string} tripId - Trip ID
     * @param {Object} updates - Object with name and/or description
     * @returns {boolean} True if updated
     */
    updateTrip(tripId, updates) {
        const trip = this.getTripById(tripId);
        if (!trip) return false;
        
        if (updates.name) trip.name = updates.name;
        if (updates.description !== undefined) trip.description = updates.description;
        trip.modified = new Date().toISOString();
        
        this.saveTrips();
        appState.notify('trips', this.trips);
        return true;
    }
    
    /**
     * Delete a trip
     * @param {string} tripId - Trip ID
     * @returns {boolean} True if deleted
     */
    deleteTrip(tripId) {
        const index = this.trips.findIndex(t => t.id === tripId);
        if (index > -1) {
            this.trips.splice(index, 1);
            this.saveTrips();
            appState.notify('trips', this.trips);
            return true;
        }
        return false;
    }
    
    /**
     * Get trip by ID
     * @param {string} tripId - Trip ID
     * @returns {Object|null} Trip object or null
     */
    getTripById(tripId) {
        return this.trips.find(t => t.id === tripId) || null;
    }
    
    /**
     * Add a day to trip
     * @param {string} tripId - Trip ID
     * @param {string} dayName - Day name (e.g., "Day 1", "August 12")
     * @returns {Object|null} Created day object or null
     */
    addDay(tripId, dayName) {
        const trip = this.getTripById(tripId);
        if (!trip) return null;
        
        const day = {
            id: Date.now().toString(),
            name: dayName,
            sites: [],
            notes: ''
        };
        
        trip.days.push(day);
        trip.modified = new Date().toISOString();
        this.saveTrips();
        appState.notify('trips', this.trips);
        return day;
    }
    
    /**
     * Remove a day from trip
     * @param {string} tripId - Trip ID
     * @param {string} dayId - Day ID
     * @returns {boolean} True if removed
     */
    removeDay(tripId, dayId) {
        const trip = this.getTripById(tripId);
        if (!trip) return false;
        
        const index = trip.days.findIndex(d => d.id === dayId);
        if (index > -1) {
            trip.days.splice(index, 1);
            trip.modified = new Date().toISOString();
            this.saveTrips();
            appState.notify('trips', this.trips);
            return true;
        }
        return false;
    }
    
    /**
     * Add site to a day
     * @param {string} tripId - Trip ID
     * @param {string} dayId - Day ID
     * @param {string} siteCode - Site code to add
     * @returns {boolean} True if added
     */
    addSiteToDay(tripId, dayId, siteCode) {
        const trip = this.getTripById(tripId);
        if (!trip) return false;
        
        const day = trip.days.find(d => d.id === dayId);
        if (!day) return false;
        
        if (!day.sites.includes(siteCode)) {
            day.sites.push(siteCode);
            trip.modified = new Date().toISOString();
            this.saveTrips();
            appState.notify('trips', this.trips);
            return true;
        }
        return false;
    }
    
    /**
     * Remove site from a day
     * @param {string} tripId - Trip ID
     * @param {string} dayId - Day ID
     * @param {string} siteCode - Site code to remove
     * @returns {boolean} True if removed
     */
    removeSiteFromDay(tripId, dayId, siteCode) {
        const trip = this.getTripById(tripId);
        if (!trip) return false;
        
        const day = trip.days.find(d => d.id === dayId);
        if (!day) return false;
        
        const index = day.sites.indexOf(siteCode);
        if (index > -1) {
            day.sites.splice(index, 1);
            trip.modified = new Date().toISOString();
            this.saveTrips();
            appState.notify('trips', this.trips);
            return true;
        }
        return false;
    }
    
    /**
     * Update day notes
     * @param {string} tripId - Trip ID
     * @param {string} dayId - Day ID
     * @param {string} notes - Notes text
     * @returns {boolean} True if updated
     */
    updateDayNotes(tripId, dayId, notes) {
        const trip = this.getTripById(tripId);
        if (!trip) return false;
        
        const day = trip.days.find(d => d.id === dayId);
        if (!day) return false;
        
        day.notes = notes;
        trip.modified = new Date().toISOString();
        this.saveTrips();
        appState.notify('trips', this.trips);
        return true;
    }
    
    /**
     * Create trip from favorites
     * @param {string} name - Trip name
     * @returns {Object|null} Created trip or null
     */
    createTripFromFavorites(name) {
        const favorites = favoritesManager.getFavoriteSites();
        if (favorites.length === 0) return null;
        
        const trip = this.createTrip(name, 'Created from favorites');
        const day = this.addDay(trip.id, 'Eclipse Day - August 12, 2026');
        
        favorites.forEach(site => {
            this.addSiteToDay(trip.id, day.id, site.code);
        });
        
        return trip;
    }
    
    /**
     * Export trip as JSON
     * @param {string} tripId - Trip ID
     * @returns {string|null} JSON string or null
     */
    exportTrip(tripId) {
        const trip = this.getTripById(tripId);
        if (!trip) return null;
        
        const exportData = {
            version: '1.0',
            exportDate: new Date().toISOString(),
            trip: {
                ...trip,
                days: trip.days.map(day => ({
                    ...day,
                    siteDetails: day.sites.map(code => {
                        const site = appState.getSiteByCode(code);
                        return site ? {
                            code: site.code,
                            denominacion: site.denominacion,
                            latitude: site.latitude,
                            longitude: site.longitude
                        } : null;
                    }).filter(s => s !== null)
                }))
            }
        };
        
        return JSON.stringify(exportData, null, 2);
    }
    
    /**
     * Import trip from JSON
     * @param {string} jsonString - JSON string to import
     * @returns {Object} Result with success status and message
     */
    importTrip(jsonString) {
        try {
            const data = JSON.parse(jsonString);
            if (!data.trip) {
                return { success: false, message: 'Invalid format' };
            }
            
            const trip = {
                ...data.trip,
                id: Date.now().toString(), // New ID to avoid conflicts
                created: new Date().toISOString(),
                modified: new Date().toISOString()
            };
            
            this.trips.push(trip);
            this.saveTrips();
            appState.notify('trips', this.trips);
            
            return {
                success: true,
                message: `Imported trip: ${trip.name}`,
                tripId: trip.id
            };
        } catch (error) {
            return { success: false, message: 'Error parsing JSON: ' + error.message };
        }
    }
    
    /**
     * Get all trips
     * @returns {Array} Array of trip objects
     */
    getAllTrips() {
        return this.trips;
    }
    
    /**
     * Set current trip
     * @param {string} tripId - Trip ID
     */
    setCurrentTrip(tripId) {
        this.currentTrip = tripId;
        appState.notify('currentTrip', tripId);
    }
    
    /**
     * Get current trip
     * @returns {Object|null} Current trip object or null
     */
    getCurrentTrip() {
        return this.currentTrip ? this.getTripById(this.currentTrip) : null;
    }
}

// Create and export singleton instance
export const tripPlanner = new TripPlanner();

// Made with Bob