#!/usr/bin/env python3
"""Drop already-handled job cards before any card is clicked. Stdlib only.

Input: the raw output(s) of scripts/linkedin_cards.js, one call per file or all pasted in one file,
in call order ("N=..;rows...MORE@n" parts are stitched back together).

Usage:
  python3 scripts/card_filter.py cards.txt [more.txt ...] [--seen data/seen-ids.txt] [--tracker tracker.md] [--json]
  ... | python3 scripts/card_filter.py - [...]

Drops: Applied/Başvuruldu badge, job ID in the seen-ID list or in a tracker Posting link,
company + role already in the tracker, duplicates on the page. Saved cards are kept and flagged.
Prints the cards to open, then one line of counts. Does not write any file.
"""
import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tracker_stats import parse  # noqa: E402

APPLIED = {"applied", "başvuruldu"}
SAVED = {"saved", "kaydedildi"}
COMPANY = {"company", "şirket", "sirket"}
ROLE = {"role", "pozisyon"}
POSTING = {"posting", "ilan"}
TITLE_MAX, COMPANY_MAX = 60, 40  # must match the slices in linkedin_cards.js


def norm(s, n=None):
    s = s.replace("İ", "i").lower()
    s = re.sub(r"[^\w]+", " ", s).strip()
    s = re.sub(r"\s+", " ", s)
    return s[:n] if n else s


def stitch(parts):
    """Join the parts of one or more calls; a row may be cut across a MORE@ boundary."""
    out = ""
    for p in parts:
        p = p.strip()
        p = re.sub(r"^N=\d+;", "", p)
        p = re.sub(r"MORE@\d+$", "", p)
        out += p
    return out


def rows_from(text):
    cards = []
    for raw in text.split("|"):
        f = raw.split("~")
        if len(f) < 2 or not f[1].strip():
            continue
        f += [""] * (5 - len(f))
        cards.append({"id": f[0].strip(), "title": f[1].strip(), "company": f[2].strip(),
                      "age": f[3].strip(), "badge": f[4].strip()})
    return cards


def read_seen(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return {line.strip() for line in fh if line.strip()}
    except FileNotFoundError:
        return set()


def tracker_keys(path):
    """Return ({company|role keys}, {job ids found in posting links})."""
    try:
        with open(path, encoding="utf-8") as fh:
            header, rows = parse(fh.read())
    except FileNotFoundError:
        return set(), set()
    if header is None:
        return set(), set()

    def idx(names):
        return next((i for i, h in enumerate(header) if h in names), -1)

    ci, ri, pi = idx(COMPANY), idx(ROLE), idx(POSTING)
    keys, ids = set(), set()
    for r in rows:
        if len(r) != len(header):
            continue
        if ci >= 0 and ri >= 0:
            keys.add(norm(r[ci], COMPANY_MAX) + "|" + norm(r[ri], TITLE_MAX))
        if pi >= 0:
            ids.update(re.findall(r"(?:/jobs/view/|currentJobId=)(\d+)", r[pi]))
    return keys, ids


def filter_cards(cards, seen, keys, tracker_ids):
    keep, counts, page = [], {"applied": 0, "seen_id": 0, "in_tracker": 0, "duplicate": 0}, set()
    for c in cards:
        key = norm(c["company"], COMPANY_MAX) + "|" + norm(c["title"], TITLE_MAX)
        badge = norm(c["badge"])
        dedupe = c["id"] or key
        if dedupe in page:
            counts["duplicate"] += 1
            continue
        page.add(dedupe)
        if badge in APPLIED:
            counts["applied"] += 1
        elif c["id"] and (c["id"] in seen or c["id"] in tracker_ids):
            counts["seen_id"] += 1
        elif key in keys:
            counts["in_tracker"] += 1
        else:
            c = dict(c, saved=badge in SAVED, needs_click=not c["id"])
            keep.append(c)
    return keep, counts


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("inputs", nargs="+")
    ap.add_argument("--seen", default=os.path.join("data", "seen-ids.txt"))
    ap.add_argument("--tracker", default="tracker.md")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    parts = []
    for p in a.inputs:
        if p == "-":
            parts.append(sys.stdin.read())
        else:
            with open(p, encoding="utf-8") as fh:
                parts.append(fh.read())
    cards = rows_from(stitch(parts))
    keys, tids = tracker_keys(a.tracker)
    keep, counts = filter_cards(cards, read_seen(a.seen), keys, tids)
    if a.json:
        print(json.dumps({"cards": len(cards), "open": keep, "dropped": counts}, ensure_ascii=False, indent=1))
        return 0
    for c in keep:
        flags = ("SAVED " if c["saved"] else "") + ("CLICK-FOR-ID " if c["needs_click"] else "")
        print(f"{c['id'] or '-':>12}  {c['title']} @ {c['company']}  [{c['age'] or '?'}] {flags}".rstrip())
    dropped = ", ".join(f"{k} {v}" for k, v in counts.items() if v) or "none"
    print(f"{len(cards)} cards: open {len(keep)}; dropped {dropped}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
