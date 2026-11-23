#!/usr/bin/env python3
"""Turn LinkedIn's job tracker (My jobs) into tracker events. Stdlib only.

Usage: python3 scripts/linkedin_sync.py MYJOBS.txt [more.txt ...] [--today YYYY-MM-DD] [--since-days 14]
                                       [--out data/mail-events-<date>.jsonl]

MYJOBS.txt holds the raw outputs of scripts/linkedin_myjobs.js (applied, interview, saved or in_progress tab).
Applied rows become "applied" events (the application went out on LinkedIn) plus one event per signal LinkedIn
shows: viewed (Application viewed), downloaded (Resume downloaded), closed (No longer accepting applications).
Interview rows become "interview" events. Draft rows (unfinished Easy Apply) become "draft" events and
"Clicked apply" rows (a company form opened from LinkedIn, not confirmed) become "clicked" events: a job with
no tracker row is proposed as a ⏳ / 🔗 row; a draft whose posting closed only notes that on an existing row. The events are appended to the same JSONL file the reply check
writes, so `python3 scripts/reply_reconcile.py check <file> --write-replies --inbox` handles both: Reply
cells for the signals, and approval cards for rows that are still waiting or missing (applications sent on
LinkedIn outside Hirepair). Saved
rows are listed as SAVED lines; with --manual FILE they are also added to the manual candidates list
(data/manual-candidates.md), which the daily scan opens and scores first, so a job saved on the phone is
picked up by the next scan.
LinkedIn shows ages such as "1w ago", so dates of older applications are approximate (7 days = "1w").
"""
import argparse
import json
import os
import re
import sys
from datetime import date, timedelta

SIGNALS = ("viewed", "downloaded", "closed")


def rows_from(text):
    """Rows (id, days, stage, signals, title, company) from one or more pasted outputs."""
    joined = ""
    for part in re.split(r"(?=N=\d+;)", text.strip()):
        part = re.sub(r"^N=\d+;", "", part.strip())
        joined += re.sub(r"MORE@\d+$", "", part) + ("" if re.search(r"MORE@\d+$", part) else "|")
    out = []
    for raw in joined.split("|"):
        f = raw.split("~")
        if len(f) < 6 or not f[0].strip().isdigit():
            continue
        try:
            days = int(f[1])
        except ValueError:
            days = -1
        out.append({"id": f[0].strip(), "days": days, "stage": f[2].strip(), "signals": [s for s in f[3].split("+") if s],
                    "title": f[4].strip(), "company": f[5].strip()})
    return out


def events(rows, today, since_days):
    ev, listed = [], []
    for r in rows:
        base = {"company": r["company"], "role": r["title"], "ref": r["id"], "from": "linkedin.com",
                "source": "linkedin", "channel": "LinkedIn form", "url": f"https://www.linkedin.com/jobs/view/{r['id']}/"}
        if r["stage"] == "applied":
            if r["days"] < 0 or r["days"] > since_days:
                continue
            when = (today - timedelta(days=r["days"])).isoformat()
            ev.append({**base, "kind": "applied", "date": when})
            ev += [{**base, "kind": s, "date": today.isoformat()} for s in SIGNALS if s in r["signals"]]
        elif r["stage"] in ("draft", "clicked_apply"):
            if r["days"] > since_days:
                continue
            if "closed" in r["signals"]:  # a dead draft: only worth a note on an existing row
                ev.append({**base, "kind": "closed", "date": today.isoformat()})
            else:
                ev.append({**base, "kind": "draft" if r["stage"] == "draft" else "clicked", "date": today.isoformat()})
        elif r["stage"] == "interview":
            ev.append({**base, "kind": "interview", "date": today.isoformat(), "undated": True})
        else:
            listed.append(r)
    return ev, listed


def add_saved(path, saved, today):
    """Append saved jobs to the manual candidates list as bullets; skip job IDs already in the file."""
    try:
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
    except FileNotFoundError:
        text = ""
    new = [r for r in saved if f"/jobs/view/{r['id']}" not in text]
    if new:
        head = "" if "## LinkedIn saved jobs" in text else "\n## LinkedIn saved jobs\n\n"
        lines = [f"- {r['company']} | {r['title']} | https://www.linkedin.com/jobs/view/{r['id']}/ | saved, seen {today}"
                 for r in new]
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, "a", encoding="utf-8") as fh:
            fh.write(("" if text else "# Manual candidates\n") + ("\n" if text and not text.endswith("\n") else "")
                     + head + "\n".join(lines) + "\n")
    return len(new)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+")
    ap.add_argument("--today")
    ap.add_argument("--since-days", type=int, default=14)
    ap.add_argument("--out")
    ap.add_argument("--manual", help="append saved jobs to this manual candidates file (skips ones already in it)")
    a = ap.parse_args(argv)
    today = date.fromisoformat(a.today) if a.today else date.today()
    rows = []
    for p in a.files:
        try:
            with open(p, encoding="utf-8") as fh:
                rows += rows_from(fh.read())
        except OSError as e:
            print(f"error: {e}", file=sys.stderr)
            return 1
    ev, listed = events(rows, today, a.since_days)
    out = a.out or os.path.join("data", f"mail-events-{today.isoformat()}.jsonl")
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    with open(out, "a", encoding="utf-8") as fh:
        for e in ev:
            fh.write(json.dumps(e, ensure_ascii=False) + "\n")
    kinds = {k: sum(1 for e in ev if e["kind"] == k) for k in ("applied", "interview", "draft", "clicked") + SIGNALS}
    print(f"{len(rows)} LinkedIn rows -> {len(ev)} events in {out} ("
          + ", ".join(f"{k} {v}" for k, v in kinds.items()) + f"; applications older than {a.since_days} days skipped)")
    for r in listed:
        tag = "SAVED" if r["stage"] == "saved" else r["stage"].upper()
        print(f"{tag:6} {r['id']}  {r['title']} @ {r['company']}")
    saved = [r for r in listed if r["stage"] == "saved"]
    if a.manual and saved:
        print(f"added {add_saved(a.manual, saved, today)} saved jobs to {a.manual}")
    print(f"next: python3 scripts/reply_reconcile.py check {out} --write-replies --inbox")
    return 0


if __name__ == "__main__":
    sys.exit(main())
