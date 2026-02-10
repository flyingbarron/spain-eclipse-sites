let sitesData = [];
let currentSite = null;
let currentImages = [];
let currentImageIndex = 0;
let activeTab = 'details'; // Track which tab is active
let selectedSites = []; // Track selected sites for multi-select (array to maintain order)
let returnToHotel = false; // Track if return to hotel is enabled
let currentRouteControl = null; // Track current route control
let routeSegments = []; // Store route segment data
let googleMapsApiKey = ''; // Google Maps API key loaded from server

// Load configuration from server
async function loadConfig() {
    try {
        const response = await fetch('/api/config');
        const config = await response.json();
        googleMapsApiKey = config.google_maps_api_key || '';
        console.log('Google Maps API key loaded:', googleMapsApiKey ? 'Yes' : 'No');
    } catch (error) {
        console.error('Error loading config:', error);
    }
}

// Convert decimal degrees to DMS (Degrees, Minutes, Seconds)
function decimalToDMS(decimal, isLat) {
    const absolute = Math.abs(decimal);
    const degrees = Math.floor(absolute);
    const minutesDecimal = (absolute - degrees) * 60;
    const minutes = Math.floor(minutesDecimal);
    const seconds = ((minutesDecimal - minutes) * 60).toFixed(1);
    
    let direction;
    if (isLat) {
        direction = decimal >= 0 ? 'N' : 'S';
    } else {
        direction = decimal >= 0 ? 'E' : 'W';
    }
    
    return `${degrees}°${minutes}'${seconds}"${direction}`;
}

// Load CSV file
async function loadCSV() {
    try {
        const response = await fetch('data/eclipse_site_data.csv');
        const text = await response.text();
        
        parseCSV(text);
        displaySites(sitesData);
    } catch (error) {
        document.getElementById('siteList').innerHTML = '<li class="error">Error loading data. Please make sure the CSV file exists.</li>';
        console.error('Error loading CSV:', error);
    }
}

// Parse CSV with proper handling of quoted fields
function parseCSV(text) {
    const lines = text.trim().split('\n');
    const headers = parseCSVLine(lines[0]);
    
    sitesData = lines.slice(1).map(line => {
        const values = parseCSVLine(line);
        const site = {};
        headers.forEach((header, index) => {
            site[header.trim()] = values[index] ? values[index].trim() : '';
        });
        return site;
    });
}

// Parse a single CSV line handling quoted fields
function parseCSVLine(line) {
    const result = [];
    let current = '';
    let inQuotes = false;
    
    for (let i = 0; i < line.length; i++) {
        const char = line[i];
        const nextChar = line[i + 1];
        
        if (char === '"') {
            if (inQuotes && nextChar === '"') {
                // Escaped quote
                current += '"';
                i++; // Skip next quote
            } else {
                // Toggle quote state
                inQuotes = !inQuotes;
            }
        } else if (char === ',' && !inQuotes) {
            // Field separator
            result.push(current);
            current = '';
        } else {
            current += char;
        }
    }
    
    // Add last field
    result.push(current);
    
    return result;
}

// Display sites in sidebar
function updateSiteCounter(visibleCount, totalCount) {
    const visibleCountEl = document.getElementById('visibleCount');
    const totalCountEl = document.getElementById('totalCount');
    
    if (visibleCountEl && totalCountEl) {
        visibleCountEl.textContent = visibleCount;
        totalCountEl.textContent = totalCount;
    }
}

function displaySites(sites) {
    const list = document.getElementById('siteList');
    
    // Update counter
    updateSiteCounter(sites.length, sitesData.length);
    
    if (sites.length === 0) {
        list.innerHTML = '<li class="loading">No sites found</li>';
        return;
    }
    
    list.innerHTML = sites.map(site => {
        let eclipseLabel = '';
        let eclipseClass = 'unknown';
        let eclipseText = '';
        
        if (site.eclipse_visibility === 'visible') {
            eclipseClass = 'visible';
            eclipseText = '🌑 Visible';
        } else if (site.eclipse_visibility === 'not_visible') {
            eclipseClass = 'not-visible';
            eclipseText = '🌑 Not visible';
        } else if (site.eclipse_visibility && site.eclipse_visibility !== 'unknown') {
            eclipseClass = 'unknown';
            eclipseText = '🌑 ' + site.eclipse_visibility;
        }
        
        if (eclipseText) {
            eclipseLabel = `<span class="site-eclipse ${eclipseClass}">${eclipseText}</span>`;
        }
        
        // Add cloud coverage label
        let cloudLabel = '';
        if (site.cloud_coverage && site.cloud_status === 'success') {
            const cloudPct = parseInt(site.cloud_coverage);
            let cloudEmoji = '☀️';
            let cloudClass = 'low';
            if (cloudPct >= 60) {
                cloudEmoji = '☁️';
                cloudClass = 'high';
            } else if (cloudPct >= 30) {
                cloudEmoji = '⛅';
                cloudClass = 'medium';
            }
            cloudLabel = `<span class="site-cloud ${cloudClass}">${cloudEmoji} ${cloudPct}%</span>`;
        }
        
        const isSelected = selectedSites.includes(site.code);
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

// Filter and sort sites
function filterSites() {
    const searchTerm = document.getElementById('searchBox').value.toLowerCase();
    const eclipseFilter = document.getElementById('eclipseFilter').checked;
    const sortBy = document.getElementById('sortBy').value;
    
    let filtered = sitesData.filter(site => {
        const matchesSearch = site.code.toLowerCase().includes(searchTerm) ||
            (site.denominacion && site.denominacion.toLowerCase().includes(searchTerm));
        
        const matchesEclipse = !eclipseFilter || site.eclipse_visibility === 'visible';
        
        return matchesSearch && matchesEclipse;
    });
    
    // Sort
    filtered.sort((a, b) => {
        if (sortBy === 'name') {
            const nameA = (a.denominacion || a.code).toLowerCase();
            const nameB = (b.denominacion || b.code).toLowerCase();
            return nameA.localeCompare(nameB);
        } else if (sortBy === 'tourist_value') {
            const valA = parseFloat(a.valor_turistico) || 0;
            const valB = parseFloat(b.valor_turistico) || 0;
            return valB - valA;
        } else {
            return a.code.localeCompare(b.code);
        }
    });
    
    displaySites(filtered);
}

// Event listeners
document.getElementById('searchBox').addEventListener('input', filterSites);
document.getElementById('eclipseFilter').addEventListener('change', filterSites);
document.getElementById('sortBy').addEventListener('change', filterSites);

// Select a site
function selectSite(code, event) {
    const site = sitesData.find(s => s.code === code);
    if (!site) return;

    // Check if Ctrl/Cmd key is pressed for multi-select
    const isMultiSelect = event && (event.ctrlKey || event.metaKey);

    if (isMultiSelect) {
        // Toggle selection
        const index = selectedSites.indexOf(code);
        if (index > -1) {
            selectedSites.splice(index, 1);
        } else {
            selectedSites.push(code);
        }
        
        console.log('Selected sites:', selectedSites);
        
        // Update visual state - refresh the entire list to update draggable attributes
        filterSites();
        
        // Verify draggable was set
        setTimeout(() => {
            const item = document.querySelector(`[data-code="${code}"]`);
            console.log('Item after refresh:', item);
            console.log('Has draggable:', item?.hasAttribute('draggable'));
            console.log('Draggable value:', item?.getAttribute('draggable'));
        }, 100);
        
        // If we have selected sites, update the map
        if (selectedSites.length > 0 && activeTab === 'map') {
            updateMapWithMultipleSites();
        }
    } else {
        // Single select - clear previous selections
        selectedSites = [code];
        currentSite = site;

        // Update active state and remove draggable
        document.querySelectorAll('.site-item').forEach(item => {
            item.classList.remove('active');
            item.removeAttribute('draggable');
            item.style.cursor = 'pointer';
        });
        const selectedItem = document.querySelector(`[data-code="${code}"]`);
        selectedItem.classList.add('active');

        // Display site details
        displaySiteDetails(site);
    }
}

// Drag and drop handlers for reordering sites in the map view
let draggedElement = null;
let draggedCode = null;

// Initialize drag and drop for site list (for selection only)
function initializeDragAndDrop() {
    const siteList = document.getElementById('siteList');
    if (!siteList) return;

    // Add click handler for site selection
    siteList.addEventListener('click', (e) => {
        const siteItem = e.target.closest('.site-item');
        if (siteItem) {
            const code = siteItem.getAttribute('data-code');
            if (code) {
                selectSite(code, e);
            }
        }
    });
}

// Initialize drag and drop for reordering sites in the route summary
function initializeReorderDragAndDrop() {
    const reorderList = document.getElementById('reorderSitesList');
    if (!reorderList) return;

    reorderList.addEventListener('dragstart', (e) => {
        const item = e.target.closest('.reorder-site-item');
        if (item) {
            draggedElement = item;
            draggedCode = item.getAttribute('data-code');
            item.style.opacity = '0.5';
            e.dataTransfer.effectAllowed = 'move';
        }
    });

    reorderList.addEventListener('dragend', (e) => {
        if (e.target.classList.contains('reorder-site-item')) {
            e.target.style.opacity = '1';
            // Clear all border highlights
            document.querySelectorAll('.reorder-site-item').forEach(item => {
                item.style.borderTop = '';
            });
        }
    });

    reorderList.addEventListener('dragover', (e) => {
        e.preventDefault();
        const target = e.target.closest('.reorder-site-item');
        if (target && target !== draggedElement) {
            e.dataTransfer.dropEffect = 'move';
            target.style.borderTop = '3px solid #007bff';
        }
    });

    reorderList.addEventListener('dragleave', (e) => {
        const target = e.target.closest('.reorder-site-item');
        if (target) {
            target.style.borderTop = '';
        }
    });

    reorderList.addEventListener('drop', (e) => {
        e.preventDefault();
        const target = e.target.closest('.reorder-site-item');
        
        if (target && target !== draggedElement) {
            target.style.borderTop = '';
            
            const targetCode = target.getAttribute('data-code');
            
            if (draggedCode && targetCode && draggedCode !== targetCode) {
                // Reorder the selectedSites array
                const draggedIndex = selectedSites.indexOf(draggedCode);
                const targetIndex = selectedSites.indexOf(targetCode);
                
                if (draggedIndex > -1 && targetIndex > -1) {
                    selectedSites.splice(draggedIndex, 1);
                    selectedSites.splice(targetIndex, 0, draggedCode);
                    
                    // Update the map with new order
                    updateMapWithMultipleSites();
                }
            }
        }
    });
}

// Update only the details tab content (without affecting the map)
function updateDetailsTabContent(site) {
    const detailsTab = document.getElementById('detailsTab');
    if (!detailsTab) return;
    
    const mapsUrl = `https://www.google.com/maps?q=${site.latitude},${site.longitude}`;
    const lat = parseFloat(site.latitude);
    const lon = parseFloat(site.longitude);
    const coordsBase64 = btoa(`${lat}, ${lon}`);
    const shademapUrl = `https://shademap.app/@${lat},${lon},17z,1786559455614t,0b,0p,0m!1786512158844!1786563246912,${coordsBase64}!${lat}!${lon}`;
    const x = lon * 20037508.34 / 180;
    const y = Math.log(Math.tan((90 + lat) * Math.PI / 360)) / (Math.PI / 180);
    const yMercator = y * 20037508.34 / 180;
    const eclipseUrl = `https://visualizadores.ign.es/eclipses/2026?center=${x},${yMercator}&zoom=16&srs=EPSG:3857`;
    
    // Update the header
    const header = document.querySelector('.detail-header');
    if (header) {
        // Google Maps Static API thumbnail (400x200, zoom 15, satellite view)
        const googleMapsThumbUrl = `https://maps.googleapis.com/maps/api/staticmap?center=${lat},${lon}&zoom=15&size=400x200&maptype=satellite&markers=color:red%7C${lat},${lon}&key=${googleMapsApiKey}`;
        
        header.innerHTML = `
            <h2>${site.denominacion || site.code}</h2>
            <div style="display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap;">
                <a href="${site.url}" target="_blank" class="link-button">🪨 View on IGME Website</a>
                <div style="display: flex; flex-direction: column; align-items: center; gap: 0.25rem;">
                    <a href="${mapsUrl}" target="_blank" class="link-button maps">📍 Open in Google Maps</a>
                    <div style="position: relative; display: inline-block;">
                        <img src="${googleMapsThumbUrl}"
                             alt="Google Maps location for ${site.code}"
                             class="eclipse-profile-thumbnail maps-thumbnail"
                             onclick="window.open('${mapsUrl}', '_blank')"
                             onerror="this.style.display='none'"
                             title="Click to open in Google Maps">
                    </div>
                </div>
                <div style="display: flex; flex-direction: column; align-items: center; gap: 0.25rem;">
                    <a href="${shademapUrl}" target="_blank" class="link-button shademap">🌄 View on Shademap</a>
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
                <div style="display: flex; flex-direction: column; align-items: center; gap: 0.25rem;">
                    <a href="${eclipseUrl}" target="_blank" class="link-button eclipse">🌑 Eclipse 2026 View</a>
                    <div style="position: relative; display: inline-block;">
                        <img src="data/eclipse_profiles/${site.code}_profile.png"
                             alt="Eclipse visibility profile for ${site.code}"
                             class="eclipse-profile-thumbnail"
                             onclick="window.open('data/eclipse_profiles/${site.code}_profile.png', '_blank')"
                             onerror="this.parentElement.style.display='none'"
                             title="Hover to preview, click to open full-size">
                        <div class="eclipse-profile-overlay">
                            <img src="data/eclipse_profiles/${site.code}_profile.png"
                                 alt="Eclipse visibility profile for ${site.code}">
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
    
    // Update the details content
    detailsTab.innerHTML = `
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
            <div class="info-value">${site.latitude}, ${site.longitude}</div>
        </div>
        ${site.eclipse_visibility ? `
        <div class="info-item">
            <div class="info-label">Eclipse 2026 Visibility</div>
            <div class="info-value" style="color: ${
                site.eclipse_visibility === 'visible' ? '#6f42c1' :
                site.eclipse_visibility === 'not_visible' ? '#dc3545' : '#ffc107'
            }">
                ${site.eclipse_visibility === 'visible' ? '🌑 Visible' :
                  site.eclipse_visibility === 'not_visible' ? '🌑 Not Visible' :
                  '🌑 ' + site.eclipse_visibility}
            </div>
        </div>
        ` : ''}
        </div>

        <div class="images-section">
            <h3>📷 Images</h3>
            <div id="imagesContainer" class="images-grid">
                <div class="loading">Loading IGME images...</div>
            </div>
        </div>
    `;
    
    // Load images
    loadSiteImages(site);
}

// Display site details
async function displaySiteDetails(site) {
    const content = document.getElementById('content');
    
    const mapsUrl = `https://www.google.com/maps?q=${site.latitude},${site.longitude}`;
    
    const lat = parseFloat(site.latitude);
    const lon = parseFloat(site.longitude);
    const coordsBase64 = btoa(`${lat}, ${lon}`);
    const shademapUrl = `https://shademap.app/@${lat},${lon},17z,1786559455614t,0b,0p,0m!1786512158844!1786563246912,${coordsBase64}!${lat}!${lon}`;
    
    const x = lon * 20037508.34 / 180;
    const y = Math.log(Math.tan((90 + lat) * Math.PI / 360)) / (Math.PI / 180);
    const yMercator = y * 20037508.34 / 180;
    
    const eclipseUrl = `https://visualizadores.ign.es/eclipses/2026?center=${x},${yMercator}&zoom=16&srs=EPSG:3857`;
    
    const eclipseFanUrl = `https://www.eclipsefan.org/?lat=${lat}&lng=${lon}&zoom=6&oz=5&lang=en`;
    
    // Build cloud coverage button if available
    let cloudButton = '';
    if (site.cloud_url && site.cloud_status === 'success') {
        cloudButton = `<a href="${site.cloud_url}" target="_blank" class="link-button cloud">🕐 timeanddate.com</a>`;
    }
    
    content.innerHTML = `
        <div class="site-details">
            <div class="detail-header">
                <h2>${site.denominacion || site.code}</h2>
                <div style="display: flex; align-items: flex-start; gap: 0.5rem; flex-wrap: wrap;">
                    <a href="${site.url}" target="_blank" class="link-button">🪨 View on IGME Website</a>
                    <div style="display: flex; flex-direction: column; align-items: center; gap: 0.25rem;">
                        <a href="${mapsUrl}" target="_blank" class="link-button maps">📍 Open in Google Maps</a>
                        <div style="position: relative; display: inline-block;">
                            <img src="https://maps.googleapis.com/maps/api/staticmap?center=${lat},${lon}&zoom=15&size=400x200&maptype=satellite&markers=color:red%7C${lat},${lon}&key=${googleMapsApiKey}"
                                 alt="Google Maps location for ${site.code}"
                                 class="eclipse-profile-thumbnail maps-thumbnail"
                                 onclick="window.open('${mapsUrl}', '_blank')"
                                 onerror="this.style.display='none'"
                                 title="Click to open in Google Maps">
                        </div>
                    </div>
                    <div style="display: flex; flex-direction: column; align-items: center; gap: 0.25rem;">
                        <a href="${shademapUrl}" target="_blank" class="link-button shademap">🌄 View on Shademap</a>
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
                    <div style="display: flex; flex-direction: column; align-items: center; gap: 0.25rem;">
                        <a href="${eclipseFanUrl}" target="_blank" class="link-button eclipsefan">🌒 EclipseFan.org</a>
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
                        <a href="${eclipseUrl}" target="_blank" class="link-button eclipse">🌑 Eclipse 2026 View</a>
                        <div style="position: relative; display: inline-block;">
                            <img src="data/scrape/ign_profiles/${site.code}_profile.png"
                                 alt="Eclipse visibility profile for ${site.code}"
                                 class="eclipse-profile-thumbnail"
                                 onclick="window.open('data/scrape/ign_profiles/${site.code}_profile.png', '_blank')"
                                 onerror="this.parentElement.style.display='none'"
                                 title="Hover to preview, click to open full-size">
                            <div class="eclipse-profile-overlay">
                                <img src="data/ign_visibility_profiles/${site.code}_profile.png"
                                     alt="Eclipse visibility profile for ${site.code}">
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="tabs">
                <button class="tab ${activeTab === 'details' ? 'active' : ''}" onclick="switchTab('details')">📋 Details</button>
                <button class="tab ${activeTab === 'map' ? 'active' : ''}" onclick="switchTab('map')">🗺️ Map</button>
                ${activeTab === 'map' ? '<span class="map-tip">💡 Hold Ctrl (Cmd on Mac) and click sites to select multiple</span>' : ''}
            </div>

            <div id="detailsTab" class="tab-content ${activeTab === 'details' ? 'active' : ''}">
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
                            ${decimalToDMS(parseFloat(site.latitude), true)} ${decimalToDMS(parseFloat(site.longitude), false)}
                        </div>
                        <div style="font-size: 0.85em; color: #6c757d;">
                            ${site.latitude}, ${site.longitude}
                        </div>
                    </div>
                </div>
                ${site.eclipse_visibility ? `
                <div class="info-item">
                    <div class="info-label">Eclipse 2026 Visibility</div>
                    <div class="info-value" style="color: ${
                        site.eclipse_visibility === 'visible' ? '#6f42c1' :
                        site.eclipse_visibility === 'not_visible' ? '#dc3545' : '#ffc107'
                    }">
                        ${site.eclipse_visibility === 'visible' ? '🌑 Visible' :
                          site.eclipse_visibility === 'not_visible' ? '🌑 Not Visible' :
                          '🌑 ' + site.eclipse_visibility}
                    </div>
                </div>
                ` : ''}
                ${site.cloud_coverage && site.cloud_status === 'success' ? `
                <div class="info-item">
                    <div class="info-label">Cloud Coverage (Aug 12)</div>
                    <div class="info-value" style="color: ${
                        parseInt(site.cloud_coverage) < 30 ? '#28a745' :
                        parseInt(site.cloud_coverage) < 60 ? '#ffc107' : '#dc3545'
                    }">
                        ${parseInt(site.cloud_coverage) < 30 ? '☀️' :
                          parseInt(site.cloud_coverage) < 60 ? '⛅' : '☁️'} ${site.cloud_coverage}%
                        ${parseInt(site.cloud_coverage) < 30 ? ' (Low - Good!)' :
                          parseInt(site.cloud_coverage) < 60 ? ' (Medium)' : ' (High)'}
                    </div>
                </div>
                ` : ''}
                </div>

                <div class="images-section">
                    <h3>📷 Images</h3>
                    <div id="imagesContainer" class="images-grid">
                        <div class="loading">Loading IGME images...</div>
                    </div>
                </div>
            </div>

            <div id="mapTab" class="tab-content ${activeTab === 'map' ? 'active' : ''}">
                <div id="mapContainer"></div>
                <div id="routeSummary" style="display: none;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                        <h4 style="margin: 0;">Route Summary</h4>
                        <button onclick="toggleRouteSummary()" id="routeSummaryToggle" style="background: none; border: none; font-size: 0.9rem; cursor: pointer; color: #6c757d; padding: 0; padding-left: 0.5rem; line-height: 1; opacity: 0.6; transition: opacity 0.2s;" onmouseover="this.style.opacity='1'" onmouseout="this.style.opacity='0.6'" title="Collapse">▼</button>
                    </div>
                    <div id="routeSummaryContent">
                    <div class="return-toggle">
                        <label>
                            <input type="checkbox" id="returnToHotel" onchange="toggleReturnToHotel()">
                            Return to hotel
                        </label>
                    </div>
                    <div id="routeSegments"></div>
                    <div id="routeTotal" class="route-total"></div>
                    <div id="routeDirections" style="display: none; margin-top: 1rem; padding: 1rem; background: #f8f9fa; border-radius: 4px; max-height: 400px; overflow-y: auto;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
                            <h4 style="margin: 0; font-size: 1rem;">Turn-by-Turn Directions</h4>
                            <button onclick="closeDirections()" style="background: none; border: none; font-size: 1.5rem; cursor: pointer; color: #6c757d; padding: 0; line-height: 1;">&times;</button>
                        </div>
                        <div id="directionsContent"></div>
                    </div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Load images from IGME
    loadSiteImages(site);
    
    // Initialize map when map tab is shown
    initializeMap(site, mapsUrl, shademapUrl, eclipseUrl);
}

// Create map with sites (unified function for single or multiple sites)
function createMapWithSites(sites, options = {}) {
    const { showRouting = true, showRouteSummary = false } = options;
    
    // Remove existing map
    if (currentMap) {
        currentMap.remove();
        currentMap = null;
        currentRoutingControl = null;
    }
    
    // Calculate bounds for all sites plus hotel
    const bounds = L.latLngBounds();
    bounds.extend([HOTEL_LAT, HOTEL_LON]);
    sites.forEach(site => {
        bounds.extend([parseFloat(site.latitude), parseFloat(site.longitude)]);
    });
    
    // Create map
    currentMap = L.map('mapContainer').fitBounds(bounds, { padding: [50, 50] });
    
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 19
    }).addTo(currentMap);
    
    // Add hotel marker
    const hotelIcon = L.divIcon({
        html: '<div style="font-size: 24px;">🏨</div>',
        className: 'hotel-marker',
        iconSize: [30, 30],
        iconAnchor: [15, 15]
    });
    
    L.marker([HOTEL_LAT, HOTEL_LON], { icon: hotelIcon })
        .addTo(currentMap)
        .bindPopup('<b>Hotel Parras Arnedillo</b><br>Starting point');
    
    // Add markers for each site
    sites.forEach((site, index) => {
        const lat = parseFloat(site.latitude);
        const lon = parseFloat(site.longitude);
        
        // Create URLs for this site
        const mapsUrl = `https://www.google.com/maps?q=${lat},${lon}`;
        const coordsBase64 = btoa(`${lat}, ${lon}`);
        const shademapUrl = `https://shademap.app/@${lat},${lon},17z,1786559455614t,0b,0p,0m!1786512158844!1786563246912,${coordsBase64}!${lat}!${lon}`;
        const x = lon * 20037508.34 / 180;
        const y = Math.log(Math.tan((90 + lat) * Math.PI / 360)) / (Math.PI / 180);
        const yMercator = y * 20037508.34 / 180;
        const eclipseUrl = `https://visualizadores.ign.es/eclipses/2026?center=${x},${yMercator}&zoom=16&srs=EPSG:3857`;
        
        const popupContent = `
            <div style="min-width: 200px;">
                <h4 style="margin: 0 0 8px 0; font-size: 0.95rem;">${site.denominacion || site.code}</h4>
                <a href="${site.url}" target="_blank">🪨 View on IGME Website</a>
                <a href="${mapsUrl}" target="_blank" class="maps">📍 Open in Google Maps</a>
                <a href="${shademapUrl}" target="_blank" class="shademap">🌄 View on Shademap</a>
                <a href="${eclipseUrl}" target="_blank" class="eclipse">🌑 Eclipse 2026 View</a>
            </div>
        `;
        
        // Add site marker (numbered for multiple sites, simple for single site)
        const markerIcon = sites.length > 1
            ? L.divIcon({
                html: `<div style="background: #007bff; color: white; border-radius: 50%; width: 30px; height: 30px; display: flex; align-items: center; justify-content: center; font-weight: bold; border: 2px solid white; box-shadow: 0 2px 4px rgba(0,0,0,0.3);">${index + 1}</div>`,
                className: 'numbered-marker',
                iconSize: [30, 30],
                iconAnchor: [15, 15]
            })
            : null; // Use default marker for single site
        
        const marker = markerIcon
            ? L.marker([lat, lon], { icon: markerIcon }).addTo(currentMap).bindPopup(popupContent)
            : L.marker([lat, lon]).addTo(currentMap).bindPopup(popupContent);
        
        // Add click handler to update details in background (without affecting map or switching tabs)
        marker.on('click', () => {
            // Update current site
            currentSite = site;
            
            // Update sidebar selection
            document.querySelectorAll('.site-item').forEach(item => {
                item.classList.remove('active');
            });
            const siteItem = document.querySelector(`[data-code="${site.code}"]`);
            if (siteItem) {
                siteItem.classList.add('active');
            }
            
            // Update only the details tab content (doesn't affect map or current tab)
            updateDetailsTabContent(site);
        });
    });
    
    // Only create routing if requested
    if (!showRouting) return;
    
    // Create waypoints list
    const waypoints = [
        L.latLng(HOTEL_LAT, HOTEL_LON),
        ...sites.map(site => L.latLng(parseFloat(site.latitude), parseFloat(site.longitude)))
    ];
    
    // Add return to hotel if enabled
    if (returnToHotel) {
        waypoints.push(L.latLng(HOTEL_LAT, HOTEL_LON));
    }
    
    // Create segments between waypoints
    const waypointNames = ['Hotel Parras Arnedillo', ...sites.map((s, i) => `${i + 1}. ${s.denominacion || s.code}`)];
    if (returnToHotel) {
        waypointNames.push('Hotel Parras Arnedillo');
    }
    
    // Colors for different segments
    const segmentColors = ['#007bff', '#28a745', '#dc3545', '#ffc107', '#6f42c1', '#fd7e14', '#17a2b8', '#e83e8c'];
    
    // Clear previous segments
    routeSegments = [];
    let totalDistance = 0;
    let totalTime = 0;
    let segmentsCompleted = 0;
    const totalSegments = waypoints.length - 1;
    const allRouteBounds = L.latLngBounds();
    
    // Create individual route for each segment
    for (let i = 0; i < waypoints.length - 1; i++) {
        const color = segmentColors[i % segmentColors.length];
        const segmentIndex = i;
        
        L.Routing.control({
            waypoints: [waypoints[i], waypoints[i + 1]],
            routeWhileDragging: false,
            addWaypoints: false,
            draggableWaypoints: false,
            fitSelectedRoutes: false,
            showAlternatives: false,
            lineOptions: {
                styles: [{ color: color, weight: 4, opacity: 0.7 }],
                extendToWaypoints: false,
                missingRouteTolerance: 0
            },
            createMarker: function() { return null; },
            router: L.Routing.osrmv1({
                serviceUrl: 'https://router.project-osrm.org/route/v1'
            }),
            show: false // Hide the default routing instructions
        }).on('routesfound', function(e) {
            const route = e.routes[0];
            const segmentDist = route.summary.totalDistance;
            const segmentTime = route.summary.totalTime;
            
            // Extend bounds with all coordinates from this route
            route.coordinates.forEach(coord => {
                allRouteBounds.extend([coord.lat, coord.lng]);
            });
            
            routeSegments[segmentIndex] = {
                from: waypointNames[segmentIndex],
                to: waypointNames[segmentIndex + 1],
                distance: segmentDist,
                time: segmentTime,
                color: color,
                index: segmentIndex,
                instructions: route.instructions // Store turn-by-turn instructions
            };
            
            totalDistance += segmentDist;
            totalTime += segmentTime;
            segmentsCompleted++;
            
            // When all segments are loaded, display summary and adjust bounds
            if (segmentsCompleted === totalSegments) {
                if (showRouteSummary) {
                    displayRouteSummary(totalDistance, totalTime);
                }
                // Fit map to show all route coordinates
                if (allRouteBounds.isValid()) {
                    // Invalidate size to ensure map container dimensions are correct
                    currentMap.invalidateSize();
                    // Fit bounds with appropriate padding
                    currentMap.fitBounds(allRouteBounds, { padding: [50, 50], maxZoom: 15 });
                }
            }
        }).addTo(currentMap);
    }
}

// Update map with multiple selected sites
function updateMapWithMultipleSites() {
    if (selectedSites.length === 0) return;
    
    // Get all selected site objects (in order)
    const sites = selectedSites.map(code =>
        sitesData.find(s => s.code === code)
    ).filter(s => s && s.latitude !== 'N/A' && s.longitude !== 'N/A');
    
    if (sites.length === 0) return;
    
    createMapWithSites(sites, { showRouting: true, showRouteSummary: true });
}

// Display route summary
function displayRouteSummary(totalDistance, totalTime) {
    // Build reorderable site list (only for multi-site routes)
    let siteListHTML = '';
    if (selectedSites.length > 1) {
        siteListHTML = `
            <div class="reorder-sites-container">
                <div class="reorder-sites-header" onclick="toggleReorderList()" style="cursor: pointer;">
                    <span id="reorderToggleIcon">▶</span> 📍 Route Order (drag to reorder)
                </div>
                <ul class="reorder-sites-list" id="reorderSitesList" style="display: none;">
        `;
        selectedSites.forEach((code, index) => {
            const site = sitesData.find(s => s.code === code);
            if (site) {
                siteListHTML += `
                    <li class="reorder-site-item" data-code="${code}" draggable="true">
                        <span class="reorder-handle">⋮⋮</span>
                        <span class="reorder-number">${index + 1}</span>
                        <span class="reorder-name">${site.denominacion || code}</span>
                    </li>
                `;
            }
        });
        siteListHTML += '</ul></div>';
    }
    
    let segmentHTML = '';
    
    routeSegments.forEach((segment, i) => {
        segmentHTML += `
            <div class="route-segment" onclick="highlightSegment(${i})" style="cursor: pointer; border-left-color: ${segment.color};">
                <div class="route-segment-header">${segment.from} → ${segment.to}</div>
                <div class="route-segment-details">
                    ${(segment.distance / 1000).toFixed(1)} km • ${Math.round(segment.time / 60)} min
                </div>
            </div>
        `;
    });
    
    document.getElementById('routeSegments').innerHTML = siteListHTML + segmentHTML;
    
    // Build Google Maps URL for the entire route
    let googleMapsUrl = 'https://www.google.com/maps/dir/';
    // Start from hotel
    googleMapsUrl += `${HOTEL_LAT},${HOTEL_LON}/`;
    // Add all sites in order
    selectedSites.forEach(code => {
        const site = sitesData.find(s => s.code === code);
        if (site) {
            googleMapsUrl += `${site.latitude},${site.longitude}/`;
        }
    });
    // Return to hotel if enabled
    if (returnToHotel) {
        googleMapsUrl += `${HOTEL_LAT},${HOTEL_LON}/`;
    }
    
    document.getElementById('routeTotal').innerHTML = `
        <div><strong>Total Distance:</strong> ${(totalDistance / 1000).toFixed(1)} km</div>
        <div><strong>Total Time:</strong> ${Math.round(totalTime / 60)} min (${(totalTime / 3600).toFixed(1)} hrs)</div>
        <div style="display: flex; gap: 0.5rem; margin-top: 0.75rem;">
            <a href="${googleMapsUrl}" target="_blank" class="google-maps-route-btn">
                📍 Open in Google Maps
            </a>
            <button onclick="exportRouteAsKML()" class="export-kml-btn">
                💾 Export as KML
            </button>
        </div>
    `;
    
    document.getElementById('routeSummary').style.display = 'block';
    
    // Initialize drag-and-drop for reordering if we have multiple sites
    if (selectedSites.length > 1) {
        initializeReorderDragAndDrop();
    }
}

// Toggle reorder list visibility
function toggleReorderList() {
    const list = document.getElementById('reorderSitesList');
    const icon = document.getElementById('reorderToggleIcon');
    
    if (list && icon) {
        if (list.style.display === 'none') {
            list.style.display = 'block';
            icon.textContent = '▼';
        } else {
            list.style.display = 'none';
            icon.textContent = '▶';
        }
    }
}

// Highlight a specific segment and show directions
function highlightSegment(index) {
    const segment = routeSegments[index];
    if (!segment) return;
    
    const directionsPanel = document.getElementById('routeDirections');
    const directionsContent = document.getElementById('directionsContent');
    
    if (!directionsPanel || !directionsContent) return;
    
    // Build the directions HTML
    let directionsHTML = `
        <div style="border-left: 4px solid ${segment.color}; padding-left: 1rem; margin-bottom: 1rem; background: white; padding: 0.75rem; border-radius: 4px;">
            <div style="font-weight: 600; font-size: 1rem; margin-bottom: 0.25rem;">${segment.from}</div>
            <div style="color: #6c757d; margin: 0.5rem 0;">↓</div>
            <div style="font-weight: 600; font-size: 1rem;">${segment.to}</div>
        </div>
        <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 0.5rem; margin-bottom: 1rem;">
            <div style="background: white; padding: 0.5rem; border-radius: 4px; text-align: center;">
                <div style="font-size: 0.7rem; color: #6c757d; margin-bottom: 0.25rem;">DISTANCE</div>
                <div style="font-size: 1rem; font-weight: 600; color: #2c3e50;">${(segment.distance / 1000).toFixed(1)} km</div>
            </div>
            <div style="background: white; padding: 0.5rem; border-radius: 4px; text-align: center;">
                <div style="font-size: 0.7rem; color: #6c757d; margin-bottom: 0.25rem;">TIME</div>
                <div style="font-size: 1rem; font-weight: 600; color: #2c3e50;">${Math.round(segment.time / 60)} min</div>
            </div>
            <div style="background: white; padding: 0.5rem; border-radius: 4px; text-align: center;">
                <div style="font-size: 0.7rem; color: #6c757d; margin-bottom: 0.25rem;">AVG SPEED</div>
                <div style="font-size: 1rem; font-weight: 600; color: #2c3e50;">${((segment.distance / 1000) / (segment.time / 3600)).toFixed(0)} km/h</div>
            </div>
        </div>
    `;
    
    // Add turn-by-turn instructions if available
    if (segment.instructions && segment.instructions.length > 0) {
        directionsHTML += '<div style="background: white; padding: 0.75rem; border-radius: 4px;">';
        segment.instructions.forEach((instruction, i) => {
            const distance = instruction.distance > 1000
                ? `${(instruction.distance / 1000).toFixed(1)} km`
                : `${Math.round(instruction.distance)} m`;
            
            // Get direction icon based on instruction type
            let icon = '➡️';
            const type = instruction.type || '';
            if (type.includes('left')) icon = '⬅️';
            else if (type.includes('right')) icon = '➡️';
            else if (type.includes('straight')) icon = '⬆️';
            else if (type.includes('uturn')) icon = '↩️';
            else if (type === 'WaypointReached') icon = '🎯';
            else if (i === 0) icon = '🚗';
            
            directionsHTML += `
                <div style="display: flex; gap: 0.75rem; padding: 0.5rem 0; border-bottom: 1px solid #e9ecef;">
                    <div style="font-size: 1.25rem; flex-shrink: 0;">${icon}</div>
                    <div style="flex: 1;">
                        <div style="font-size: 0.9rem; color: #2c3e50; margin-bottom: 0.25rem;">${instruction.text || 'Continue'}</div>
                        ${instruction.road ? `<div style="font-size: 0.75rem; color: #6c757d;">on ${instruction.road}</div>` : ''}
                        <div style="font-size: 0.75rem; color: #6c757d; margin-top: 0.25rem;">${distance}</div>
                    </div>
                </div>
            `;
        });
        directionsHTML += '</div>';
    } else {
        directionsHTML += '<div style="background: white; padding: 1rem; border-radius: 4px; text-align: center; color: #6c757d;">No detailed directions available for this segment.</div>';
    }
    
    directionsContent.innerHTML = directionsHTML;
    directionsPanel.style.display = 'block';
    
    // Scroll to directions panel
    directionsPanel.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function closeDirections() {
    const directionsPanel = document.getElementById('routeDirections');
    if (directionsPanel) {
        directionsPanel.style.display = 'none';
    }
}

// Toggle route summary collapse/expand
function toggleRouteSummary() {
    const content = document.getElementById('routeSummaryContent');
    const toggle = document.getElementById('routeSummaryToggle');
    
    if (content.style.display === 'none') {
        content.style.display = 'block';
        toggle.textContent = '▼';
        toggle.title = 'Collapse';
    } else {
        content.style.display = 'none';
        toggle.textContent = '▶';
        toggle.title = 'Expand';
    }
}

// Toggle return to hotel
function toggleReturnToHotel() {
    returnToHotel = document.getElementById('returnToHotel').checked;
    if (selectedSites.length > 0) {
        updateMapWithMultipleSites();
    }
}

// Initialize Leaflet map
let currentMap = null;
let currentRoutingControl = null;
let mapInitialized = false;
const HOTEL_LAT = 42.2106162276457;
const HOTEL_LON = -2.24015444418023;

function initializeMap(site, mapsUrl, shademapUrl, eclipseUrl) {
    // Reset map initialization flag when switching sites
    mapInitialized = false;

    // Function to create/update the map
    function createMap() {
        setTimeout(() => {
            // Use same behavior as multi-site (with route summary)
            createMapWithSites([site], { showRouting: true, showRouteSummary: true });
        }, 100);
    }

    // If map tab is already active, create map immediately
    if (activeTab === 'map') {
        createMap();
        mapInitialized = true;
    } else {
        // Otherwise, create map when tab is clicked
        const mapTab = document.querySelector('.tab:nth-child(2)');
        if (!mapInitialized) {
            mapTab.addEventListener('click', function initMap() {
                mapTab.removeEventListener('click', initMap);
                createMap();
                mapInitialized = true;
            }, { once: true });
        }
    }
}

// Load images from IGME website
async function loadSiteImages(site) {
    const container = document.getElementById('imagesContainer');
    
    try {
        const response = await fetch(`/api/images?url=${encodeURIComponent(site.url)}`);
        const data = await response.json();
        
        if (data.images && data.images.length > 0) {
            currentImages = data.images.map(img => `/api/proxy-image?url=${encodeURIComponent(img.src)}`);
            
            container.innerHTML = data.images.map((img, index) => `
                <div class="image-card">
                    <img src="/api/proxy-image?url=${encodeURIComponent(img.src)}"
                         alt="${img.alt}"
                         onclick="openModal(${index})"
                         onerror="this.parentElement.style.display='none'">
                    <div class="image-caption">${img.alt}</div>
                </div>
            `).join('');
        } else {
            container.innerHTML = '<div class="no-images">No images found for this site</div>';
        }
    } catch (error) {
        console.error('Error loading images:', error);
        container.innerHTML = '<div class="no-images">Error loading images. Please try again later.</div>';
    }
}

// Modal functions
function openModal(index) {
    currentImageIndex = index;
    const modal = document.getElementById('imageModal');
    const modalImg = document.getElementById('modalImage');
    const counter = document.getElementById('modalCounter');
    
    modal.style.display = 'block';
    modalImg.src = currentImages[currentImageIndex];
    counter.textContent = `${currentImageIndex + 1} / ${currentImages.length}`;
}

function closeModal() {
    document.getElementById('imageModal').style.display = 'none';
}

function nextImage() {
    currentImageIndex = (currentImageIndex + 1) % currentImages.length;
    document.getElementById('modalImage').src = currentImages[currentImageIndex];
    document.getElementById('modalCounter').textContent = `${currentImageIndex + 1} / ${currentImages.length}`;
}

function prevImage() {
    currentImageIndex = (currentImageIndex - 1 + currentImages.length) % currentImages.length;
    document.getElementById('modalImage').src = currentImages[currentImageIndex];
    document.getElementById('modalCounter').textContent = `${currentImageIndex + 1} / ${currentImages.length}`;
}

// Modal event listeners
document.getElementById('modalClose').addEventListener('click', closeModal);
document.getElementById('modalNext').addEventListener('click', nextImage);
document.getElementById('modalPrev').addEventListener('click', prevImage);

// Keyboard navigation
document.addEventListener('keydown', (e) => {
    const modal = document.getElementById('imageModal');
    if (modal.style.display === 'block') {
        if (e.key === 'Escape') closeModal();
        else if (e.key === 'ArrowRight') nextImage();
        else if (e.key === 'ArrowLeft') prevImage();
    }
});

// Close modal when clicking outside image
document.getElementById('imageModal').addEventListener('click', (e) => {
    if (e.target.id === 'imageModal') closeModal();
});

// Tab switching function
function switchTab(tabName) {
    // Store active tab
    activeTab = tabName;
    
    // Update tab buttons
    document.querySelectorAll('.tab').forEach(tab => {
        tab.classList.remove('active');
    });
    event.target.classList.add('active');

    // Update tab content
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });

    if (tabName === 'details') {
        document.getElementById('detailsTab').classList.add('active');
    } else if (tabName === 'map') {
        document.getElementById('mapTab').classList.add('active');
    }
    
    // Show/hide map tip
    const tabsContainer = document.querySelector('.tabs');
    let existingTip = tabsContainer.querySelector('.map-tip');
    
    if (tabName === 'map') {
        // Add tip if it doesn't exist
        if (!existingTip) {
            const tip = document.createElement('span');
            tip.className = 'map-tip';
            tip.textContent = '💡 Hold Ctrl (Cmd on Mac) and click multiple sites in the list to plan a route';
            tabsContainer.appendChild(tip);
        }
    } else {
        // Remove tip if it exists
        if (existingTip) {
            existingTip.remove();
        }
    }
}
// Export route as KML file
function exportRouteAsKML() {
    if (selectedSites.length === 0) return;
    
    // Build KML content
    let kml = `<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>Spain Eclipse Sites Route</name>
    <description>Route visiting ${selectedSites.length} geological sites</description>
    
    <!-- Style for hotel -->
    <Style id="hotelIcon">
      <IconStyle>
        <Icon>
          <href>http://maps.google.com/mapfiles/kml/shapes/lodging.png</href>
        </Icon>
      </IconStyle>
    </Style>
    
    <!-- Style for sites -->
    <Style id="siteIcon">
      <IconStyle>
        <Icon>
          <href>http://maps.google.com/mapfiles/kml/paddle/blu-circle.png</href>
        </Icon>
      </IconStyle>
    </Style>
    
    <!-- Hotel start point -->
    <Placemark>
      <name>Hotel Parras Arnedillo (Start)</name>
      <description>Starting point</description>
      <styleUrl>#hotelIcon</styleUrl>
      <Point>
        <coordinates>${HOTEL_LON},${HOTEL_LAT},0</coordinates>
      </Point>
    </Placemark>
    
`;
    
    // Add each site as a placemark
    selectedSites.forEach((code, index) => {
        const site = sitesData.find(s => s.code === code);
        if (site) {
            kml += `    <!-- Site ${index + 1} -->
    <Placemark>
      <name>${index + 1}. ${site.denominacion || site.code}</name>
      <description><![CDATA[
        <b>Code:</b> ${site.code}<br/>
        <b>Tourist Value:</b> ${site.valor_turistico}<br/>
        <b>Privacy:</b> ${site.confidencialidad}<br/>
        <b>Eclipse Visibility:</b> ${site.eclipse_visibility || 'Unknown'}<br/>
        <b>URL:</b> <a href="${site.url}">${site.url}</a>
      ]]></description>
      <styleUrl>#siteIcon</styleUrl>
      <Point>
        <coordinates>${site.longitude},${site.latitude},0</coordinates>
      </Point>
    </Placemark>
    
`;
        }
    });
    
    // Add return to hotel if enabled
    if (returnToHotel) {
        kml += `    <!-- Return to hotel -->
    <Placemark>
      <name>Hotel Parras Arnedillo (Return)</name>
      <description>End point</description>
      <styleUrl>#hotelIcon</styleUrl>
      <Point>
        <coordinates>${HOTEL_LON},${HOTEL_LAT},0</coordinates>
      </Point>
    </Placemark>
    
`;
    }
    
    // Add route line
    kml += `    <!-- Route line -->
    <Placemark>
      <name>Route</name>
      <description>Driving route between sites</description>
      <Style>
        <LineStyle>
          <color>ff0000ff</color>
          <width>3</width>
        </LineStyle>
      </Style>
      <LineString>
        <tessellate>1</tessellate>
        <coordinates>
          ${HOTEL_LON},${HOTEL_LAT},0
`;
    
    selectedSites.forEach(code => {
        const site = sitesData.find(s => s.code === code);
        if (site) {
            kml += `          ${site.longitude},${site.latitude},0\n`;
        }
    });
    
    if (returnToHotel) {
        kml += `          ${HOTEL_LON},${HOTEL_LAT},0\n`;
    }
    
    kml += `        </coordinates>
      </LineString>
    </Placemark>
    
  </Document>
</kml>`;
    
    // Create blob and download
    const blob = new Blob([kml], { type: 'application/vnd.google-earth.kml+xml' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `spain-eclipse-route-${selectedSites.length}-sites.kml`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}


// Side panel functions
function openPanel(panelId) {
    const panel = document.getElementById(panelId);
    const overlay = document.getElementById('panelOverlay');
    
    if (panel && overlay) {
        // Close any other open panels first
        document.querySelectorAll('.info-modal').forEach(p => {
            p.classList.remove('active');
        });
        
        panel.classList.add('active');
        overlay.classList.add('active');
        
        // Update URL hash for direct linking
        const hashMap = {
            'resourcesModal': 'resources',
            'aboutModal': 'about',
            'helpModal': 'help'
        };
        if (hashMap[panelId]) {
            window.history.pushState(null, null, '#' + hashMap[panelId]);
        }
    }
}

function closePanel(panelId) {
    const panel = document.getElementById(panelId);
    const overlay = document.getElementById('panelOverlay');
    
    if (panel) {
        panel.classList.remove('active');
    }
    if (overlay) {
        overlay.classList.remove('active');
    }
}

function closeAllPanels() {
    document.querySelectorAll('.info-modal').forEach(panel => {
        panel.classList.remove('active');
    });
    const overlay = document.getElementById('panelOverlay');
    if (overlay) {
        overlay.classList.remove('active');
    }
    
    // Clear URL hash
    if (window.location.hash) {
        window.history.pushState(null, null, window.location.pathname);
    }
}

// Footer toggle function
function toggleFooter() {
    const toggle = document.getElementById('footerToggle');
    const details = document.getElementById('footerDetails');
    
    if (toggle && details) {
        toggle.classList.toggle('expanded');
        details.classList.toggle('expanded');
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', async () => {
    await loadConfig(); // Load API keys first
    initializeDragAndDrop();
    loadCSV();
    
    // Check for hash in URL and open corresponding panel
    const hash = window.location.hash.substring(1); // Remove the #
    if (hash === 'resources') {
        openPanel('resourcesModal');
    } else if (hash === 'about') {
        openPanel('aboutModal');
    } else if (hash === 'help') {
        openPanel('helpModal');
    }
    
    // Setup panel buttons
    const resourcesBtn = document.getElementById('resourcesBtn');
    const aboutBtn = document.getElementById('aboutBtn');
    const helpBtn = document.getElementById('helpBtn');
    
    if (resourcesBtn) {
        resourcesBtn.addEventListener('click', () => openPanel('resourcesModal'));
    }
    if (aboutBtn) {
        aboutBtn.addEventListener('click', () => openPanel('aboutModal'));
    }
    if (helpBtn) {
        helpBtn.addEventListener('click', () => openPanel('helpModal'));
    }
    
    // Setup panel close buttons
    document.querySelectorAll('.info-modal-close').forEach(closeBtn => {
        closeBtn.addEventListener('click', function() {
            const panelId = this.getAttribute('data-modal');
            closePanel(panelId);
        });
    });
    
    // Close panels when clicking overlay
    const overlay = document.getElementById('panelOverlay');
    if (overlay) {
        overlay.addEventListener('click', closeAllPanels);
    }
    
    // Close panels with Escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            closeAllPanels();
        }
    });
    
    // Setup footer toggle
    const footerToggle = document.getElementById('footerToggle');
    if (footerToggle) {
        footerToggle.addEventListener('click', toggleFooter);
    }
    
    // Clear hash when clicking on main content (not in panels)
    document.addEventListener('click', (e) => {
        // Check if click is outside any panel and not on a panel button
        const isInsidePanel = e.target.closest('.info-modal');
        const isPanelButton = e.target.closest('.nav-item');
        const isOverlay = e.target.id === 'panelOverlay';
        
        if (!isInsidePanel && !isPanelButton && !isOverlay && window.location.hash) {
            // Only clear if a panel hash exists
            const hash = window.location.hash.substring(1);
            if (hash === 'resources' || hash === 'about' || hash === 'help') {
                window.history.pushState(null, null, window.location.pathname);
            }
        }
    });
});

// Made with Bob
