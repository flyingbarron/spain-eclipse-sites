/**
 * Site Details Module
 * Handles rendering of detailed site information with tabs
 */

import { appState } from './state.js';
import { decimalToDMS } from './utils.js';
import { googleMapsApiKey } from './config.js';
import { loadSiteImages } from './image-loader.js';
import { initializeSingleSiteMap, updateMapWithMultipleSites } from './map-handler.js';

/**
 * Generate external URLs for a site
 * @param {Object} site - Site object
 * @returns {Object} Object with various external URLs
 */
function generateSiteUrls(site) {
    const lat = parseFloat(site.latitude);
    const lon = parseFloat(site.longitude);
    
    // Google Maps
    const mapsUrl = `https://www.google.com/maps?q=${lat},${lon}`;
    
    // Shademap
    const coordsBase64 = btoa(`${lat}, ${lon}`);
    const shademapUrl = `https://shademap.app/@${lat},${lon},17z,1786559455614t,0b,0p,0m!1786512158844!1786563246912,${coordsBase64}!${lat}!${lon}`;
    
    // IGN Eclipse viewer (Web Mercator projection)
    const x = lon * 20037508.34 / 180;
    const y = Math.log(Math.tan((90 + lat) * Math.PI / 360)) / (Math.PI / 180);
    const yMercator = y * 20037508.34 / 180;
    const eclipseUrl = `https://visualizadores.ign.es/eclipses/2026?center=${x},${yMercator}&zoom=16&srs=EPSG:3857`;
    
    // EclipseFan
    const eclipseFanUrl = `https://www.eclipsefan.org/?lat=${lat}&lng=${lon}&zoom=6&oz=5&lang=en`;
    
    // Xavier Jubier Eclipse Map
    const xavierJubierUrl = `http://xjubier.free.fr/en/site_pages/solar_eclipses/TSE_2026_GoogleMapFull.html?Lat=${lat}&Lng=${lon}&Zoom=8&LC=1`;
    
    // Google Maps Static API
    const googleMapsStaticUrl = googleMapsApiKey ?
        `https://maps.googleapis.com/maps/api/staticmap?center=${lat},${lon}&zoom=15&size=400x200&maptype=satellite&markers=color:red%7C${lat},${lon}&key=${googleMapsApiKey}` :
        null;
    
    return {
        maps: mapsUrl,
        shademap: shademapUrl,
        eclipse: eclipseUrl,
        eclipseFan: eclipseFanUrl,
        xavierJubier: xavierJubierUrl,
        googleStatic: googleMapsStaticUrl,
        cloud: site.cloud_url
    };
}

/**
 * Render site header with external links and thumbnails
 * @param {Object} site - Site object
 * @param {Object} urls - External URLs object
 * @returns {string} HTML string
 */
function renderSiteHeader(site, urls) {
    // Cloud button if available
    let cloudButton = '';
    if (urls.cloud && site.cloud_status === 'success') {
        cloudButton = `<a href="${urls.cloud}" target="_blank" class="link-button cloud">🕐 timeanddate.com</a>`;
    }
    
    return `
        <div class="detail-header">
            <h2>${site.denominacion || site.code}</h2>
            <div style="display: flex; align-items: flex-start; gap: 0.5rem; flex-wrap: wrap;">
                <a href="${site.url}" target="_blank" class="link-button">🪨 View on IGME Website</a>
                
                <div style="display: flex; flex-direction: column; align-items: center; gap: 0.25rem;">
                    <a href="${urls.maps}" target="_blank" class="link-button maps">📍 Open in Google Maps</a>
                    ${urls.googleStatic ? `
                        <div style="position: relative; display: inline-block;">
                            <img src="${urls.googleStatic}"
                                 alt="Google Maps location for ${site.code}"
                                 class="eclipse-profile-thumbnail maps-thumbnail"
                                 onclick="window.open('${urls.maps}', '_blank')"
                                 onerror="this.style.display='none'"
                                 title="Click to open in Google Maps">
                        </div>
                    ` : ''}
                </div>
                
                <div style="display: flex; flex-direction: column; align-items: center; gap: 0.25rem;">
                    <a href="${urls.shademap}" target="_blank" class="link-button shademap">🌄 View on Shademap</a>
                    <div style="position: relative; display: inline-block;">
                        <img src="data/scrape/shademap_snapshots/${site.code}_shademap.jpg"
                             alt="Shademap visualization for ${site.code}"
                             class="eclipse-profile-thumbnail shademap-thumbnail"
                             onclick="window.open('data/scrape/shademap_snapshots/${site.code}_shademap.jpg', '_blank')"
                             onerror="this.parentElement.style.display='none'"
                             title="Hover to preview, click to open full-size">
                        <div class="eclipse-profile-overlay">
                            <img src="data/scrape/shademap_snapshots/${site.code}_shademap.jpg"
                                 alt="Shademap visualization for ${site.code}">
                        </div>
                    </div>
                </div>
                
                ${cloudButton}
                
                <a href="${urls.xavierJubier}" target="_blank" class="link-button xavier">🗺️ Xavier Jubier Eclipse Map</a>
                
                <div style="display: flex; flex-direction: column; align-items: center; gap: 0.25rem;">
                    <a href="${urls.eclipseFan}" target="_blank" class="link-button eclipsefan">🌒 EclipseFan.org</a>
                    <div style="position: relative; display: inline-block;">
                        <img src="data/scrape/eclipsefan_horizons/${site.code}_horizon.png"
                             alt="Horizon profile for ${site.code}"
                             class="eclipse-profile-thumbnail"
                             onclick="window.open('data/scrape/eclipsefan_horizons/${site.code}_horizon.png', '_blank')"
                             onerror="this.parentElement.style.display='none'"
                             title="Hover to preview, click to open full-size">
                        <div class="eclipse-profile-overlay">
                            <img src="data/scrape/eclipsefan_horizons/${site.code}_horizon.png"
                                 alt="Horizon profile for ${site.code}">
                        </div>
                    </div>
                </div>
                
                <div style="display: flex; flex-direction: column; align-items: center; gap: 0.25rem;">
                    <a href="${urls.eclipse}" target="_blank" class="link-button eclipse">🌑 Eclipse 2026 View</a>
                    <div style="position: relative; display: inline-block;">
                        <img src="data/scrape/ign_profiles/${site.code}_profile.png"
                             alt="Eclipse visibility profile for ${site.code}"
                             class="eclipse-profile-thumbnail"
                             onclick="window.open('data/scrape/ign_profiles/${site.code}_profile.png', '_blank')"
                             onerror="this.parentElement.style.display='none'"
                             title="Hover to preview, click to open full-size">
                        <div class="eclipse-profile-overlay">
                            <img src="data/scrape/ign_profiles/${site.code}_profile.png"
                                 alt="Eclipse visibility profile for ${site.code}">
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
}

/**
 * Render details tab content
 * @param {Object} site - Site object
 * @returns {string} HTML string
 */
function renderDetailsTab(site) {
    const lat = parseFloat(site.latitude);
    const lon = parseFloat(site.longitude);
    const latDMS = decimalToDMS(lat, true);
    const lonDMS = decimalToDMS(lon, false);
    
    // Eclipse visibility color
    let eclipseColor = '#ffc107';
    if (site.eclipse_visibility === 'visible') {
        eclipseColor = '#6f42c1';
    } else if (site.eclipse_visibility === 'not_visible') {
        eclipseColor = '#dc3545';
    }
    
    // Cloud coverage display
    let cloudInfo = '';
    if (site.cloud_coverage && site.cloud_status === 'success') {
        const cloudPct = parseInt(site.cloud_coverage);
        let cloudEmoji = '☀️';
        if (cloudPct >= 60) cloudEmoji = '☁️';
        else if (cloudPct >= 30) cloudEmoji = '⛅';
        
        cloudInfo = `
            <div class="info-item">
                <div class="info-label">Cloud Coverage (August avg)</div>
                <div class="info-value">${cloudEmoji} ${cloudPct}%</div>
            </div>
        `;
    }
    
    return `
        <div class="detail-info">
            <div class="info-item">
                <div class="info-label">Code</div>
                <div class="info-value">${site.code}</div>
            </div>
            <div class="info-item">
                <div class="info-label">Tourist Value</div>
                <div class="info-value">${site.valor_turistico}</div>
            </div>
            <div class="info-item">
                <div class="info-label">Privacy</div>
                <div class="info-value">${site.confidencialidad}</div>
            </div>
            ${site.route_difficulty && site.route_difficulty !== 'N/A' ? `
                <div class="info-item">
                    <div class="info-label">Route Difficulty</div>
                    <div class="info-value">${site.route_difficulty}</div>
                </div>
            ` : ''}
            <div class="info-item">
                <div class="info-label">Coordinates</div>
                <div class="info-value">
                    <div style="margin-bottom: 0.25rem;">
                        <strong>Decimal:</strong> ${lat.toFixed(6)}, ${lon.toFixed(6)}
                    </div>
                    <div>
                        <strong>DMS:</strong> ${latDMS}, ${lonDMS}
                    </div>
                </div>
            </div>
            ${site.eclipse_visibility ? `
                <div class="info-item">
                    <div class="info-label">Eclipse 2026 Visibility</div>
                    <div class="info-value" style="color: ${eclipseColor}">
                        ${site.eclipse_visibility === 'visible' ? '🌑 Visible' :
                          site.eclipse_visibility === 'not_visible' ? '🌑 Not Visible' :
                          '🌑 ' + site.eclipse_visibility}
                    </div>
                </div>
            ` : ''}
            ${cloudInfo}
        </div>
        
        <div class="images-section">
            <h3>📷 Images</h3>
            <div id="imagesContainer" class="images-grid">
                <div class="loading">Loading IGME images...</div>
            </div>
        </div>
    `;
}

/**
 * Render map tab content
 * @param {Object} site - Site object
 * @returns {string} HTML string
 */
function renderMapTab(site) {
    return `
        <div id="mapContainer" style="height: 600px; width: 100%;"></div>
        <div id="routeSummary" style="display: none; margin-top: 1rem;">
            <div style="background: white; padding: 1rem; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <div id="routeTotal" style="margin-bottom: 1rem;"></div>
                <div id="routeSegments"></div>
            </div>
        </div>
        <div id="routeDirections" style="display: none; margin-top: 1rem; background: white; padding: 1rem; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <h3 style="margin-top: 0;">Turn-by-turn Directions</h3>
            <div id="directionsContent"></div>
        </div>
        <div class="map-note">
            💡 Hold Ctrl (Cmd on Mac) and click multiple sites in the list to plan a route
        </div>
    `;
}

/**
 * Display full site details with tabs
 * @param {Object} site - Site object to display
 */
export function displaySiteDetails(site) {
    const content = document.getElementById('content');
    if (!content) return;
    
    const urls = generateSiteUrls(site);
    const activeTab = appState.activeTab;
    
    content.innerHTML = `
        <div class="site-details">
            ${renderSiteHeader(site, urls)}
            
            <div class="tabs">
                <button class="tab ${activeTab === 'details' ? 'active' : ''}" data-tab="details">📋 Details</button>
                <button class="tab ${activeTab === 'map' ? 'active' : ''}" data-tab="map">🗺️ Map</button>
                ${activeTab === 'map' ? '<span class="map-tip">💡 Hold Ctrl (Cmd on Mac) and click sites to select multiple</span>' : ''}
            </div>
            
            <div id="detailsTab" class="tab-content ${activeTab === 'details' ? 'active' : ''}">
                ${renderDetailsTab(site)}
            </div>
            
            <div id="mapTab" class="tab-content ${activeTab === 'map' ? 'active' : ''}">
                ${renderMapTab(site)}
            </div>
        </div>
    `;
    
    // Setup tab switching
    setupTabListeners();
    
    // Load images if on details tab
    if (activeTab === 'details') {
        loadSiteImages(site);
    }
    
    // Initialize map if on map tab
    if (activeTab === 'map') {
        // Check if we have multiple selected sites for routing
        if (appState.selectedSites.length > 1) {
            updateMapWithMultipleSites();
        } else {
            initializeSingleSiteMap(site);
        }
    }
}

/**
 * Setup tab switching listeners
 */
function setupTabListeners() {
    document.querySelectorAll('.tab').forEach(tab => {
        tab.addEventListener('click', (e) => {
            const tabName = e.target.dataset.tab;
            if (tabName) {
                switchTab(tabName);
            }
        });
    });
}

/**
 * Switch between tabs
 * @param {string} tabName - Name of tab to switch to ('details' or 'map')
 */
export function switchTab(tabName) {
    appState.setActiveTab(tabName);
    
    // Update tab buttons
    document.querySelectorAll('.tab').forEach(tab => {
        tab.classList.remove('active');
        if (tab.dataset.tab === tabName) {
            tab.classList.add('active');
        }
    });
    
    // Update tab content
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    
    if (tabName === 'details') {
        const detailsTab = document.getElementById('detailsTab');
        if (detailsTab) {
            detailsTab.classList.add('active');
            // Load images if not already loaded
            if (appState.currentSite) {
                loadSiteImages(appState.currentSite);
            }
        }
    } else if (tabName === 'map') {
        const mapTab = document.getElementById('mapTab');
        if (mapTab) {
            mapTab.classList.add('active');
            // Initialize map
            if (appState.currentSite) {
                if (appState.selectedSites.length > 1) {
                    updateMapWithMultipleSites();
                } else {
                    initializeSingleSiteMap(appState.currentSite);
                }
            }
        }
    }
    
    // Update map tip visibility
    const tabsContainer = document.querySelector('.tabs');
    let existingTip = tabsContainer?.querySelector('.map-tip');
    
    if (tabName === 'map' && !existingTip && tabsContainer) {
        const tip = document.createElement('span');
        tip.className = 'map-tip';
        tip.textContent = '💡 Hold Ctrl (Cmd on Mac) and click multiple sites in the list to plan a route';
        tabsContainer.appendChild(tip);
    } else if (tabName !== 'map' && existingTip) {
        existingTip.remove();
    }
}

// Made with Bob
