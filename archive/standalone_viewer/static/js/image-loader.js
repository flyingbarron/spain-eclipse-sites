/**
 * Image Loader Module - Standalone Version
 * Loads images from embedded data and local files
 */

import { appState } from './state.js';
import { openImageModal } from './modal-handler.js';

/**
 * Load images for a site from embedded data
 * @param {Object} site - Site object with code
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
    
    try {
        // Get images from embedded data
        const siteImages = window.EMBEDDED_SITE_DATA?.siteImages?.[site.code] || [];
        
        if (siteImages.length > 0) {
            // Map to local image paths
            const imageUrls = siteImages.map(img => 
                `images/igme/${img.hash}.jpg`
            );
            appState.setCurrentImages(imageUrls);
            
            // Render image grid
            container.innerHTML = siteImages.map((img, index) => `
                <div class="image-card">
                    <img src="images/igme/${img.hash}.jpg"
                         alt="${img.alt || 'Site image'}"
                         data-index="${index}"
                         class="site-image"
                         onerror="this.parentElement.style.display='none'">
                    <div class="image-caption">${img.alt || 'Site image'}</div>
                </div>
            `).join('');
            
            // Add click listeners to images
            container.querySelectorAll('.site-image').forEach(img => {
                img.addEventListener('click', () => {
                    const index = parseInt(img.dataset.index);
                    openImageModal(index);
                });
            });
            
            return siteImages;
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
