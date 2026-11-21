#!/usr/bin/env python3
"""Move old closed rows from tracker.md to tracker-archive.md. Stdlib only.

Usage: python3 scripts/tracker_archive.py [tracker.md] [--days 90] [--date YYYY-MM-DD] [--dry-run]

A row moves when its Date is more than --days ago and its Status is closed: ✅ (submitted) or ⛔
(rejected / dropped). Rows waiting for the human (⏳ ✉️ 💬 🔗 🔒) never move. The archive keeps the
tracker's header; card_filter.py, candidates_check.py and rescore_queue.py read both files, so archived
jobs are never prepared again, and tracker_stats.py counts both. Text outside the table is kept as is.
"""
import argparse
import os
import sys
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from card_filter import archive_path  # noqa: E402
from tracker_stats import STATUS, cells  # noqa: E402

DATE = {"date", "tarih"}
CLOSED = ("✅", "⛔")


def split(text, today, days):
    """(kept text, header line, separator line, moved row lines)."""
    lines = text.splitlines(keepends=True)
    header = sep = None
    di = si = -1
    kept, moved = [], []
    cutoff = today - timedelta(days=days)
    for line in lines:
        if not line.startswith("|"):
            kept.append(line)
            continue
        c = cells(line)
        if header is None:
            header = line
            names = [h.lower() for h in c]
            di = next((i for i, h in enumerate(names) if h in DATE), -1)
            si = next((i for i, h in enumerate(names) if h in STATUS), -1)
            kept.append(line)
            continue
        if sep is None and set("".join(c)) <= set("-: "):
            sep = line
            kept.append(line)
            continue
        old = False
        if di >= 0 and si >= 0 and len(c) > max(di, si):
            try:
                old = date.fromisoformat(c[di][:10]) < cutoff
            except ValueError:
                old = False
        if old and c[si].startswith(CLOSED):
            moved.append(line)
        else:
            kept.append(line)
    return "".join(kept), header, sep, moved


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("tracker", nargs="?", default="tracker.md")
    ap.add_argument("--days", type=int, default=90)
    ap.add_argument("--date")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    today = date.fromisoformat(a.date) if a.date else date.today()
    try:
        with open(a.tracker, encoding="utf-8") as fh:
            text = fh.read()
    except FileNotFoundError:
        print(f"error: {a.tracker} not found", file=sys.stderr)
        return 1
    kept, header, sep, moved = split(text, today, a.days)
    if header is None:
        print("error: no table found", file=sys.stderr)
        return 1
    print(f"{len(moved)} closed rows older than {a.days} days" + (" (dry run, nothing moved)" if a.dry_run else ""))
    if a.dry_run or not moved:
        return 0
    arch = archive_path(a.tracker)
    new_file = not os.path.exists(arch) or os.path.getsize(arch) == 0
    with open(arch, "a", encoding="utf-8") as fh:
        if new_file:
            fh.write("# Tracker archive\n\n" + header + (sep or ""))
        fh.writelines(r if r.endswith("\n") else r + "\n" for r in moved)
    tmp = a.tracker + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        fh.write(kept)
    os.replace(tmp, a.tracker)  # archive written first: a crash in between duplicates rows, never loses them
    print(f"moved to {arch}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
