"""Shared local HTTP target server for attack tests."""
import http.server
import socketserver
import threading
import time
import socket
from contextlib import contextmanager

class CountingHandler(http.server.BaseHTTPRequestHandler):
    counter = {"get": 0, "post": 0, "head": 0, "headers": []}

    def log_message(self, format, *args):
        pass

    def _record(self, method):
        type(self).counter[method] += 1
        type(self).counter["headers"].append(dict(self.headers))

    def do_GET(self):
        self._record("get")
        body = b"ok"
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        self._record("post")
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"ok")

    def do_HEAD(self):
        self._record("head")
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Content-Length", "2")
        self.end_headers()

class _ReusableServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True

@contextmanager
def http_target():
    CountingHandler.counter = {"get": 0, "post": 0, "head": 0, "headers": []}
    srv = _ReusableServer(("127.0.0.1", 0), CountingHandler)
    port = srv.server_address[1]
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()
    deadline = time.time() + 5
    while time.time() < deadline:
        try:
            _s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            _s.settimeout(0.3)
            _s.connect(("127.0.0.1", port))
            _s.close()
            break
        except Exception:
            time.sleep(0.05)
    try:
        yield port, CountingHandler.counter
    finally:
        time.sleep(0.2)
        srv.shutdown()
        srv.server_close()
