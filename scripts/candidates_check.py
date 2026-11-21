#!/usr/bin/env python3
"""Check the search subagent's candidate file and print the prepare queue. Stdlib only.

Usage:
  python3 scripts/candidates_check.py data/candidates-<date>.md [--profile profile.local.yml]
                                      [--tracker tracker.md] [--jobs data/jobs] [--date YYYY-MM-DD] [--json]
  python3 scripts/candidates_check.py data/candidates-<date>.md --done-only

--done-only  exit 0 once the file ends with a SUBAGENT_DONE line, else exit 2 (for a Monitor until-loop).

The file format is in prompts/daily-scan.md ("Search subagent"). Exit codes: 0 ok, 1 problems that
make the scan incomplete or a row invalid (listed), 2 subagent not done yet. Does not write any file.
"""
import argparse
import json
import os
import re
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from card_filter import COMPANY_MAX, TITLE_MAX, mini_yaml, norm, tracker_keys  # noqa: E402
from tracker_stats import parse  # noqa: E402

DONE = re.compile(r"^SUBAGENT_DONE\b", re.M)
MUST_KNOW = ("easy apply", "location", "applicants", "age (days)")


def tables(text):
    """Split the file into {section heading (lowercase): (header, rows)} for every Markdown table."""
    out, name, buf = {}, "", []

    def flush():
        if buf:
            h, rows = parse("\n".join(buf))
            if h:
                out[name] = (h, [r for r in rows if len(r) == len(h)])

    for line in text.splitlines():
        if line.startswith("#"):
            flush()
            buf = []
            name = line.lstrip("#").strip().lower()
        elif line.startswith("|"):
            buf.append(line)
    flush()
    return out


def num(s):
    m = re.match(r"^\s*(\d+(?:[.,]\d+)?)", s or "")
    return float(m.group(1).replace(",", ".")) if m else None


def prepared_today(tracker_path, today):
    try:
        with open(tracker_path, encoding="utf-8") as fh:
            header, rows = parse(fh.read())
    except FileNotFoundError:
        return 0
    if not header:
        return 0
    di = next((i for i, h in enumerate(header) if h in ("date", "tarih")), -1)
    si = next((i for i, h in enumerate(header) if h in ("status", "durum")), -1)
    n = 0
    for r in rows:
        if len(r) == len(header) and di >= 0 and r[di].strip() == today:
            if si < 0 or not r[si].strip().startswith("⛔"):
                n += 1
    return n


def check(text, profile_text="", tracker_path="tracker.md", jobs_dir=os.path.join("data", "jobs"), today=None):
    today = today or date.today().isoformat()
    t = tables(text)
    problems, warnings = [], []
    cand = next(((h, rows) for k, (h, rows) in t.items() if k.startswith("candidates")), None)
    if cand is None:
        return {"done": bool(DONE.search(text)), "problems": ["no 'Candidates' table"], "warnings": [],
                "queue": [], "next": [], "coverage": {}}
    header, rows = cand
    col = {h: i for i, h in enumerate(header)}
    for need in ("job id", "company", "role", "score", "url", "evidence") + MUST_KNOW:
        if need not in col:
            problems.append(f"Candidates table has no '{need}' column")
    if problems:
        return {"done": bool(DONE.search(text)), "problems": problems, "warnings": [], "queue": [], "next": [],
                "coverage": {}}

    def g(r, k):
        return r[col[k]].strip() if k in col else ""

    keys, tids = tracker_keys(tracker_path)
    items = []
    for r in rows:
        jid, score = g(r, "job id"), num(g(r, "score"))
        label = f"{g(r, 'company')} / {g(r, 'role')}"
        if score is None or not 1 <= score <= 5:
            problems.append(f"{label}: score must be 1-5, got '{g(r, 'score')}'")
            continue
        if score > 3.5 and '"' not in g(r, "evidence") and "“" not in g(r, "evidence"):
            problems.append(f"{label}: score {score} above 3.5 needs a quoted job requirement in Evidence")
        if score >= 3.0:
            for k in MUST_KNOW:
                if g(r, k) in ("", "?", "-"):
                    problems.append(f"{label}: '{k}' is required for scores 3.0+ (got '{g(r, k)}')")
            if jid and not os.path.isfile(os.path.join(jobs_dir, f"{jid}.txt")):
                warnings.append(f"{label}: job text not cached at {jobs_dir}/{jid}.txt")
        key = norm(g(r, "company"), COMPANY_MAX) + "|" + norm(g(r, "role"), TITLE_MAX)
        handled = (jid and jid in tids) or key in keys
        items.append({"job_id": jid, "company": g(r, "company"), "role": g(r, "role"), "score": score,
                      "age_days": num(g(r, "age (days)")), "applicants": num(g(r, "applicants")),
                      "url": g(r, "url"), "in_tracker": bool(handled)})

    coverage = {"working": 0, "empty": 0, "failed": []}
    cov = next(((h, rs) for k, (h, rs) in t.items() if k.startswith("coverage")), None)
    if cov is None:
        problems.append("no 'Coverage' table: cannot tell which queries ran")
    else:
        ch, crows = cov
        qi = ch.index("query") if "query" in ch else 0
        ri = ch.index("result") if "result" in ch else len(ch) - 1
        for r in crows:
            res = norm(r[ri])
            if res.startswith("fail"):
                coverage["failed"].append(r[qi])
            elif res.startswith("empty"):
                coverage["empty"] += 1
            else:
                coverage["working"] += 1
        if coverage["failed"]:
            problems.append("queries failed (scan incomplete, re-run them): " + ", ".join(coverage["failed"]))

    y = mini_yaml(profile_text or "")
    per_round = int(num((y["limits.max_prepared_per_round"] or ["5"])[0]) or 5)
    cap = int(num((y["limits.daily_prepared_cap"] or [str(per_round)])[0]) or per_round)
    room = max(0, min(per_round, cap - prepared_today(tracker_path, today)))
    pool = [i for i in items if i["score"] >= 3.0 and not i["in_tracker"]]
    big = float("inf")
    pool.sort(key=lambda i: (-i["score"], i["age_days"] if i["age_days"] is not None else big,
                             i["applicants"] if i["applicants"] is not None else big))
    return {"done": bool(DONE.search(text)), "problems": problems, "warnings": warnings, "coverage": coverage,
            "rows": len(items), "room": room, "queue": pool[:room], "next": pool[room:]}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--profile", default="profile.local.yml")
    ap.add_argument("--tracker", default="tracker.md")
    ap.add_argument("--jobs", default=os.path.join("data", "jobs"))
    ap.add_argument("--date")
    ap.add_argument("--done-only", action="store_true")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    try:
        with open(a.file, encoding="utf-8") as fh:
            text = fh.read()
    except FileNotFoundError:
        if not a.done_only:
            print(f"not started: {a.file} does not exist")
        return 2
    if a.done_only:
        return 0 if DONE.search(text) else 2
    try:
        with open(a.profile, encoding="utf-8") as fh:
            prof = fh.read()
    except FileNotFoundError:
        prof = ""
    r = check(text, prof, a.tracker, a.jobs, a.date)
    if a.json:
        print(json.dumps(r, ensure_ascii=False, indent=1))
    else:
        if not r["done"]:
            print("NOT DONE: no SUBAGENT_DONE line yet")
        c = r["coverage"]
        if c:
            print(f"{r.get('rows', 0)} scored rows; queries working {c['working']}, empty {c['empty']}, "
                  f"failed {len(c['failed'])}; room today {r.get('room', 0)}")
        for p in r["problems"]:
            print("PROBLEM", p)
        for w in r["warnings"]:
            print("WARN   ", w)
        for i in r["queue"]:
            print(f"PREPARE {i['score']:.1f}  {i['company']} / {i['role']}  {i['job_id'] or '-'}")
        for i in r["next"]:
            print(f"NEXT    {i['score']:.1f}  {i['company']} / {i['role']}  {i['job_id'] or '-'}")
    if not r["done"]:
        return 2
    return 1 if r["problems"] else 0


if __name__ == "__main__":
    sys.exit(main())
