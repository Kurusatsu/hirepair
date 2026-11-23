#!/usr/bin/env python3
"""Skill demand vs. your CV and LinkedIn skills, from saved job descriptions. Stdlib only.

Usage:
  python3 scripts/skill_gap.py --jobs data/jobs [--cv cv.local.md] [--linkedin data/linkedin-skills.local.txt]
                               [--vocab templates/skills-vocab.txt] [--min-share 0.15] [--json]

--jobs      folder of job descriptions (*.txt / *.md), one file per job (the daily scan saves them there)
--linkedin  your current LinkedIn skills, one per line (copy them from your profile; optional)

Report only. A skill is suggested for your LinkedIn profile ONLY if your CV already states it.
Skills the market asks for but your CV does not state are listed as gaps: never add them to a CV
or profile unless they are true and you can show evidence.
"""
import argparse
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_VOCAB = os.path.join(HERE, "..", "templates", "skills-vocab.txt")


def norm(s):
    return s.replace("İ", "i").lower()


def load_vocab(paths):
    """Return {canonical: [patterns]} keeping file order; later files may add aliases to a skill."""
    vocab = {}
    for path in paths:
        try:
            with open(path, encoding="utf-8") as f:
                lines = f.read().splitlines()
        except FileNotFoundError:
            continue
        for line in lines:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            names = [n.strip() for n in line.split("|") if n.strip()]
            canon = names[0]
            pats = vocab.setdefault(canon, [])
            for n in names:
                p = re.compile(r"(?<![\w])" + re.escape(norm(n)) + r"(?![\w])")
                if p.pattern not in {x.pattern for x in pats}:
                    pats.append(p)
    return vocab


def skills_in(text, vocab):
    t = norm(text)
    return {canon for canon, pats in vocab.items() if any(p.search(t) for p in pats)}


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


# Benefit text describes the employer, not the job: "health insurance" is not demand for Insurance and a
# "training budget" is not demand for Training. A benefits section runs until a requirements-type heading.
BENEFITS_HEAD = re.compile(r"^\W*(what we offer|what we provide|our benefits|benefits|perks|yan haklar|"
                           r"neler sunuyoruz|sunduğumuz (imkanlar|olanaklar|haklar))\b")
REQUIREMENTS_HEAD = re.compile(r"^\W*(requirements|qualifications|responsibilities|about you|role summary|"
                               r"what (are we|we are) looking for|what you will do|how to succeed|"
                               r"aranan nitelikler|beklediğimiz nitelikler|nitelikler|sorumluluklar|"
                               r"görev tanımı|iş tanımı)\b")
BENEFIT_LINE = re.compile(r"\b(health|medical|life|private) insurance|pension plan|meal card|sağlık sigortası|"
                          r"hayat (ve ferdi kaza )?sigortası|ferdi kaza|yemek kartı|bireysel emeklilik")


def job_text(raw):
    """Job file text without what is not a requirement: the company name in the cache's first line
    ("company | role | URL") and benefit lines or sections."""
    lines = raw.splitlines()
    if lines and lines[0].count("|") >= 2:
        lines[0] = lines[0].split("|")[1]
    out, in_benefits = [], False
    for line in lines:
        n = norm(line).strip()
        if BENEFITS_HEAD.match(n):
            in_benefits = True
        elif in_benefits and REQUIREMENTS_HEAD.match(n):
            in_benefits = False
        if not in_benefits and not BENEFIT_LINE.search(n):
            out.append(line)
    return "\n".join(out)


def analyse(jobs, cv_text, linkedin, vocab, min_share=0.15):
    """jobs: {name: text}. Returns a dict report. linkedin: list of skill names or None."""
    n = len(jobs)
    demand = {}
    for text in jobs.values():
        for s in skills_in(text, vocab):
            demand[s] = demand.get(s, 0) + 1
    in_cv = skills_in(cv_text, vocab) if cv_text else set()
    li_raw = [x.strip() for x in (linkedin or []) if x.strip()]
    li = skills_in("\n".join(li_raw), vocab) if li_raw else set()
    order = sorted(demand, key=lambda s: (-demand[s], s))
    rows = [{"skill": s, "jobs": demand[s], "share": round(demand[s] / n, 2) if n else 0,
             "in_cv": s in in_cv, "on_linkedin": s in li} for s in order]
    hot = [r for r in rows if r["share"] >= min_share]
    report = {
        "jobs": n,
        "demand": rows,
        "add_to_linkedin": [r["skill"] for r in hot if r["in_cv"] and not r["on_linkedin"]] if li_raw else [],
        "top_skills": [r["skill"] for r in rows if r["in_cv"]][:5],
        "gaps": [r["skill"] for r in hot if not r["in_cv"]],
        "linkedin_not_in_cv": sorted(li - in_cv) if li_raw else [],
        "linkedin_unmatched": [x for x in li_raw if not skills_in(x, vocab)],
        "skill_queries": [r["skill"] for r in hot if r["in_cv"]][:6],
        "linkedin_given": bool(li_raw),
    }
    return report


def render(r):
    out = [f"Skill report from {r['jobs']} job descriptions (report only; nothing is changed)."]
    if not r["jobs"]:
        out.append("No job descriptions found. The daily scan saves them to data/jobs/<job-id>.txt.")
        return "\n".join(out)
    out.append("\nDemand (jobs mentioning the skill):")
    for row in r["demand"][:30]:
        flags = ("CV" if row["in_cv"] else "--") + (" LI" if row["on_linkedin"] else "   ")
        out.append(f"  {row['jobs']:>3}  {row['share']:>4.0%}  {flags}  {row['skill']}")
    out.append("\nTop skills to pin (in your CV, most asked): " + (", ".join(r["top_skills"]) or "-"))
    if r["linkedin_given"]:
        out.append("Add to LinkedIn (in CV, asked, not on profile): " + (", ".join(r["add_to_linkedin"]) or "-"))
        out.append("On LinkedIn but not in CV (check they are true, or add evidence to the CV): "
                   + (", ".join(r["linkedin_not_in_cv"]) or "-"))
        if r["linkedin_unmatched"]:
            out.append("LinkedIn skills not in the vocabulary (not scored): " + ", ".join(r["linkedin_unmatched"]))
    else:
        out.append("Add --linkedin FILE (your current LinkedIn skills, one per line) for add/remove suggestions.")
    out.append("Gaps (asked, not in CV; do NOT add unless true and provable): " + (", ".join(r["gaps"]) or "-"))
    out.append("Skill search queries (for queries.skills in the profile): " + (", ".join(r["skill_queries"]) or "-"))
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", required=True)
    ap.add_argument("--cv", default="cv.local.md")
    ap.add_argument("--linkedin")
    ap.add_argument("--vocab", action="append")
    ap.add_argument("--min-share", type=float, default=0.15)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    vocab_paths = a.vocab or [DEFAULT_VOCAB, os.path.join("data", "skills-vocab.local.txt")]
    vocab = load_vocab(vocab_paths)
    if not vocab:
        print("error: empty skill vocabulary", file=sys.stderr)
        return 1
    files = sorted(glob.glob(os.path.join(a.jobs, "*.txt")) + glob.glob(os.path.join(a.jobs, "*.md")))
    jobs = {os.path.basename(p): job_text(read(p)) for p in files}
    cv = read(a.cv) if a.cv and os.path.isfile(a.cv) else ""
    if not cv:
        print(f"warning: CV not found at {a.cv}; every skill will show as a gap", file=sys.stderr)
    li = read(a.linkedin).splitlines() if a.linkedin else None
    r = analyse(jobs, cv, li, vocab, a.min_share)
    print(json.dumps(r, ensure_ascii=False, indent=1) if a.json else render(r))
    return 0


if __name__ == "__main__":
    sys.exit(main())
