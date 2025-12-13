import socket
import select
import http.server
import socketserver
import sys

PORT = 8888

class Proxy(http.server.SimpleHTTPRequestHandler):
    def do_CONNECT(self):
        address = self.path.split(':')
        if len(address) == 2:
            host, port = address
        else:
            host = address[0]
            port = 443
        
        try:
            s = socket.create_connection((host, int(port)))
            self.send_response(200, 'Connection Established')
            self.end_headers()
            
            conns = [self.connection, s]
            self.close_connection = 0
            
            while True:
                rlist, wlist, xlist = select.select(conns, [], conns, 3)
                if xlist or not rlist:
                    break
                
                for r in rlist:
                    other = conns[1] if r is conns[0] else conns[0]
                    data = r.recv(8192)
                    if not data:
                        return
                    other.sendall(data)
        except Exception as e:
            self.send_error(502, str(e))

    def do_GET(self):
        self.copyfile(urllib.request.urlopen(self.path), self.wfile)

print(f"🚀 HTTPS Proxy active on 0.0.0.0:{PORT}")
# Use ThreadingTCPServer for concurrent connections
class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    daemon_threads = True

with ThreadedTCPServer(("", PORT), Proxy) as httpd:
    httpd.serve_forever()
