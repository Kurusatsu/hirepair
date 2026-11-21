#!/usr/bin/env python3
"""ATS-friendliness checker for a Markdown/plain-text CV. Stdlib only.

Usage: python3 scripts/ats_check.py CV.md [--jd JOB.txt] [--lang en|tr|auto] [--pair OTHER_LANG_CV.md]

Reports problems; never edits the CV and never suggests adding skills you lack.
Exit code 1 if any ERROR is found, else 0.
"""
import argparse
import datetime
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
    return re.sub(r"\s+", " ", s.strip().replace("İ", "i").replace("I", "ı").lower())


def headings(lines):
    out = []
    for i, l in enumerate(lines, 1):
        m = re.match(r"^\s{0,3}#{1,6}\s+(.*?)\s*#*\s*$", l)
        if m:
            out.append((i, norm(m.group(1))))
    return out


CORE_ORDER = ["summary", "experience", "education", "skills", "languages"]


def section_key(name):
    for key, v in SECTIONS.items():
        if name in v["en"] + v["tr"]:
            return key
    return None


def date_ranges(text):
    """Return [(start 'MM/YYYY', end 'MM/YYYY' or 'present')] for MM/YYYY ranges."""
    out = []
    for m in MONTH_RANGE.finditer(text):
        end = m.group(3).lower()
        end = end if re.match(r"\d", end) else "present"
        out.append((f"{m.group(1)}/{m.group(2)}", end))
    return out


def career_years(ranges):
    """Span from earliest start to latest end, in years (not the sum of jobs)."""
    if not ranges:
        return 0.0
    today = datetime.date.today()

    def ym(s):
        mm, yy = s.split("/")
        return int(yy) * 12 + int(mm)

    start = min(ym(a) for a, _ in ranges)
    end = max(today.year * 12 + today.month if b == "present" else ym(b) for _, b in ranges)
    return max(0, end - start) / 12


def detect_lang(names, forced="auto"):
    if forced != "auto":
        return forced
    tr = sum(any(n in names for n in v["tr"]) for v in SECTIONS.values())
    en = sum(any(n in names for n in v["en"]) for v in SECTIONS.values())
    return "tr" if tr > en else "en"


def pair_check(text, other, lang, other_lang):
    """Compare a CV with its other-language twin. Returns (errors, warnings)."""
    errors, warns = [], []
    if lang == other_lang:
        warns.append(f"both CVs look like {lang.upper()}; a TR/EN pair needs one of each")
    d1, d2 = date_ranges(text), date_ranges(other)
    if sorted(d1) != sorted(d2):
        only1, only2 = sorted(set(d1) - set(d2)), sorted(set(d2) - set(d1))
        errors.append(f"pair: date ranges differ (only in this CV: {only1 or '-'}; only in the other: {only2 or '-'})")
    if set(EMAIL.findall(text)) != set(EMAIL.findall(other)):
        errors.append("pair: e-mail addresses differ")
    k1 = [section_key(h) for _, h in headings(text.splitlines()) if section_key(h)]
    k2 = [section_key(h) for _, h in headings(other.splitlines()) if section_key(h)]
    if k1 != k2:
        errors.append(f"pair: section sequence differs ({', '.join(k1) or '-'} vs {', '.join(k2) or '-'})")

    def numbers(t):
        t = MONTH_RANGE.sub(" ", t)
        t = re.sub(r"(?<=\d)[.,](?=\d{3}\b)", "", t)
        return Counter(re.findall(r"\d+(?:[.,]\d+)?%?", t))

    n1, n2 = numbers(text), numbers(other)
    diff = sorted(set((n1 - n2).elements()) | set((n2 - n1).elements()))
    if diff:
        warns.append(f"pair: numbers appear in only one CV: {', '.join(diff)}; check they were not changed in translation")
    return errors, warns


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cv")
    ap.add_argument("--jd")
    ap.add_argument("--lang", default="auto", choices=["en", "tr", "auto"])
    ap.add_argument("--pair", help="the same CV in the other language (TR/EN consistency check)")
    a = ap.parse_args()
    text = open(a.cv, encoding="utf-8").read()
    lines = text.splitlines()
    errors, warns = [], []

    hs = headings(lines)
    names = {h for _, h in hs}
    lang = detect_lang(names, a.lang)
    for key, v in SECTIONS.items():
        if not any(n in names for n in v[lang]):
            errors.append(f"missing section heading '{v[lang][0]}' ({lang.upper()} standard names: {', '.join(v[lang])})")
    if hs:
        known = {n for v in list(SECTIONS.values()) + list(OPTIONAL.values()) for n in v["en"] + v["tr"]}
        for i, h in hs:
            if h not in known and not re.match(r"^#{3,}", lines[i - 1].strip()) and lines[i - 1].lstrip().startswith("##"):
                warns.append(f"line {i}: non-standard section heading '{h}'")

    order = [k for k in (section_key(h) for _, h in hs) if k in CORE_ORDER]
    ranked = [CORE_ORDER.index(k) for k in order]
    if ranked != sorted(ranked):
        warns.append(f"section order is {' > '.join(order)}; recommended: {' > '.join(CORE_ORDER)}")

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
    years = career_years(date_ranges(text))
    if words > 900:
        warns.append(f"{words} words; likely over 2 pages (limit 2)")
    elif years < 5 and words > 550:
        warns.append(f"{words} words for about {years:.0f} years of experience; aim for 1 page (about 550 words or fewer)")
    elif years >= 5 and words < 250:
        warns.append(f"only {words} words for about {years:.0f} years of experience; the CV may be too thin")

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

    if a.pair:
        other = open(a.pair, encoding="utf-8").read()
        other_lang = detect_lang({h for _, h in headings(other.splitlines())})
        pe, pw = pair_check(text, other, lang, other_lang)
        errors += pe
        warns += pw
        for e in pe:
            print("ERROR", e)
        for w in pw:
            print("WARN ", w)

    print("\nResult:", "FAIL" if errors else "PASS", f"({len(errors)} errors, {len(warns)} warnings)")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
