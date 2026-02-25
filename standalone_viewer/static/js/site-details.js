/**
 * Site Details Module - Standalone Version
 * Handles rendering of detailed site information with tabs
 */

import { appState } from './state.js';
import { decimalToDMS } from './utils.js';
import { googleMapsApiKey } from './config.js';
import { loadSiteImages } from './image-loader.js';
import { initializeSingleSiteMap, updateMapWithMultipleSites } from './map-handler.js';
import { initialize3DMap, cleanup3DMap } from './terrain-3d.js';

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
    
    // Dark Sky Sites
    const darkSkySitesUrl = `https://www.darkskysites.com/?lat=${lat}&lng=${lon}&zoom=8`;
    
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
        darkSkySites: darkSkySitesUrl,
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
    
    // Check if IGME URL is valid
    const hasValidIgmeUrl = site.url && site.url !== 'N/A' && site.url.trim() !== '';
    const igmeButtonClass = hasValidIgmeUrl ? 'link-button' : 'link-button inactive';
    const igmeButtonHref = hasValidIgmeUrl ? site.url : '#';
    const igmeButtonTitle = hasValidIgmeUrl ? '' : ' title="No IGME website available for this site"';
    
    return `
        <div class="detail-header">
            <h2>${site.denominacion || site.code}</h2>
            <div style="display: flex; align-items: flex-start; gap: 0.5rem; flex-wrap: wrap;">
                <!-- Left column: IGME, timeanddate, Xavier Jubier, Dark Sky Sites stacked vertically -->
                <div style="display: flex; flex-direction: column; gap: 0.25rem;">
                    <a href="${igmeButtonHref}" target="_blank" class="${igmeButtonClass}"${igmeButtonTitle}>🪨 View on IGME Website</a>
                    ${cloudButton}
                    <a href="${urls.xavierJubier}" target="_blank" class="link-button xavier">🗺️ Xavier Jubier Eclipse Map</a>
                    <a href="${urls.darkSkySites}" target="_blank" class="link-button darksky">🌌 Dark Sky Sites</a>
                </div>
                
                <!-- Right side: Buttons with previews -->
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
                        <img src="images/shademap_snapshots/${site.code}_shademap.jpg"
                             alt="Shademap visualization for ${site.code}"
                             class="eclipse-profile-thumbnail shademap-thumbnail"
                             onclick="window.open('images/shademap_snapshots/${site.code}_shademap.jpg', '_blank')"
                             onerror="this.parentElement.style.display='none'"
                             title="Hover to preview, click to open full-size">
                        <div class="eclipse-profile-overlay">
                            <img src="images/shademap_snapshots/${site.code}_shademap.jpg"
                                 alt="Shademap visualization for ${site.code}">
                        </div>
                    </div>
                </div>
                
                <div style="display: flex; flex-direction: column; align-items: center; gap: 0.25rem;">
                    <a href="${urls.eclipseFan}" target="_blank" class="link-button eclipsefan">🌒 EclipseFan.org</a>
                    <div style="position: relative; display: inline-block;">
                        <img src="images/eclipsefan_horizons/${site.code}_horizon.png"
                             alt="Horizon profile for ${site.code}"
                             class="eclipse-profile-thumbnail"
                             onclick="window.open('images/eclipsefan_horizons/${site.code}_horizon.png', '_blank')"
                             onerror="this.parentElement.style.display='none'"
                             title="Hover to preview, click to open full-size">
                        <div class="eclipse-profile-overlay">
                            <img src="images/eclipsefan_horizons/${site.code}_horizon.png"
                                 alt="Horizon profile for ${site.code}">
                        </div>
                    </div>
                </div>
                
                <div style="display: flex; flex-direction: column; align-items: center; gap: 0.25rem;">
                    <a href="${urls.eclipse}" target="_blank" class="link-button eclipse">🌑 Eclipse 2026 View</a>
                    <div style="position: relative; display: inline-block;">
                        <img src="images/ign_profiles/${site.code}_profile.png"
                             alt="Eclipse visibility profile for ${site.code}"
                             class="eclipse-profile-thumbnail"
                             onclick="window.open('images/ign_profiles/${site.code}_profile.png', '_blank')"
                             onerror="this.parentElement.style.display='none'"
                             title="Hover to preview, click to open full-size">
                        <div class="eclipse-profile-overlay">
                            <img src="images/ign_profiles/${site.code}_profile.png"
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
    
    // Bortle scale display
    let bortleInfo = '';
    if (site.bortle_scale && site.bortle_status === 'success') {
        const bortle = parseInt(site.bortle_scale);
        let bortleEmoji = '🌌';
        let bortleDesc = 'Excellent dark-sky site';
        
        if (bortle <= 2) {
            bortleEmoji = '🌌';
            bortleDesc = bortle === 1 ? 'Excellent dark-sky site' : 'Typical truly dark site';
        } else if (bortle <= 4) {
            bortleEmoji = '🌃';
            bortleDesc = bortle === 3 ? 'Rural sky' : 'Rural/suburban transition';
        } else if (bortle <= 6) {
            bortleEmoji = '🌆';
            bortleDesc = bortle === 5 ? 'Suburban sky' : 'Bright suburban sky';
        } else {
            bortleEmoji = '🏙️';
            bortleDesc = bortle === 7 ? 'Suburban/urban transition' : bortle === 8 ? 'City sky' : 'Inner-city sky';
        }
        
        bortleInfo = `
            <div class="info-item">
                <div class="info-label">Bortle Scale (Light Pollution)</div>
                <div class="info-value">${bortleEmoji} Class ${bortle} - ${bortleDesc}</div>
            </div>
        `;
    }
    
    // Dark Sky Sites data display
    let darkSkyInfo = '';
    if (site.darksky_sqm || site.darksky_bortle || site.darksky_darkness) {
        const sqm = site.darksky_sqm ? parseFloat(site.darksky_sqm).toFixed(2) : 'N/A';
        const bortle = site.darksky_bortle || 'N/A';
        const darkness = site.darksky_darkness ? parseFloat(site.darksky_darkness).toFixed(1) + '%' : 'N/A';
        
        darkSkyInfo = `
            <div class="info-item">
                <div class="info-label">Dark Sky Sites Data</div>
                <div class="info-value">
                    <div style="margin-bottom: 0.25rem;">
                        <strong>SQM:</strong> ${sqm} ${sqm !== 'N/A' ? '(mag/arcsec²)' : ''}
                    </div>
                    <div style="margin-bottom: 0.25rem;">
                        <strong>Bortle:</strong> ${bortle}
                    </div>
                    <div>
                        <strong>Darkness:</strong> ${darkness}
                    </div>
                </div>
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
            ${bortleInfo}
            ${darkSkyInfo}
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
        <div style="position: relative;">
            <div style="position: absolute; top: 10px; right: 10px; z-index: 1000; display: flex; gap: 0.5rem;">
                <button id="toggle2DBtn" class="map-toggle-btn active">2D Map</button>
                <button id="toggle3DBtn" class="map-toggle-btn">3D Terrain</button>
            </div>
            <div id="map" style="height: 600px; width: 100%;"></div>
            <div id="map3d" style="height: 600px; width: 100%; display: none;"></div>
        </div>
    `;
}

/**
 * Render route tab content
 * @returns {string} HTML string
 */
function renderRouteTab() {
    const selectedSites = appState.selectedSites;
    
    if (selectedSites.length === 0) {
        return `
            <div class="route-info">
                <p>Hold Ctrl (Cmd on Mac) and click sites in the list to add them to your route.</p>
                <p>You can then drag sites in the route summary below to reorder them.</p>
            </div>
        `;
    }
    
    return `
        <div class="route-info">
            <h3>Selected Sites (${selectedSites.length})</h3>
            <p>Drag sites to reorder your route:</p>
            <ul id="routeSitesList" class="route-sites-list">
                ${selectedSites.map((code, index) => {
                    const site = appState.getSiteByCode(code);
                    return `
                        <li class="route-site-item" data-code="${code}" draggable="true">
                            <span class="route-site-number">${index + 1}</span>
                            <span class="route-site-name">${site.denominacion || code}</span>
                            <button class="route-site-remove" data-code="${code}">×</button>
                        </li>
                    `;
                }).join('')}
            </ul>
            <div class="route-actions">
                <button id="exportGoogleMapsBtn" class="action-btn">📍 Open in Google Maps</button>
                <button id="exportKMLBtn" class="action-btn">📄 Export as KML</button>
                <button id="clearRouteBtn" class="action-btn danger">🗑️ Clear Route</button>
            </div>
        </div>
        <div id="routeMap" style="height: 400px; width: 100%; margin-top: 1rem;"></div>
    `;
}

/**
 * Display site details with tabs
 * @param {Object} site - Site object
 */
export function displaySiteDetails(site) {
    const content = document.getElementById('content');
    if (!content) return;
    
    const urls = generateSiteUrls(site);
    
    content.innerHTML = `
        ${renderSiteHeader(site, urls)}
        
        <div class="tabs">
            <button class="tab-btn active" data-tab="details">📋 Details</button>
            <button class="tab-btn" data-tab="map">🗺️ Map</button>
            <button class="tab-btn" data-tab="route">🚗 Route</button>
        </div>
        
        <div class="tab-content active" data-tab="details">
            ${renderDetailsTab(site)}
        </div>
        
        <div class="tab-content" data-tab="map">
            ${renderMapTab(site)}
        </div>
        
        <div class="tab-content" data-tab="route">
            ${renderRouteTab()}
        </div>
    `;
    
    // Setup tab switching
    setupTabSwitching();
    
    // Setup map toggle buttons
    setupMapToggleButtons();
    
    // Load images
    loadSiteImages(site);
    
    // Initialize map
    initializeSingleSiteMap(site);
    
    // Setup route functionality if on route tab
    setupRouteFunctionality();
}

/**
 * Setup tab switching functionality
 */
function setupTabSwitching() {
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const tabName = btn.dataset.tab;
            switchTab(tabName);
        });
    });
}

/**
 * Switch to a specific tab
 * @param {string} tabName - Name of the tab to switch to
 */
export function switchTab(tabName) {
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabBtns.forEach(btn => {
        if (btn.dataset.tab === tabName) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });
    
    tabContents.forEach(content => {
        if (content.dataset.tab === tabName) {
            content.classList.add('active');
        } else {
            content.classList.remove('active');
        }
    });
    
    // Handle tab-specific initialization
    if (tabName === 'map') {
        // Reinitialize map if needed
        const currentSite = appState.currentSite;
        if (currentSite) {
            setTimeout(() => {
                if (appState.selectedSites.length > 1) {
                    updateMapWithMultipleSites();
                } else {
                    initializeSingleSiteMap(currentSite);
                }
            }, 100);
        }
    } else if (tabName === 'route') {
        // Update route display
        const routeContent = document.querySelector('.tab-content[data-tab="route"]');
        if (routeContent) {
            routeContent.innerHTML = renderRouteTab();
            setupRouteFunctionality();
            if (appState.selectedSites.length > 1) {
                updateMapWithMultipleSites();
            }
        }
    }
}

/**
 * Setup map toggle buttons (2D/3D)
 */
function setupMapToggleButtons() {
    const toggle2DBtn = document.getElementById('toggle2DBtn');
    const toggle3DBtn = document.getElementById('toggle3DBtn');
    const map2D = document.getElementById('map');
    const map3D = document.getElementById('map3d');
    
    if (!toggle2DBtn || !toggle3DBtn || !map2D || !map3D) return;
    
    toggle2DBtn.addEventListener('click', () => {
        toggle2DBtn.classList.add('active');
        toggle3DBtn.classList.remove('active');
        map2D.style.display = 'block';
        map3D.style.display = 'none';
        cleanup3DMap();
        
        // Reinitialize 2D map
        const currentSite = appState.currentSite;
        if (currentSite) {
            setTimeout(() => initializeSingleSiteMap(currentSite), 100);
        }
    });
    
    toggle3DBtn.addEventListener('click', () => {
        toggle3DBtn.classList.add('active');
        toggle2DBtn.classList.remove('active');
        map2D.style.display = 'none';
        map3D.style.display = 'block';
        
        // Initialize 3D map
        const currentSite = appState.currentSite;
        if (currentSite) {
            setTimeout(() => initialize3DMap(currentSite), 100);
        }
    });
}

/**
 * Setup route functionality (drag and drop, export, etc.)
 */
function setupRouteFunctionality() {
    const routeList = document.getElementById('routeSitesList');
    if (routeList) {
        setupRouteDragAndDrop(routeList);
    }
    
    // Export buttons
    const exportGoogleMapsBtn = document.getElementById('exportGoogleMapsBtn');
    const exportKMLBtn = document.getElementById('exportKMLBtn');
    const clearRouteBtn = document.getElementById('clearRouteBtn');
    
    if (exportGoogleMapsBtn) {
        exportGoogleMapsBtn.addEventListener('click', exportToGoogleMaps);
    }
    
    if (exportKMLBtn) {
        exportKMLBtn.addEventListener('click', exportToKML);
    }
    
    if (clearRouteBtn) {
        clearRouteBtn.addEventListener('click', () => {
            appState.selectedSites = [];
            switchTab('route');
        });
    }
    
    // Remove buttons
    document.querySelectorAll('.route-site-remove').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const code = e.target.dataset.code;
            appState.toggleSiteSelection(code);
            switchTab('route');
        });
    });
}

/**
 * Setup drag and drop for route reordering
 * @param {HTMLElement} list - Route list element
 */
function setupRouteDragAndDrop(list) {
    let draggedItem = null;
    
    list.querySelectorAll('.route-site-item').forEach(item => {
        item.addEventListener('dragstart', (e) => {
            draggedItem = item;
            e.dataTransfer.effectAllowed = 'move';
            item.classList.add('dragging');
        });
        
        item.addEventListener('dragend', () => {
            item.classList.remove('dragging');
        });
        
        item.addEventListener('dragover', (e) => {
            e.preventDefault();
            const afterElement = getDragAfterElement(list, e.clientY);
            if (afterElement == null) {
                list.appendChild(draggedItem);
            } else {
                list.insertBefore(draggedItem, afterElement);
            }
        });
    });
    
    list.addEventListener('drop', (e) => {
        e.preventDefault();
        // Update appState with new order
        const newOrder = Array.from(list.querySelectorAll('.route-site-item'))
            .map(item => item.dataset.code);
        appState.selectedSites = newOrder;
        updateMapWithMultipleSites();
    });
}

/**
 * Get element after drag position
 * @param {HTMLElement} container - Container element
 * @param {number} y - Y coordinate
 * @returns {HTMLElement|null} Element after position
 */
function getDragAfterElement(container, y) {
    const draggableElements = [...container.querySelectorAll('.route-site-item:not(.dragging)')];
    
    return draggableElements.reduce((closest, child) => {
        const box = child.getBoundingClientRect();
        const offset = y - box.top - box.height / 2;
        
        if (offset < 0 && offset > closest.offset) {
            return { offset: offset, element: child };
        } else {
            return closest;
        }
    }, { offset: Number.NEGATIVE_INFINITY }).element;
}

/**
 * Export route to Google Maps
 */
function exportToGoogleMaps() {
    const sites = appState.selectedSites.map(code => appState.getSiteByCode(code));
    if (sites.length === 0) return;
    
    // Build Google Maps URL with waypoints
    const origin = `${sites[0].latitude},${sites[0].longitude}`;
    const destination = `${sites[sites.length - 1].latitude},${sites[sites.length - 1].longitude}`;
    
    let url = `https://www.google.com/maps/dir/${origin}`;
    
    // Add waypoints (middle sites)
    for (let i = 1; i < sites.length - 1; i++) {
        url += `/${sites[i].latitude},${sites[i].longitude}`;
    }
    
    url += `/${destination}`;
    
    window.open(url, '_blank');
}

/**
 * Export route to KML file
 */
function exportToKML() {
    const sites = appState.selectedSites.map(code => appState.getSiteByCode(code));
    if (sites.length === 0) return;
    
    // Generate KML content
    let kml = `<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>Eclipse Sites Route</name>
    <description>Selected eclipse viewing sites</description>
`;
    
    sites.forEach((site, index) => {
        kml += `
    <Placemark>
      <name>${index + 1}. ${site.denominacion || site.code}</name>
      <description>${site.code}</description>
      <Point>
        <coordinates>${site.longitude},${site.latitude},0</coordinates>
      </Point>
    </Placemark>`;
    });
    
    kml += `
  </Document>
</kml>`;
    
    // Download KML file
    const blob = new Blob([kml], { type: 'application/vnd.google-earth.kml+xml' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'eclipse_sites_route.kml';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

// Made with Bob
