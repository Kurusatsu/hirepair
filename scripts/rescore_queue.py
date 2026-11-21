#!/usr/bin/env python3
"""List cached jobs to re-score after the profile changed, without opening any page. Stdlib only.

Usage:
  python3 scripts/rescore_queue.py --fingerprint [--profile profile.local.yml]
  python3 scripts/rescore_queue.py [--profile profile.local.yml] [--candidates "data/candidates-*.md"]
                                   [--jobs data/jobs] [--tracker tracker.md] [--max-age 14] [--date YYYY-MM-DD] [--json]

--fingerprint  print the hash of the scoring-relevant profile fields; the search writes it into every
               candidate file as "Profile: <hash>" right under the "# Candidates <date>" heading.

The queue holds every job whose latest score was made with a different (or unknown) profile hash, whose
text is cached in data/jobs/<id>.txt, that is not in the tracker, and that was posted at most --max-age
days ago (file date minus "Age (days)"). Titles card_filter.py never opened have no cached text and are
not covered. Does not write any file.
"""
import argparse
import glob
import json
import os
import re
import sys
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from candidates_check import PROFILE_LINE, num, tables  # noqa: E402
from card_filter import COMPANY_MAX, TITLE_MAX, fingerprint, norm, tracker_keys  # noqa: E402

FILE_DATE = re.compile(r"(\d{4}-\d{2}-\d{2})")


def latest_scores(paths):
    """{job id: row dict} from candidate files, later files (by date in the name) winning."""
    def key(p):
        m = FILE_DATE.search(os.path.basename(p))
        return (m.group(1) if m else "", p)

    latest = {}
    for p in sorted(paths, key=key):
        with open(p, encoding="utf-8") as fh:
            text = fh.read()
        m = FILE_DATE.search(os.path.basename(p))
        fdate = m.group(1) if m else None
        fp = PROFILE_LINE.search(text)
        cand = next(((h, rows) for k, (h, rows) in tables(text).items() if k.startswith("candidates")), None)
        if cand is None:
            continue
        h, rows = cand
        col = {x: i for i, x in enumerate(h)}
        if "job id" not in col:
            continue
        for r in rows:
            jid = r[col["job id"]].strip()
            if not jid:
                continue
            get = lambda k: r[col[k]].strip() if k in col else ""  # noqa: E731
            latest[jid] = {"job_id": jid, "company": get("company"), "role": get("role"),
                           "score": num(get("score")), "age_days": num(get("age (days)")),
                           "file": p, "file_date": fdate, "profile": fp.group(1) if fp else None}
    return latest


def queue(latest, current_fp, jobs_dir, tracker_path, today, max_age):
    keys, tids = tracker_keys(tracker_path)
    out, skipped = [], {"same_profile": 0, "no_text": 0, "in_tracker": 0, "too_old": 0}
    for jid, r in sorted(latest.items()):
        if r["profile"] == current_fp:
            skipped["same_profile"] += 1
            continue
        text = os.path.join(jobs_dir, f"{jid}.txt")
        if not os.path.isfile(text):
            skipped["no_text"] += 1
            continue
        k = norm(r["company"], COMPANY_MAX) + "|" + norm(r["role"], TITLE_MAX)
        if jid in tids or k in keys:
            skipped["in_tracker"] += 1
            continue
        if r["file_date"] and r["age_days"] is not None:
            posted = date.fromisoformat(r["file_date"]) - timedelta(days=r["age_days"])
            if (today - posted).days > max_age:
                skipped["too_old"] += 1
                continue
        out.append(dict(r, text=text))
    out.sort(key=lambda r: -(r["score"] or 0))
    return out, skipped


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--profile", default="profile.local.yml")
    ap.add_argument("--fingerprint", action="store_true")
    ap.add_argument("--candidates", default=os.path.join("data", "candidates-*.md"))
    ap.add_argument("--jobs", default=os.path.join("data", "jobs"))
    ap.add_argument("--tracker", default="tracker.md")
    ap.add_argument("--max-age", type=int, default=14)
    ap.add_argument("--date")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    try:
        with open(a.profile, encoding="utf-8") as fh:
            fp = fingerprint(fh.read())
    except FileNotFoundError:
        print(f"error: {a.profile} not found", file=sys.stderr)
        return 1
    if a.fingerprint:
        print(fp)
        return 0
    today = date.fromisoformat(a.date) if a.date else date.today()
    q, skipped = queue(latest_scores(glob.glob(a.candidates)), fp, a.jobs, a.tracker, today, a.max_age)
    if a.json:
        print(json.dumps({"profile": fp, "queue": q, "skipped": skipped}, ensure_ascii=False, indent=1))
        return 0
    print(f"Profile {fp}: {len(q)} cached jobs to re-score from text; skipped "
          + ", ".join(f"{k} {v}" for k, v in skipped.items()))
    for r in q:
        old = f"{r['score']:.1f}" if r["score"] is not None else "?"
        print(f"RESCORE {r['job_id']}  was {old} ({r['profile'] or 'no hash'})  {r['company']} / {r['role']}  {r['text']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
