import http.server
import socketserver
import urllib.request
import shutil
import sys

PORT = 8888

class Proxy(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        print(f"Request: {self.path}", file=sys.stderr)
        try:
            req = urllib.request.Request(self.path)
            with urllib.request.urlopen(req) as response:
                self.send_response(response.status)
                for header, value in response.headers.items():
                    self.send_header(header, value)
                self.end_headers()
                shutil.copyfileobj(response, self.wfile)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            self.send_error(500, str(e))

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    daemon_threads = True

print(f"🚀 Proxy active on 127.0.0.1:{PORT}")
try:
    with ThreadedTCPServer(("127.0.0.1", PORT), Proxy) as httpd:
        httpd.serve_forever()
except KeyboardInterrupt:
    print("\nStopping proxy.")
