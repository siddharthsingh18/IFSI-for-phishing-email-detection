"""Lightweight local IPv4-only HTTP/HTTPS CONNECT proxy."""

from __future__ import annotations

import select
import socket
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer

KNOWN_HOSTS = {
    "registry.ollama.ai": "104.18.17.170",
    "ollama.ai": "104.18.17.170",
}


class ProxyHandler(BaseHTTPRequestHandler):
    def do_CONNECT(self):
        address = self.path.split(":")
        host = address[0]
        port = int(address[1]) if len(address) > 1 else 443

        target_ip = KNOWN_HOSTS.get(host)
        if not target_ip:
            try:
                addr_info = socket.getaddrinfo(host, port, socket.AF_INET, socket.SOCK_STREAM)
                target_ip = addr_info[0][4][0]
            except Exception as e:
                self.send_error(502, f"Bad Gateway: {e}")
                return

        try:
            upstream = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            upstream.connect((target_ip, port))
            self.send_response(200, "Connection Established")
            self.end_headers()
        except Exception as e:
            self.send_error(502, f"Bad Gateway connecting upstream: {e}")
            return

        self.wfile.flush()
        conns = [self.connection, upstream]
        while True:
            r, _, _ = select.select(conns, [], [], 30)
            if not r:
                break
            for s in r:
                other = upstream if s is self.connection else self.connection
                try:
                    data = s.recv(65536)
                    if not data:
                        return
                    other.sendall(data)
                except Exception:
                    return

    def log_message(self, format, *args):
        pass


def run_proxy(port=18888):
    server = HTTPServer(("127.0.0.1", port), ProxyHandler)
    server.serve_forever()


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 18888
    run_proxy(port)
