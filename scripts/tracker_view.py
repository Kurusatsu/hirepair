#!/usr/bin/env python3
"""Read-only local view of tracker.md: status counts, a "waiting for you" list and a filterable table.

Usage: python3 scripts/tracker_view.py [tracker.md] [--port 8765] [--out tracker.html]

Serves on 127.0.0.1 only and re-reads the file on every request. It never writes to the tracker
and has no buttons that act on anything; approvals stay in the chat. Standard library only.
"""
import argparse
import html
import os
import re
import sys
from collections import Counter
from http.server import BaseHTTPRequestHandler, HTTPServer

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tracker_stats import STATUS, parse  # noqa: E402

WAITING = {"⏳", "✉", "💬", "🔗", "🔒", "⏸", "📋"}
POSTING = {"posting", "ilan"}
ROLE = {"role", "pozisyon"}
COMPANY = {"company", "şirket"}
CSS = """
:root{--bg:#fff;--fg:#1a1a1a;--mut:#666;--line:#ddd;--card:#f6f6f6;--acc:#0b5fff}
@media (prefers-color-scheme:dark){:root{--bg:#161616;--fg:#eee;--mut:#9a9a9a;--line:#333;--card:#222;--acc:#7aa7ff}}
body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.5 system-ui,sans-serif}
main{max-width:1100px;margin:0 auto;padding:16px}
h1{font-size:1.4rem;margin:.2em 0}h2{font-size:1.05rem;margin:1.4em 0 .5em}
.chips{display:flex;flex-wrap:wrap;gap:8px}.chip{background:var(--card);border:1px solid var(--line);border-radius:999px;padding:2px 12px}
.wait li{margin:.3em 0}.mut{color:var(--mut)}a{color:var(--acc)}
input{width:100%;box-sizing:border-box;padding:8px;border:1px solid var(--line);border-radius:6px;background:var(--bg);color:var(--fg);margin:8px 0}
.wrap{overflow-x:auto}table{border-collapse:collapse;width:100%;font-size:13px}
th,td{border-bottom:1px solid var(--line);padding:6px 8px;text-align:left;vertical-align:top}th{position:sticky;top:0;background:var(--bg)}
"""


def status_emoji(value):
    parts = value.split()
    return parts[0].replace("️", "") if parts else ""


def esc(t):
    return html.escape(t, quote=True)


def cell_html(value, linkable):
    if linkable and re.match(r"^https?://\S+$", value):
        return f'<a href="{esc(value)}" rel="noreferrer noopener">link</a>'
    return esc(value)


def render(text, path="tracker.md"):
    header, rows = parse(text)
    if header is None:
        return "<!doctype html><meta charset=utf-8><title>Tracker</title><body>No table found in " + esc(path)
    si = next((i for i, h in enumerate(header) if h in STATUS), None)
    pi = next((i for i, h in enumerate(header) if h in POSTING), None)
    ri = next((i for i, h in enumerate(header) if h in ROLE), None)
    ci = next((i for i, h in enumerate(header) if h in COMPANY), None)
    rows = [r for r in rows if len(r) == len(header)]
    counts = Counter(status_emoji(r[si]) for r in rows) if si is not None else Counter()
    waiting = [r for r in rows if si is not None and status_emoji(r[si]) in WAITING]

    out = ["<!doctype html><html lang=en><head><meta charset=utf-8>",
           '<meta name=viewport content="width=device-width,initial-scale=1">',
           f"<title>Hirepair tracker</title><style>{CSS}</style></head><body><main>",
           f"<h1>Tracker</h1><p class=mut>Read-only view of {esc(path)}: {len(rows)} rows. "
           "Approvals and sending happen in the chat, not here.</p>",
           '<div class=chips>' + "".join(f'<span class=chip>{esc(k)} {v}</span>' for k, v in counts.most_common()) + "</div>",
           f"<h2>Waiting for you ({len(waiting)})</h2>"]
    if waiting:
        out.append("<ul class=wait>")
        for r in waiting:
            who = f"{r[ci]} - {r[ri]}" if ci is not None and ri is not None else " / ".join(r[:3])
            out.append(f"<li><b>{esc(who)}</b> <span class=mut>{esc(r[si])}</span></li>")
        out.append("</ul>")
    else:
        out.append("<p class=mut>Nothing is waiting.</p>")
    out += ["<h2>All rows</h2>", '<input id=q placeholder="Filter (company, role, status...)" aria-label=Filter>',
            '<div class=wrap><table id=t><thead><tr>' + "".join(f"<th>{esc(h)}</th>" for h in header) + "</tr></thead><tbody>"]
    for r in rows:
        out.append("<tr>" + "".join(f"<td>{cell_html(v, i == pi)}</td>" for i, v in enumerate(r)) + "</tr>")
    out += ["</tbody></table></div>",
            "<script>document.getElementById('q').addEventListener('input',function(e){var v=e.target.value.toLowerCase();"
            "document.querySelectorAll('#t tbody tr').forEach(function(r){r.style.display=r.textContent.toLowerCase().includes(v)?'':'none'})})</script>",
            "</main></body></html>"]
    return "".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("tracker", nargs="?", default="tracker.md")
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--out", help="write a static HTML file instead of serving")
    a = ap.parse_args()

    def page():
        with open(a.tracker, encoding="utf-8") as f:
            return render(f.read(), os.path.basename(a.tracker))

    if a.out:
        with open(a.out, "w", encoding="utf-8") as f:
            f.write(page())
        print("wrote", a.out)
        return

    class H(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path != "/":
                self.send_error(404)
                return
            body = page().encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *args):
            pass

    print(f"Serving {a.tracker} read-only at http://127.0.0.1:{a.port}/ (Ctrl+C to stop)")
    HTTPServer(("127.0.0.1", a.port), H).serve_forever()


if __name__ == "__main__":
    main()
