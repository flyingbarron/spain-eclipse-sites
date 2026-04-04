/**
 * Notes Manager Module
 * Handles personal notes/comments for sites with localStorage persistence
 */

import { appState } from './state.js';

const STORAGE_KEY = 'eclipse_sites_notes';

export class NotesManager {
    constructor() {
        this.notes = this.loadNotes();
    }
    
    /**
     * Load notes from localStorage
     * @returns {Object} Object mapping site codes to notes
     */
    loadNotes() {
        try {
            const stored = localStorage.getItem(STORAGE_KEY);
            return stored ? JSON.parse(stored) : {};
        } catch (error) {
            console.error('Error loading notes:', error);
            return {};
        }
    }
    
    /**
     * Save notes to localStorage
     */
    saveNotes() {
        try {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(this.notes));
        } catch (error) {
            console.error('Error saving notes:', error);
        }
    }
    
    /**
     * Get note for a site
     * @param {string} siteCode - Site code
     * @returns {string} Note text or empty string
     */
    getNote(siteCode) {
        return this.notes[siteCode] || '';
    }
    
    /**
     * Set note for a site
     * @param {string} siteCode - Site code
     * @param {string} note - Note text
     */
    setNote(siteCode, note) {
        if (note && note.trim()) {
            this.notes[siteCode] = note.trim();
        } else {
            delete this.notes[siteCode];
        }
        this.saveNotes();
        appState.notify('notes', this.notes);
    }
    
    /**
     * Check if site has a note
     * @param {string} siteCode - Site code
     * @returns {boolean} True if site has a note
     */
    hasNote(siteCode) {
        return !!this.notes[siteCode];
    }
    
    /**
     * Delete note for a site
     * @param {string} siteCode - Site code
     */
    deleteNote(siteCode) {
        delete this.notes[siteCode];
        this.saveNotes();
        appState.notify('notes', this.notes);
    }
    
    /**
     * Get all notes
     * @returns {Object} All notes
     */
    getAllNotes() {
        return { ...this.notes };
    }
    
    /**
     * Clear all notes
     */
    clearAll() {
        this.notes = {};
        this.saveNotes();
        appState.notify('notes', this.notes);
    }
    
    /**
     * Export notes as JSON
     * @returns {string} JSON string of notes
     */
    exportNotes() {
        const exportData = {
            version: '1.0',
            exportDate: new Date().toISOString(),
            notes: this.notes
        };
        return JSON.stringify(exportData, null, 2);
    }
    
    /**
     * Import notes from JSON
     * @param {string} jsonString - JSON string to import
     * @returns {Object} Result with success status and message
     */
    importNotes(jsonString) {
        try {
            const data = JSON.parse(jsonString);
            if (!data.notes || typeof data.notes !== 'object') {
                return { success: false, message: 'Invalid format' };
            }
            
            let imported = 0;
            Object.entries(data.notes).forEach(([code, note]) => {
                if (note && typeof note === 'string') {
                    this.notes[code] = note;
                    imported++;
                }
            });
            
            this.saveNotes();
            appState.notify('notes', this.notes);
            
            return {
                success: true,
                message: `Imported ${imported} notes`,
                imported: imported
            };
        } catch (error) {
            return { success: false, message: 'Error parsing JSON: ' + error.message };
        }
    }
    
    /**
     * Get notes count
     * @returns {number} Number of notes
     */
    getCount() {
        return Object.keys(this.notes).length;
    }
}

// Create and export singleton instance
export const notesManager = new NotesManager();

// Made with Bob