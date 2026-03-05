#!/usr/bin/env python3
"""
Simple HTTP server to serve the IGME viewer application.
This avoids CORS issues when loading the CSV file and provides image proxy.
"""

import http.server
import socketserver
import webbrowser
import os
import urllib.request
import urllib.parse
from bs4 import BeautifulSoup
import json
import signal
import sys
import threading
import yaml
from dotenv import load_dotenv

PORT = 8000

# Load environment variables from .env file
load_dotenv()

# Load configuration
def load_config():
    """Load configuration from config.yaml"""
    try:
        with open('config.yaml', 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Warning: Could not load config.yaml: {e}")
        return {}

CONFIG = load_config()

# Global server reference for clean shutdown
server_instance = None

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Add CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        super().end_headers()
    
    def do_GET(self):
        # Handle shutdown endpoint
        if self.path == '/api/shutdown':
            self.handle_shutdown()
        # Handle config endpoint
        elif self.path == '/api/config':
            self.handle_config()
        # Handle horizon files list endpoint
        elif self.path == '/api/horizon-files':
            self.handle_horizon_files()
        # Handle image scraping API endpoint
        elif self.path.startswith('/api/images?'):
            self.handle_images_api()
        # Handle image proxy endpoint
        elif self.path.startswith('/api/proxy-image?'):
            self.handle_image_proxy()
        else:
            # Default file serving
            super().do_GET()
    
    def handle_config(self):
        """Serve configuration data (API keys, etc.)"""
        try:
            # Load API keys from environment variables (preferred) or config.yaml (fallback)
            google_maps_key = os.environ.get('ECLIPSE_SITES_API_KEYS_GOOGLE_MAPS', '')
            if not google_maps_key:
                google_maps_key = CONFIG.get('api_keys', {}).get('google_maps', '')
            
            mapbox_key = os.environ.get('ECLIPSE_SITES_API_KEYS_MAPBOX', '')
            if not mapbox_key:
                mapbox_key = CONFIG.get('api_keys', {}).get('mapbox', '')
            
            config_data = {
                'google_maps_api_key': google_maps_key,
                'mapbox_api_key': mapbox_key
            }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(config_data).encode())
            
        except Exception as e:
            self.send_error(500, f"Error loading config: {str(e)}")
    
    def handle_horizon_files(self):
        """Serve list of available horizon files"""
        try:
            import glob
            import re
            
            # Get all horizon files
            horizon_files = glob.glob('data/horizons/horizon_*_(ib*.png')
            
            # Extract site codes from filenames
            horizon_map = {}
            for filepath in horizon_files:
                filename = os.path.basename(filepath)
                # Extract code from filename like: horizon_name_(ib034h).png
                match = re.search(r'\((ib[0-9]+[a-z]*)\)\.png$', filename, re.IGNORECASE)
                if match:
                    code = match.group(1).upper()
                    horizon_map[code] = filename
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(horizon_map).encode())
            
        except Exception as e:
            self.send_error(500, f"Error listing horizon files: {str(e)}")
    
    def handle_shutdown(self):
        """Handle graceful server shutdown"""
        try:
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'message': 'Server shutting down...'}).encode())
            
            # Schedule immediate shutdown after response is sent
            def shutdown():
                import time
                time.sleep(0.1)  # Brief delay to ensure response is sent
                print("\n\nShutdown requested via API...")
                print("Server stopped cleanly. Socket released.")
                os._exit(0)  # Immediate clean exit
            
            threading.Thread(target=shutdown, daemon=True).start()
            
        except Exception as e:
            self.send_error(500, f"Error during shutdown: {str(e)}")
    
    def handle_images_api(self):
        """Scrape images from IGME site and return as JSON with caching"""
        try:
            # Parse query parameters
            query = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(query)
            url = params.get('url', [None])[0]
            
            if not url:
                self.send_error(400, "Missing 'url' parameter")
                return
            
            # Create cache directory if it doesn't exist
            cache_dir = 'data/cache/igme_html'
            os.makedirs(cache_dir, exist_ok=True)
            
            # Generate cache filename from URL hash
            import hashlib
            url_hash = hashlib.md5(url.encode()).hexdigest()
            html_cache_file = os.path.join(cache_dir, f"{url_hash}.html")
            json_cache_file = os.path.join(cache_dir, f"{url_hash}.json")
            
            # Check if cached JSON exists
            if os.path.exists(json_cache_file):
                # Serve from cache
                with open(json_cache_file, 'r', encoding='utf-8') as f:
                    cached_data = f.read()
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(cached_data.encode())
                return
            
            # Check if HTML is cached
            if os.path.exists(html_cache_file):
                with open(html_cache_file, 'r', encoding='utf-8') as f:
                    html = f.read()
            else:
                # Fetch the IGME page
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                req = urllib.request.Request(url, headers=headers)
                
                with urllib.request.urlopen(req, timeout=10) as response:
                    html = response.read().decode('utf-8')
                
                # Cache the HTML
                with open(html_cache_file, 'w', encoding='utf-8') as f:
                    f.write(html)
            
            # Parse HTML and extract images
            soup = BeautifulSoup(html, 'html.parser')
            images = []
            
            # Find all image tags in the content area
            for img in soup.find_all('img'):
                src = img.get('src', '')
                alt = img.get('alt', '')
                
                # Skip small icons and logos
                if any(skip in src.lower() for skip in ['icon', 'logo', 'banner', 'button']):
                    continue
                
                # Make absolute URL
                if src.startswith('/'):
                    src = 'https://info.igme.es' + src
                elif not src.startswith('http'):
                    src = 'https://info.igme.es/ielig/' + src
                
                # Only include actual site images
                if 'ielig' in src.lower() or 'fotos' in src.lower():
                    images.append({
                        'src': src,
                        'alt': alt or 'Site image'
                    })
            
            # Prepare JSON response
            json_response = json.dumps({'images': images})
            
            # Cache the JSON response
            with open(json_cache_file, 'w', encoding='utf-8') as f:
                f.write(json_response)
            
            # Send JSON response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json_response.encode())
            
        except Exception as e:
            self.send_error(500, f"Error scraping images: {str(e)}")
    
    def handle_image_proxy(self):
        """Proxy image requests to avoid CORS issues with disk caching"""
        try:
            # Parse query parameters
            query = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(query)
            image_url = params.get('url', [None])[0]
            
            if not image_url:
                self.send_error(400, "Missing 'url' parameter")
                return
            
            # Create cache directory if it doesn't exist
            cache_dir = 'data/cache/igme_images'
            os.makedirs(cache_dir, exist_ok=True)
            
            # Generate cache filename from URL hash
            import hashlib
            url_hash = hashlib.md5(image_url.encode()).hexdigest()
            # Try to preserve extension from URL
            url_ext = os.path.splitext(urllib.parse.urlparse(image_url).path)[1]
            if not url_ext or url_ext not in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
                url_ext = '.jpg'  # Default extension
            cache_file = os.path.join(cache_dir, f"{url_hash}{url_ext}")
            
            # Check if cached file exists
            if os.path.exists(cache_file):
                # Serve from cache
                with open(cache_file, 'rb') as f:
                    image_data = f.read()
                
                # Determine content type from extension
                content_type_map = {
                    '.jpg': 'image/jpeg',
                    '.jpeg': 'image/jpeg',
                    '.png': 'image/png',
                    '.gif': 'image/gif',
                    '.webp': 'image/webp'
                }
                content_type = content_type_map.get(url_ext, 'image/jpeg')
            else:
                # Fetch the image from IGME
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Referer': 'https://info.igme.es/'
                }
                req = urllib.request.Request(image_url, headers=headers)
                
                with urllib.request.urlopen(req, timeout=10) as response:
                    image_data = response.read()
                    content_type = response.headers.get('Content-Type', 'image/jpeg')
                
                # Save to cache
                with open(cache_file, 'wb') as f:
                    f.write(image_data)
            
            # Send image response
            self.send_response(200)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', str(len(image_data)))
            self.end_headers()
            self.wfile.write(image_data)
            
        except Exception as e:
            self.send_error(500, f"Error proxying image: {str(e)}")

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    print("\n\nReceived shutdown signal. Cleaning up...")
    print("Server stopped cleanly. Socket released.")
    os._exit(0)  # Immediate clean exit

def main():
    global server_instance
    
    # Change to the script's directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Register signal handlers for clean shutdown
    signal.signal(signal.SIGINT, signal_handler)   # Ctrl+C
    signal.signal(signal.SIGTERM, signal_handler)  # kill command
    
    Handler = MyHTTPRequestHandler
    
    # Allow socket reuse to avoid "Address already in use" errors
    socketserver.TCPServer.allow_reuse_address = True
    
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        server_instance = httpd
        
        print("=" * 60)
        print("IGME Sites Viewer Server")
        print("=" * 60)
        print(f"Server running at: http://localhost:{PORT}")
        print(f"Opening viewer in browser...")
        print("\nShutdown options:")
        print("  • Press Ctrl+C in this terminal")
        print("  • Visit http://localhost:{PORT}/api/shutdown")
        print("  • Use 'kill' command with the process ID")
        print("=" * 60)
        
        # Open browser
        webbrowser.open(f'http://localhost:{PORT}/viewer.html')
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\nShutdown via Ctrl+C...")
        finally:
            print("Server stopped cleanly. Socket released.")
            server_instance = None

if __name__ == "__main__":
    main()

# Made with Bob
