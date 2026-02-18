/**
 * Site Display Module
 * Handles rendering of site list in sidebar
 */

import { appState } from './state.js';
import { getCloudInfo, getEclipseInfo } from './utils.js';
import { filterAndSortSites } from './data-loader.js';

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
        // Eclipse visibility label
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
        
        const isSelected = appState.isSiteSelected(site.code);
        return `
            <li class="site-item ${isSelected ? 'active' : ''}" data-code="${site.code}">
                <div class="site-code">${site.code}</div>
                <div class="site-name">${site.denominacion || 'N/A'}</div>
                <div>
                    <span class="site-value">VT: ${site.valor_turistico}</span>
                    <span class="site-privacy">${site.confidencialidad}</span>
                    ${eclipseLabel}
                    ${cloudLabel}
                </div>
            </li>
        `;
    }).join('');
}

/**
 * Filter and display sites based on current filter settings
 */
export function filterSites() {
    const searchTerm = document.getElementById('searchBox').value;
    const eclipseOnly = document.getElementById('eclipseFilter').checked;
    const sortBy = document.getElementById('sortBy').value;
    
    const filtered = filterAndSortSites(appState.sitesData, {
        searchTerm,
        eclipseOnly,
        sortBy
    });
    
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
    
    // Sort dropdown
    const sortBy = document.getElementById('sortBy');
    if (sortBy) {
        sortBy.addEventListener('change', filterSites);
    }
}

// Made with Bob
