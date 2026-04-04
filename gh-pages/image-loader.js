/**
 * Image Loader Module - GitHub Pages Version
 * Handles loading and displaying IGME site images from static cache
 */

import { CONFIG } from './config.js';
import { appState } from '../static/js/state.js';
import { openImageModal } from '../static/js/modal-handler.js';

/**
 * Load images for a site from cached IGME images
 * @param {Object} site - Site object with code and url
 * @returns {Promise<Array>} Array of image URLs
 */
export async function loadSiteImages(site) {
    const container = document.getElementById('imagesContainer');
    
    if (!container) {
        console.warn('Images container not found');
        return [];
    }
    
    // Show loading state
    container.innerHTML = '<div class="loading">Loading images...</div>';
    
    try {
        // Try to load from cached IGME HTML metadata (has descriptions)
        const images = await loadFromIgmeCache(site);
        
        if (images && images.length > 0) {
            const imageUrls = images.map(img => img.src);
            appState.setCurrentImages(imageUrls);
            
            // Render image grid with descriptions
            container.innerHTML = images.map((img, index) => `
                <div class="image-card">
                    <img src="${img.src}"
                         alt="${img.alt || 'Site image'}"
                         data-index="${index}"
                         class="site-image"
                         onerror="this.parentElement.style.display='none'">
                    <div class="image-caption">${img.alt || `Image ${index + 1}`}</div>
                </div>
            `).join('');
            
            // Setup click handlers for modal
            const imageElements = container.querySelectorAll('.site-image');
            imageElements.forEach(img => {
                img.addEventListener('click', () => {
                    const index = parseInt(img.dataset.index);
                    openImageModal(index);
                });
            });
            
            console.log('[Static] Loaded', images.length, 'cached images for', site.code);
            return images;
        } else {
            container.innerHTML = '<div class="no-images">No images available for this site</div>';
            return [];
        }
        
    } catch (error) {
        console.error('Error loading images:', error);
        container.innerHTML = '<div class="error">Error loading images</div>';
        return [];
    }
}

/**
 * Load images from IGME HTML cache (includes descriptions)
 * @param {Object} site - Site object with url
 * @returns {Promise<Array>} Array of image objects with src and alt
 */
async function loadFromIgmeCache(site) {
    if (!site.url) {
        return null;
    }
    
    // Calculate MD5 hash of the URL (same as Python backend)
    const hash = await md5(site.url);
    const jsonPath = `data/cache/igme_html/${hash}.json`;
    
    try {
        const response = await fetch(jsonPath);
        if (response.ok) {
            const data = await response.json();
            return data.images || [];
        }
    } catch (e) {
        console.log('No cached IGME metadata found for', site.code);
    }
    
    return null;
}

/**
 * Calculate MD5 hash of a string (for cache key)
 * @param {string} str - String to hash
 * @returns {Promise<string>} MD5 hash
 */
async function md5(str) {
    const encoder = new TextEncoder();
    const data = encoder.encode(str);
    const hashBuffer = await crypto.subtle.digest('MD5', data);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
}

// Made with Bob
