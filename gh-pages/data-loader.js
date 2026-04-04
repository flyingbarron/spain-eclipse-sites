/**
 * Data Loader Module - GitHub Pages Version
 * Uses gh-pages config instead of static/js config
 */

import { CONFIG } from './config.js';
import { parseCSVLine } from '../static/js/utils.js';
import { appState } from '../static/js/state.js';

/**
 * Load and parse CSV file
 * @returns {Promise<Array>} Array of site objects
 */
export async function loadCSV() {
    try {
        const response = await fetch(CONFIG.CSV_PATH);
        const text = await response.text();
        
        const sites = parseCSV(text);
        appState.setSitesData(sites);
        
        return sites;
    } catch (error) {
        console.error('Error loading CSV:', error);
        throw error;
    }
}

/**
 * Parse CSV text into array of site objects
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
 * Filter and sort sites based on current filters
 * @param {Array} sites - Array of site objects
 * @param {Object} filters - Filter options
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
        } else if (sortBy === 'name_desc') {
            const nameA = (a.denominacion || a.code).toLowerCase();
            const nameB = (b.denominacion || b.code).toLowerCase();
            return nameB.localeCompare(nameA);
        } else if (sortBy === 'tourist_value') {
            const valueA = parseFloat(a.valor_turistico) || 0;
            const valueB = parseFloat(b.valor_turistico) || 0;
            return valueB - valueA;
        } else if (sortBy === 'tourist_value_asc') {
            const valueA = parseFloat(a.valor_turistico) || 0;
            const valueB = parseFloat(b.valor_turistico) || 0;
            return valueA - valueB;
        } else if (sortBy === 'darkness') {
            const darknessA = parseFloat(a.darksky_darkness) || 0;
            const darknessB = parseFloat(a.darksky_darkness) || 0;
            return darknessB - darknessA;
        } else if (sortBy === 'darkness_asc') {
            const darknessA = parseFloat(a.darksky_darkness) || 0;
            const darknessB = parseFloat(b.darksky_darkness) || 0;
            return darknessA - darknessB;
        } else if (sortBy === 'clearance') {
            const clearanceA = parseFloat(a.terrain_clearance) || -999;
            const clearanceB = parseFloat(b.terrain_clearance) || -999;
            return clearanceB - clearanceA;
        } else if (sortBy === 'clearance_asc') {
            const clearanceA = parseFloat(a.terrain_clearance) || 999;
            const clearanceB = parseFloat(b.terrain_clearance) || 999;
            return clearanceA - clearanceB;
        } else if (sortBy === 'code_desc') {
            return b.code.localeCompare(a.code);
        } else {
            return a.code.localeCompare(b.code);
        }
    });
    
    return filtered;
}

// Made with Bob