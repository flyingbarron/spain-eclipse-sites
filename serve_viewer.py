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

PORT = 8000

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Add CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        super().end_headers()
    
    def do_GET(self):
        # Handle image scraping API endpoint
        if self.path.startswith('/api/images?'):
            self.handle_images_api()
        # Handle image proxy endpoint
        elif self.path.startswith('/api/proxy-image?'):
            self.handle_image_proxy()
        else:
            # Default file serving
            super().do_GET()
    
    def handle_images_api(self):
        """Scrape images from IGME site and return as JSON"""
        try:
            # Parse query parameters
            query = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(query)
            url = params.get('url', [None])[0]
            
            if not url:
                self.send_error(400, "Missing 'url' parameter")
                return
            
            # Fetch the IGME page
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            req = urllib.request.Request(url, headers=headers)
            
            with urllib.request.urlopen(req, timeout=10) as response:
                html = response.read().decode('utf-8')
            
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
            
            # Send JSON response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'images': images}).encode())
            
        except Exception as e:
            self.send_error(500, f"Error scraping images: {str(e)}")
    
    def handle_image_proxy(self):
        """Proxy image requests to avoid CORS issues"""
        try:
            # Parse query parameters
            query = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(query)
            image_url = params.get('url', [None])[0]
            
            if not image_url:
                self.send_error(400, "Missing 'url' parameter")
                return
            
            # Fetch the image
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': 'https://info.igme.es/'
            }
            req = urllib.request.Request(image_url, headers=headers)
            
            with urllib.request.urlopen(req, timeout=10) as response:
                image_data = response.read()
                content_type = response.headers.get('Content-Type', 'image/jpeg')
            
            # Send image response
            self.send_response(200)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', str(len(image_data)))
            self.end_headers()
            self.wfile.write(image_data)
            
        except Exception as e:
            self.send_error(500, f"Error proxying image: {str(e)}")

def main():
    # Change to the script's directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    Handler = MyHTTPRequestHandler
    
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print("=" * 60)
        print("IGME Sites Viewer Server")
        print("=" * 60)
        print(f"Server running at: http://localhost:{PORT}")
        print(f"Opening viewer in browser...")
        print("\nPress Ctrl+C to stop the server")
        print("=" * 60)
        
        # Open browser
        webbrowser.open(f'http://localhost:{PORT}/viewer.html')
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\nServer stopped.")

if __name__ == "__main__":
    main()

# Made with Bob
