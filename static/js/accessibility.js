/**
 * Accessibility Module
 * Handles accessibility features including high contrast mode, font size adjustments,
 * keyboard navigation, and ARIA support
 */

export class AccessibilityManager {
    constructor() {
        this.highContrastEnabled = localStorage.getItem('highContrast') === 'true';
        this.fontSize = localStorage.getItem('fontSize') || 'medium';
        this.keyboardShortcuts = new Map();
        
        this.init();
    }
    
    /**
     * Initialize accessibility features
     */
    init() {
        this.applyHighContrast();
        this.applyFontSize();
        this.setupKeyboardNavigation();
        this.setupAccessibilityControls();
        this.enhanceFocusIndicators();
    }
    
    /**
     * Apply high contrast mode
     */
    applyHighContrast() {
        if (this.highContrastEnabled) {
            document.body.classList.add('high-contrast');
        } else {
            document.body.classList.remove('high-contrast');
        }
    }
    
    /**
     * Toggle high contrast mode
     */
    toggleHighContrast() {
        this.highContrastEnabled = !this.highContrastEnabled;
        localStorage.setItem('highContrast', this.highContrastEnabled);
        this.applyHighContrast();
        
        // Announce change to screen readers
        this.announceToScreenReader(
            `High contrast mode ${this.highContrastEnabled ? 'enabled' : 'disabled'}`
        );
    }
    
    /**
     * Apply font size
     */
    applyFontSize() {
        document.body.classList.remove('font-small', 'font-medium', 'font-large', 'font-xlarge');
        document.body.classList.add(`font-${this.fontSize}`);
    }
    
    /**
     * Set font size
     * @param {string} size - 'small', 'medium', 'large', or 'xlarge'
     */
    setFontSize(size) {
        this.fontSize = size;
        localStorage.setItem('fontSize', size);
        this.applyFontSize();
        
        // Announce change to screen readers
        this.announceToScreenReader(`Font size set to ${size}`);
    }
    
    /**
     * Setup keyboard navigation
     */
    setupKeyboardNavigation() {
        // Global keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            // Skip if user is typing in an input
            if (e.target.matches('input, textarea, select')) {
                return;
            }
            
            // Alt+H: Toggle high contrast
            if (e.altKey && e.key === 'h') {
                e.preventDefault();
                this.toggleHighContrast();
            }
            
            // Alt+Plus: Increase font size
            if (e.altKey && (e.key === '+' || e.key === '=')) {
                e.preventDefault();
                this.increaseFontSize();
            }
            
            // Alt+Minus: Decrease font size
            if (e.altKey && e.key === '-') {
                e.preventDefault();
                this.decreaseFontSize();
            }
            
            // Alt+0: Reset font size
            if (e.altKey && e.key === '0') {
                e.preventDefault();
                this.setFontSize('medium');
            }
            
            // Alt+S: Focus search box
            if (e.altKey && e.key === 's') {
                e.preventDefault();
                const searchBox = document.getElementById('searchBox');
                if (searchBox) {
                    searchBox.focus();
                    this.announceToScreenReader('Search box focused');
                }
            }
            
            // Alt+F: Toggle favorites filter
            if (e.altKey && e.key === 'f') {
                e.preventDefault();
                const favoritesFilter = document.getElementById('favoritesFilter');
                if (favoritesFilter) {
                    favoritesFilter.click();
                }
            }
            
            // Alt+E: Toggle eclipse filter
            if (e.altKey && e.key === 'e') {
                e.preventDefault();
                const eclipseFilter = document.getElementById('eclipseFilter');
                if (eclipseFilter) {
                    eclipseFilter.click();
                }
            }
            
            // Question mark: Show help
            if (e.key === '?' && !e.shiftKey) {
                e.preventDefault();
                const helpBtn = document.getElementById('helpBtn');
                if (helpBtn) {
                    helpBtn.click();
                }
            }
        });
        
        // Improve tab navigation for site list
        this.setupSiteListNavigation();
    }
    
    /**
     * Setup site list keyboard navigation
     */
    setupSiteListNavigation() {
        const siteList = document.getElementById('siteList');
        if (!siteList) return;
        
        siteList.addEventListener('keydown', (e) => {
            const currentItem = e.target.closest('.site-item');
            if (!currentItem) return;
            
            let nextItem = null;
            
            // Arrow down: Next site
            if (e.key === 'ArrowDown') {
                e.preventDefault();
                nextItem = currentItem.nextElementSibling;
            }
            
            // Arrow up: Previous site
            if (e.key === 'ArrowUp') {
                e.preventDefault();
                nextItem = currentItem.previousElementSibling;
            }
            
            // Enter or Space: Select site
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                currentItem.click();
            }
            
            if (nextItem && nextItem.classList.contains('site-item')) {
                nextItem.focus();
                nextItem.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            }
        });
    }
    
    /**
     * Increase font size
     */
    increaseFontSize() {
        const sizes = ['small', 'medium', 'large', 'xlarge'];
        const currentIndex = sizes.indexOf(this.fontSize);
        if (currentIndex < sizes.length - 1) {
            this.setFontSize(sizes[currentIndex + 1]);
        }
    }
    
    /**
     * Decrease font size
     */
    decreaseFontSize() {
        const sizes = ['small', 'medium', 'large', 'xlarge'];
        const currentIndex = sizes.indexOf(this.fontSize);
        if (currentIndex > 0) {
            this.setFontSize(sizes[currentIndex - 1]);
        }
    }
    
    /**
     * Setup accessibility controls in header
     */
    setupAccessibilityControls() {
        const headerNav = document.querySelector('.header-nav');
        if (!headerNav) return;
        
        // Create accessibility menu button
        const a11yBtn = document.createElement('button');
        a11yBtn.className = 'nav-item';
        a11yBtn.id = 'accessibilityBtn';
        a11yBtn.innerHTML = '♿ Accessibility';
        a11yBtn.setAttribute('aria-label', 'Open accessibility settings');
        a11yBtn.setAttribute('aria-haspopup', 'dialog');
        
        // Insert before help button
        const helpBtn = document.getElementById('helpBtn');
        if (helpBtn) {
            headerNav.insertBefore(a11yBtn, helpBtn);
        } else {
            headerNav.appendChild(a11yBtn);
        }
        
        // Create accessibility modal
        this.createAccessibilityModal();
        
        // Setup click handler
        a11yBtn.addEventListener('click', () => {
            this.showAccessibilityModal();
        });
    }
    
    /**
     * Create accessibility modal
     */
    createAccessibilityModal() {
        const modal = document.createElement('div');
        modal.className = 'info-modal';
        modal.id = 'accessibilityModal';
        modal.setAttribute('role', 'dialog');
        modal.setAttribute('aria-labelledby', 'a11yModalTitle');
        modal.setAttribute('aria-modal', 'true');
        
        modal.innerHTML = `
            <div class="info-modal-content">
                <span class="info-modal-close" data-modal="accessibilityModal" aria-label="Close accessibility settings">&times;</span>
                <h2 id="a11yModalTitle">♿ Accessibility Settings</h2>
                <div class="modal-text-content">
                    <div class="a11y-section">
                        <h3>Visual Settings</h3>
                        <div class="a11y-control">
                            <label for="highContrastToggle">
                                <input type="checkbox" id="highContrastToggle" ${this.highContrastEnabled ? 'checked' : ''}>
                                High Contrast Mode
                            </label>
                            <p class="a11y-help">Increases contrast for better visibility (Alt+H)</p>
                        </div>
                        
                        <div class="a11y-control">
                            <label>Font Size</label>
                            <div class="font-size-controls" role="group" aria-label="Font size controls">
                                <button class="a11y-btn ${this.fontSize === 'small' ? 'active' : ''}" data-size="small" aria-label="Small font size">A</button>
                                <button class="a11y-btn ${this.fontSize === 'medium' ? 'active' : ''}" data-size="medium" aria-label="Medium font size">A</button>
                                <button class="a11y-btn ${this.fontSize === 'large' ? 'active' : ''}" data-size="large" aria-label="Large font size">A</button>
                                <button class="a11y-btn ${this.fontSize === 'xlarge' ? 'active' : ''}" data-size="xlarge" aria-label="Extra large font size">A</button>
                            </div>
                            <p class="a11y-help">Adjust text size (Alt+Plus/Minus, Alt+0 to reset)</p>
                        </div>
                    </div>
                    
                    <div class="a11y-section">
                        <h3>Keyboard Shortcuts</h3>
                        <dl class="keyboard-shortcuts">
                            <dt>Alt+H</dt><dd>Toggle high contrast mode</dd>
                            <dt>Alt+Plus/Minus</dt><dd>Adjust font size</dd>
                            <dt>Alt+0</dt><dd>Reset font size</dd>
                            <dt>Alt+S</dt><dd>Focus search box</dd>
                            <dt>Alt+F</dt><dd>Toggle favorites filter</dd>
                            <dt>Alt+E</dt><dd>Toggle eclipse filter</dd>
                            <dt>?</dt><dd>Show help</dd>
                            <dt>Arrow Keys</dt><dd>Navigate site list</dd>
                            <dt>Enter/Space</dt><dd>Select site</dd>
                            <dt>Escape</dt><dd>Close modals</dd>
                        </dl>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Setup event listeners
        const highContrastToggle = modal.querySelector('#highContrastToggle');
        highContrastToggle.addEventListener('change', () => {
            this.toggleHighContrast();
        });
        
        const fontSizeBtns = modal.querySelectorAll('.font-size-controls .a11y-btn');
        fontSizeBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                const size = btn.dataset.size;
                this.setFontSize(size);
                
                // Update active state
                fontSizeBtns.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
            });
        });
        
        // Close button
        const closeBtn = modal.querySelector('.info-modal-close');
        closeBtn.addEventListener('click', () => {
            modal.style.display = 'none';
            document.getElementById('accessibilityBtn').focus();
        });
        
        // Close on overlay click
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.style.display = 'none';
                document.getElementById('accessibilityBtn').focus();
            }
        });
        
        // Close on Escape
        modal.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                modal.style.display = 'none';
                document.getElementById('accessibilityBtn').focus();
            }
        });
    }
    
    /**
     * Show accessibility modal
     */
    showAccessibilityModal() {
        const modal = document.getElementById('accessibilityModal');
        if (modal) {
            modal.style.display = 'flex';
            
            // Focus first interactive element
            const firstInput = modal.querySelector('input, button');
            if (firstInput) {
                setTimeout(() => firstInput.focus(), 100);
            }
        }
    }
    
    /**
     * Enhance focus indicators
     */
    enhanceFocusIndicators() {
        // Add focus-visible class support for older browsers
        document.addEventListener('keydown', () => {
            document.body.classList.add('keyboard-nav');
        });
        
        document.addEventListener('mousedown', () => {
            document.body.classList.remove('keyboard-nav');
        });
    }
    
    /**
     * Announce message to screen readers
     * @param {string} message - Message to announce
     */
    announceToScreenReader(message) {
        let announcer = document.getElementById('a11y-announcer');
        
        if (!announcer) {
            announcer = document.createElement('div');
            announcer.id = 'a11y-announcer';
            announcer.setAttribute('role', 'status');
            announcer.setAttribute('aria-live', 'polite');
            announcer.setAttribute('aria-atomic', 'true');
            announcer.style.position = 'absolute';
            announcer.style.left = '-10000px';
            announcer.style.width = '1px';
            announcer.style.height = '1px';
            announcer.style.overflow = 'hidden';
            document.body.appendChild(announcer);
        }
        
        // Clear and set new message
        announcer.textContent = '';
        setTimeout(() => {
            announcer.textContent = message;
        }, 100);
    }
}

// Create and export singleton instance
export const accessibilityManager = new AccessibilityManager();

// Made with Bob