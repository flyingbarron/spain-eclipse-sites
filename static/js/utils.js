/**
 * Utility Functions Module
 * Common helper functions used throughout the application
 */

/**
 * Convert decimal degrees to DMS (Degrees, Minutes, Seconds)
 * @param {number} decimal - Decimal degrees
 * @param {boolean} isLat - True if latitude, false if longitude
 * @returns {string} Formatted DMS string
 */
export function decimalToDMS(decimal, isLat) {
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

/**
 * Parse a single CSV line handling quoted fields
 * @param {string} line - CSV line to parse
 * @returns {Array<string>} Array of field values
 */
export function parseCSVLine(line) {
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

/**
 * Get cloud coverage emoji and class based on percentage
 * @param {number} cloudPct - Cloud coverage percentage
 * @returns {Object} Object with emoji and class
 */
export function getCloudInfo(cloudPct) {
    let cloudEmoji = '☀️';
    let cloudClass = 'low';
    
    if (cloudPct >= 60) {
        cloudEmoji = '☁️';
        cloudClass = 'high';
    } else if (cloudPct >= 30) {
        cloudEmoji = '⛅';
        cloudClass = 'medium';
    }
    
    return { emoji: cloudEmoji, class: cloudClass };
}

/**
 * Get eclipse visibility info
 * @param {string} visibility - Eclipse visibility status
 * @returns {Object} Object with class and text
 */
export function getEclipseInfo(visibility) {
    let eclipseClass = 'unknown';
    let eclipseText = '';
    
    if (visibility === 'visible') {
        eclipseClass = 'visible';
        eclipseText = '🌑 Visible';
    } else if (visibility === 'not_visible') {
        eclipseClass = 'not-visible';
        eclipseText = '🌑 Not visible';
    } else if (visibility && visibility !== 'unknown') {
        eclipseClass = 'unknown';
        eclipseText = '🌑 ' + visibility;
    }
    
    return { class: eclipseClass, text: eclipseText };
}

/**
 * Get URL parameter value
 * @param {string} param - Parameter name
 * @returns {string|null} Parameter value or null
 */
export function getUrlParameter(param) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(param);
}

/**
 * Set URL parameter without reloading page
 * @param {string} param - Parameter name
 * @param {string} value - Parameter value
 */
export function setUrlParameter(param, value) {
    const url = new URL(window.location);
    if (value) {
        url.searchParams.set(param, value);
    } else {
        url.searchParams.delete(param);
    }
    window.history.pushState({}, '', url);
}

/**
 * Generate shareable URL for a site
 * @param {string} siteCode - Site code
 * @returns {string} Full URL with site parameter
 */
export function generateShareUrl(siteCode) {
    const url = new URL(window.location.origin + window.location.pathname);
    url.searchParams.set('site', siteCode);
    return url.toString();
}

/**
 * Copy text to clipboard
 * @param {string} text - Text to copy
 * @returns {Promise<boolean>} True if successful
 */
export async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        return true;
    } catch (err) {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.position = 'fixed';
        textArea.style.left = '-999999px';
        document.body.appendChild(textArea);
        textArea.select();
        try {
            document.execCommand('copy');
            document.body.removeChild(textArea);
            return true;
        } catch (err) {
            document.body.removeChild(textArea);
            return false;
        }
    }
}

// Made with Bob
