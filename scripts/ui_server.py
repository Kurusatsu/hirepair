#!/usr/bin/env python3
"""Local UI server for Hirepair (see docs/ui-design.md). Standard library only.

Usage: python3 scripts/ui_server.py [--root .] [--port 8765]

Binds 127.0.0.1 only. Reads tracker.md, profile.local.yml, data/inbox.jsonl, reports/shortlist.md.
Writes only data/decisions.jsonl (append). Never serves cv.local.md or anything outside ui/.
"""
import argparse
import hashlib
import json
import os
import re
import secrets
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ui_protocol as proto  # noqa: E402
from tracker_stats import parse  # noqa: E402

CSP = "default-src 'self'; img-src 'self' data:; frame-ancestors 'none'; base-uri 'none'; form-action 'none'"
MAX_BODY = 16 * 1024
STATIC_TYPES = {".css": "text/css; charset=utf-8", ".js": "application/javascript; charset=utf-8"}
WRITE_LOCK = threading.Lock()


def read_text(path):
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return None


def profile_summary(text):
    """Tiny line-based reader (no YAML library): approved flag, role titles, limits."""
    if text is None:
        return {"exists": False, "approved": False, "roles": [], "limits": {}}
    approved = bool(re.search(r"^\s*approved:\s*true\b", text, re.M))
    roles = [m.group(1) for m in re.finditer(r'^\s+-\s*title:\s*"?([^"\n]+?)"?\s*$', text, re.M)]
    limits = {}
    block = re.search(r"^limits:[^\n]*\n((?:[ \t]+.*\n?)+)", text, re.M)
    if block:
        for m in re.finditer(r'^\s+(\w+):\s*"?([^"#\n]+?)"?\s*(?:#.*)?$', block.group(1), re.M):
            v = m.group(2).strip()
            limits[m.group(1)] = int(v) if v.isdigit() else v
    return {"exists": True, "approved": approved, "roles": roles, "limits": limits}


class App:
    def __init__(self, root, port):
        self.root = os.path.abspath(root)
        self.port = port
        self.token = secrets.token_urlsafe(24)
        self.ui_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "ui")
        self.hosts = {f"127.0.0.1:{port}", f"localhost:{port}"}
        self.inbox_p, self.dec_p = proto.paths(self.root)

    def p(self, *parts):
        return os.path.join(self.root, *parts)

    def sources(self, route):
        """Files each route depends on, so a change in one file does not invalidate every route."""
        return {"/api/tracker": [self.p("tracker.md")], "/api/inbox": [self.inbox_p, self.dec_p],
                "/api/profile": [self.p("profile.local.yml")],
                "/api/shortlist": [self.p("reports", "shortlist.md")]}[route]

    def etag(self, route):
        h = hashlib.sha256(route.encode())
        for s in self.sources(route):
            try:
                st = os.stat(s)
                h.update(f"{s}:{st.st_mtime_ns}:{st.st_size};".encode())
            except FileNotFoundError:
                h.update(f"{s}:-;".encode())
        return '"' + h.hexdigest()[:20] + '"'

    def api_tracker(self):
        header, rows = parse(read_text(self.p("tracker.md")) or "")
        if header is None:
            return {"header": [], "rows": []}
        return {"header": header, "rows": [r for r in rows if len(r) == len(header)]}

    def api_inbox(self):
        return {"items": proto.view(proto.read_jsonl(self.inbox_p), proto.read_jsonl(self.dec_p))}

    def api_profile(self):
        return profile_summary(read_text(self.p("profile.local.yml")))

    def api_shortlist(self):
        return {"markdown": read_text(self.p("reports", "shortlist.md"))}

    def add_decision(self, body):
        inbox = proto.read_jsonl(self.inbox_p)
        d = {k: body.get(k, "") for k in ("item", "hash", "decision", "text")} if isinstance(body, dict) else body
        with WRITE_LOCK:
            ok, err = proto.validate_decision(d, inbox)
            if not ok:
                return False, err
            d["at"] = proto.now_iso()
            proto.append_jsonl(self.dec_p, d)
        return True, ""


def make_handler(app):
    class H(BaseHTTPRequestHandler):
        server_version = "Hirepair"
        sys_version = ""

        def log_message(self, *a):
            pass

        def _send(self, code, body=b"", ctype="application/json; charset=utf-8", extra=None):
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Content-Security-Policy", CSP)
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Referrer-Policy", "no-referrer")
            self.send_header("Cache-Control", "no-store")
            for k, v in (extra or {}).items():
                self.send_header(k, v)
            self.end_headers()
            if self.command != "HEAD":
                self.wfile.write(body)

        def _json(self, code, obj, extra=None):
            self._send(code, json.dumps(obj, ensure_ascii=False).encode("utf-8"), extra=extra)

        def _host_ok(self):
            if self.headers.get("Host", "") not in app.hosts:
                self._json(403, {"error": "bad host"})
                return False
            return True

        def do_GET(self):
            if not self._host_ok():
                return
            path = self.path.split("?", 1)[0]
            if path == "/":
                page = read_text(os.path.join(app.ui_dir, "index.html"))
                if page is None:
                    return self._send(500, b"ui/index.html missing", "text/plain; charset=utf-8")
                return self._send(200, page.replace("{{CSRF}}", app.token).encode("utf-8"), "text/html; charset=utf-8")
            if path.startswith("/static/"):
                name = path[len("/static/"):]
                ext = os.path.splitext(name)[1]
                if "/" in name or "\\" in name or name.startswith(".") or ext not in STATIC_TYPES:
                    return self._send(404, b"not found", "text/plain; charset=utf-8")
                body = read_text(os.path.join(app.ui_dir, name))
                if body is None:
                    return self._send(404, b"not found", "text/plain; charset=utf-8")
                return self._send(200, body.encode("utf-8"), STATIC_TYPES[ext])
            routes = {"/api/tracker": app.api_tracker, "/api/inbox": app.api_inbox,
                      "/api/profile": app.api_profile, "/api/shortlist": app.api_shortlist}
            fn = routes.get(path)
            if fn is None:
                return self._send(404, b"not found", "text/plain; charset=utf-8")
            tag = app.etag(path)
            if self.headers.get("If-None-Match") == tag:
                return self._send(304, extra={"ETag": tag})
            self._json(200, fn(), extra={"ETag": tag})

        def do_POST(self):
            if not self._host_ok():
                return
            if self.path.split("?", 1)[0] != "/api/decisions":
                return self._send(404, b"not found", "text/plain; charset=utf-8")
            origin = self.headers.get("Origin")
            if origin is not None and origin not in {f"http://{h}" for h in app.hosts}:
                return self._json(403, {"error": "bad origin"})
            if not secrets.compare_digest(self.headers.get("X-CSRF", ""), app.token):
                return self._json(403, {"error": "bad token"})
            if "application/json" not in self.headers.get("Content-Type", ""):
                return self._json(415, {"error": "json required"})
            try:
                n = int(self.headers.get("Content-Length", "0"))
            except ValueError:
                n = -1
            if n <= 0 or n > MAX_BODY:
                return self._json(413, {"error": "bad body size"})
            try:
                body = json.loads(self.rfile.read(n).decode("utf-8"))
            except ValueError:
                return self._json(400, {"error": "invalid json"})
            ok, err = app.add_decision(body)
            self._json(200 if ok else 400, {"ok": True} if ok else {"error": err})

    return H


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--port", type=int, default=8765)
    a = ap.parse_args()
    app = App(a.root, a.port)
    srv = ThreadingHTTPServer(("127.0.0.1", a.port), make_handler(app))
    print(f"Hirepair UI: http://127.0.0.1:{a.port}/  (local only, Ctrl+C to stop)")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
