import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(__file__)
SCRIPT = os.path.join(HERE, "..", "scripts", "card_filter.py")
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
import card_filter as f  # noqa: E402

TRACKER = ("| Date | Company | Role | Posting | Status |\n|---|---|---|---|---|\n"
           "| 2030-01-01 | Example Bank | Business Analyst | https://www.linkedin.com/jobs/view/111/ | ✅ |\n"
           "| 2030-01-02 | Örnek A.Ş. | İş Analisti | - | ⏳ |\n")


class CardFilter(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.tracker = os.path.join(self.tmp.name, "tracker.md")
        self.seen = os.path.join(self.tmp.name, "seen.txt")
        open(self.tracker, "w", encoding="utf-8").write(TRACKER)
        open(self.seen, "w", encoding="utf-8").write("222\n")

    def tearDown(self):
        self.tmp.cleanup()

    def run_filter(self, cards_text):
        cards = f.rows_from(f.stitch([cards_text]))
        keys, ids = f.tracker_keys(self.tracker)
        return f.filter_cards(cards, f.read_seen(self.seen), keys, ids)

    def test_drop_reasons(self):
        text = ("N=7;111~Business Analyst~Example Bank~1 day ago~|"
                "222~Product Owner~Seen Co~2 days ago~|"
                "333~Analyst~Applied Co~1 hour ago~Applied|"
                "~İŞ ANALİSTİ~Örnek A.Ş.~3 gün önce~|"
                "444~Release Manager~New Co~5 hours ago~Kaydedildi|"
                "444~Release Manager~New Co~5 hours ago~Kaydedildi|"
                "~Data Analyst~Other Co~1 day ago~")
        keep, counts = self.run_filter(text)
        self.assertEqual([c["title"] for c in keep], ["Release Manager", "Data Analyst"])
        self.assertTrue(keep[0]["saved"])
        self.assertTrue(keep[1]["needs_click"])
        self.assertEqual(counts, {"applied": 1, "seen_id": 2, "in_tracker": 1, "duplicate": 1})

    def test_row_cut_across_parts_is_stitched(self):
        parts = ["N=2;555~Business Anal", "yst~Fresh Co~1 day ago~|666~PO~X~1 day ago~MORE@40"]
        cards = f.rows_from(f.stitch(parts))
        self.assertEqual([(c["id"], c["title"]) for c in cards], [("555", "Business Analyst"), ("666", "PO")])

    def test_long_titles_match_truncated_cards(self):
        long_role = "Senior Business Analyst for Payments and Card Issuing Platforms (Hybrid)"
        open(self.tracker, "a", encoding="utf-8").write(f"| 2030-01-03 | Pay Co | {long_role} | - | ⏳ |\n")
        keep, counts = self.run_filter(f"~{long_role[:60]}~Pay Co~1 day ago~")
        self.assertEqual((keep, counts["in_tracker"]), ([], 1))

    def test_missing_files_keep_everything(self):
        keep, _ = f.filter_cards(f.rows_from("1~A~B~~"), set(), *f.tracker_keys("/nonexistent"))
        self.assertEqual(len(keep), 1)

    def test_cli_summary(self):
        p = os.path.join(self.tmp.name, "c.txt")
        open(p, "w", encoding="utf-8").write("N=2;111~Business Analyst~Example Bank~~|777~QA~Z~~")
        out = subprocess.run([sys.executable, SCRIPT, p, "--seen", self.seen, "--tracker", self.tracker],
                             capture_output=True, text=True)
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertIn("2 cards: open 1; dropped seen_id 1", out.stdout)


if __name__ == "__main__":
    unittest.main()
