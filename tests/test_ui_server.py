import http.client
import json
import os
import sys
import tempfile
import threading
import unittest
from http.server import ThreadingHTTPServer

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import ui_protocol as proto  # noqa: E402
import ui_server  # noqa: E402

TRACKER = "| Date | Company | Role | Status |\n|---|---|---|---|\n| 2030-01-01 | A | B | ⏳ Ready |\n"
PROFILE = 'approved_roles:\n  approved: true\n  roles:\n    - title: "Business Analyst"\nlimits:   # asked in onboarding\n  scans_per_day: 1            # one round\n  approval_mode: "one_by_one"\n'


class Server(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        r = cls.tmp.name
        open(os.path.join(r, "tracker.md"), "w", encoding="utf-8").write(TRACKER)
        open(os.path.join(r, "profile.local.yml"), "w", encoding="utf-8").write(PROFILE)
        open(os.path.join(r, "cv.local.md"), "w", encoding="utf-8").write("SECRET CV")
        cls.item = proto.make_item("approve", "cv_upload", "CV ready", preview="p", item_id="a1")
        cls.human = proto.make_item("human", "consent", "Tick consent", item_id="h1")
        proto.append_jsonl(os.path.join(r, "data", "inbox.jsonl"), cls.item)
        proto.append_jsonl(os.path.join(r, "data", "inbox.jsonl"), cls.human)
        probe = ThreadingHTTPServer(("127.0.0.1", 0), ui_server.BaseHTTPRequestHandler)
        cls.port = probe.server_address[1]
        probe.server_close()
        cls.app = ui_server.App(r, cls.port)
        cls.srv = ThreadingHTTPServer(("127.0.0.1", cls.port), ui_server.make_handler(cls.app))
        threading.Thread(target=cls.srv.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.srv.shutdown()
        cls.srv.server_close()
        cls.tmp.cleanup()

    def req(self, method, path, body=None, headers=None, host=None):
        c = http.client.HTTPConnection("127.0.0.1", self.port)
        h = {"Host": host or f"127.0.0.1:{self.port}"}
        h.update(headers or {})
        c.request(method, path, body=body, headers=h)
        r = c.getresponse()
        data = r.read()
        c.close()
        return r.status, dict(r.getheaders()), data

    def post(self, obj, token=True, **kw):
        h = {"Content-Type": "application/json"}
        if token:
            h["X-CSRF"] = self.app.token
        h.update(kw.pop("headers", {}))
        return self.req("POST", "/api/decisions", json.dumps(obj), h, **kw)

    def test_reads(self):
        s, h, b = self.req("GET", "/api/tracker")
        self.assertEqual(s, 200)
        self.assertEqual(json.loads(b)["rows"][0][1], "A")
        self.assertIn("default-src 'self'", h["Content-Security-Policy"])
        prof = json.loads(self.req("GET", "/api/profile")[2])
        self.assertEqual(prof["roles"], ["Business Analyst"])
        self.assertEqual(prof["limits"]["scans_per_day"], 1)
        self.assertTrue(prof["approved"])
        items = json.loads(self.req("GET", "/api/inbox")[2])["items"]
        self.assertEqual({i["id"] for i in items}, {"a1", "h1"})

    def test_etag_returns_304(self):
        _, h, _ = self.req("GET", "/api/tracker")
        s, _, _ = self.req("GET", "/api/tracker", headers={"If-None-Match": h["ETag"]})
        self.assertEqual(s, 304)

    def test_wrong_host_rejected(self):
        self.assertEqual(self.req("GET", "/api/tracker", host="evil.example:80")[0], 403)

    def test_cv_and_other_files_are_never_served(self):
        for path in ("/cv.local.md", "/static/../cv.local.md", "/static/%2e%2e/cv.local.md", "/static/.hidden.js", "/static/a.md"):
            self.assertEqual(self.req("GET", path)[0], 404, path)

    def test_post_needs_token_origin_and_json(self):
        body = {"item": "a1", "hash": self.item["hash"], "decision": "approve"}
        self.assertEqual(self.post(body, token=False)[0], 403)
        self.assertEqual(self.post(body, headers={"Origin": "http://evil.example"})[0], 403)
        s, _, _ = self.req("POST", "/api/decisions", json.dumps(body), {"X-CSRF": self.app.token, "Content-Type": "text/plain"})
        self.assertEqual(s, 415)

    def test_human_item_cannot_be_approved_and_stale_is_rejected(self):
        s, _, b = self.post({"item": "h1", "hash": self.human["hash"], "decision": "approve"})
        self.assertEqual(s, 400)
        s, _, b = self.post({"item": "a1", "hash": "sha256:old", "decision": "approve"})
        self.assertEqual(s, 400)
        self.assertIn("stale", json.loads(b)["error"])

    def test_valid_decision_is_appended_and_visible(self):
        s, _, _ = self.post({"item": "h1", "hash": self.human["hash"], "decision": "done"})
        self.assertEqual(s, 200)
        rows = proto.read_jsonl(os.path.join(self.tmp.name, "data", "decisions.jsonl"))
        self.assertEqual(rows[-1]["decision"], "done")
        items = {i["id"]: i for i in json.loads(self.req("GET", "/api/inbox")[2])["items"]}
        self.assertEqual(items["h1"]["status"], "decided")


if __name__ == "__main__":
    unittest.main()
