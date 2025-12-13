import select
import socket
import struct
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn

class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    address_family = socket.AF_INET6
    daemon_threads = True
    
    def server_bind(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        super().server_bind()

class ProxyRequestHandler(BaseHTTPRequestHandler):
    def do_CONNECT(self):
        address = self.path.split(':', 1)
        if len(address) == 1:
            address.append(80)
        else:
            address[1] = int(address[1])
        
        try:
            s = socket.create_connection(address, timeout=10)
        except Exception as e:
            self.send_error(502)
            return

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

    def do_GET(self):
        self.handle_http_request()

    def do_POST(self):
        self.handle_http_request()

    def handle_http_request(self):
        # Simple HTTP forwarding (not fully robust but enough for apt/docker if they use CONNECT for HTTPS)
        # For plain HTTP, we'd need to parse and forward. 
        # Docker mostly uses HTTPS (CONNECT).
        self.send_error(501, "Only CONNECT is supported for this simple proxy")

if __name__ == '__main__':
    # Listen on IPv4
    ThreadingHTTPServer.address_family = socket.AF_INET
    server = ThreadingHTTPServer(('0.0.0.0', 8888), ProxyRequestHandler)
    print("Starting CONNECT-capable proxy on port 8888...")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
