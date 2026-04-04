/**
 * Image Loader Module - GitHub Pages Version
 * Handles loading and displaying IGME site images from static cache
 */

import { CONFIG } from './config.js';
import { appState } from '../static/js/state.js';
import { openImageModal } from '../static/js/modal-handler.js';

/**
 * Load images for a site from cached IGME images
 * @param {Object} site - Site object with code
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
        // For GitHub Pages, we look for cached images in data/igme_images/{site_code}/
        const imageDir = `${CONFIG.IMAGES.IGME_CACHE}${site.code}/`;
        
        // Try to load a manifest file if it exists, otherwise try common image names
        const imageUrls = await findSiteImages(site.code, imageDir);
        
        if (imageUrls.length > 0) {
            appState.setCurrentImages(imageUrls);
            
            // Render image grid
            container.innerHTML = imageUrls.map((url, index) => `
                <div class="image-card">
                    <img src="${url}"
                         alt="Site image ${index + 1}"
                         data-index="${index}"
                         class="site-image"
                         onerror="this.parentElement.style.display='none'">
                    <div class="image-caption">Image ${index + 1}</div>
                </div>
            `).join('');
            
            // Setup click handlers for modal
            const images = container.querySelectorAll('.site-image');
            images.forEach(img => {
                img.addEventListener('click', () => {
                    const index = parseInt(img.dataset.index);
                    openImageModal(index);
                });
            });
            
            return imageUrls;
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
 * Find cached images for a site
 * @param {string} siteCode - Site code
 * @param {string} imageDir - Image directory path
 * @returns {Promise<Array>} Array of image URLs
 */
async function findSiteImages(siteCode, imageDir) {
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
        }
    }
    
    return imageUrls;
}

// Made with Bob
