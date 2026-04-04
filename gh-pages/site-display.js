/**
 * Site Display Module - GitHub Pages Standalone Version
 * Complete standalone version without dependencies on static/js modules
 */

import { appState } from '../static/js/state.js';
import { getCloudInfo, getEclipseInfo } from '../static/js/utils.js';
import { filterAndSortSites } from './data-loader.js';
import { favoritesManager } from '../static/js/favorites-manager.js';
import { notesManager } from '../static/js/notes-manager.js';

/**
 * Update site counter display
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
 */
export function displaySites(sites) {
    const list = document.getElementById('siteList');
    
    updateSiteCounter(sites.length, appState.sitesData.length);
    
    if (sites.length === 0) {
        list.innerHTML = '<li class="loading">No sites found</li>';
        return;
    }
    
    list.innerHTML = sites.map(site => {
        const eclipseInfo = getEclipseInfo(site.eclipse_visibility);
        const eclipseLabel = eclipseInfo.text ?
            `<span class="site-eclipse ${eclipseInfo.class}">${eclipseInfo.text}</span>` : '';
        
        let cloudLabel = '';
        if (site.cloud_coverage && site.cloud_status === 'success') {
            const cloudPct = parseInt(site.cloud_coverage);
            const cloudInfo = getCloudInfo(cloudPct);
            cloudLabel = `<span class="site-cloud ${cloudInfo.class}">${cloudInfo.emoji} ${cloudPct}%</span>`;
        }
        
        let bortleLabel = '';
        if (site.darksky_bortle && site.darksky_status === 'success') {
            const bortle = parseFloat(site.darksky_bortle);
            let bortleIcon = '🌌';
            if (bortle <= 2) bortleIcon = '🌙';
            else if (bortle === 3) bortleIcon = '🌃';
            else if (bortle === 4) bortleIcon = '🌠';
            else if (bortle <= 6) bortleIcon = '🌌';
            else if (bortle <= 8) bortleIcon = '💡';
            else bortleIcon = '🌆';
            bortleLabel = `<span class="site-bortle" title="Bortle ${bortle}">${bortleIcon}</span>`;
        }
        
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
            <li class="site-item ${isSelected ? 'active' : ''}" data-code="${site.code}">
                <div class="site-header">
                    <div class="site-code">${site.code} ${noteIndicator}</div>
                    <button class="favorite-btn ${isFavorite ? 'is-favorite' : ''}"
                            data-code="${site.code}"
                            data-action="favorite"
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
 */
export function applyAdvancedFilters(sites) {
    const filters = appState.advancedFilters;
    
    return sites.filter(site => {
        const touristValue = parseFloat(site.valor_turistico) || 0;
        if (touristValue < filters.touristValueMin || touristValue > filters.touristValueMax) {
            return false;
        }
        
        if (site.cloud_coverage && site.cloud_status === 'success') {
            const cloudPct = parseInt(site.cloud_coverage);
            if (cloudPct > filters.cloudCoverageMax) {
                return false;
            }
        }
        
        if (site.darksky_bortle && site.darksky_status === 'success') {
            const bortle = parseFloat(site.darksky_bortle);
            if (bortle > filters.bortleMax) {
                return false;
            }
        }
        
        if (filters.routeDifficulty.length > 0) {
            if (!site.route_difficulty || !filters.routeDifficulty.includes(site.route_difficulty)) {
                return false;
            }
        }
        
        return true;
    });
}

/**
 * Filter sites based on current state
 */
export function filterSites() {
    let filtered = appState.sitesData;
    
    const searchTerm = appState.searchTerm ? appState.searchTerm.toLowerCase() : '';
    if (searchTerm) {
        filtered = filtered.filter(site =>
            (site.code && site.code.toLowerCase().includes(searchTerm)) ||
            (site.denominacion && site.denominacion.toLowerCase().includes(searchTerm))
        );
    }
    
    if (appState.eclipseFilter) {
        filtered = filtered.filter(site => site.eclipse_visibility === 'visible');
    }
    
    if (appState.favoritesFilter) {
        filtered = filtered.filter(site => favoritesManager.isFavorite(site.code));
    }
    
    if (appState.notesFilter) {
        filtered = filtered.filter(site => {
            const hasNote = notesManager.hasNote(site.code);
            const hasBrochure = site.brochure_url && site.brochure_url.trim() !== '';
            return hasNote || hasBrochure;
        });
    }
    
    filtered = applyAdvancedFilters(filtered);
    
    filtered = filterAndSortSites(filtered, { sortBy: appState.sortBy });
    
    displaySites(filtered);
}

/**
 * Setup site list event listeners
 */
export function setupSiteListListeners() {
    const searchBox = document.getElementById('searchBox');
    const eclipseFilter = document.getElementById('eclipseFilter');
    const favoritesFilter = document.getElementById('favoritesFilter');
    const notesFilter = document.getElementById('notesFilter');
    const sortBy = document.getElementById('sortBy');
    
    if (searchBox) {
        searchBox.addEventListener('input', (e) => {
            appState.searchTerm = e.target.value;
            filterSites();
        });
    }
    
    if (eclipseFilter) {
        eclipseFilter.addEventListener('change', (e) => {
            appState.eclipseFilter = e.target.checked;
            filterSites();
        });
    }
    
    if (favoritesFilter) {
        favoritesFilter.addEventListener('change', (e) => {
            appState.favoritesFilter = e.target.checked;
            filterSites();
        });
    }
    
    if (notesFilter) {
        notesFilter.addEventListener('change', (e) => {
            appState.notesFilter = e.target.checked;
            filterSites();
        });
    }
    
    if (sortBy) {
        sortBy.addEventListener('change', (e) => {
            appState.sortBy = e.target.value;
            filterSites();
        });
    }
    
    setupAdvancedFilterListeners();
    
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
                
                // Update favorites count in header
                import('./main.js').then(module => {
                    module.updateFavoritesCount();
                });
                
                filterSites(); // Refresh display
                return;
            }
        });
    }
    
    document.addEventListener('favoriteToggled', () => {
        if (appState.favoritesFilter) {
            filterSites();
        } else {
            displaySites(appState.sitesData);
        }
    });
}

function setupAdvancedFilterListeners() {
    const touristValueMin = document.getElementById('touristValueMin');
    const touristValueMax = document.getElementById('touristValueMax');
    const cloudCoverageMax = document.getElementById('cloudCoverageMax');
    const cloudCoverageValue = document.getElementById('cloudCoverageValue');
    const bortleMax = document.getElementById('bortleMax');
    const bortleValue = document.getElementById('bortleValue');
    const difficultyCheckboxes = document.querySelectorAll('.difficulty-checkbox');
    
    if (touristValueMin) {
        touristValueMin.addEventListener('input', (e) => {
            appState.advancedFilters.touristValueMin = parseFloat(e.target.value);
            filterSites();
        });
    }
    
    if (touristValueMax) {
        touristValueMax.addEventListener('input', (e) => {
            appState.advancedFilters.touristValueMax = parseFloat(e.target.value);
            filterSites();
        });
    }
    
    if (cloudCoverageMax) {
        cloudCoverageMax.addEventListener('input', (e) => {
            const value = parseInt(e.target.value);
            appState.advancedFilters.cloudCoverageMax = value;
            if (cloudCoverageValue) {
                cloudCoverageValue.textContent = `${value}%`;
            }
            filterSites();
        });
    }
    
    if (bortleMax) {
        bortleMax.addEventListener('input', (e) => {
            const value = parseInt(e.target.value);
            appState.advancedFilters.bortleMax = value;
            if (bortleValue) {
                bortleValue.textContent = value;
            }
            filterSites();
        });
    }
    
    difficultyCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', () => {
            const checked = Array.from(difficultyCheckboxes)
                .filter(cb => cb.checked)
                .map(cb => cb.value);
            appState.advancedFilters.routeDifficulty = checked;
            filterSites();
        });
    });
}

// Made with Bob