/**
 * Site Details Module - GitHub Pages Version
 * Re-exports site-details with gh-pages image loader
 */

// Import everything from the original module
export * from '../static/js/site-details.js';

// Override the loadSiteImages function with our GitHub Pages version
import { loadSiteImages as ghLoadSiteImages } from './image-loader.js';

// Re-export with the GitHub Pages image loader
export { ghLoadSiteImages as loadSiteImages };

// Made with Bob
