#!/usr/bin/env python3
"""Recruiter mode: how rare each approved criterion is in the scored candidate pool. Advisory, stdlib only.

Usage: python3 scripts/criteria_rarity.py CRITERIA.json SCORES_DIR [--masked MASKED_DIR] [--rare 0.2] [--json]

Per must-have / nice-to-have: how many candidates match it (yes, partial), lack it (no) or do not say
(not_stated). A must-have met by fewer than --rare of the pool is flagged:
  RARE      most candidates clearly lack it: the human may consider making it a nice-to-have or trainable
  UNCLEAR   most candidates do not state it: ask them (the questions in the score files) before relaxing it
With --masked, skills from templates/skills-vocab.txt named in a criterion are also counted in the masked CVs.
Reads candidate IDs and match values only; never names. It never edits the criteria: the human decides.
"""
import argparse
import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import skill_gap  # noqa: E402

KINDS = (("must_have", "must"), ("nice_to_have", "nice"))


def rarity(criteria, scores, masked=None, vocab=None, rare=0.2):
    """criteria: dict; scores: list of score dicts; masked: {candidate_id: text} or None."""
    n = len(scores)
    rows = []
    for key, kind in KINDS:
        for c in criteria.get(key, []):
            cnt = {"yes": 0, "partial": 0, "no": 0, "not_stated": 0}
            for s in scores:
                m = next((r.get("match") for r in s.get("criteria", []) if r.get("id") == c["id"]), "not_stated")
                cnt[m if m in cnt else "not_stated"] += 1
            met = cnt["yes"] + cnt["partial"]
            row = {"id": c["id"], "kind": kind, "text": c.get("text", ""), "met": met,
                   "share": round(met / n, 2) if n else 0, **cnt, "flag": ""}
            if kind == "must" and n and met / n < rare:
                row["flag"] = "UNCLEAR" if cnt["not_stated"] > cnt["no"] else "RARE"
            if masked is not None and vocab:
                row["skills"] = {s: sum(1 for t in masked.values() if s in skill_gap.skills_in(t, vocab))
                                 for s in sorted(skill_gap.skills_in(c.get("text", ""), vocab))}
            rows.append(row)
    return {"candidates": n, "criteria": rows}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("criteria")
    ap.add_argument("scores")
    ap.add_argument("--masked")
    ap.add_argument("--vocab", action="append")
    ap.add_argument("--rare", type=float, default=0.2)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    try:
        with open(a.criteria, encoding="utf-8") as f:
            criteria = json.load(f)
        scores = []
        for p in sorted(glob.glob(os.path.join(a.scores, "*.json"))):
            with open(p, encoding="utf-8") as f:
                scores.append(json.load(f))
    except (OSError, ValueError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    masked = vocab = None
    if a.masked:
        masked = {os.path.splitext(os.path.basename(p))[0]: skill_gap.read(p)
                  for p in sorted(glob.glob(os.path.join(a.masked, "*.txt")))}
        vocab = skill_gap.load_vocab(a.vocab or [skill_gap.DEFAULT_VOCAB])
    r = rarity(criteria, scores, masked, vocab, a.rare)
    if a.json:
        print(json.dumps(r, ensure_ascii=False, indent=1))
        return 0
    n = r["candidates"]
    print(f"Criteria coverage in {n} scored candidates (advisory; the human edits criteria, nobody is rejected)")
    if n < 5:
        print("WARN  fewer than 5 candidates: too few to judge rarity")
    for c in r["criteria"]:
        skills = ", ".join(f"{s} {k}/{len(masked)}" for s, k in c.get("skills", {}).items())
        print(f"{c['flag'] or '-':8} {c['id']:4} {c['kind']:4} met {c['met']}/{n} (yes {c['yes']}, partial "
              f"{c['partial']}, no {c['no']}, not stated {c['not_stated']})  {c['text']}"
              + (f"  [CVs naming: {skills}]" if skills else ""))
    if any(c["flag"] == "RARE" for c in r["criteria"]):
        print("RARE: most candidates clearly lack it; the human may consider making it a nice-to-have or trainable.")
    if any(c["flag"] == "UNCLEAR" for c in r["criteria"]):
        print("UNCLEAR: most candidates do not state it; ask before relaxing (see each score file's questions).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
