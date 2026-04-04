/**
 * Site Display Module
 * Handles rendering of site list in sidebar
 */

import { appState } from './state.js';
import { getCloudInfo, getEclipseInfo } from './utils.js';
import { filterAndSortSites } from './data-loader.js';
import { favoritesManager } from './favorites-manager.js';
import { notesManager } from './notes-manager.js';

/**
 * Update site counter display
 * @param {number} visibleCount - Number of visible sites
 * @param {number} totalCount - Total number of sites
 */
export function updateSiteCounter(visibleCount, totalCount) {
    const visibleCountEl = document.getElementById('visibleCount');
    const totalCountEl = document.getElementById('totalCount');
    
    if (visibleCountEl && totalCountEl) {
        visibleCountEl.textContent = visibleCount;
        totalCountEl.textContent = totalCount;
    }
}

/**
 * Display sites in sidebar list
 * @param {Array} sites - Array of site objects to display
 */
export function displaySites(sites) {
    const list = document.getElementById('siteList');
    
    // Update counter
    updateSiteCounter(sites.length, appState.sitesData.length);
    
    if (sites.length === 0) {
        list.innerHTML = '<li class="loading">No sites found</li>';
        return;
    }
    
    list.innerHTML = sites.map(site => {
        // Eclipse visibility marker
        const eclipseInfo = getEclipseInfo(site.eclipse_visibility);
        const eclipseLabel = eclipseInfo.text ?
            `<span class="site-eclipse ${eclipseInfo.class}">${eclipseInfo.text}</span>` : '';
        
        // Cloud coverage label
        let cloudLabel = '';
        if (site.cloud_coverage && site.cloud_status === 'success') {
            const cloudPct = parseInt(site.cloud_coverage);
            const cloudInfo = getCloudInfo(cloudPct);
            cloudLabel = `<span class="site-cloud ${cloudInfo.class}">${cloudInfo.emoji} ${cloudPct}%</span>`;
        }
        
        // Bortle scale icon - different icons for different values
        let bortleLabel = '';
        if (site.darksky_bortle && site.darksky_status === 'success') {
            const bortle = parseFloat(site.darksky_bortle);
            let bortleIcon = '🌌'; // Default
            if (bortle <= 2) bortleIcon = '🌙'; // Excellent dark sky (1-2)
            else if (bortle === 3) bortleIcon = '🌃'; // Good dark sky (3)
            else if (bortle === 4) bortleIcon = '🌠'; // Rural sky (4)
            else if (bortle <= 6) bortleIcon = '🌌'; // Moderate (5-6)
            else if (bortle <= 8) bortleIcon = '💡'; // Light pollution (7-8)
            else bortleIcon = '🌆'; // Heavy light pollution (9+)
            bortleLabel = `<span class="site-bortle" title="Bortle ${bortle}">${bortleIcon}</span>`;
        }
        
        // Horizon clearance label
        let clearanceLabel = '';
        if (site.terrain_clearance) {
            const clearance = parseFloat(site.terrain_clearance);
            const clearanceColor = clearance >= 0 ? '#28a745' : '#dc3545';
            const clearanceIcon = clearance >= 0 ? '✓' : '✗';
            clearanceLabel = `<span class="site-clearance" style="color: ${clearanceColor}" title="Horizon clearance: ${site.terrain_clearance}°">🏔️${clearanceIcon}</span>`;
        }
        
        const isSelected = appState.isSiteSelected(site.code);
        const isFavorite = favoritesManager.isFavorite(site.code);
        const favoriteIcon = isFavorite ? '⭐' : '☆';
        const hasNote = notesManager.hasNote(site.code);
        const hasBrochure = site.brochure_url && site.brochure_url.trim() !== '';
        const hasContent = hasNote || hasBrochure;
        const noteIndicator = hasContent ? '<span class="note-indicator" title="Has personal note or brochure">📝</span>' : '';
        
        return `
            <li class="site-item ${isSelected ? 'active' : ''}"
                data-code="${site.code}"
                role="listitem"
                tabindex="0"
                aria-label="${site.code}: ${site.denominacion || 'N/A'}. ${eclipseInfo.text || ''}. ${site.cloud_coverage ? `Cloud coverage ${site.cloud_coverage}%` : ''}">
                <div class="site-header">
                    <div class="site-code">${site.code} ${noteIndicator}</div>
                    <button class="favorite-btn ${isFavorite ? 'is-favorite' : ''}"
                            data-code="${site.code}"
                            data-action="favorite"
                            tabindex="-1"
                            aria-label="${isFavorite ? 'Remove from favorites' : 'Add to favorites'}"
                            title="${isFavorite ? 'Remove from favorites' : 'Add to favorites'}">
                        ${favoriteIcon}
                    </button>
                </div>
                <div class="site-name">${site.denominacion || 'N/A'}</div>
                <div>
                    ${eclipseLabel}
                    ${cloudLabel ? ' | ' + cloudLabel : ''}
                    ${bortleLabel ? ' | ' + bortleLabel : ''}
                    ${clearanceLabel ? ' | ' + clearanceLabel : ''}
                </div>
            </li>
        `;
    }).join('');
}

/**
 * Apply advanced filters to sites
 * @param {Array} sites - Sites to filter
 * @returns {Array} Filtered sites
 */
export function applyAdvancedFilters(sites) {
    const filters = appState.advancedFilters;
    
    return sites.filter(site => {
        // Tourist value range
        const touristValue = parseFloat(site.valor_turistico) || 0;
        if (touristValue < filters.touristValueMin || touristValue > filters.touristValueMax) {
            return false;
        }
        
        // Cloud coverage max
        if (site.cloud_coverage && site.cloud_status === 'success') {
            const cloudPct = parseInt(site.cloud_coverage);
            if (cloudPct > filters.cloudCoverageMax) {
                return false;
            }
        }
        
        // Bortle scale max
        if (site.darksky_bortle && site.darksky_status === 'success') {
            const bortle = parseFloat(site.darksky_bortle);
            if (bortle > filters.bortleMax) {
                return false;
            }
        }
        
        // Route difficulty
        if (filters.routeDifficulty.length > 0) {
            if (!filters.routeDifficulty.includes(site.route_difficulty)) {
                return false;
            }
        }
        
        return true;
    });
}

/**
 * Filter and display sites based on current filter settings
 */
export function filterSites() {
    const searchTerm = document.getElementById('searchBox').value;
    const eclipseOnly = document.getElementById('eclipseFilter').checked;
    const favoritesOnly = document.getElementById('favoritesFilter')?.checked || false;
    const notesOnly = document.getElementById('notesFilter')?.checked || false;
    const sortBy = document.getElementById('sortBy').value;
    
    let filtered = filterAndSortSites(appState.sitesData, {
        searchTerm,
        eclipseOnly,
        sortBy
    });
    
    // Apply favorites filter
    if (favoritesOnly) {
        const favoriteCodes = favoritesManager.favorites;
        filtered = filtered.filter(site => favoriteCodes.includes(site.code));
    }
    
    // Apply notes filter (includes sites with notes OR brochures)
    if (notesOnly) {
        filtered = filtered.filter(site => {
            const hasNote = notesManager.hasNote(site.code);
            const hasBrochure = site.brochure_url && site.brochure_url.trim() !== '';
            return hasNote || hasBrochure;
        });
    }
    
    // Apply advanced filters
    filtered = applyAdvancedFilters(filtered);
    
    displaySites(filtered);
}

/**
 * Setup event listeners for site list interactions
 */
export function setupSiteListListeners() {
    // Search box
    const searchBox = document.getElementById('searchBox');
    if (searchBox) {
        searchBox.addEventListener('input', filterSites);
    }
    
    // Eclipse filter checkbox
    const eclipseFilter = document.getElementById('eclipseFilter');
    if (eclipseFilter) {
        eclipseFilter.addEventListener('change', filterSites);
    }
    
    // Favorites filter checkbox
    const favoritesFilter = document.getElementById('favoritesFilter');
    if (favoritesFilter) {
        favoritesFilter.addEventListener('change', filterSites);
    }
    
    // Notes filter checkbox
    const notesFilter = document.getElementById('notesFilter');
    if (notesFilter) {
        notesFilter.addEventListener('change', filterSites);
    }
    
    // Sort dropdown
    const sortBy = document.getElementById('sortBy');
    if (sortBy) {
        sortBy.addEventListener('change', filterSites);
    }
    
    // Favorite buttons (event delegation)
    const siteList = document.getElementById('siteList');
    if (siteList) {
        siteList.addEventListener('click', (e) => {
            // Check if clicked element or its parent is the favorite button
            const favoriteBtn = e.target.closest('[data-action="favorite"]');
            if (favoriteBtn) {
                e.stopPropagation(); // Prevent site selection
                const code = favoriteBtn.dataset.code;
                favoritesManager.toggleFavorite(code);
                filterSites(); // Refresh display
                return;
            }
        });
    }
    
    // Subscribe to favorites changes
    appState.subscribe((property, value) => {
        if (property === 'favorites') {
            filterSites(); // Refresh when favorites change
        }
    });
}

// Made with Bob
