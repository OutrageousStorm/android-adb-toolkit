#!/usr/bin/env python3
"""
web-ui.py -- Lightweight HTTP server for ADB web UI
Usage: python3 web-ui.py [--port 8080]
Then open: http://localhost:8080
"""
from http.server import HTTPServer, SimpleHTTPRequestHandler
import subprocess, json, sys, argparse
from urllib.parse import urlparse, parse_qs

class ADBHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            html = open('index.html').read() if hasattr(self, 'server_root') else '<h1>ADB Toolkit</h1>'
            self.wfile.write(html.encode())
        elif self.path.startswith('/api/'):
            self.api_handler()
        else:
            super().do_GET()

    def api_handler(self):
        if '/device' in self.path:
            result = subprocess.run("adb shell getprop ro.product.model", shell=True, capture_output=True, text=True)
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"device": result.stdout.strip()}).encode())

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8080)
    args = parser.parse_args()
    server = HTTPServer(('0.0.0.0', args.port), ADBHandler)
    print(f"ADB Toolkit running on http://localhost:{args.port}")
    server.serve_forever()
