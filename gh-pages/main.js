/**
 * Main Application Module - GitHub Pages Version
 * Initializes and coordinates all application modules
 * Uses static file paths instead of API endpoints
 */

import { CONFIG, loadConfig } from './config.js';
import { appState } from '../static/js/state.js';
import { loadCSV } from './data-loader.js';
import { displaySites, filterSites, setupSiteListListeners } from './site-display.js';
import { displaySiteDetails, switchTab } from './site-details.js';
import { setupModalListeners } from '../static/js/modal-handler.js';
import { updateMapWithMultipleSites } from '../static/js/map-handler.js';
import { favoritesManager } from '../static/js/favorites-manager.js';


/**
 * Initialize the application
 */
async function init() {
    try {
        console.log('Initializing Spain Eclipse Sites Viewer (GitHub Pages)...');
        
        // Load configuration from static config.json
        await loadConfig();
        
        // Load site data
        const sites = await loadCSV();
        console.log(`Loaded ${sites.length} sites`);
        
        // Display sites
        displaySites(sites);
        
        // Setup event listeners
        setupSiteListListeners();
        setupSiteClickListeners();
        setupFooterToggle();
        setupModalListeners();
        setupFavoritesListeners();
        setupDocumentationButtons();
        
        // Update favorites count
        updateFavoritesCount();

        console.log('Application initialized successfully');
        
    } catch (error) {
        console.error('Error initializing application:', error);
        const siteList = document.getElementById('siteList');
        if (siteList) {
            siteList.innerHTML = '<li class="error">Error loading data. Please refresh the page.</li>';
        }
    }
}

/**
 * Setup click listeners for site items
 */
function setupSiteClickListeners() {
    const siteList = document.getElementById('siteList');
    if (!siteList) return;
    
    siteList.addEventListener('click', (e) => {
        const siteItem = e.target.closest('.site-item');
        if (!siteItem) return;
        
        const code = siteItem.dataset.code;
        const site = appState.getSiteByCode(code);
        
        if (!site) return;
        
        // Check for multi-select (Ctrl/Cmd + Click)
        if (e.ctrlKey || e.metaKey) {
            appState.toggleSiteSelection(code);
            filterSites(); // Refresh display to show selection
            
            // If we have multiple sites selected and current site is displayed, switch to map tab
            if (appState.selectedSites.length > 1 && appState.currentSite) {
                switchTab('map');
                updateMapWithMultipleSites();
            }
            return;
        }
        
        // Single site selection - use full details view
        appState.setCurrentSite(site);
        appState.selectedSites = []; // Clear multi-selection
        displaySiteDetails(site);
    });
}

/**
 * Setup footer toggle functionality
 */
function setupFooterToggle() {
    const footerToggle = document.getElementById('footerToggle');
    const footerDetails = document.getElementById('footerDetails');
    
    if (footerToggle && footerDetails) {
        footerToggle.addEventListener('click', () => {
            footerDetails.classList.toggle('expanded');
            const icon = footerToggle.querySelector('.footer-toggle-icon');
            if (icon) {
                icon.textContent = footerDetails.classList.contains('expanded') ? '▼' : '▶';
            }
        });
    }
}

/**
 * Setup favorites button and modal
 */
function setupFavoritesListeners() {
    const favoritesBtn = document.getElementById('favoritesBtn');
    if (favoritesBtn) {
        favoritesBtn.addEventListener('click', () => {
            favoritesManager.showFavoritesModal();
        });
    }
}

/**
 * Update favorites count in header
 */
function updateFavoritesCount() {
    const countElement = document.getElementById('favoritesCount');
    if (countElement) {
        countElement.textContent = favoritesManager.getFavorites().length;
    }
}

/**
 * Setup advanced filter toggle
 */
function setupAdvancedFilterListeners() {
    const toggleBtn = document.getElementById('advancedFilterToggle');
    const filtersDiv = document.getElementById('advancedFilters');
    
    if (toggleBtn && filtersDiv) {
        toggleBtn.addEventListener('click', () => {
            const isVisible = filtersDiv.style.display !== 'none';
            filtersDiv.style.display = isVisible ? 'none' : 'block';
            toggleBtn.textContent = isVisible ? '🔧 Advanced Filters' : '🔧 Hide Filters';
        });
    }
}

/**
 * Setup documentation buttons (README and Credits)
 * For GitHub Pages, these open static HTML files
 */
function setupDocumentationButtons() {
    const openReadmeBtn = document.getElementById('openReadmeBtn');
    const openCreditsBtn = document.getElementById('openCreditsBtn');
    
    if (openReadmeBtn) {
        openReadmeBtn.addEventListener('click', () => {
            window.open('readme.html', '_blank');
        });
    }
    
    if (openCreditsBtn) {
        openCreditsBtn.addEventListener('click', () => {
            window.open('credits.html', '_blank');
        });
    }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}

// Export for use in other modules
export { updateFavoritesCount };

// Made with Bob
