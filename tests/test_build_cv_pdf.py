import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(__file__)
SCRIPT = os.path.join(HERE, "..", "scripts", "build_cv_pdf.py")
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
import build_cv_pdf as b  # noqa: E402

CV = """# Alex Example

Business Analyst

Istanbul, alex@example.com

## Özet

Analist <script>x</script> & **SQL**.

## İş Deneyimi

### Analyst
Acme, Istanbul, 01/2020 – Günümüz

- Requirements analysis
- UAT

## Eğitim

- B.Sc., Example University, 09/2015 – 06/2019
"""


class Html(unittest.TestCase):
    def test_markdown_subset_becomes_single_column_html(self):
        page = b.md_to_html(CV)
        self.assertIn('<html lang="tr">', page)
        self.assertIn("<title>Alex Example</title>", page)
        self.assertIn("<h2>İş Deneyimi</h2>", page)
        self.assertIn("<h3>Analyst</h3>", page)
        self.assertIn("<ul>\n<li>Requirements analysis</li>\n<li>UAT</li>\n</ul>", page)
        self.assertIn("&lt;script&gt;x&lt;/script&gt; &amp; <b>SQL</b>", page)  # escaped, bold kept
        for banned in ("<table", "<img", "<svg", "column", "position:"):
            self.assertNotIn(banned, page)

    def test_pdf_facts(self):
        self.assertEqual(b.pdf_facts(b"/Type /Pages /Type /Page /Font /Type/Page"), (2, True))


@unittest.skipUnless(b.find_chrome(), "Chrome not installed")
class Build(unittest.TestCase):
    def run_script(self, text, *args):
        d = tempfile.mkdtemp()
        md = os.path.join(d, "Alex_Example_Business_Analyst_Cv.md")
        with open(md, "w", encoding="utf-8") as f:
            f.write(text)
        r = subprocess.run([sys.executable, SCRIPT, md, *args], capture_output=True, text=True)
        return r, os.path.join(d, "Alex_Example_Business_Analyst_Cv.pdf")

    def test_builds_one_page_text_pdf(self):
        r, pdf = self.run_script(CV)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("(1 page)", r.stdout)
        self.assertNotIn("WARN", r.stdout)
        with open(pdf, "rb") as f:
            self.assertEqual(b.pdf_facts(f.read()), (1, True))

    def test_refuses_more_than_two_pages(self):
        r, pdf = self.run_script(CV + "\n".join(f"- bullet {i}" for i in range(400)))
        self.assertEqual(r.returncode, 1)
        self.assertIn("max 2", r.stderr)
        self.assertFalse(os.path.exists(pdf))


if __name__ == "__main__":
    unittest.main()
