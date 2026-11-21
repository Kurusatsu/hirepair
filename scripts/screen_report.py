#!/usr/bin/env python3
"""Build a ranked, advisory Markdown shortlist from per-candidate JSON score files.

Usage: python3 scripts/screen_report.py CRITERIA.json SCORES_DIR [--out report.md]

Scoring: yes=1, partial=0.5, no/not_stated=0. Must-have points and nice-to-have
points are scaled to the weights in the criteria file (default 70/30).
Reports candidate IDs only. Stdlib only. Never rejects anyone: exclusion hits are
flagged for human review. Exit code 1 if a score file is invalid.
"""
import argparse
import glob
import json
import os
import sys

VALUE = {"yes": 1.0, "partial": 0.5, "no": 0.0, "not_stated": 0.0}


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def score(crit, cand, problems):
    by_id = {c["id"]: c for c in cand.get("criteria", [])}
    cid = cand.get("candidate_id", "?")

    def part(items):
        if not items:
            return 0.0
        total = 0.0
        for it in items:
            r = by_id.get(it["id"])
            if r is None:
                problems.append(f"{cid}: criterion {it['id']} missing")
                continue
            m = r.get("match")
            if m not in VALUE:
                problems.append(f"{cid}: {it['id']} has invalid match '{m}'")
                continue
            if m in ("yes", "partial") and not r.get("evidence", "").strip():
                problems.append(f"{cid}: {it['id']} is '{m}' without an evidence quote")
                continue
            total += VALUE[m]
        return total / len(items)

    w = crit.get("weights", {"must_have": 70, "nice_to_have": 30})
    must = part(crit["must_have"]) * w["must_have"]
    nice = part(crit.get("nice_to_have", [])) * w["nice_to_have"]
    hits = [x for x in crit.get("exclusions", []) if by_id.get(x["id"], {}).get("match") in ("yes", "partial")]
    return round(must + nice, 1), round(must, 1), round(nice, 1), hits, by_id


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("criteria")
    ap.add_argument("scores_dir")
    ap.add_argument("--out")
    a = ap.parse_args()
    crit = load(a.criteria)
    problems, rows = [], []
    for p in sorted(glob.glob(os.path.join(a.scores_dir, "*.json"))):
        cand = load(p)
        total, must, nice, hits, by_id = score(crit, cand, problems)
        rows.append((total, must, nice, hits, by_id, cand))
    if problems:
        print("INVALID INPUT:\n" + "\n".join(problems), file=sys.stderr)
        sys.exit(1)
    rows.sort(key=lambda r: -r[0])
    w = crit.get("weights", {"must_have": 70, "nice_to_have": 30})
    out = [f"# Candidate shortlist: {crit.get('role', '')}", "",
           "Advisory only. A human decides. Scores come from approved criteria and CV quotes; "
           "`not_stated` means the CV does not say, not that the candidate lacks it. Review the lower group too.", "",
           "| Rank | ID | Score | Must-have | Nice-to-have | Flags |", "|---|---|---|---|---|---|"]
    for i, (t, m, n, h, _, c) in enumerate(rows, 1):
        flags = "exclusion hit: review" if h else "-"
        out.append(f"| {i} | {c['candidate_id']} | {t}/100 | {m}/{w['must_have']} | {n}/{w['nice_to_have']} | {flags} |")
    texts = {x["id"]: x["text"] for k in ("must_have", "nice_to_have", "exclusions") for x in crit.get(k, [])}
    for i, (t, m, n, h, by_id, c) in enumerate(rows, 1):
        out += ["", f"## {i}. {c['candidate_id']} ({t}/100)", ""]
        for cid, text in texts.items():
            r = by_id.get(cid)
            if not r:
                continue
            ev = f' "{r["evidence"]}"' if r.get("evidence") else ""
            out.append(f"- {cid} {text}: **{r['match']}**{ev}")
        if c.get("gaps"):
            out.append("- Gaps: " + "; ".join(c["gaps"]))
        if c.get("questions"):
            out.append("- Questions to ask: " + " / ".join(c["questions"]))
        if c.get("warnings"):
            out.append("- Warnings: " + "; ".join(c["warnings"]))
    out += ["", "Candidate files and reports are personal data: delete them when the recruitment purpose ends."]
    text = "\n".join(out) + "\n"
    if a.out:
        os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
        open(a.out, "w", encoding="utf-8").write(text)
        print(f"wrote {a.out} ({len(rows)} candidates)")
    else:
        print(text)


if __name__ == "__main__":
    main()
