#!/usr/bin/env python3
"""Count tracker rows by status emoji and by channel.

Usage: python3 scripts/tracker_stats.py [tracker.md]
Reads a Markdown table; the header row decides which columns are Status/Channel/Reply
(English or the original Turkish names). Standard library only.
"""
import sys
from collections import Counter

STATUS = {"status", "durum"}
CHANNEL = {"channel", "kanal"}
REPLY = {"reply", "yanıt", "yanit"}
NO_REPLY = {"", "-", "—"}


def cells(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def parse(text):
    header = None
    rows = []
    for line in text.splitlines():
        if not line.startswith("|"):
            continue
        c = cells(line)
        if header is None:
            header = [h.lower() for h in c]
            continue
        if set("".join(c)) <= set("-: "):
            continue
        rows.append(c)
    return header, rows


def col(header, names):
    for i, h in enumerate(header):
        if h in names:
            return i
    raise SystemExit("missing column: " + "/".join(sorted(names)))


def status_key(value):
    parts = value.split()
    return parts[0] if parts else "(empty)"


def main(path):
    with open(path, encoding="utf-8") as f:
        header, rows = parse(f.read())
    if header is None:
        raise SystemExit("no table found")
    si, ci, ri = col(header, STATUS), col(header, CHANNEL), col(header, REPLY)
    rows = [r for r in rows if len(r) > max(si, ci, ri)]
    status = Counter(status_key(r[si]) for r in rows)
    print("rows:", len(rows))
    print("by status:")
    for k, v in status.most_common():
        print(f"  {k}  {v}")
    print("by channel (rows / with reply):")
    chan = Counter(r[ci] for r in rows)
    for k, v in chan.most_common():
        replied = sum(1 for r in rows if r[ci] == k and r[ri] not in NO_REPLY)
        print(f"  {k}: {v} / {replied}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "tracker.md")
