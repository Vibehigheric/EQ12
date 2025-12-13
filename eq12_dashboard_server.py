#!/usr/bin/env python3
"""
Simple EQ12 Dashboard HTTP Server
A lightweight HTTP server for serving the EQ12 dashboard with proper routing
"""

import http.server
import json
import os
import socketserver
import sys
from datetime import datetime
from urllib.parse import urlparse


class EQ12DashboardHandler(http.server.SimpleHTTPRequestHandler):
    """Custom handler for EQ12 Dashboard with proper routing"""

    def __init__(self, *args, **kwargs):
        # Set the directory to serve from
        super().__init__(*args, directory="dashboard", **kwargs)

    def do_GET(self):
        """Handle GET requests with custom routing"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path

        # Health check endpoints
        if path == "/health":
            self.send_health_response()
            return
        if path == "/api/health":
            self.send_api_health_response()
            return

        # Root redirect to dashboard
        if path == "/":
            self.send_response(302)
            self.send_header("Location", "/dashboard")
            self.end_headers()
            return

        # Dashboard route
        if path == "/dashboard":
            self.serve_dashboard()
            return

        # Try to serve static files
        super().do_GET()

    def send_health_response(self):
        """Send health check response"""
        response = {
            "status": "OK",
            "service": "EQ12 Dashboard",
            "timestamp": datetime.now().isoformat(),
            "path": self.path,
        }

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(response, indent=2).encode())

    def send_api_health_response(self):
        """Send API health check response"""
        response = {
            "status": "healthy",
            "service": "EQ12 Dashboard API",
            "timestamp": datetime.now().isoformat(),
        }

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(response, indent=2).encode())

    def serve_dashboard(self):
        """Serve the main dashboard HTML"""
        try:
            with open("dashboard/index.html", encoding="utf-8") as f:
                content = f.read()

            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(content.encode("utf-8"))

        except FileNotFoundError:
            self.send_error(404, "Dashboard not found - index.html missing")
        except Exception as e:
            self.send_error(500, f"Error serving dashboard: {e!s}")

    def log_message(self, format, *args):
        """Override to add EQ12 prefix to log messages"""
        print(f"[EQ12 Dashboard] {datetime.now().strftime('%H:%M:%S')} - {format % args}")


def main():
    """Main server function"""
    port = int(os.environ.get("PORT", 3000))

    # Change to EQ12 directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    print(f"[EQ12] Starting dashboard server on port {port}")
    print(f"[EQ12] Working directory: {os.getcwd()}")
    print(f"[EQ12] Dashboard files: {os.path.exists('dashboard/index.html')}")

    try:
        with socketserver.TCPServer(("", port), EQ12DashboardHandler) as httpd:
            print(f"[EQ12] Dashboard server running on http://localhost:{port}")
            print(f"[EQ12] Dashboard URL: http://localhost:{port}/dashboard")
            print(f"[EQ12] Health URL: http://localhost:{port}/health")
            print("[EQ12] Press Ctrl+C to stop")

            httpd.serve_forever()

    except KeyboardInterrupt:
        print("\n[EQ12] Dashboard server stopped")
    except Exception as e:
        print(f"[EQ12] Error starting server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
