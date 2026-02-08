let sitesData = [];
let currentSite = null;
let currentImages = [];
let currentImageIndex = 0;
let activeTab = 'details'; // Track which tab is active
let selectedSites = new Set(); // Track selected sites for multi-select
let returnToHotel = false; // Track if return to hotel is enabled
let currentRouteControl = null; // Track current route control
let routeSegments = []; // Store route segment data

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
function displaySites(sites) {
    const list = document.getElementById('siteList');
    
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
        
        const isSelected = selectedSites.has(site.code);
        return `
            <li class="site-item ${isSelected ? 'active' : ''}" data-code="${site.code}" onclick="selectSite('${site.code}', event)">
                <div class="site-code">${site.code}</div>
                <div class="site-name">${site.denominacion || 'N/A'}</div>
                <div>
                    <span class="site-value">VT: ${site.valor_turistico}</span>
                    <span class="site-privacy">${site.confidencialidad}</span>
                    ${eclipseLabel}
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
        if (selectedSites.has(code)) {
            selectedSites.delete(code);
        } else {
            selectedSites.add(code);
        }
        
        // Update visual state
        const item = document.querySelector(`[data-code="${code}"]`);
        if (item) {
            item.classList.toggle('active');
        }
        
        // If we have selected sites, update the map
        if (selectedSites.size > 0 && activeTab === 'map') {
            updateMapWithMultipleSites();
        }
    } else {
        // Single select - clear previous selections
        selectedSites.clear();
        selectedSites.add(code);
        currentSite = site;

        // Update active state
        document.querySelectorAll('.site-item').forEach(item => {
            item.classList.remove('active');
        });
        document.querySelector(`[data-code="${code}"]`).classList.add('active');

        // Display site details
        displaySiteDetails(site);
    }
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
    
    content.innerHTML = `
        <div class="site-details">
            <div class="detail-header">
                <h2>${site.denominacion || site.code}</h2>
                <div style="display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap;">
                    <a href="${site.url}" target="_blank" class="link-button">🪨 View on IGME Website</a>
                    <a href="${mapsUrl}" target="_blank" class="link-button maps">📍 Open in Google Maps</a>
                    <a href="${shademapUrl}" target="_blank" class="link-button shademap">🌄 View on Shademap</a>
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

            <div class="tabs">
                <button class="tab ${activeTab === 'details' ? 'active' : ''}" onclick="switchTab('details')">📋 Details</button>
                <button class="tab ${activeTab === 'map' ? 'active' : ''}" onclick="switchTab('map')">🗺️ Map</button>
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
                        <div class="loading">Loading images from IGME...</div>
                    </div>
                </div>
            </div>

            <div id="mapTab" class="tab-content ${activeTab === 'map' ? 'active' : ''}">
                <div id="mapContainer"></div>
                <div id="routeSummary" style="display: none;">
                    <h4>Route Summary</h4>
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
    `;
    
    // Load images from IGME
    loadSiteImages(site);
    
    // Initialize map when map tab is shown
    initializeMap(site, mapsUrl, shademapUrl, eclipseUrl);
}

// Update map with multiple selected sites
function updateMapWithMultipleSites() {
    if (selectedSites.size === 0) return;
    
    // Get all selected site objects
    const sites = Array.from(selectedSites).map(code =>
        sitesData.find(s => s.code === code)
    ).filter(s => s && s.latitude !== 'N/A' && s.longitude !== 'N/A');
    
    if (sites.length === 0) return;
    
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
        
        // Add site marker with numbered label
        const markerIcon = L.divIcon({
            html: `<div style="background: #007bff; color: white; border-radius: 50%; width: 30px; height: 30px; display: flex; align-items: center; justify-content: center; font-weight: bold; border: 2px solid white; box-shadow: 0 2px 4px rgba(0,0,0,0.3);">${index + 1}</div>`,
            className: 'numbered-marker',
            iconSize: [30, 30],
            iconAnchor: [15, 15]
        });
        
        L.marker([lat, lon], { icon: markerIcon })
            .addTo(currentMap)
            .bindPopup(popupContent);
    });
    
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
                displayRouteSummary(totalDistance, totalTime);
                // Fit map to show all route coordinates
                if (allRouteBounds.isValid()) {
                    currentMap.fitBounds(allRouteBounds, { padding: [80, 80] });
                }
            }
        }).addTo(currentMap);
    }
}

// Display route summary
function displayRouteSummary(totalDistance, totalTime) {
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
    
    document.getElementById('routeSegments').innerHTML = segmentHTML;
    
    document.getElementById('routeTotal').innerHTML = `
        <div><strong>Total Distance:</strong> ${(totalDistance / 1000).toFixed(1)} km</div>
        <div><strong>Total Time:</strong> ${Math.round(totalTime / 60)} min (${(totalTime / 3600).toFixed(1)} hrs)</div>
    `;
    
    document.getElementById('routeSummary').style.display = 'block';
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

// Toggle return to hotel
function toggleReturnToHotel() {
    returnToHotel = document.getElementById('returnToHotel').checked;
    if (selectedSites.size > 0) {
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
    const lat = parseFloat(site.latitude);
    const lon = parseFloat(site.longitude);

    // Reset map initialization flag when switching sites
    mapInitialized = false;

    // Function to create/update the map
    function createMap() {
        // Remove existing map if any
        if (currentMap) {
            currentMap.remove();
            currentMap = null;
            currentRoutingControl = null;
        }

        setTimeout(() => {
            // Calculate bounds to fit both hotel and site
            const bounds = L.latLngBounds(
                [HOTEL_LAT, HOTEL_LON],
                [lat, lon]
            );
            
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

            // Add site marker with popup
            const popupContent = `
                <div style="min-width: 200px;">
                    <h4 style="margin: 0 0 8px 0; font-size: 0.95rem;">${site.denominacion || site.code}</h4>
                    <a href="${site.url}" target="_blank">🪨 View on IGME Website</a>
                    <a href="${mapsUrl}" target="_blank" class="maps">📍 Open in Google Maps</a>
                    <a href="${shademapUrl}" target="_blank" class="shademap">🌄 View on Shademap</a>
                    <a href="${eclipseUrl}" target="_blank" class="eclipse">🌑 Eclipse 2026 View</a>
                </div>
            `;

            L.marker([lat, lon])
                .addTo(currentMap)
                .bindPopup(popupContent);

            // Add routing
            currentRoutingControl = L.Routing.control({
                waypoints: [
                    L.latLng(HOTEL_LAT, HOTEL_LON),
                    L.latLng(lat, lon)
                ],
                routeWhileDragging: false,
                addWaypoints: false,
                draggableWaypoints: false,
                fitSelectedRoutes: false,
                showAlternatives: false,
                lineOptions: {
                    styles: [{ color: '#007bff', weight: 4, opacity: 0.7 }]
                },
                createMarker: function() { return null; }, // Don't create default markers
                router: L.Routing.osrmv1({
                    serviceUrl: 'https://router.project-osrm.org/route/v1'
                })
            }).addTo(currentMap);
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
}

// Load data on page load
loadCSV();

// Made with Bob
