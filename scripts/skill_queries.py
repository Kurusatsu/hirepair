#!/usr/bin/env python3
"""Suggest changes to the profile's queries.skills. Stdlib only; never writes the profile.

Usage:
  python3 scripts/skill_queries.py [--profile profile.local.yml] [--jobs data/jobs] [--cv cv.local.md]
                                   [--candidates "data/candidates-*.md"] [--days 30] [--stale-days 7]
                                   [--min-share 0.15] [--date YYYY-MM-DD] [--stale-only] [--json]

ADD    a skill the CV states that at least --min-share of the job texts cached in the last --days ask for,
       not yet in queries.skills (from skill_gap.py).
DROP   a skill query whose Coverage rows (Kind "skills") found nothing new for --stale-days: no "working"
       result since its first run, or since its last "working" run. "failed" runs count neither way.
CHECK  a skill query the CV does not state (skill search must stay CV-backed).
--stale-only  only the DROP / CHECK part (cheap; the daily scan runs it, the full report runs monthly).
The user approves every change in chat before anyone edits profile.local.yml.
"""
import argparse
import glob
import json
import os
import sys
import time
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from candidates_check import tables  # noqa: E402
from card_filter import mini_yaml, norm  # noqa: E402
from rescore_queue import FILE_DATE  # noqa: E402
import skill_gap  # noqa: E402


def recent_jobs(jobs_dir, today, days):
    """{name: text} of cached job texts modified within the last `days` days of `today`."""
    cutoff = time.mktime((today - timedelta(days=days)).timetuple())
    out = {}
    for p in sorted(glob.glob(os.path.join(jobs_dir, "*.txt")) + glob.glob(os.path.join(jobs_dir, "*.md"))):
        if os.path.getmtime(p) >= cutoff:
            out[os.path.basename(p)] = skill_gap.read(p)
    return out


def skill_runs(paths):
    """{normalised query: [(date, result)]} from the Coverage tables (Kind 'skills') of candidate files."""
    runs = {}
    for p in paths:
        m = FILE_DATE.search(os.path.basename(p))
        if not m:
            continue
        d = date.fromisoformat(m.group(1))
        with open(p, encoding="utf-8") as fh:
            cov = next(((h, rs) for k, (h, rs) in tables(fh.read()).items() if k.startswith("coverage")), None)
        if cov is None:
            continue
        h, rows = cov
        qi, ki = h.index("query") if "query" in h else 0, h.index("kind") if "kind" in h else -1
        ri = h.index("result") if "result" in h else len(h) - 1
        for r in rows:
            if ki >= 0 and not norm(r[ki]).startswith("skill"):
                continue
            runs.setdefault(norm(r[qi]), []).append((d, norm(r[ri])))
    return runs


def stale(query, runs, today, stale_days):
    """Days without a new result if the query is stale, else None."""
    rs = sorted(runs.get(norm(query), []))
    if not rs:
        return None
    working = [d for d, res in rs if res.startswith("work")]
    since = working[-1] if working else rs[0][0]
    if not [d for d, res in rs if res.startswith("empty") and (not working or d > since)]:
        return None
    days = (today - since).days
    return days if days >= stale_days else None


def suggest(profile_text, jobs, cv_text, runs, vocab, today, min_share=0.15, stale_days=7, stale_only=False):
    current = mini_yaml(profile_text)["queries.skills"]
    in_cv = skill_gap.skills_in(cv_text, vocab) if cv_text else set()
    cur_canon = set()
    out = {"current": current, "add": [], "drop": [], "check": [], "jobs": len(jobs)}
    for q in current:
        canon = skill_gap.skills_in(q, vocab)
        cur_canon |= canon
        if cv_text and canon and not canon & in_cv:
            out["check"].append(q)
        days = stale(q, runs, today, stale_days)
        if days is not None:
            out["drop"].append({"query": q, "days": days})
    if not stale_only:
        rep = skill_gap.analyse(jobs, cv_text, None, vocab, min_share)
        share = {r["skill"]: r for r in rep["demand"]}
        out["add"] = [{"skill": s, "jobs": share[s]["jobs"], "share": share[s]["share"]}
                      for s in rep["skill_queries"] if s not in cur_canon]
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--profile", default="profile.local.yml")
    ap.add_argument("--jobs", default=os.path.join("data", "jobs"))
    ap.add_argument("--cv", default="cv.local.md")
    ap.add_argument("--candidates", default=os.path.join("data", "candidates-*.md"))
    ap.add_argument("--vocab", action="append")
    ap.add_argument("--days", type=int, default=30)
    ap.add_argument("--stale-days", type=int, default=7)
    ap.add_argument("--min-share", type=float, default=0.15)
    ap.add_argument("--date")
    ap.add_argument("--stale-only", action="store_true")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    today = date.fromisoformat(a.date) if a.date else date.today()
    try:
        with open(a.profile, encoding="utf-8") as fh:
            prof = fh.read()
    except FileNotFoundError:
        print(f"error: {a.profile} not found", file=sys.stderr)
        return 1
    vocab = skill_gap.load_vocab(a.vocab or [skill_gap.DEFAULT_VOCAB, os.path.join("data", "skills-vocab.local.txt")])
    cv = skill_gap.read(a.cv) if os.path.isfile(a.cv) else ""
    jobs = {} if a.stale_only else recent_jobs(a.jobs, today, a.days)
    r = suggest(prof, jobs, cv, skill_runs(glob.glob(a.candidates)), vocab, today, a.min_share, a.stale_days,
                a.stale_only)
    if a.json:
        print(json.dumps(r, ensure_ascii=False, indent=1))
        return 0
    if not a.stale_only:
        print(f"queries.skills: {len(r['current'])} now; {r['jobs']} job texts from the last {a.days} days "
              "(suggestions only; edit the profile after the user's yes)")
        if r["jobs"] < 10:
            print("WARN  fewer than 10 recent job texts: the ADD list is weak")
    for x in r["add"]:
        print(f"ADD   {x['skill']}  ({x['jobs']}/{r['jobs']} jobs, in CV)")
    for x in r["drop"]:
        print(f"DROP  {x['query']}  (nothing new for {x['days']} days)")
    for q in r["check"]:
        print(f"CHECK {q}  (not stated in the CV: remove, or add CV evidence)")
    if not (r["add"] or r["drop"] or r["check"]):
        print("no changes suggested")
    return 0


if __name__ == "__main__":
    sys.exit(main())
