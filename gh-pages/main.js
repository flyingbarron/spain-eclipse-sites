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
import { updateMapWithMultipleSites } from './map-handler.js';
import { favoritesManager } from '../static/js/favorites-manager.js';


/**
 * Initialize the application
 */
async function init() {
    try {
        console.log('🚀 Initializing Spain Eclipse Sites Viewer (GitHub Pages Static Build v2)...');
        
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
            siteList.innerHTML = `<li class="error">
                <strong>Error loading data</strong><br>
                ${error.message || error}<br>
                <small>Check console for details</small>
            </li>`;
        }
        
        // Also show error in content area
        const content = document.getElementById('content');
        if (content) {
            content.innerHTML = `
                <div class="error" style="padding: 2rem; margin: 1rem;">
                    <h3>Error Loading Application</h3>
                    <p><strong>Error:</strong> ${error.message || error}</p>
                    <p><strong>Stack:</strong></p>
                    <pre style="background: #f8f9fa; padding: 1rem; overflow-x: auto; font-size: 0.8rem;">${error.stack || 'No stack trace available'}</pre>
                    <p>Please try:</p>
                    <ul>
                        <li>Refreshing the page</li>
                        <li>Clearing your browser cache</li>
                        <li>Using a different browser</li>
                    </ul>
                </div>
            `;
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
        
        // On mobile, collapse sidebar after selecting a site
        if (window.innerWidth <= 768) {
            collapseSidebarOnMobile();
        }
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
        countElement.textContent = favoritesManager.favorites.length;
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
    
    // Get the base URL (works for both local and GitHub Pages)
    const baseUrl = window.location.origin + window.location.pathname.replace(/\/[^\/]*$/, '/');
    
    if (openReadmeBtn) {
        openReadmeBtn.addEventListener('click', () => {
            window.open(baseUrl + 'readme.html', '_blank');
        });
    }
    
    if (openCreditsBtn) {
        openCreditsBtn.addEventListener('click', () => {
            window.open(baseUrl + 'credits.html', '_blank');
        });
    }
}

/**
 * Collapse sidebar on mobile to show full site details
 * Also expand the content area to use full screen
 */
function collapseSidebarOnMobile() {
    const sidebar = document.querySelector('.sidebar');
    const content = document.querySelector('.content');
    
    if (sidebar && window.innerWidth <= 768) {
        sidebar.classList.add('collapsed');
        sidebar.classList.remove('expanded');
    }
    
    // Expand content area when sidebar is collapsed
    if (content && window.innerWidth <= 768) {
        content.classList.remove('collapsed');
    }
}

/**
 * Expand sidebar on mobile to show site list
 * Also collapse the content area to give more room for the list
 */
function expandSidebarOnMobile() {
    const sidebar = document.querySelector('.sidebar');
    const content = document.querySelector('.content');
    
    if (sidebar) {
        sidebar.classList.remove('collapsed');
        // Add expanded class to sidebar when content is collapsed
        if (window.innerWidth <= 768) {
            sidebar.classList.add('expanded');
        }
    }
    
    // On mobile, collapse content area when showing list
    if (content && window.innerWidth <= 768) {
        content.classList.add('collapsed');
    }
}

/**
 * Setup mobile sidebar collapse/expand functionality
 */
function setupMobileSidebarToggle() {
    const expandBtn = document.getElementById('sidebarExpandBtn');
    if (expandBtn) {
        expandBtn.addEventListener('click', expandSidebarOnMobile);
    }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}

// Setup mobile sidebar toggle after DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', setupMobileSidebarToggle);
} else {
    setupMobileSidebarToggle();
}

// Export for use in other modules
export { updateFavoritesCount, collapseSidebarOnMobile, expandSidebarOnMobile };

// Made with Bob
