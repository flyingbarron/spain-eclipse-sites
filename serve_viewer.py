#!/usr/bin/env python3
"""
Simple HTTP server to serve the IGME viewer application.
This avoids CORS issues when loading the CSV file and provides image proxy.
"""

import http.server
import socketserver
import webbrowser
import os
import urllib.parse
import json
import signal
import sys
import threading
import yaml
from dotenv import load_dotenv
from src.constants import HORIZON_FILES_DIR
from src.igme_image_service import get_cached_igme_images, get_cached_proxy_image

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

    def _get_query_param(self, name):
        """Return a single query parameter value from the request path."""
        query = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(query)
        return params.get(name, [None])[0]

    def _send_json_response(self, payload, status=200):
        """Send a JSON response from a Python object or pre-serialized JSON string."""
        response_body = payload if isinstance(payload, str) else json.dumps(payload)
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(response_body.encode())

    def _send_binary_response(self, data, content_type, status=200):
        """Send a binary response with content metadata."""
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        # Handle shutdown endpoint
        if self.path == '/api/shutdown':
            self.handle_shutdown()
        # Handle config endpoint
        elif self.path == '/api/config':
            self.handle_config()
        # Handle README endpoint
        elif self.path == '/api/readme':
            self.handle_readme()
        # Handle CREDITS endpoint
        elif self.path == '/api/credits':
            self.handle_credits()
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

            self._send_json_response(config_data)

        except Exception as e:
            self.send_error(500, f"Error loading config: {str(e)}")
    
    def handle_readme(self):
        """Serve README content for in-app viewing."""
        try:
            with open('README.md', 'r', encoding='utf-8') as file:
                self._send_json_response({'content': file.read()})
        except Exception as e:
            self.send_error(500, f"Error loading README: {str(e)}")
    
    def handle_credits(self):
        """Serve CREDITS content for in-app viewing."""
        try:
            with open('CREDITS.md', 'r', encoding='utf-8') as file:
                self._send_json_response({'content': file.read()})
        except Exception as e:
            self.send_error(500, f"Error loading CREDITS: {str(e)}")

    def handle_horizon_files(self):
        """Serve list of available horizon files"""
        try:
            import glob
            import re
            
            # Get all horizon files
            horizon_files = glob.glob(os.path.join(HORIZON_FILES_DIR, 'horizon_*_(ib*.png'))
            
            # Extract site codes from filenames
            horizon_map = {}
            for filepath in horizon_files:
                filename = os.path.basename(filepath)
                # Extract code from filename like: horizon_name_(ib034h).png
                match = re.search(r'\((ib[0-9]+[a-z]*)\)\.png$', filename, re.IGNORECASE)
                if match:
                    code = match.group(1).upper()
                    horizon_map[code] = filename
            
            self._send_json_response(horizon_map)

        except Exception as e:
            self.send_error(500, f"Error listing horizon files: {str(e)}")
    
    def handle_shutdown(self):
        """Handle graceful server shutdown"""
        try:
            self._send_json_response({'message': 'Server shutting down...'})

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
            url = self._get_query_param('url')

            if not url:
                self.send_error(400, "Missing 'url' parameter")
                return

            json_response = get_cached_igme_images(url)
            self._send_json_response(json_response)

        except Exception as e:
            self.send_error(500, f"Error scraping images: {str(e)}")
    
    def handle_image_proxy(self):
        """Proxy image requests to avoid CORS issues with disk caching"""
        try:
            image_url = self._get_query_param('url')

            if not image_url:
                self.send_error(400, "Missing 'url' parameter")
                return

            proxy_image = get_cached_proxy_image(image_url)
            self._send_binary_response(
                proxy_image['image_data'],
                proxy_image['content_type'],
            )

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
        print(f"  • Visit http://localhost:{PORT}/api/shutdown")
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
