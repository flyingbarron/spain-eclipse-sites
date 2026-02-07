#!/usr/bin/env python3
"""
Simple HTTP server to serve the IGME viewer application.
This avoids CORS issues when loading the CSV file.
"""

import http.server
import socketserver
import webbrowser
import os

PORT = 8000

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Add CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        super().end_headers()

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
