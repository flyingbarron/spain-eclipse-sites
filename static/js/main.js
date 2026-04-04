/**
 * Main Application Module
 * Initializes and coordinates all application modules
 */

import { CONFIG, loadConfig } from './config.js';
import { appState } from './state.js';
import { loadCSV } from './data-loader.js';
import { displaySites, filterSites, setupSiteListListeners } from './site-display.js';
import { displaySiteDetails, switchTab } from './site-details.js';
import { setupModalListeners } from './modal-handler.js';
import { updateMapWithMultipleSites } from './map-handler.js';
import { favoritesManager } from './favorites-manager.js';
import { getUrlParameter, setUrlParameter } from './utils.js';
import { accessibilityManager } from './accessibility.js';


/**
 * Initialize the application
 */
async function init() {
    try {
        console.log('Initializing Spain Eclipse Sites Viewer...');
        
        // Load configuration from server
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
        setupAdvancedFilterListeners();
        
        // Update favorites count
        updateFavoritesCount();
        
        // Check for site parameter in URL
        checkUrlParameters();

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
        
        // Update URL with site parameter
        setUrlParameter('site', code);
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
 * Setup favorites-related event listeners
 */
function setupFavoritesListeners() {
    const favoritesBtn = document.getElementById('favoritesBtn');
    const favoritesModal = document.getElementById('favoritesModal');
    const closeFavoritesModal = document.getElementById('closeFavoritesModal');
    
    if (favoritesBtn) {
        favoritesBtn.addEventListener('click', () => {
            showFavoritesModal();
        });
    }
    
    if (closeFavoritesModal) {
        closeFavoritesModal.addEventListener('click', () => {
            favoritesModal.style.display = 'none';
        });
    }
    
    // Export favorites
    const exportFavoritesBtn = document.getElementById('exportFavoritesBtn');
    if (exportFavoritesBtn) {
        exportFavoritesBtn.addEventListener('click', () => {
            const json = favoritesManager.exportFavorites();
            downloadJSON(json, 'eclipse-sites-favorites.json');
        });
    }
    
    // Import favorites
    const importFavoritesBtn = document.getElementById('importFavoritesBtn');
    if (importFavoritesBtn) {
        importFavoritesBtn.addEventListener('click', () => {
            showImportModal('favorites');
        });
    }
    
    // Clear favorites
    const clearFavoritesBtn = document.getElementById('clearFavoritesBtn');
    if (clearFavoritesBtn) {
        clearFavoritesBtn.addEventListener('click', () => {
            if (confirm('Are you sure you want to clear all favorites?')) {
                favoritesManager.clearAll();
                showFavoritesModal(); // Refresh
                updateFavoritesCount();
            }
        });
    }
    
    // Subscribe to favorites changes
    appState.subscribe((property, value) => {
        if (property === 'favorites') {
            updateFavoritesCount();
        }
    });
}

/**
 * Setup advanced filter event listeners
 */
function setupAdvancedFilterListeners() {
    const advancedFilterToggle = document.getElementById('advancedFilterToggle');
    const advancedFilters = document.getElementById('advancedFilters');
    
    if (advancedFilterToggle && advancedFilters) {
        advancedFilterToggle.addEventListener('click', () => {
            const isVisible = advancedFilters.style.display !== 'none';
            advancedFilters.style.display = isVisible ? 'none' : 'block';
            advancedFilterToggle.textContent = isVisible ? '🔧 Advanced Filters' : '🔧 Hide Filters';
        });
    }
    
    // Tourist value inputs
    const touristValueMin = document.getElementById('touristValueMin');
    const touristValueMax = document.getElementById('touristValueMax');
    if (touristValueMin && touristValueMax) {
        touristValueMin.addEventListener('change', () => {
            appState.setAdvancedFilters({ touristValueMin: parseFloat(touristValueMin.value) });
            filterSites();
        });
        touristValueMax.addEventListener('change', () => {
            appState.setAdvancedFilters({ touristValueMax: parseFloat(touristValueMax.value) });
            filterSites();
        });
    }
    
    // Cloud coverage slider
    const cloudCoverageMax = document.getElementById('cloudCoverageMax');
    const cloudCoverageValue = document.getElementById('cloudCoverageValue');
    if (cloudCoverageMax && cloudCoverageValue) {
        cloudCoverageMax.addEventListener('input', () => {
            cloudCoverageValue.textContent = cloudCoverageMax.value + '%';
            appState.setAdvancedFilters({ cloudCoverageMax: parseInt(cloudCoverageMax.value) });
            filterSites();
        });
    }
    
    // Bortle scale slider
    const bortleMax = document.getElementById('bortleMax');
    const bortleValue = document.getElementById('bortleValue');
    if (bortleMax && bortleValue) {
        bortleMax.addEventListener('input', () => {
            bortleValue.textContent = bortleMax.value;
            appState.setAdvancedFilters({ bortleMax: parseInt(bortleMax.value) });
            filterSites();
        });
    }
    
    // Route difficulty checkboxes
    const difficultyCheckboxes = document.querySelectorAll('.difficulty-checkbox');
    difficultyCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', () => {
            const selected = Array.from(difficultyCheckboxes)
                .filter(cb => cb.checked)
                .map(cb => cb.value);
            appState.setAdvancedFilters({ routeDifficulty: selected });
            filterSites();
        });
    });
    
    // Reset filters button
    const resetFiltersBtn = document.getElementById('resetFiltersBtn');
    if (resetFiltersBtn) {
        resetFiltersBtn.addEventListener('click', () => {
            appState.resetAdvancedFilters();
            // Reset UI elements
            if (touristValueMin) touristValueMin.value = 0;
            if (touristValueMax) touristValueMax.value = 10;
            if (cloudCoverageMax) {
                cloudCoverageMax.value = 100;
                cloudCoverageValue.textContent = '100%';
            }
            if (bortleMax) {
                bortleMax.value = 9;
                bortleValue.textContent = '9';
            }
            difficultyCheckboxes.forEach(cb => cb.checked = false);
            filterSites();
        });
    }
}

/**
 * Update favorites count in header
 */
function updateFavoritesCount() {
    const favoritesCount = document.getElementById('favoritesCount');
    if (favoritesCount) {
        favoritesCount.textContent = favoritesManager.getCount();
    }
}

/**
 * Show favorites modal
 */
function showFavoritesModal() {
    const modal = document.getElementById('favoritesModal');
    const favoritesList = document.getElementById('favoritesList');
    
    const favorites = favoritesManager.getFavoriteSites();
    
    if (favorites.length === 0) {
        favoritesList.innerHTML = '<p class="empty-message">No favorites yet. Click the ☆ icon on any site to add it to your favorites.</p>';
    } else {
        favoritesList.innerHTML = favorites.map(site => `
            <div class="favorite-item" data-code="${site.code}">
                <div class="favorite-info">
                    <strong>${site.code}</strong> - ${site.denominacion}
                    <div class="favorite-meta">
                        ${site.eclipse_visibility === 'visible' ? '🌑 Eclipse Visible' : ''}
                        ${site.cloud_coverage ? ` | ☁️ ${site.cloud_coverage}%` : ''}
                    </div>
                </div>
                <button class="remove-favorite-btn" data-code="${site.code}">✕</button>
            </div>
        `).join('');
        
        // Add click listeners
        favoritesList.querySelectorAll('.favorite-item').forEach(item => {
            item.addEventListener('click', (e) => {
                if (!e.target.classList.contains('remove-favorite-btn')) {
                    const code = item.dataset.code;
                    const site = appState.getSiteByCode(code);
                    if (site) {
                        modal.style.display = 'none';
                        displaySiteDetails(site);
                    }
                }
            });
        });
        
        favoritesList.querySelectorAll('.remove-favorite-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const code = btn.dataset.code;
                favoritesManager.removeFavorite(code);
                showFavoritesModal(); // Refresh
                updateFavoritesCount();
            });
        });
    }
    
    modal.style.display = 'flex';
}

/**
 * Show import modal
 * @param {string} type - 'favorites' or 'trip'
 */
function showImportModal(type) {
    const modal = document.getElementById('importModal');
    const confirmBtn = document.getElementById('confirmImportBtn');
    const cancelBtn = document.getElementById('cancelImportBtn');
    const closeBtn = document.getElementById('closeImportModal');
    const input = document.getElementById('importDataInput');
    const result = document.getElementById('importResult');
    
    input.value = '';
    result.textContent = '';
    
    const handleImport = () => {
        const jsonString = input.value.trim();
        if (!jsonString) {
            result.textContent = 'Please paste JSON data';
            result.style.color = 'red';
            return;
        }
        
        const importResult = favoritesManager.importFavorites(jsonString);
        
        result.textContent = importResult.message;
        result.style.color = importResult.success ? 'green' : 'red';
        
        if (importResult.success) {
            setTimeout(() => {
                modal.style.display = 'none';
                if (type === 'favorites') {
                    updateFavoritesCount();
                    filterSites();
                }
            }, 1500);
        }
    };
    
    confirmBtn.onclick = handleImport;
    cancelBtn.onclick = () => modal.style.display = 'none';
    closeBtn.onclick = () => modal.style.display = 'none';
    
    modal.style.display = 'flex';
}

/**
 * Download JSON data as file
 * @param {string} jsonString - JSON string
 * @param {string} filename - Filename
 */
function downloadJSON(jsonString, filename) {
    const blob = new Blob([jsonString], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

/**
 * Check URL parameters and load site if specified
 */
function checkUrlParameters() {
    const siteCode = getUrlParameter('site');
    if (siteCode) {
        const site = appState.getSiteByCode(siteCode.toUpperCase());
        if (site) {
            // Display the site
            appState.setCurrentSite(site);
            displaySiteDetails(site);
            
            // Scroll to the site in the list
            const siteItem = document.querySelector(`.site-item[data-code="${site.code}"]`);
            if (siteItem) {
                siteItem.scrollIntoView({ behavior: 'smooth', block: 'center' });
                siteItem.classList.add('highlighted');
                setTimeout(() => {
                    siteItem.classList.remove('highlighted');
                }, 2000);
            }
        } else {
            console.warn(`Site not found: ${siteCode}`);
            // Clear invalid parameter
            setUrlParameter('site', null);
        }
    }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}

// Made with Bob
