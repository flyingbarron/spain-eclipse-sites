/**
 * Image Loader Module
 * Handles loading and displaying IGME site images
 */

import { CONFIG } from './config.js';
import { appState } from './state.js';
import { openImageModal } from './modal-handler.js';

/**
 * Load images for a site from IGME
 * @param {Object} site - Site object with URL
 * @returns {Promise<Array>} Array of image objects
 */
export async function loadSiteImages(site) {
    const container = document.getElementById('imagesContainer');
    
    if (!container) {
        console.warn('Images container not found');
        return [];
    }
    
    // Show loading state
    container.innerHTML = '<div class="loading">Loading IGME images...</div>';
    
    try {
        const response = await fetch(`${CONFIG.API.IMAGES}?url=${encodeURIComponent(site.url)}`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
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
            
            return data.images;
        } else {
            container.innerHTML = '<div class="no-images">No images found for this site</div>';
            appState.setCurrentImages([]);
            return [];
        }
    } catch (error) {
        console.error('Error loading images:', error);
        container.innerHTML = '<div class="no-images">Error loading images. Please try again later.</div>';
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
