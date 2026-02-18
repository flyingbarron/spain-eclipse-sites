/**
 * Data Loader Module - Standalone Version
 * Loads data from embedded window.EMBEDDED_SITE_DATA
 */

import { parseCSVLine } from './utils.js';
import { appState } from './state.js';

/**
 * Load embedded site data
 * @returns {Promise<Array>} Array of site objects
 */
export async function loadCSV() {
    try {
        if (!window.EMBEDDED_SITE_DATA || !window.EMBEDDED_SITE_DATA.sites) {
            throw new Error('Embedded site data not found');
        }
        
        const sites = window.EMBEDDED_SITE_DATA.sites;
        appState.setSitesData(sites);
        
        console.log(`Loaded ${sites.length} sites from embedded data`);
        return sites;
    } catch (error) {
        console.error('Error loading embedded data:', error);
        throw error;
    }
}

/**
 * Parse CSV text into array of site objects (not used in standalone)
 * @param {string} text - CSV text content
 * @returns {Array} Array of site objects
 */
export function parseCSV(text) {
    const lines = text.trim().split('\n');
    const headers = parseCSVLine(lines[0]);
    
    const sites = lines.slice(1).map(line => {
        const values = parseCSVLine(line);
        const site = {};
        headers.forEach((header, index) => {
            site[header.trim()] = values[index] ? values[index].trim() : '';
        });
        return site;
    });
    
    return sites;
}

/**
 * Filter and sort sites based on criteria
 * @param {Array} sites - Array of site objects
 * @param {Object} filters - Filter criteria
 * @returns {Array} Filtered and sorted sites
 */
export function filterAndSortSites(sites, filters) {
    const { searchTerm = '', eclipseOnly = false, sortBy = 'code' } = filters;
    
    // Filter
    let filtered = sites.filter(site => {
        const matchesSearch = site.code.toLowerCase().includes(searchTerm.toLowerCase()) ||
            (site.denominacion && site.denominacion.toLowerCase().includes(searchTerm.toLowerCase()));
        
        const matchesEclipse = !eclipseOnly || site.eclipse_visibility === 'visible';
        
        return matchesSearch && matchesEclipse;
    });
    
    // Sort
    filtered.sort((a, b) => {
        if (sortBy === 'name') {
            const nameA = (a.denominacion || a.code).toLowerCase();
            const nameB = (b.denominacion || b.code).toLowerCase();
            return nameA.localeCompare(nameB);
        } else if (sortBy === 'tourist_value') {
            const valueA = parseFloat(a.valor_turistico) || 0;
            const valueB = parseFloat(b.valor_turistico) || 0;
            return valueB - valueA; // Descending order
        } else {
            // Default: sort by code
            return a.code.localeCompare(b.code);
        }
    });
    
    return filtered;
}

// Made with Bob
