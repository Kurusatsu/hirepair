import os
import subprocess
import sys
import tempfile
import unittest

SCRIPT = os.path.join(os.path.dirname(__file__), "..", "scripts", "ats_check.py")

EN = """# Alex Example
alex@example.com

## Professional Summary
Analyst.

## Work Experience
Analyst, Acme, 01/2015 - 12/2020
- Cut reporting time by 40%.

## Education
BSc, Example University, 09/2010 - 06/2014

## Skills
SQL, Excel

## Languages
English, Turkish
"""

TR = """# Alex Example
alex@example.com

## Özet
Analist.

## İş Deneyimi
Analist, Acme, 01/2015 - 12/2020
- Raporlama süresini %40 azalttı. 40

## Eğitim
Lisans, Örnek Üniversitesi, 09/2010 - 06/2014

## Beceriler
SQL, Excel

## Diller
İngilizce, Türkçe
"""


def run(*files_and_args):
    with tempfile.TemporaryDirectory() as d:
        args = []
        for item in files_and_args:
            if item.startswith("--"):
                args.append(item)
            else:
                path = os.path.join(d, f"f{len(args)}.md")
                with open(path, "w", encoding="utf-8") as f:
                    f.write(item)
                args.append(path)
        r = subprocess.run([sys.executable, SCRIPT, *args], capture_output=True, text=True)
        return r.returncode, r.stdout


class AtsCheck(unittest.TestCase):
    def test_clean_cv_passes(self):
        code, out = run(EN)
        self.assertEqual(code, 0, out)
        self.assertNotIn("section order", out)

    def test_section_order_warns(self):
        bad = EN.replace("## Skills\nSQL, Excel\n\n", "").replace("## Professional Summary", "## Skills\nSQL, Excel\n\n## Professional Summary")
        code, out = run(bad)
        self.assertIn("section order", out)

    def test_entry_level_long_cv_warns(self):
        short_career = EN.replace("01/2015 - 12/2020", "01/2020 - 12/2021").replace("09/2010 - 06/2014", "09/2018 - 06/2020")
        long_cv = short_career + "\n" + ("word\n" * 600)
        code, out = run(long_cv)
        self.assertIn("aim for 1 page", out)

    def test_month_year_to_present_is_not_year_only(self):
        for end in ("Günümüz", "Present"):
            code, out = run(TR.replace("09/2010 - 06/2014", f"09/2026 – {end}"), "--lang=tr")
            self.assertNotIn("year-only", out)
        code, out = run(TR.replace("09/2010 - 06/2014", "2010 - Günümüz"), "--lang=tr")
        self.assertIn("year-only ranges: 1", out)

    def test_senior_thin_cv_warns(self):
        code, out = run(EN)
        self.assertIn("too thin", out)

    def test_turkish_dotted_capital_heading_is_recognised(self):
        code, out = run(TR.replace(" 40", ""), "--lang=tr")
        self.assertNotIn("missing section", out)

    def test_pair_consistent_has_no_errors(self):
        code, out = run(EN, "--pair", TR.replace(" 40", ""))
        self.assertEqual(code, 0, out)

    def test_pair_date_mismatch_is_error(self):
        code, out = run(EN, "--pair", TR.replace("01/2015", "02/2015"))
        self.assertEqual(code, 1, out)
        self.assertIn("date ranges differ", out)

    def test_pair_number_mismatch_warns(self):
        code, out = run(EN, "--pair", TR)
        self.assertIn("numbers appear in only one CV", out)

    def test_pair_same_language_warns(self):
        code, out = run(EN, "--pair", EN)
        self.assertIn("a TR/EN pair needs one of each", out)


if __name__ == "__main__":
    unittest.main()
