"""Local TLS authority fixture; credentials/certificate are generated, never committed."""

import base64
import json
import secrets
import ssl
import subprocess
import tempfile
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs

from pydantic import SecretStr

from backend.app.operations.infrastructure.introspection import AuthorityConfiguration, IntrospectionAuthority


class TLSAuthorityFixture:
    def __init__(self):
        self.directory = tempfile.TemporaryDirectory()
        cert, key = Path(self.directory.name) / "cert.pem", Path(self.directory.name) / "key.pem"
        subprocess.run(
            [
                "openssl",
                "req",
                "-x509",
                "-newkey",
                "rsa:2048",
                "-nodes",
                "-keyout",
                str(key),
                "-out",
                str(cert),
                "-days",
                "1",
                "-subj",
                "/CN=localhost",
                "-addext",
                "subjectAltName=DNS:localhost",
            ],
            check=True,
            capture_output=True,
        )
        self.token, self.secret = secrets.token_urlsafe(36), secrets.token_urlsafe(36)
        now = int(time.time())
        self.claims = {
            "active": True,
            "sub": "test-operator",
            "iss": "https://issuer.example.invalid",
            "aud": "shahab-operations",
            "exp": now + 240,
            "iat": now,
            "auth_time": now,
            "client_id": "operator-cli",
            "amr": ["mfa"],
            "roles": ["data-editor", "admin"],
        }
        self.status, self.redirect, self.calls = 200, False, 0
        owner = self

        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):
                owner.calls += 1
                authorization = "Basic " + base64.b64encode(("resource-cli:" + owner.secret).encode()).decode()
                body = self.rfile.read(int(self.headers.get("Content-Length", "0")))
                authorized = self.headers.get("Authorization") == authorization and (
                    parse_qs(body.decode()).get("token") == [owner.token]
                )
                self.send_response(302 if owner.redirect else owner.status)
                if owner.redirect:
                    self.send_header("Location", "https://untrusted.example.invalid/introspect")
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(owner.claims if authorized else {"active": False}).encode())

            def log_message(self, *args):
                pass

        self.server = ThreadingHTTPServer(("localhost", 0), Handler)
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(cert, key)
        self.server.socket = context.wrap_socket(self.server.socket, server_side=True)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.configuration = AuthorityConfiguration(
            endpoint=f"https://localhost:{self.server.server_port}/introspect",
            issuer=self.claims["iss"],
            audience=self.claims["aud"],
            client_id="resource-cli",
            client_secret=SecretStr(self.secret),
            service_client_ids=frozenset({"service-import"}),
            ca_file=str(cert),
        )

    def authority(self):
        return IntrospectionAuthority(self.configuration, SecretStr(self.token))

    def close(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=3)
        self.directory.cleanup()
