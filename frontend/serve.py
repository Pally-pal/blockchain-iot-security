#!/usr/bin/env python3
"""
Frontend Server - Serves the IoT Blockchain Security frontend
Run this to serve the frontend on a separate port from the API
"""
# At the top of serve.py
from ml_module import ml_blueprint, init_predictor

import os
import sys
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading
import webbrowser
from urllib.parse import urlparse

# Configuration
FRONTEND_PORT = 8000
FRONTEND_HOST = '0.0.0.0'
AUTO_OPEN_BROWSER = True

class CORSRequestHandler(SimpleHTTPRequestHandler):
    """HTTP request handler with CORS and proper MIME types"""
    
    def end_headers(self):
        """Add CORS headers"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        
        # Set proper MIME types
        if self.path.endswith('.js'):
            self.send_header('Content-Type', 'application/javascript')
        elif self.path.endswith('.css'):
            self.send_header('Content-Type', 'text/css')
        
        super().end_headers()
    
    def do_OPTIONS(self):
        """Handle OPTIONS requests"""
        self.send_response(200)
        self.end_headers()
    
    def log_message(self, format, *args):
        """Custom logging"""
        print(f"[{self.log_date_time_string()}] {format % args}")

def run_server():
    """Start the frontend server"""
    
    # Change to frontend directory
    frontend_dir = Path(__file__).parent.absolute()
    os.chdir(frontend_dir)
    
    # Create server
    server_address = (FRONTEND_HOST, FRONTEND_PORT)
    httpd = HTTPServer(server_address, CORSRequestHandler)
    
    # Print startup information
    print("\n" + "=" * 70)
    print("IoT Blockchain Security - Frontend Server")
    print("=" * 70)
    print(f"Frontend Directory: {frontend_dir}")
    print(f"Server started on http://localhost:{FRONTEND_PORT}")
    print(f"Serving from: {frontend_dir}")
    print("\nAccess the frontend at:")
    print(f"  → http://localhost:{FRONTEND_PORT}")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 70 + "\n")
    
    # Open browser if requested
    if AUTO_OPEN_BROWSER:
        def open_browser():
            import time
            time.sleep(1)
            webbrowser.open(f'http://localhost:{FRONTEND_PORT}')
        
        browser_thread = threading.Thread(target=open_browser, daemon=True)
        browser_thread.start()
    
    # Start server
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\nShutting down server...")
        httpd.shutdown()
        print("Server stopped.")
        sys.exit(0)

if __name__ == '__main__':
    run_server()
