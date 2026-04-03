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

function escapeHtml(text) {
    return text
        .replace(/&/g, '&')
        .replace(/</g, '<')
        .replace(/>/g, '>');
}

function renderReadmeMarkdown(markdown) {
    const escaped = escapeHtml(markdown);
    return escaped
        .replace(/^### (.*)$/gm, '<h3>$1</h3>')
        .replace(/^## (.*)$/gm, '<h2>$1</h2>')
        .replace(/^# (.*)$/gm, '<h1>$1</h1>')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" target="_blank">$1</a>')
        .replace(/`([^`]+)`/g, '<code>$1</code>')
        .replace(/\n/g, '<br>');
}

async function loadReadmeContent() {
    const readmeContent = document.getElementById('readmeContent');
    if (!readmeContent) return;

    try {
        const response = await fetch(CONFIG.API.README);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const payload = await response.json();
        readmeContent.innerHTML = renderReadmeMarkdown(payload.content || '');
    } catch (error) {
        console.error('Error loading README:', error);
        readmeContent.innerHTML = '<div class="error">Unable to load README content.</div>';
    }
}

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
        await loadReadmeContent();

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

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}

// Made with Bob
