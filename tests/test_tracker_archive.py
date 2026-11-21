import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(__file__)
SCRIPTS = os.path.join(HERE, "..", "scripts")
sys.path.insert(0, SCRIPTS)
import card_filter as cf  # noqa: E402

TRACKER = """# Tracker

| Date | Company | Role | Posting | Status | Channel | Reply |
|---|---|---|---|---|---|---|
| 2030-01-01 | Old Co | BA | https://www.linkedin.com/jobs/view/11/ | ✅ Submitted | LinkedIn form | Rejected |
| 2030-01-02 | Gone Co | PO | - | ⛔ Rejected by scan | - | - |
| 2030-01-03 | Wait Co | BA | - | 🔒 Sign-in needed | Company portal | - |
| 2030-05-01 | New Co | BA | - | ✅ Submitted | E-mail | - |

Notes stay here.
"""


class TrackerArchive(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.t = os.path.join(self.tmp.name, "tracker.md")
        with open(self.t, "w", encoding="utf-8") as fh:
            fh.write(TRACKER)
        self.arch = os.path.join(self.tmp.name, "tracker-archive.md")

    def tearDown(self):
        self.tmp.cleanup()

    def run_script(self, name, *args):
        return subprocess.run([sys.executable, os.path.join(SCRIPTS, name), *args], capture_output=True, text=True)

    def test_moves_only_old_closed_rows_and_dedupe_still_sees_them(self):
        before = cf.tracker_keys(self.t)
        out = self.run_script("tracker_archive.py", self.t, "--date", "2030-05-10", "--dry-run")
        self.assertIn("2 closed rows", out.stdout)
        self.assertFalse(os.path.exists(self.arch))
        out = self.run_script("tracker_archive.py", self.t, "--date", "2030-05-10")
        self.assertEqual(out.returncode, 0, out.stderr)
        kept, arch = open(self.t, encoding="utf-8").read(), open(self.arch, encoding="utf-8").read()
        self.assertIn("Wait Co", kept)
        self.assertIn("New Co", kept)
        self.assertIn("Notes stay here.", kept)
        self.assertNotIn("Old Co", kept)
        self.assertIn("| Date | Company |", arch)
        self.assertIn("Old Co", arch)
        self.assertIn("Gone Co", arch)
        self.assertEqual(cf.tracker_keys(self.t), before)  # archived jobs are never prepared again
        self.assertNotIn("11", cf.tracker_keys(self.t, archive=False)[1])
        stats = self.run_script("tracker_stats.py", self.t).stdout
        self.assertIn("rows: 4 (2 archived)", stats)
        # a second run moves nothing and does not duplicate the header
        self.run_script("tracker_archive.py", self.t, "--date", "2030-05-10")
        self.assertEqual(open(self.arch, encoding="utf-8").read().count("| Date |"), 1)


if __name__ == "__main__":
    unittest.main()
