/**
 * Map Handler Module
 * Handles Leaflet map initialization, routing, and route management
 */

import { CONFIG } from './config.js';
import { appState } from './state.js';
import { displaySiteDetails } from './site-details.js';

// Global map instance
let currentMap = null;

/**
 * Create map with single or multiple sites
 * @param {Array} sites - Array of site objects to display
 * @param {Object} options - Map options
 */
export function createMapWithSites(sites, options = {}) {
    const { showRouting = true, showRouteSummary = false } = options;
    
    // Remove existing map
    if (currentMap) {
        currentMap.remove();
        currentMap = null;
    }
    
    // Calculate bounds for all sites plus hotel
    const bounds = L.latLngBounds();
    bounds.extend(CONFIG.HOTEL_COORDS);
    sites.forEach(site => {
        bounds.extend([parseFloat(site.latitude), parseFloat(site.longitude)]);
    });
    
    // Create map with a small delay to ensure container is ready
    setTimeout(() => {
        currentMap = L.map('mapContainer').fitBounds(bounds, { padding: [50, 50] });
        
        L.tileLayer(CONFIG.MAP.TILE_LAYER, {
            attribution: CONFIG.MAP.ATTRIBUTION,
            maxZoom: 19
        }).addTo(currentMap);
        
        // Add hotel marker
        const hotelIcon = L.divIcon({
            html: '<div style="font-size: 24px;">🏨</div>',
            className: 'hotel-marker',
            iconSize: [30, 30],
            iconAnchor: [15, 15]
        });
        
        L.marker(CONFIG.HOTEL_COORDS, { icon: hotelIcon })
            .addTo(currentMap)
            .bindPopup(`<b>${CONFIG.HOTEL_NAME}</b><br>Starting point`);
        
        // Add markers for each site
        sites.forEach((site, index) => {
            const lat = parseFloat(site.latitude);
            const lon = parseFloat(site.longitude);
            
            // Create popup content with links
            const popupContent = createMarkerPopup(site, lat, lon);
            
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
            
            // Add click handler to update details
            marker.on('click', () => {
                appState.setCurrentSite(site);
                
                // Update sidebar selection
                document.querySelectorAll('.site-item').forEach(item => {
                    item.classList.remove('active');
                });
                const siteItem = document.querySelector(`[data-code="${site.code}"]`);
                if (siteItem) {
                    siteItem.classList.add('active');
                }
                
                // Update details tab content (without switching tabs)
                updateDetailsTabOnly(site);
            });
        });
        
        // Only create routing if requested
        if (showRouting) {
            // Add another small delay to ensure map is fully rendered before routing
            setTimeout(() => {
                createRoute(sites, showRouteSummary);
            }, 100);
        }
    }, 50);
}

/**
 * Create marker popup content
 * @param {Object} site - Site object
 * @param {number} lat - Latitude
 * @param {number} lon - Longitude
 * @returns {string} HTML string
 */
function createMarkerPopup(site, lat, lon) {
    const mapsUrl = `https://www.google.com/maps?q=${lat},${lon}`;
    const coordsBase64 = btoa(`${lat}, ${lon}`);
    const shademapUrl = `https://shademap.app/@${lat},${lon},17z,1786559455614t,0b,0p,0m!1786512158844!1786563246912,${coordsBase64}!${lat}!${lon}`;
    const x = lon * 20037508.34 / 180;
    const y = Math.log(Math.tan((90 + lat) * Math.PI / 360)) / (Math.PI / 180);
    const yMercator = y * 20037508.34 / 180;
    const eclipseUrl = `https://visualizadores.ign.es/eclipses/2026?center=${x},${yMercator}&zoom=16&srs=EPSG:3857`;
    const darkSkySitesUrl = `https://www.darkskysites.com/?lat=${lat}&lng=${lon}&zoom=8`;
    
    // Check if IGME URL is valid
    const hasValidIgmeUrl = site.url && site.url !== 'N/A' && site.url.trim() !== '';
    const igmeLink = hasValidIgmeUrl
        ? `<a href="${site.url}" target="_blank">🪨 View on IGME Website</a>`
        : `<a href="#" class="inactive" title="No IGME website available">🪨 View on IGME Website</a>`;
    
    return `
        <div style="min-width: 200px;">
            <h4 style="margin: 0 0 8px 0; font-size: 0.95rem;">${site.denominacion || site.code}</h4>
            ${igmeLink}
            <a href="${mapsUrl}" target="_blank" class="maps">📍 Open in Google Maps</a>
            <a href="${shademapUrl}" target="_blank" class="shademap">🌄 View on Shademap</a>
            <a href="${eclipseUrl}" target="_blank" class="eclipse">🌑 Eclipse 2026 View</a>
            <a href="${darkSkySitesUrl}" target="_blank" class="darksky">🌌 Dark Sky Sites</a>
        </div>
    `;
}

/**
 * Update only the details tab content without switching tabs
 * @param {Object} site - Site object
 */
function updateDetailsTabOnly(site) {
    // This would update the details tab content
    // For now, just update the full view
    displaySiteDetails(site);
}

/**
 * Create route between waypoints
 * @param {Array} sites - Array of site objects
 * @param {boolean} showRouteSummary - Whether to show route summary
 */
function createRoute(sites, showRouteSummary) {
    // Store sites in appState for KML export
    appState.currentRouteSites = sites;
    
    // Create waypoints list
    const waypoints = [
        L.latLng(CONFIG.HOTEL_COORDS[0], CONFIG.HOTEL_COORDS[1]),
        ...sites.map(site => L.latLng(parseFloat(site.latitude), parseFloat(site.longitude)))
    ];
    
    // Add return to hotel if enabled
    if (appState.returnToHotel) {
        waypoints.push(L.latLng(CONFIG.HOTEL_COORDS[0], CONFIG.HOTEL_COORDS[1]));
    }
    
    // Create segments between waypoints
    const waypointNames = [CONFIG.HOTEL_NAME, ...sites.map((s, i) => `${i + 1}. ${s.denominacion || s.code}`)];
    if (appState.returnToHotel) {
        waypointNames.push(CONFIG.HOTEL_NAME);
    }
    
    // Colors for different segments
    const segmentColors = ['#007bff', '#28a745', '#dc3545', '#ffc107', '#6f42c1', '#fd7e14', '#17a2b8', '#e83e8c'];
    
    // Clear previous segments
    const routeSegments = [];
    let totalDistance = 0;
    let totalTime = 0;
    let segmentsCompleted = 0;
    const totalSegments = waypoints.length - 1;
    const allRouteBounds = L.latLngBounds();
    
    // Create individual route for each segment
    for (let i = 0; i < waypoints.length - 1; i++) {
        const color = segmentColors[i % segmentColors.length];
        const segmentIndex = i;
        
        const routingControl = L.Routing.control({
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
        });
        
        routingControl.on('routesfound', function(e) {
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
                appState.setRouteSegments(routeSegments);
                
                if (showRouteSummary) {
                    displayRouteSummary(totalDistance, totalTime, routeSegments);
                }
                
                // Fit map to show all route coordinates
                if (allRouteBounds.isValid()) {
                    currentMap.invalidateSize();
                    currentMap.fitBounds(allRouteBounds, { padding: [50, 50], maxZoom: 15 });
                }
            }
        });
        
        // Explicitly add the routing control to the map
        routingControl.addTo(currentMap);
    }
}

/**
 * Display route summary with segments
 * @param {number} totalDistance - Total distance in meters
 * @param {number} totalTime - Total time in seconds
 * @param {Array} routeSegments - Array of route segment objects
 */
function displayRouteSummary(totalDistance, totalTime, routeSegments) {
    const routeSummary = document.getElementById('routeSummary');
    const routeSegmentsEl = document.getElementById('routeSegments');
    const routeTotal = document.getElementById('routeTotal');
    const routeSummaryContent = document.getElementById('routeSummaryContent');
    
    if (!routeSummary || !routeSegmentsEl || !routeTotal || !routeSummaryContent) return;
    
    // Build header with collapse button and drag handle - insert at top of routeSummary
    const headerHTML = `
        <div class="route-summary-header" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem; cursor: move; padding: 0.5rem; background: #f8f9fa; border-radius: 4px; user-select: none;">
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <span style="cursor: grab; font-size: 1.2rem;">⋮⋮</span>
                <strong>Route Summary</strong>
            </div>
            <button id="routeCollapseBtn" style="background: none; border: none; font-size: 1.2rem; cursor: pointer; padding: 0.25rem 0.5rem;">▼</button>
        </div>
    `;
    
    // Insert header at the beginning of routeSummary
    if (!routeSummary.querySelector('.route-summary-header')) {
        routeSummary.insertAdjacentHTML('afterbegin', headerHTML);
    }
    
    // Build reorderable site list (only for multi-site routes)
    let siteListHTML = '';
    if (appState.selectedSites.length > 1) {
        siteListHTML = `
            <div class="reorder-sites-container">
                <div class="reorder-sites-header" style="cursor: pointer;">
                    <span id="reorderToggleIcon">▶</span> 📍 Route Order (drag to reorder)
                </div>
                <ul class="reorder-sites-list" id="reorderSitesList" style="display: none;">
        `;
        appState.selectedSites.forEach((code, index) => {
            const site = appState.getSiteByCode(code);
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
    
    // Build segments HTML
    let segmentHTML = '';
    routeSegments.forEach((segment, i) => {
        segmentHTML += `
            <div class="route-segment" data-segment="${i}" style="cursor: pointer; border-left-color: ${segment.color};">
                <div class="route-segment-header">${segment.from} → ${segment.to}</div>
                <div class="route-segment-details">
                    ${(segment.distance / 1000).toFixed(1)} km • ${Math.round(segment.time / 60)} min
                </div>
            </div>
        `;
    });
    
    routeSegmentsEl.innerHTML = siteListHTML + segmentHTML;
    
    // Build Google Maps URL for the entire route
    let googleMapsUrl = 'https://www.google.com/maps/dir/';
    googleMapsUrl += `${CONFIG.HOTEL_COORDS[0]},${CONFIG.HOTEL_COORDS[1]}/`;
    appState.selectedSites.forEach(code => {
        const site = appState.getSiteByCode(code);
        if (site) {
            googleMapsUrl += `${site.latitude},${site.longitude}/`;
        }
    });
    if (appState.returnToHotel) {
        googleMapsUrl += `${CONFIG.HOTEL_COORDS[0]},${CONFIG.HOTEL_COORDS[1]}/`;
    }
    
    routeTotal.innerHTML = `
        <div><strong>Total Distance:</strong> ${(totalDistance / 1000).toFixed(1)} km</div>
        <div><strong>Total Time:</strong> ${Math.round(totalTime / 60)} min (${(totalTime / 3600).toFixed(1)} hrs)</div>
        <div style="display: flex; gap: 0.5rem; margin-top: 0.75rem;">
            <a href="${googleMapsUrl}" target="_blank" class="google-maps-route-btn">
                📍 Open in Google Maps
            </a>
            <button id="exportKmlBtn" class="export-kml-btn">
                💾 Export as KML
            </button>
        </div>
    `;
    
    routeSummary.style.display = 'block';
    
    // Setup event listeners
    setupRouteListeners();
    
    // Setup collapse button (must be after HTML is inserted)
    setupCollapseButton();
    
    // Make route summary draggable (must be after HTML is inserted)
    makeRouteSummaryDraggable(routeSummary);
}

/**
 * Make route summary panel draggable
 * @param {HTMLElement} element - Route summary element
 */
function makeRouteSummaryDraggable(element) {
    let isDragging = false;
    let currentX;
    let currentY;
    let initialX;
    let initialY;
    let xOffset = 0;
    let yOffset = 0;
    
    // Make it positioned absolutely when dragging starts
    element.style.position = 'absolute';
    element.style.zIndex = '1001';
    
    // Set initial position (top-left of map container)
    element.style.top = '10px';
    element.style.left = '10px';
    
    const header = element.querySelector('.route-summary-header');
    if (!header) return;
    
    header.addEventListener('mousedown', dragStart);
    document.addEventListener('mousemove', drag);
    document.addEventListener('mouseup', dragEnd);
    
    function dragStart(e) {
        // Only drag if clicking on the header (not the collapse button)
        if (e.target.id === 'routeCollapseBtn' || e.target.closest('#routeCollapseBtn')) {
            return;
        }
        
        initialX = e.clientX - xOffset;
        initialY = e.clientY - yOffset;
        
        if (e.target === header || header.contains(e.target)) {
            isDragging = true;
            header.style.cursor = 'grabbing';
        }
    }
    
    function drag(e) {
        if (isDragging) {
            e.preventDefault();
            
            currentX = e.clientX - initialX;
            currentY = e.clientY - initialY;
            
            xOffset = currentX;
            yOffset = currentY;
            
            setTranslate(currentX, currentY, element);
        }
    }
    
    function dragEnd() {
        if (isDragging) {
            initialX = currentX;
            initialY = currentY;
            isDragging = false;
            header.style.cursor = 'move';
        }
    }
    
    function setTranslate(xPos, yPos, el) {
        el.style.transform = `translate(${xPos}px, ${yPos}px)`;
    }
}

/**
 * Setup collapse/expand button for route summary
 */
function setupCollapseButton() {
    const collapseBtn = document.getElementById('routeCollapseBtn');
    const routeSummaryContent = document.getElementById('routeSummaryContent');
    
    if (!collapseBtn || !routeSummaryContent) return;
    
    let isCollapsed = false;
    
    collapseBtn.addEventListener('click', (e) => {
        e.stopPropagation(); // Prevent dragging when clicking collapse button
        
        isCollapsed = !isCollapsed;
        
        if (isCollapsed) {
            routeSummaryContent.style.display = 'none';
            collapseBtn.textContent = '▶';
        } else {
            routeSummaryContent.style.display = 'block';
            collapseBtn.textContent = '▼';
        }
    });
}

/**
 * Setup event listeners for route interactions
 */
function setupRouteListeners() {
    // Reorder toggle
    const reorderHeader = document.querySelector('.reorder-sites-header');
    if (reorderHeader) {
        reorderHeader.addEventListener('click', toggleReorderList);
    }
    
    // Segment click handlers
    document.querySelectorAll('.route-segment').forEach(segment => {
        segment.addEventListener('click', (e) => {
            const index = parseInt(e.currentTarget.dataset.segment);
            highlightSegment(index);
        });
    });
    
    // Export KML button
    const exportBtn = document.getElementById('exportKmlBtn');
    if (exportBtn) {
        exportBtn.addEventListener('click', (e) => {
            e.preventDefault();
            exportRouteAsKML();
        });
    }
    
    // Initialize drag-and-drop for reordering if we have multiple sites
    if (appState.selectedSites.length > 1) {
        initializeReorderDragAndDrop();
    }
}

/**
 * Toggle reorder list visibility
 */
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

/**
 * Highlight a specific segment and show directions
 * @param {number} index - Segment index
 */
function highlightSegment(index) {
    const segment = appState.routeSegments[index];
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
                <div style="font-size: 0.7rem; color: #6c757d; margin-bottom: 0.25rem;">SEGMENT</div>
                <div style="font-size: 1rem; font-weight: 600; color: #2c3e50;">${index + 1}</div>
            </div>
        </div>
        <div style="background: white; padding: 0.75rem; border-radius: 4px;">
            <div style="font-weight: 600; margin-bottom: 0.5rem;">Turn-by-turn Directions:</div>
            <ol style="margin: 0; padding-left: 1.5rem;">
    `;
    
    if (segment.instructions && segment.instructions.length > 0) {
        segment.instructions.forEach(instruction => {
            directionsHTML += `<li style="margin-bottom: 0.5rem;">${instruction.text}</li>`;
        });
    } else {
        directionsHTML += '<li>No detailed directions available</li>';
    }
    
    directionsHTML += '</ol></div>';
    
    directionsContent.innerHTML = directionsHTML;
    directionsPanel.style.display = 'block';
}

/**
 * Export route as KML file
 */
function exportRouteAsKML() {
    // Use currentRouteSites if available, otherwise fall back to selectedSites
    const sites = appState.currentRouteSites || appState.selectedSites.map(code => appState.getSiteByCode(code)).filter(s => s);
    
    if (!sites || sites.length === 0) {
        alert('No route to export. Please create a route first by selecting sites.');
        return;
    }
    
    // Build KML content
    let kml = `<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>Spain Eclipse Sites Route</name>
    <description>Route visiting ${sites.length} geological sites</description>
    
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
      <name>${CONFIG.HOTEL_NAME} (Start)</name>
      <description>Starting point</description>
      <styleUrl>#hotelIcon</styleUrl>
      <Point>
        <coordinates>${CONFIG.HOTEL_COORDS[1]},${CONFIG.HOTEL_COORDS[0]},0</coordinates>
      </Point>
    </Placemark>
    
`;
    
    // Add each site as a placemark
    sites.forEach((site, index) => {
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
    });
    
    // Add return to hotel if enabled
    if (appState.returnToHotel) {
        kml += `    <!-- Return to hotel -->
    <Placemark>
      <name>${CONFIG.HOTEL_NAME} (Return)</name>
      <description>End point</description>
      <styleUrl>#hotelIcon</styleUrl>
      <Point>
        <coordinates>${CONFIG.HOTEL_COORDS[1]},${CONFIG.HOTEL_COORDS[0]},0</coordinates>
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
          ${CONFIG.HOTEL_COORDS[1]},${CONFIG.HOTEL_COORDS[0]},0
`;
    
    sites.forEach(site => {
        kml += `          ${site.longitude},${site.latitude},0\n`;
    });
    
    if (appState.returnToHotel) {
        kml += `          ${CONFIG.HOTEL_COORDS[1]},${CONFIG.HOTEL_COORDS[0]},0\n`;
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
    a.download = `spain-eclipse-route-${sites.length}-sites.kml`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

/**
 * Initialize drag-and-drop for reordering sites
 */
function initializeReorderDragAndDrop() {
    const list = document.getElementById('reorderSitesList');
    if (!list) return;
    
    let draggedItem = null;
    
    list.querySelectorAll('.reorder-site-item').forEach(item => {
        item.addEventListener('dragstart', (e) => {
            draggedItem = item;
            e.dataTransfer.effectAllowed = 'move';
            item.style.opacity = '0.5';
        });
        
        item.addEventListener('dragend', () => {
            item.style.opacity = '1';
        });
        
        item.addEventListener('dragover', (e) => {
            e.preventDefault();
            e.dataTransfer.dropEffect = 'move';
            
            if (draggedItem !== item) {
                const rect = item.getBoundingClientRect();
                const midpoint = rect.top + rect.height / 2;
                
                if (e.clientY < midpoint) {
                    list.insertBefore(draggedItem, item);
                } else {
                    list.insertBefore(draggedItem, item.nextSibling);
                }
            }
        });
    });
    
    list.addEventListener('drop', (e) => {
        e.preventDefault();
        
        // Update the order in state
        const newOrder = Array.from(list.querySelectorAll('.reorder-site-item'))
            .map(item => item.dataset.code);
        
        appState.selectedSites = newOrder;
        
        // Recreate the route with new order
        updateMapWithMultipleSites();
    });
}

/**
 * Update map with multiple selected sites
 */
export function updateMapWithMultipleSites() {
    if (appState.selectedSites.length === 0) return;
    
    // Get all selected site objects (in order)
    const sites = appState.selectedSites
        .map(code => appState.getSiteByCode(code))
        .filter(s => s && s.latitude !== 'N/A' && s.longitude !== 'N/A');
    
    if (sites.length === 0) return;
    
    createMapWithSites(sites, { showRouting: true, showRouteSummary: true });
}

/**
 * Initialize map for single site
 * @param {Object} site - Site object
 */
export function initializeSingleSiteMap(site) {
    if (!site || site.latitude === 'N/A' || site.longitude === 'N/A') {
        const mapContainer = document.getElementById('mapContainer');
        if (mapContainer) {
            mapContainer.innerHTML = '<div class="loading">No coordinates available for this site</div>';
        }
        return;
    }
    
    createMapWithSites([site], { showRouting: true, showRouteSummary: true });
}

// Made with Bob
