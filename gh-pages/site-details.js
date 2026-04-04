/**
 * Site Details Module - GitHub Pages Standalone Version
 * Handles rendering of detailed site information with tabs
 */

import { appState } from '../static/js/state.js';
import { decimalToDMS } from '../static/js/utils.js';
import { CONFIG } from './config.js';
import { loadSiteImages } from './image-loader.js';
import { initializeSingleSiteMap, updateMapWithMultipleSites } from './map-handler.js';
import { initialize3DMap, cleanup3DMap } from './terrain-3d.js';
import { notesManager } from '../static/js/notes-manager.js';

const ASSET_PATHS = {
    horizons: 'data/horizons',
    shademap: 'data/scrape/shademap_snapshots',
    eclipsefan: 'data/scrape/eclipsefan_horizons',
    ignProfiles: 'data/scrape/ign_profiles',
};

const HEADER_COLUMN_STYLE = 'display: flex; flex-direction: column; align-items: center; gap: 0.25rem;';
const HEADER_STACK_STYLE = 'display: flex; flex-direction: column; gap: 0.25rem;';
const THUMBNAIL_WRAPPER_STYLE = 'position: relative; display: inline-block;';

/**
 * Cache for horizon files mapping
 */
let horizonFilesCache = null;

/**
 * Fetch available horizon files from server
 * Falls back to static JSON file for GitHub Pages
 * @returns {Promise<Object>} Map of site codes to filenames
 */
async function fetchHorizonFiles() {
    console.log('fetchHorizonFiles called, cache status:', horizonFilesCache ? 'cached' : 'not cached');
    
    if (horizonFilesCache) {
        console.log('Returning cached horizon files:', Object.keys(horizonFilesCache).length, 'files');
        return horizonFilesCache;
    }
    
    // Skip API endpoint on GitHub Pages - go straight to static JSON
    const isGitHubPages = window.location.hostname.includes('github.io');
    
    if (!isGitHubPages) {
        try {
            // Try API endpoint first (for local development with Python server)
            console.log('Trying API endpoint /api/horizon-files');
            const response = await fetch('/api/horizon-files');
            if (response.ok) {
                horizonFilesCache = await response.json();
                console.log('Loaded from API:', Object.keys(horizonFilesCache).length, 'files');
                return horizonFilesCache;
            }
            console.log('API endpoint not available, status:', response.status);
        } catch (error) {
            console.log('API not available, trying static JSON file. Error:', error.message);
        }
    } else {
        console.log('GitHub Pages detected, skipping API endpoint');
    }
    
    try {
        // Fall back to static JSON file for GitHub Pages
        // Use relative path that works with GitHub Pages subdirectory
        const basePath = window.location.pathname.substring(0, window.location.pathname.lastIndexOf('/') + 1);
        const jsonUrl = basePath + 'data/horizon_files.json';
        console.log('Trying to load horizon files from:', jsonUrl);
        const response = await fetch(jsonUrl);
        console.log('Fetch response status:', response.status, 'OK:', response.ok);
        if (response.ok) {
            const data = await response.json();
            horizonFilesCache = data;
            console.log(`✓ Loaded ${Object.keys(horizonFilesCache).length} horizon files from static JSON`);
            console.log('Sample entries:', Object.entries(horizonFilesCache).slice(0, 3));
            return horizonFilesCache;
        } else {
            console.warn('Failed to load horizon files, status:', response.status);
        }
    } catch (error) {
        console.error('Could not load horizon files:', error);
    }
    
    // Last resort: empty cache
    console.warn('Using empty horizon files cache');
    horizonFilesCache = {};
    return horizonFilesCache;
}

/**
 * Get horizon filename for a site code
 * @param {string} code - Site code
 * @returns {string|null} Horizon filename or null if not available
 */
function getHorizonFilename(code) {
    // This will be populated by fetchHorizonFiles
    if (horizonFilesCache && horizonFilesCache[code.toUpperCase()]) {
        return horizonFilesCache[code.toUpperCase()];
    }
    return null;
}

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
    const googleMapsStaticUrl = CONFIG.MAPS.GOOGLE_API_KEY ?
        `https://maps.googleapis.com/maps/api/staticmap?center=${lat},${lon}&zoom=15&size=400x200&maptype=satellite&markers=color:red%7C${lat},${lon}&key=${CONFIG.MAPS.GOOGLE_API_KEY}` :
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

function buildAssetUrl(basePath, filename) {
    // Get the base URL path for GitHub Pages compatibility
    const baseUrlPath = window.location.pathname.substring(0, window.location.pathname.lastIndexOf('/') + 1);
    return `${baseUrlPath}${basePath}/${filename}`;
}

function renderHeaderPreview({ buttonHtml, imageUrl, alt, extraClass = '', title }) {
    return `
        <div style="${HEADER_COLUMN_STYLE}">
            ${buttonHtml}
            <div style="${THUMBNAIL_WRAPPER_STYLE}">
                <img src="${imageUrl}"
                     alt="${alt}"
                     class="eclipse-profile-thumbnail ${extraClass}".trim()
                     onclick="window.open('${imageUrl}', '_blank')"
                     onerror="this.parentElement.style.display='none'"
                     title="${title}">
                <div class="eclipse-profile-overlay">
                    <img src="${imageUrl}" alt="${alt}">
                </div>
            </div>
        </div>
    `;
}

function renderSimplePreview({ linkUrl, buttonClass, buttonLabel, imageUrl, alt, extraClass = '', title }) {
    return renderHeaderPreview({
        buttonHtml: `<a href="${linkUrl}" target="_blank" class="${buttonClass}">${buttonLabel}</a>`,
        imageUrl,
        alt,
        extraClass,
        title,
    });
}

function renderMapsPreview(site, urls) {
    if (!urls.googleStatic) {
        return '';
    }

    return `
        <div style="${HEADER_COLUMN_STYLE}">
            <a href="${urls.maps}" target="_blank" class="link-button maps">📍 Open in Google Maps</a>
            <div style="${THUMBNAIL_WRAPPER_STYLE}">
                <img src="${urls.googleStatic}"
                     alt="Google Maps location for ${site.code}"
                     class="eclipse-profile-thumbnail maps-thumbnail"
                     onclick="window.open('${urls.maps}', '_blank')"
                     onerror="this.style.display='none'"
                     title="Click to open in Google Maps">
            </div>
        </div>
    `;
}

function renderHorizonPreview(site, horizonFile) {
    if (!horizonFile) {
        return '';
    }

    const imageUrl = buildAssetUrl(ASSET_PATHS.horizons, horizonFile);
    return renderHeaderPreview({
        buttonHtml: '<span class="link-button" style="background: #17a2b8; cursor: default;">🌄 Horizon Profile</span>',
        imageUrl,
        alt: `Horizon profile for ${site.code}`,
        extraClass: 'horizon-thumbnail',
        title: 'Hover to preview full size, click to open in new tab',
    });
}

/**
 * Render site header with external links and thumbnails
 * @param {Object} site - Site object
 * @param {Object} urls - External URLs object
 * @returns {string} HTML string
 */
function renderSiteHeader(site, urls) {
    const cloudButton = urls.cloud && site.cloud_status === 'success'
        ? `<a href="${urls.cloud}" target="_blank" class="link-button cloud">🕐 timeanddate.com</a>`
        : '';

    const hasValidIgmeUrl = site.url && site.url !== 'N/A' && site.url.trim() !== '';
    const igmeButtonClass = hasValidIgmeUrl ? 'link-button' : 'link-button inactive';
    const igmeButtonHref = hasValidIgmeUrl ? site.url : '#';
    const igmeButtonTitle = hasValidIgmeUrl ? '' : ' title="No IGME website available for this site"';

    const horizonFile = getHorizonFilename(site.code);
    const shademapUrl = buildAssetUrl(ASSET_PATHS.shademap, `${site.code}_shademap.jpg`);
    const eclipsefanUrl = buildAssetUrl(ASSET_PATHS.eclipsefan, `${site.code}_horizon.png`);
    const ignProfileUrl = buildAssetUrl(ASSET_PATHS.ignProfiles, `${site.code}_profile.png`);

    return `
        <div class="detail-header">
            <h2>${site.denominacion || site.code}</h2>
            <div style="display: flex; align-items: flex-start; gap: 0.5rem; flex-wrap: wrap;">
                <div style="${HEADER_STACK_STYLE}">
                    <a href="${igmeButtonHref}" target="_blank" class="${igmeButtonClass}"${igmeButtonTitle}>🪨 View on IGME Website</a>
                    ${cloudButton}
                    <a href="${urls.xavierJubier}" target="_blank" class="link-button xavier">🗺️ Xavier Jubier Eclipse Map</a>
                    <a href="${urls.darkSkySites}" target="_blank" class="link-button darksky">🌌 Dark Sky Sites</a>
                </div>

                ${renderMapsPreview(site, urls)}
                ${renderHorizonPreview(site, horizonFile)}
                ${renderSimplePreview({
                    linkUrl: urls.shademap,
                    buttonClass: 'link-button shademap',
                    buttonLabel: '🌄 View on Shademap',
                    imageUrl: shademapUrl,
                    alt: `Shademap visualization for ${site.code}`,
                    extraClass: 'shademap-thumbnail',
                    title: 'Hover to preview, click to open full-size',
                })}
                ${renderSimplePreview({
                    linkUrl: urls.eclipseFan,
                    buttonClass: 'link-button eclipsefan',
                    buttonLabel: '🌒 EclipseFan.org',
                    imageUrl: eclipsefanUrl,
                    alt: `EclipseFan horizon profile for ${site.code}`,
                    title: 'Hover to preview, click to open full-size',
                })}
                ${renderSimplePreview({
                    linkUrl: urls.eclipse,
                    buttonClass: 'link-button eclipse',
                    buttonLabel: '🌑 Eclipse 2026 View',
                    imageUrl: ignProfileUrl,
                    alt: `Eclipse visibility profile for ${site.code}`,
                    title: 'Hover to preview, click to open full-size',
                })}
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
                <div class="info-label">Site Info</div>
                <div class="info-value">
                    <div style="margin-bottom: 0.25rem;">
                        <strong>Tourist Value:</strong> ${site.valor_turistico}
                    </div>
                    <div style="margin-bottom: 0.25rem;">
                        <strong>Privacy:</strong> ${site.confidencialidad}
                    </div>
                    ${site.route_difficulty && site.route_difficulty !== 'N/A' ? `
                        <div>
                            <strong>Route Difficulty:</strong> ${site.route_difficulty}
                        </div>
                    ` : ''}
                </div>
            </div>
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
            ${site.terrain_clearance ? `
                <div class="info-item">
                    <div class="info-label">Horizon Clearance</div>
                    <div class="info-value" style="color: ${parseFloat(site.terrain_clearance) >= 0 ? '#28a745' : '#dc3545'}">
                        🏔️ ${site.terrain_clearance}° ${parseFloat(site.terrain_clearance) >= 0 ? '(Clear)' : '(Blocked)'}
                    </div>
                </div>
            ` : ''}
            ${cloudInfo}
            ${darkSkyInfo}
        </div>
        
        <div class="notes-section">
            <div class="notes-header" id="notesHeader">
                <h3>📎 Attachments</h3>
                <button class="notes-toggle-btn" id="notesToggleBtn">▼</button>
            </div>
            <div class="notes-content" id="notesContent">
                ${site.brochure_url ? `
                    <div style="margin-bottom: 0.75rem; padding: 0.5rem; background: #f0e6ff; border-left: 3px solid #8e44ad; border-radius: 4px;">
                        <strong>📄 Site Brochure:</strong>
                        <a href="${site.brochure_url}" target="_blank" style="color: #8e44ad; text-decoration: underline;">${site.brochure_title || 'View PDF'}</a>
                    </div>
                ` : ''}
                <textarea id="siteNotes" class="site-notes-textarea" placeholder="Add your personal notes about this site...">${notesManager.getNote(site.code)}</textarea>
                <div class="notes-actions">
                    <button class="save-note-btn" id="saveNoteBtn">💾 Save Note</button>
                    <button class="delete-note-btn" id="deleteNoteBtn">🗑️ Delete Note</button>
                </div>
            </div>
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
export async function displaySiteDetails(site) {
    const content = document.getElementById('content');
    if (!content) return;
    
    // Fetch horizon files list
    await fetchHorizonFiles();
    
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
    
    // Setup notes functionality
    setupNotesFunctionality(site);
}

/**
 * Setup notes save/delete functionality
 * @param {Object} site - Site object
 */
function setupNotesFunctionality(site) {
    const saveBtn = document.getElementById('saveNoteBtn');
    const deleteBtn = document.getElementById('deleteNoteBtn');
    const notesTextarea = document.getElementById('siteNotes');
    const notesToggleBtn = document.getElementById('notesToggleBtn');
    const notesContent = document.getElementById('notesContent');
    const notesHeader = document.getElementById('notesHeader');
    
    // Check if site has a note or brochure
    const hasNote = notesManager.hasNote(site.code);
    const hasBrochure = site.brochure_url && site.brochure_url.trim() !== '';
    const hasContent = hasNote || hasBrochure;
    
    // Setup toggle functionality and set initial state
    if (notesToggleBtn && notesContent) {
        // Start closed if no note or brochure exists
        if (!hasContent) {
            notesContent.style.display = 'none';
            notesToggleBtn.textContent = '▶';
        }
        
        notesToggleBtn.addEventListener('click', () => {
            const isVisible = notesContent.style.display !== 'none';
            notesContent.style.display = isVisible ? 'none' : 'block';
            notesToggleBtn.textContent = isVisible ? '▶' : '▼';
        });
    }
    
    if (saveBtn && notesTextarea) {
        saveBtn.addEventListener('click', () => {
            const note = notesTextarea.value.trim();
            notesManager.setNote(site.code, note);
            
            // Show feedback
            saveBtn.textContent = '✅ Saved!';
            setTimeout(() => {
                saveBtn.textContent = '💾 Save Note';
            }, 2000);
            
            // Note: Site list refresh will happen on next filter/display
        });
    }
    
    if (deleteBtn && notesTextarea) {
        deleteBtn.addEventListener('click', () => {
            notesManager.deleteNote(site.code);
            notesTextarea.value = '';
            
            // Show feedback
            deleteBtn.textContent = '✅ Deleted!';
            setTimeout(() => {
                deleteBtn.textContent = '🗑️ Delete Note';
            }, 2000);
            
            // Note: Site list refresh will happen on next filter/display
        });
    }
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
