import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from tracker_view import render  # noqa: E402

T = """| Date | Company | Role | Fit | Posting | CV | Cover note | Status | Channel | Reply |
|---|---|---|---|---|---|---|---|---|---|
| 2030-01-06 | <b>Evil</b> | Analyst | 4 | https://example.com/j/1 | a.pdf | - | ⏳ Ready | LinkedIn form | - |
| 2030-01-07 | Demo | Owner | 3 | javascript:alert(1) | b.pdf | - | ✅ Submitted | LinkedIn form | - |
| 2030-01-08 | Sample | Lead | 3 | https://example.com/j/2 | c.pdf | - | ⏸️ Waiting | Workday | - |
"""


class View(unittest.TestCase):
    def test_html_is_escaped(self):
        h = render(T)
        self.assertNotIn("<b>Evil</b>", h)
        self.assertIn("&lt;b&gt;Evil&lt;/b&gt;", h)

    def test_only_http_links_become_anchors(self):
        h = render(T)
        self.assertIn('href="https://example.com/j/1"', h)
        self.assertNotIn('href="javascript', h)

    def test_waiting_list_includes_pending_and_paused_but_not_submitted(self):
        h = render(T)
        self.assertIn("Waiting for you (2)", h)

    def test_empty_input(self):
        self.assertIn("No table found", render("nothing"))


if __name__ == "__main__":
    unittest.main()
