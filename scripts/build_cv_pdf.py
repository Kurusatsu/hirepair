#!/usr/bin/env python3
"""Build an ATS-safe PDF from a tailored CV in Markdown. Stdlib only; uses the local Chrome to print.

Usage: python3 scripts/build_cv_pdf.py data/cv/First_Last_Role_Cv.md [--out FILE.pdf] [--chrome PATH] [--html-only]

The Markdown is the subset the tailored CVs use: "# Name", "## Section", "### Job title", "- bullet",
plain lines and **bold**. It becomes one single-column HTML page (Arial, 10.5 pt, A4, no tables, icons,
headers or footers), which headless Chrome prints to a selectable-text PDF next to the Markdown file.
Run scripts/ats_check.py on the Markdown first. The build fails if the PDF has more than 2 pages or no
text layer. Chrome is found via --chrome, $CHROME, the macOS app path or PATH.
"""
import argparse
import html
import os
import re
import shutil
import subprocess
import sys
import tempfile

MAX_PAGES = 2
MAC_CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
NAME_OK = re.compile(r"^[A-Za-z0-9]+(_[A-Za-z0-9]+)*_Cv\.pdf$")

CSS = """
@page { size: A4; margin: 14mm 16mm; }
body { font-family: Arial, Helvetica, sans-serif; font-size: 10.5pt; line-height: 1.35; color: #000; margin: 0; }
h1 { font-size: 17pt; margin: 0 0 2pt; }
h2 { font-size: 12pt; border-bottom: 0.75pt solid #000;
     margin: 10pt 0 4pt; padding-bottom: 1pt; }
h3 { font-size: 10.5pt; margin: 7pt 0 1pt; }
p { margin: 0 0 3pt; }
ul { margin: 2pt 0 4pt; padding-left: 14pt; }
li { margin: 0 0 2pt; }
h2, h3 { break-after: avoid; }
li, p { break-inside: avoid; }
"""


def inline(s):
    s = html.escape(s, quote=False)
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)


def md_to_html(text, lang=None):
    """Markdown subset -> a complete single-column HTML document."""
    if lang is None:
        lang = "tr" if re.search(r"[çğışöüÇĞİŞÖÜ]", text) else "en"
    out, in_list, title = [], False, ""
    for raw in text.splitlines():
        line = raw.strip()
        bullet = re.match(r"^[-*•]\s+(.*)$", line)
        if in_list and not bullet:
            out.append("</ul>")
            in_list = False
        if not line:
            continue
        head = re.match(r"^(#{1,3})\s+(.*)$", line)
        if head:
            level = len(head.group(1))
            title = title or (head.group(2) if level == 1 else "")
            out.append(f"<h{level}>{inline(head.group(2))}</h{level}>")
        elif bullet:
            if not in_list:
                out.append("<ul>")
                in_list = True
            out.append(f"<li>{inline(bullet.group(1))}</li>")
        else:
            out.append(f"<p>{inline(line)}</p>")
    if in_list:
        out.append("</ul>")
    return (f'<!doctype html>\n<html lang="{lang}"><head><meta charset="utf-8"><title>{html.escape(title)}</title>'
            f"<style>{CSS}</style></head><body>\n" + "\n".join(out) + "\n</body></html>\n")


def find_chrome(explicit=None):
    for c in (explicit, os.environ.get("CHROME"), MAC_CHROME):
        if c and os.path.isfile(c) and os.access(c, os.X_OK):
            return c
    for name in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "chrome"):
        p = shutil.which(name)
        if p:
            return p
    return None


def pdf_facts(data):
    """(page count, has a text layer) from the raw PDF bytes."""
    pages = len(re.findall(rb"/Type\s*/Page(?![s\w])", data))
    return pages, b"/Font" in data


def print_pdf(chrome, html_path, pdf_path):
    with tempfile.TemporaryDirectory() as profile:  # a throwaway profile: never touches the user's Chrome
        cmd = [chrome, "--headless=new", "--disable-gpu", "--no-first-run", "--no-default-browser-check",
               f"--user-data-dir={profile}", "--no-pdf-header-footer", f"--print-to-pdf={pdf_path}",
               "file://" + os.path.abspath(html_path)]
        return subprocess.run(cmd, capture_output=True, text=True, timeout=120)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("cv")
    ap.add_argument("--out")
    ap.add_argument("--chrome")
    ap.add_argument("--html-only", action="store_true", help="write the HTML next to the CV and stop")
    a = ap.parse_args(argv)
    try:
        with open(a.cv, encoding="utf-8") as fh:
            text = fh.read()
    except OSError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    base = os.path.splitext(a.cv)[0]
    out = a.out or base + ".pdf"
    page = md_to_html(text)
    if a.html_only:
        with open(base + ".html", "w", encoding="utf-8") as fh:
            fh.write(page)
        print(f"wrote {base}.html")
        return 0
    chrome = find_chrome(a.chrome)
    if not chrome:
        print("error: Chrome not found; pass --chrome PATH or set CHROME (or use --html-only and print it yourself)",
              file=sys.stderr)
        return 1
    with tempfile.TemporaryDirectory() as d:
        html_path = os.path.join(d, "cv.html")
        with open(html_path, "w", encoding="utf-8") as fh:
            fh.write(page)
        tmp_pdf = os.path.join(d, "cv.pdf")
        r = print_pdf(chrome, html_path, tmp_pdf)
        if not os.path.isfile(tmp_pdf):
            print(f"error: Chrome did not write a PDF: {r.stderr.strip()[-300:]}", file=sys.stderr)
            return 1
        with open(tmp_pdf, "rb") as fh:
            data = fh.read()
        pages, has_text = pdf_facts(data)
        if pages > MAX_PAGES or not has_text:
            print(f"error: {pages} pages (max {MAX_PAGES}), text layer: {has_text}; shorten the CV, nothing written",
                  file=sys.stderr)
            return 1
        os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
        shutil.move(tmp_pdf, out)
    print(f"wrote {out} ({pages} page{'s' if pages != 1 else ''})")
    if not NAME_OK.match(os.path.basename(out)):
        print("WARN  file name should be First_Last_Role_Cv.pdf (ASCII letters and underscores)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
