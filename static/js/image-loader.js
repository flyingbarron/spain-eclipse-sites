/**
 * Image Loader Module
 * Handles loading and displaying IGME site images
 */

import { CONFIG } from './config.js';
import { appState } from './state.js';
import { openImageModal } from './modal-handler.js';

/**
 * Load images for a site from IGME
 * Tries API endpoint first (local dev), then falls back to static cache (GitHub Pages)
 * @param {Object} site - Site object with URL and code
 * @returns {Promise<Array>} Array of image objects
 */
export async function loadSiteImages(site) {
    const container = document.getElementById('imagesContainer');
    
    if (!container) {
        console.warn('Images container not found');
        return [];
    }
    
    // Show loading state
    container.innerHTML = '<div class="loading">Loading images...</div>';
    
    // Try API endpoint first (local development with Python backend)
    try {
        const response = await fetch(`${CONFIG.API.IMAGES}?url=${encodeURIComponent(site.url)}`);
        
        if (response.ok) {
            const data = await response.json();
            
            if (data.images && data.images.length > 0) {
                // Store proxied image URLs in state
                const imageUrls = data.images.map(img =>
                    `${CONFIG.API.PROXY_IMAGE}?url=${encodeURIComponent(img.src)}`
                );
                appState.setCurrentImages(imageUrls);
                
                // Render image grid
                container.innerHTML = data.images.map((img, index) => `
                    <div class="image-card">
                        <img src="${CONFIG.API.PROXY_IMAGE}?url=${encodeURIComponent(img.src)}"
                             alt="${img.alt || `${site.denominacion || site.code} - Image ${index + 1}`}"
                             data-index="${index}"
                             class="site-image"
                             role="button"
                             tabindex="0"
                             aria-label="View full size image ${index + 1} of ${data.images.length}"
                             onerror="this.parentElement.style.display='none'">
                        <div class="image-caption">${img.alt || `Image ${index + 1}`}</div>
                    </div>
                `).join('');
                
                // Add click and keyboard listeners to images
                container.querySelectorAll('.site-image').forEach(img => {
                    img.addEventListener('click', () => {
                        const index = parseInt(img.dataset.index);
                        openImageModal(index);
                    });
                    img.addEventListener('keydown', (e) => {
                        if (e.key === 'Enter' || e.key === ' ') {
                            e.preventDefault();
                            const index = parseInt(img.dataset.index);
                            openImageModal(index);
                        }
                    });
                });
                
                console.log('[API] Loaded', data.images.length, 'images for', site.code);
                return data.images;
            }
        }
    } catch (error) {
        console.log('[API] Not available, trying static cache...');
    }
    
    // Fall back to static cached images (GitHub Pages mode)
    try {
        const imageDir = `data/cache/igme_images/${site.code}/`;
        const imageUrls = await findCachedImages(site.code, imageDir);
        
        if (imageUrls.length > 0) {
            appState.setCurrentImages(imageUrls);
            
            // Render image grid
            container.innerHTML = imageUrls.map((url, index) => `
                <div class="image-card">
                    <img src="${url}"
                         alt="${site.denominacion || site.code} - Image ${index + 1} of ${imageUrls.length}"
                         data-index="${index}"
                         class="site-image"
                         role="button"
                         tabindex="0"
                         aria-label="View full size image ${index + 1} of ${imageUrls.length}"
                         onerror="this.parentElement.style.display='none'">
                    <div class="image-caption">Image ${index + 1}</div>
                </div>
            `).join('');
            
            // Add click and keyboard listeners to images
            container.querySelectorAll('.site-image').forEach(img => {
                img.addEventListener('click', () => {
                    const index = parseInt(img.dataset.index);
                    openImageModal(index);
                });
                img.addEventListener('keydown', (e) => {
                    if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault();
                        const index = parseInt(img.dataset.index);
                        openImageModal(index);
                    }
                });
            });
            
            console.log('[Static] Loaded', imageUrls.length, 'cached images for', site.code);
            return imageUrls;
        } else {
            container.innerHTML = '<div class="no-images">No images available for this site</div>';
            appState.setCurrentImages([]);
            return [];
        }
    } catch (error) {
        console.error('Error loading images:', error);
        container.innerHTML = '<div class="no-images">Error loading images</div>';
        appState.setCurrentImages([]);
        return [];
    }
}

/**
 * Find cached images for a site (GitHub Pages mode)
 * @param {string} siteCode - Site code
 * @param {string} imageDir - Image directory path
 * @returns {Promise<Array>} Array of image URLs
 */
async function findCachedImages(siteCode, imageDir) {
    // Try to load images.json manifest if it exists
    try {
        const manifestResponse = await fetch(`${imageDir}images.json`);
        if (manifestResponse.ok) {
            const manifest = await manifestResponse.json();
            return manifest.images.map(img => `${imageDir}${img}`);
        }
    } catch (e) {
        // Manifest doesn't exist, try common patterns
    }
    
    // Try common image file patterns
    const patterns = [
        'image_1.jpg', 'image_2.jpg', 'image_3.jpg', 'image_4.jpg', 'image_5.jpg',
        '1.jpg', '2.jpg', '3.jpg', '4.jpg', '5.jpg',
        'photo_1.jpg', 'photo_2.jpg', 'photo_3.jpg'
    ];
    
    const imageUrls = [];
    for (const pattern of patterns) {
        const url = `${imageDir}${pattern}`;
        try {
            const response = await fetch(url, { method: 'HEAD' });
            if (response.ok) {
                imageUrls.push(url);
            }
        } catch (e) {
            // Image doesn't exist, continue
            break; // Stop after first missing image
        }
    }
    
    return imageUrls;
}

/**
 * Preload images for better performance
 * @param {Array<string>} imageUrls - Array of image URLs to preload
 */
export function preloadImages(imageUrls) {
    imageUrls.forEach(url => {
        const img = new Image();
        img.src = url;
    });
}

/**
 * Clear images container
 */
export function clearImages() {
    const container = document.getElementById('imagesContainer');
    if (container) {
        container.innerHTML = '';
    }
    appState.setCurrentImages([]);
}

// Made with Bob
