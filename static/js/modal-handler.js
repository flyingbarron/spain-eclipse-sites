/**
 * Modal Handler Module
 * Manages image carousel and info panel modals
 */

import { appState } from './state.js';

/**
 * Open image modal at specific index
 * @param {number} index - Image index to display
 */
export function openImageModal(index) {
    appState.setCurrentImageIndex(index);
    
    const modal = document.getElementById('imageModal');
    const modalImg = document.getElementById('modalImage');
    const counter = document.getElementById('modalCounter');
    
    if (!modal || !modalImg || !counter) return;
    
    modal.style.display = 'block';
    modalImg.src = appState.currentImages[appState.currentImageIndex];
    counter.textContent = `${appState.currentImageIndex + 1} / ${appState.currentImages.length}`;
}

/**
 * Close image modal
 */
export function closeImageModal() {
    const modal = document.getElementById('imageModal');
    if (modal) {
        modal.style.display = 'none';
    }
}

/**
 * Show next image in carousel
 */
export function nextImage() {
    const newIndex = (appState.currentImageIndex + 1) % appState.currentImages.length;
    appState.setCurrentImageIndex(newIndex);
    
    const modalImg = document.getElementById('modalImage');
    const counter = document.getElementById('modalCounter');
    
    if (modalImg && counter) {
        modalImg.src = appState.currentImages[appState.currentImageIndex];
        counter.textContent = `${appState.currentImageIndex + 1} / ${appState.currentImages.length}`;
    }
}

/**
 * Show previous image in carousel
 */
export function prevImage() {
    const newIndex = (appState.currentImageIndex - 1 + appState.currentImages.length) % appState.currentImages.length;
    appState.setCurrentImageIndex(newIndex);
    
    const modalImg = document.getElementById('modalImage');
    const counter = document.getElementById('modalCounter');
    
    if (modalImg && counter) {
        modalImg.src = appState.currentImages[appState.currentImageIndex];
        counter.textContent = `${appState.currentImageIndex + 1} / ${appState.currentImages.length}`;
    }
}

/**
 * Open info panel (Resources, About, Help)
 * @param {string} panelId - ID of panel to open
 */
export function openPanel(panelId) {
    const panel = document.getElementById(panelId);
    const overlay = document.getElementById('panelOverlay');
    
    if (!panel || !overlay) return;
    
    // Close any other open panels first
    closeAllPanels();
    
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

/**
 * Close specific info panel
 * @param {string} panelId - ID of panel to close
 */
export function closePanel(panelId) {
    const panel = document.getElementById(panelId);
    const overlay = document.getElementById('panelOverlay');
    
    if (panel) {
        panel.classList.remove('active');
    }
    
    // Only close overlay if no panels are open
    const anyPanelOpen = document.querySelector('.info-modal.active');
    if (!anyPanelOpen && overlay) {
        overlay.classList.remove('active');
    }
}

/**
 * Close all info panels
 */
export function closeAllPanels() {
    document.querySelectorAll('.info-modal').forEach(panel => {
        panel.classList.remove('active');
    });
    
    const overlay = document.getElementById('panelOverlay');
    if (overlay) {
        overlay.classList.remove('active');
    }
    
    // Clear URL hash
    if (window.location.hash) {
        const hash = window.location.hash.substring(1);
        if (['resources', 'about', 'help'].includes(hash)) {
            window.history.pushState(null, null, window.location.pathname);
        }
    }
}

/**
 * Setup all modal event listeners
 */
export function setupModalListeners() {
    // Image modal controls
    const modalClose = document.getElementById('modalClose');
    const modalNext = document.getElementById('modalNext');
    const modalPrev = document.getElementById('modalPrev');
    
    if (modalClose) {
        modalClose.addEventListener('click', closeImageModal);
    }
    if (modalNext) {
        modalNext.addEventListener('click', nextImage);
    }
    if (modalPrev) {
        modalPrev.addEventListener('click', prevImage);
    }
    
    // Keyboard navigation for image modal
    document.addEventListener('keydown', (e) => {
        const modal = document.getElementById('imageModal');
        if (modal && modal.style.display === 'block') {
            if (e.key === 'ArrowRight') {
                nextImage();
            } else if (e.key === 'ArrowLeft') {
                prevImage();
            } else if (e.key === 'Escape') {
                closeImageModal();
            }
        }
    });
    
    // Click outside modal to close
    const imageModal = document.getElementById('imageModal');
    if (imageModal) {
        imageModal.addEventListener('click', (e) => {
            if (e.target === imageModal) {
                closeImageModal();
            }
        });
    }
    
    // Info panel buttons
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
    
    // Panel close buttons
    document.querySelectorAll('.info-modal-close').forEach(closeBtn => {
        closeBtn.addEventListener('click', function() {
            const panelId = this.getAttribute('data-modal');
            if (panelId) {
                closePanel(panelId);
            }
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
    
    // Check for hash in URL and open corresponding panel
    const hash = window.location.hash.substring(1);
    if (hash === 'resources') {
        openPanel('resourcesModal');
    } else if (hash === 'about') {
        openPanel('aboutModal');
    } else if (hash === 'help') {
        openPanel('helpModal');
    }
}

// Made with Bob
