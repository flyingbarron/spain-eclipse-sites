/**
 * Map View Module - GitHub Pages Version
 * Handles full-screen map view with all filtered sites
 */

import { appState } from '../static/js/state.js';
import { CONFIG } from './config.js';
import { displaySiteDetails } from './site-details.js';

// Global map instance for map view
let mapViewInstance = null;
let markerClusterGroup = null;
let currentMarkers = new Map(); // Map of site code to marker
let detailPanelOpen = false;

/**
 * Get marker color based on eclipse visibility
 * @param {string} visibility - Eclipse visibility status
 * @returns {string} Color hex code
 */
function getMarkerColor(visibility) {
    switch (visibility) {
        case 'visible':
            return '#6f42c1'; // Purple
        case 'not_visible':
            return '#dc3545'; // Red
        default:
            return '#ffc107'; // Yellow/amber
    }
}

/**
 * Create custom marker icon
 * @param {Object} site - Site object
 * @param {boolean} isSelected - Whether site is selected
 * @returns {L.DivIcon} Leaflet div icon
 */
function createMarkerIcon(site, isSelected = false) {
    const color = getMarkerColor(site.eclipse_visibility);
    const selectedClass = isSelected ? 'eclipse-marker-selected' : '';
    
    return L.divIcon({
        html: `<div class="eclipse-marker-icon ${selectedClass}" style="background: ${color};">🌑</div>`,
        className: 'eclipse-marker',
        iconSize: [30, 30],
        iconAnchor: [15, 15],
        popupAnchor: [0, -15]
    });
}

/**
 * Create marker popup content
 * @param {Object} site - Site object
 * @returns {string} HTML string
 */
function createMarkerPopup(site) {
    const eclipseStatus = site.eclipse_visibility === 'visible' ? '🌑 Visible' :
                         site.eclipse_visibility === 'not_visible' ? '🌑 Not Visible' :
                         '🌑 Unknown';
    
    let cloudInfo = '';
    if (site.cloud_coverage && site.cloud_status === 'success') {
        const cloudPct = parseInt(site.cloud_coverage);
        const cloudEmoji = cloudPct >= 60 ? '☁️' : cloudPct >= 30 ? '⛅' : '☀️';
        cloudInfo = `<div>${cloudEmoji} Cloud: ${cloudPct}%</div>`;
    }
    
    return `
        <div style="min-width: 180px;">
            <h4 style="margin: 0 0 8px 0; font-size: 0.95rem;">${site.denominacion || site.code}</h4>
            <div style="font-size: 0.85rem; color: #666;">
                <div><strong>Code:</strong> ${site.code}</div>
                <div><strong>Eclipse:</strong> ${eclipseStatus}</div>
                ${cloudInfo}
            </div>
            <button onclick="window.showSiteDetailsInPanel('${site.code}')" 
                    style="margin-top: 8px; padding: 4px 12px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; width: 100%;">
                View Details
            </button>
        </div>
    `;
}

/**
 * Initialize map view with filtered sites
 * @param {Array} sites - Array of site objects to display
 */
export function initializeMapView(sites) {
    const container = document.getElementById('fullMapContainer');
    
    // Remove existing map if any
    if (mapViewInstance) {
        mapViewInstance.remove();
        mapViewInstance = null;
    }
    
    // Clear markers map
    currentMarkers.clear();
    
    // Create new map
    setTimeout(() => {
        mapViewInstance = L.map('fullMapContainer', {
            center: [41.5, -3.0], // Center of Spain
            zoom: 7
        });
        
        L.tileLayer(CONFIG.MAP.TILE_LAYER, {
            attribution: CONFIG.MAP.ATTRIBUTION,
            maxZoom: 19
        }).addTo(mapViewInstance);
        
        // Create marker cluster group
        markerClusterGroup = L.markerClusterGroup({
            maxClusterRadius: 50,
            spiderfyOnMaxZoom: true,
            showCoverageOnHover: false,
            zoomToBoundsOnClick: true
        });
        
        // Add markers for each site
        const bounds = L.latLngBounds();
        
        sites.forEach(site => {
            const lat = parseFloat(site.latitude);
            const lon = parseFloat(site.longitude);
            
            if (isNaN(lat) || isNaN(lon)) return;
            
            bounds.extend([lat, lon]);
            
            const marker = L.marker([lat, lon], {
                icon: createMarkerIcon(site)
            });
            
            marker.bindPopup(createMarkerPopup(site));
            
            // Add click handler
            marker.on('click', () => {
                selectSiteOnMap(site.code);
            });
            
            markerClusterGroup.addLayer(marker);
            currentMarkers.set(site.code, marker);
        });
        
        mapViewInstance.addLayer(markerClusterGroup);
        
        // Fit bounds if we have sites
        if (sites.length > 0) {
            mapViewInstance.fitBounds(bounds, { padding: [50, 50] });
        }
        
        // Add legend
        addMapLegend();
        
        // Invalidate size to ensure proper rendering
        setTimeout(() => {
            mapViewInstance.invalidateSize();
        }, 100);
    }, 50);
}

/**
 * Add legend to map
 */
function addMapLegend() {
    const legend = L.control({ position: 'bottomleft' });
    
    legend.onAdd = function() {
        const div = L.DomUtil.create('div', 'map-legend');
        div.innerHTML = `
            <h4>Eclipse Visibility</h4>
            <div class="map-legend-item">
                <div class="map-legend-color" style="background: #6f42c1;"></div>
                <span>Visible</span>
            </div>
            <div class="map-legend-item">
                <div class="map-legend-color" style="background: #dc3545;"></div>
                <span>Not Visible</span>
            </div>
            <div class="map-legend-item">
                <div class="map-legend-color" style="background: #ffc107;"></div>
                <span>Unknown</span>
            </div>
        `;
        return div;
    };
    
    legend.addTo(mapViewInstance);
}

/**
 * Select a site on the map
 * @param {string} siteCode - Site code to select
 */
export function selectSiteOnMap(siteCode) {
    const site = appState.getSiteByCode(siteCode);
    if (!site) return;
    
    // Update all markers to show selection
    currentMarkers.forEach((marker, code) => {
        const markerSite = appState.getSiteByCode(code);
        const isSelected = code === siteCode;
        marker.setIcon(createMarkerIcon(markerSite, isSelected));
    });
    
    // Show site details in panel
    showSiteDetailsPanel(site);
    
    // Update sidebar selection
    document.querySelectorAll('.site-item').forEach(item => {
        item.classList.remove('active');
    });
    const siteItem = document.querySelector(`[data-code="${siteCode}"]`);
    if (siteItem) {
        siteItem.classList.add('active');
        siteItem.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
    
    // Update app state
    appState.setCurrentSite(site);
}

/**
 * Show site details in slide-in panel
 * @param {Object} site - Site object
 */
function showSiteDetailsPanel(site) {
    const panel = document.getElementById('mapDetailPanel');
    const content = document.getElementById('mapDetailContent');
    
    if (!panel || !content) return;
    
    // Generate site details HTML
    content.innerHTML = generateSiteDetailsHTML(site);
    
    // Show panel
    panel.style.display = 'block';
    setTimeout(() => {
        panel.classList.add('active');
    }, 10);
    
    detailPanelOpen = true;
}

/**
 * Close site details panel
 */
export function closeSiteDetailsPanel() {
    const panel = document.getElementById('mapDetailPanel');
    if (!panel) return;
    
    panel.classList.remove('active');
    setTimeout(() => {
        panel.style.display = 'none';
    }, 300);
    
    detailPanelOpen = false;
    
    // Clear selection on map
    currentMarkers.forEach((marker, code) => {
        const site = appState.getSiteByCode(code);
        marker.setIcon(createMarkerIcon(site, false));
    });
}

/**
 * Generate simplified site details HTML for panel
 * @param {Object} site - Site object
 * @returns {string} HTML string
 */
function generateSiteDetailsHTML(site) {
    const lat = parseFloat(site.latitude);
    const lon = parseFloat(site.longitude);
    const mapsUrl = `https://www.google.com/maps?q=${lat},${lon}`;
    
    const eclipseColor = site.eclipse_visibility === 'visible' ? '#6f42c1' :
                        site.eclipse_visibility === 'not_visible' ? '#dc3545' : '#ffc107';
    
    let cloudInfo = '';
    if (site.cloud_coverage && site.cloud_status === 'success') {
        const cloudPct = parseInt(site.cloud_coverage);
        const cloudEmoji = cloudPct >= 60 ? '☁️' : cloudPct >= 30 ? '⛅' : '☀️';
        cloudInfo = `
            <div style="margin: 0.5rem 0;">
                <strong>Cloud Coverage:</strong> ${cloudEmoji} ${cloudPct}%
            </div>
        `;
    }
    
    return `
        <h2 style="margin-bottom: 1rem;">${site.denominacion || site.code}</h2>
        
        <div style="margin-bottom: 1rem;">
            <div style="margin: 0.5rem 0;">
                <strong>Code:</strong> ${site.code}
            </div>
            <div style="margin: 0.5rem 0;">
                <strong>Tourist Value:</strong> ${site.valor_turistico}
            </div>
            <div style="margin: 0.5rem 0;">
                <strong>Eclipse Visibility:</strong> 
                <span style="color: ${eclipseColor}; font-weight: bold;">
                    ${site.eclipse_visibility === 'visible' ? '🌑 Visible' :
                      site.eclipse_visibility === 'not_visible' ? '🌑 Not Visible' :
                      '🌑 ' + site.eclipse_visibility}
                </span>
            </div>
            ${cloudInfo}
        </div>
        
        <div style="margin-bottom: 1rem;">
            <strong>Coordinates:</strong><br>
            ${lat.toFixed(6)}, ${lon.toFixed(6)}
        </div>
        
        <div style="display: flex; flex-direction: column; gap: 0.5rem;">
            <a href="${mapsUrl}" target="_blank" style="padding: 0.5rem; background: #007bff; color: white; text-decoration: none; border-radius: 4px; text-align: center;">
                📍 Open in Google Maps
            </a>
            <button onclick="window.viewFullSiteDetails('${site.code}')" style="padding: 0.5rem; background: #28a745; color: white; border: none; border-radius: 4px; cursor: pointer;">
                📄 View Full Details
            </button>
        </div>
    `;
}

/**
 * Update map view with new filtered sites
 * @param {Array} sites - Array of site objects
 */
export function updateMapView(sites) {
    if (!mapViewInstance) {
        initializeMapView(sites);
        return;
    }
    
    // Clear existing markers
    if (markerClusterGroup) {
        markerClusterGroup.clearLayers();
    }
    currentMarkers.clear();
    
    // Add new markers
    const bounds = L.latLngBounds();
    
    sites.forEach(site => {
        const lat = parseFloat(site.latitude);
        const lon = parseFloat(site.longitude);
        
        if (isNaN(lat) || isNaN(lon)) return;
        
        bounds.extend([lat, lon]);
        
        const marker = L.marker([lat, lon], {
            icon: createMarkerIcon(site)
        });
        
        marker.bindPopup(createMarkerPopup(site));
        marker.on('click', () => {
            selectSiteOnMap(site.code);
        });
        
        markerClusterGroup.addLayer(marker);
        currentMarkers.set(site.code, marker);
    });
    
    // Fit bounds if we have sites
    if (sites.length > 0) {
        mapViewInstance.fitBounds(bounds, { padding: [50, 50] });
    }
}

/**
 * Cleanup map view
 */
export function cleanupMapView() {
    if (mapViewInstance) {
        mapViewInstance.remove();
        mapViewInstance = null;
    }
    markerClusterGroup = null;
    currentMarkers.clear();
    closeSiteDetailsPanel();
}

// Global functions for onclick handlers
window.showSiteDetailsInPanel = (siteCode) => {
    selectSiteOnMap(siteCode);
};

window.viewFullSiteDetails = (siteCode) => {
    const site = appState.getSiteByCode(siteCode);
    if (site) {
        // Switch to list view and show full details
        document.getElementById('listViewBtn').click();
        setTimeout(() => {
            displaySiteDetails(site);
        }, 100);
    }
};

// Made with Bob