#!/usr/bin/env python3
"""ATS-friendliness checker for a Markdown/plain-text CV. Stdlib only.

Usage: python3 scripts/ats_check.py CV.md [--jd JOB.txt] [--lang en|tr|auto]

Reports problems; never edits the CV and never suggests adding skills you lack.
Exit code 1 if any ERROR is found, else 0.
"""
import argparse
import re
import sys
import unicodedata
from collections import Counter

SECTIONS = {
    "summary": {"en": ["professional summary", "summary"], "tr": ["özet", "profesyonel özet"]},
    "experience": {"en": ["work experience", "experience"], "tr": ["iş deneyimi", "deneyim"]},
    "education": {"en": ["education"], "tr": ["eğitim"]},
    "skills": {"en": ["skills"], "tr": ["beceriler", "yetenekler"]},
    "languages": {"en": ["languages"], "tr": ["diller", "yabancı diller"]},
}
OPTIONAL = {
    "certifications": {"en": ["certifications"], "tr": ["sertifikalar"]},
    "projects": {"en": ["projects"], "tr": ["projeler"]},
}
MONTH_RANGE = re.compile(r"\b(0[1-9]|1[0-2])/(\d{4})\s*[-–—]\s*((?:0[1-9]|1[0-2])/\d{4}|present|günümüz|devam)", re.I)
YEAR_RANGE = re.compile(r"\b(19|20)\d{2}\s*[-–—]\s*((?:19|20)\d{2}|present|günümüz|devam)", re.I)
NAMED_MONTH = re.compile(r"\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec|ocak|şubat|mart|nisan|mayıs|haziran|temmuz|ağustos|eylül|ekim|kasım|aralık)[a-zçğıöşü]*\.?\s+\d{4}", re.I)
EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
STOP = set("""the and for with you your are our will from that this have has not but all can any who
 their they them its into out about more than also such per via etc using use work working team role
 years year experience ability strong good skills knowledge be as at by in is it of on or to we an a
 ve ile bir bu için olan veya gibi daha çok en da de ki mi ne ise olarak sahip tercihen deneyim yıl
 bilgi beceri iş aranan nitelikler""".split())


def norm(s):
    return re.sub(r"\s+", " ", s.strip().lower())


def headings(lines):
    out = []
    for i, l in enumerate(lines, 1):
        m = re.match(r"^\s{0,3}#{1,6}\s+(.*?)\s*#*\s*$", l)
        if m:
            out.append((i, norm(m.group(1))))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cv")
    ap.add_argument("--jd")
    ap.add_argument("--lang", default="auto", choices=["en", "tr", "auto"])
    a = ap.parse_args()
    text = open(a.cv, encoding="utf-8").read()
    lines = text.splitlines()
    errors, warns = [], []

    hs = headings(lines)
    names = {h for _, h in hs}
    lang = a.lang
    if lang == "auto":
        tr_hits = sum(any(n in names for n in v["tr"]) for v in SECTIONS.values())
        en_hits = sum(any(n in names for n in v["en"]) for v in SECTIONS.values())
        lang = "tr" if tr_hits > en_hits else "en"
    for key, v in SECTIONS.items():
        if not any(n in names for n in v[lang]):
            errors.append(f"missing section heading '{v[lang][0]}' ({lang.upper()} standard names: {', '.join(v[lang])})")
    if hs:
        known = {n for v in list(SECTIONS.values()) + list(OPTIONAL.values()) for n in v["en"] + v["tr"]}
        for i, h in hs:
            if h not in known and not re.match(r"^#{3,}", lines[i - 1].strip()) and lines[i - 1].lstrip().startswith("##"):
                warns.append(f"line {i}: non-standard section heading '{h}'")

    month, year, named = len(MONTH_RANGE.findall(text)), len(YEAR_RANGE.findall(text)), len(NAMED_MONTH.findall(text))
    if month == 0:
        errors.append("no dates in MM/YYYY – MM/YYYY form found")
    if year or named:
        errors.append(f"non-standard date formats present (year-only ranges: {year}, named months: {named}); use MM/YYYY – MM/YYYY")

    for i, l in enumerate(lines, 1):
        if "|" in l:
            errors.append(f"line {i}: pipe character (table or separator); tables are not ATS-safe")
        if re.match(r"^\s*[-:| ]{3,}\s*$", l) and "|" in l:
            errors.append(f"line {i}: table separator row")
        bad = sorted({c for c in l if ord(c) > 0x2000 and unicodedata.category(c) in ("So", "Sk", "Cs")
                      or ord(c) >= 0x1F000 or c in "★►●◆■□▪✓✔➤→•"})
        if bad:
            errors.append(f"line {i}: icon/emoji/special symbols {''.join(bad)}")
        if len(l) > 160:
            warns.append(f"line {i}: {len(l)} characters; split long lines")
        if "<" in l and ">" in l and re.search(r"</?\w+[^>]*>", l):
            warns.append(f"line {i}: HTML tag; use plain text")
        if re.search(r"!\[.*\]\(", l):
            errors.append(f"line {i}: image; critical info must be text")

    if not EMAIL.search(text):
        errors.append("no e-mail address found in the CV body (contact info must be in the body, not a header/footer)")
    words = len(re.findall(r"\w+", text))
    if words > 900:
        warns.append(f"{words} words; likely over 2 pages (limit 2)")

    print(f"ATS check: {a.cv}  (language: {lang}, words: {words})")
    for e in errors:
        print("ERROR", e)
    for w in warns:
        print("WARN ", w)

    if a.jd:
        jd = open(a.jd, encoding="utf-8").read().lower()
        cv = text.lower()
        toks = [t for t in re.findall(r"[a-zçğıöşü][a-zçğıöşü0-9+#.]{2,}", jd) if t.strip(".") not in STOP]
        toks = [t.strip(".") for t in toks]
        top = [t for t, _ in Counter(toks).most_common(40)]
        found = [t for t in top if t in cv]
        missing = [t for t in top if t not in cv]
        ratio = len(found) / len(top) if top else 0
        print(f"\nKeyword report (top {len(top)} job-text terms): {len(found)} in CV, {len(missing)} not in CV ({ratio:.0%})")
        print("In CV:      ", ", ".join(found) or "-")
        print("Not in CV:  ", ", ".join(missing) or "-")
        print("Note: report only. Use a missing term only if it is TRUE for you AND already supported by your CV facts.")

    print("\nResult:", "FAIL" if errors else "PASS", f"({len(errors)} errors, {len(warns)} warnings)")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
