#!/usr/bin/env python3
"""Build a ranked, advisory Markdown shortlist from per-candidate JSON score files.

Usage: python3 scripts/screen_report.py CRITERIA.json SCORES_DIR [--out report.md] [--masked MASKED_DIR]

With --masked, every yes/partial evidence quote must appear verbatim (whitespace-insensitive) in
MASKED_DIR/<candidate_id>.txt; candidates without such a file are skipped. This enforces "no quote, no yes".

Scoring: yes=1, partial=0.5, no/not_stated=0. Must-have points and nice-to-have
points are scaled to the weights in the criteria file (default 70/30).
Reports candidate IDs only. Optional per-candidate "source" (for example "linkedin-search (headline-level)")
and "deepened" (true after a user-chosen profile reading) fields; headline-level candidates cannot be strong_match.
 Stdlib only. Never rejects anyone: exclusion hits are
flagged for human review. Exit code 1 if a score file is invalid.
"""
import argparse
import glob
import json
import os
import sys

CATEGORIES = {"strong_match": "Strong match", "possible": "Possible",
              "needs_clarification": "Needs clarification", "not_matching": "Does not meet criteria (suggestion)"}
VALUE = {"yes": 1.0, "partial": 0.5, "no": 0.0, "not_stated": 0.0}


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def norm(t):
    return " ".join(t.split()).lower()


def check_quotes(cand, masked_dir, problems):
    cid = cand.get("candidate_id", "?")
    path = os.path.join(masked_dir, f"{cid}.txt")
    if not os.path.isfile(path):
        return
    with open(path, encoding="utf-8") as f:
        cv = norm(f.read())
    for r in cand.get("criteria", []):
        ev = r.get("evidence", "").strip()
        if r.get("match") in ("yes", "partial") and ev and norm(ev) not in cv:
            problems.append(f"{cid}: {r.get('id')} evidence is not a verbatim quote of the masked CV: \"{ev[:60]}\"")


def score(crit, cand, problems):
    by_id = {c["id"]: c for c in cand.get("criteria", [])}
    cid = cand.get("candidate_id", "?")
    if cand.get("category") not in CATEGORIES:
        problems.append(f"{cid}: category must be one of {', '.join(CATEGORIES)}")
    elif not cand.get("category_evidence", "").strip():
        problems.append(f"{cid}: category without category_evidence")
    if str(cand.get("source", "")).startswith("linkedin-search") and not cand.get("deepened") \
            and cand.get("category") in ("strong_match", "not_matching"):
        problems.append(f"{cid}: headline-level (not deepened) candidates may only be 'possible' or "
                        "'needs_clarification'; 'strong_match' requires a user-chosen profile deepening")

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
    ap.add_argument("--masked", help="folder of masked CVs (<ID>.txt) to verify evidence quotes against")
    a = ap.parse_args()
    crit = load(a.criteria)
    problems, rows = [], []
    for p in sorted(glob.glob(os.path.join(a.scores_dir, "*.json"))):
        cand = load(p)
        if a.masked:
            check_quotes(cand, a.masked, problems)
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
           "| Rank | ID | Source | Category | Score | Must-have | Nice-to-have | Flags |", "|---|---|---|---|---|---|---|---|"]
    for i, (t, m, n, h, _, c) in enumerate(rows, 1):
        flags = "exclusion hit: review" if h else "-"
        out.append(f"| {i} | {c['candidate_id']} | {c.get('source', 'local')} | {CATEGORIES.get(c.get('category'), '?')} | {t}/100 | {m}/{w['must_have']} | {n}/{w['nice_to_have']} | {flags} |")
    out += ["", "## Category summary", ""]
    for key, label in CATEGORIES.items():
        ids = [r[5]["candidate_id"] for r in rows if r[5].get("category") == key]
        out.append(f"- {label}: {len(ids)}" + (f" ({', '.join(ids)})" if ids else ""))
    out.append("- `not_matching` is a suggestion only; nobody is rejected by this tool.")
    texts = {x["id"]: x["text"] for k in ("must_have", "nice_to_have", "exclusions") for x in crit.get(k, [])}
    for i, (t, m, n, h, by_id, c) in enumerate(rows, 1):
        out += ["", f"## {i}. {c['candidate_id']} ({t}/100) - {CATEGORIES.get(c.get('category'), '?')}", "", f"Category evidence: {c.get('category_evidence', '')}"]
        for cid, text in texts.items():
            r = by_id.get(cid)
            if not r:
                continue
            ev = f' "{r["evidence"]}"' if r.get("evidence") else ""
            out.append(f"- {cid} {text}: **{r['match']}**{ev}")
        if str(c.get("source", "")).startswith("linkedin-search") and not c.get("deepened"):
            out.append("- Evidence level: HEADLINE ONLY (years and skills are not visible); weak evidence, profile deepening needed before any firm view.")
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
