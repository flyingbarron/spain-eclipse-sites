/**
 * Site Display Module - GitHub Pages Version
 * Re-exports site-display with gh-pages data-loader
 */

// Import the filterAndSortSites from gh-pages data-loader
import { filterAndSortSites } from './data-loader.js';

// Import everything else from the original module
import { appState } from '../static/js/state.js';
import { getCloudInfo, getEclipseInfo } from '../static/js/utils.js';
import { favoritesManager } from '../static/js/favorites-manager.js';
import { notesManager } from '../static/js/notes-manager.js';

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

// Re-export everything else from the original module
export { displaySites, filterSites, setupSiteListListeners } from '../static/js/site-display.js';

// Made with Bob