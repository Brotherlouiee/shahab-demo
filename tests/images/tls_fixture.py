"""Synthetic HTTPS echo upstream, mounted only into disposable image-smoke containers."""

import json
import ssl
from http.server import BaseHTTPRequestHandler, HTTPServer


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass  # Never emit request paths, headers, cookies or bodies into CI logs.

    def do_GET(self):
        self.do_POST()

    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0"))
        if length > 1024:
            self.send_error(413)
            return
        payload = json.dumps(
            {
                "method": self.command,
                "path": self.path,
                "host": self.headers.get("Host"),
                "origin": self.headers.get("Origin"),
                "scheme": self.headers.get("X-Forwarded-Proto"),
                "forwarded": self.headers.get("X-Forwarded-For"),
                "cookie": self.headers.get("Cookie"),
                "body": self.rfile.read(length).decode(),
            }
        ).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Set-Cookie", "fixture=synthetic; Secure; HttpOnly; SameSite=Lax; Path=/api/v1")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)


if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", 8443), Handler)
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain("/fixture/cert.pem", "/fixture/key.pem")
    server.socket = context.wrap_socket(server.socket, server_side=True)
    server.serve_forever()
