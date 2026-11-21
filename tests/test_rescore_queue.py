import os
import subprocess
import sys
import tempfile
import unittest
from datetime import date

HERE = os.path.dirname(__file__)
SCRIPT = os.path.join(HERE, "..", "scripts", "rescore_queue.py")
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
import candidates_check as cc  # noqa: E402
import card_filter as cf  # noqa: E402
import rescore_queue as rq  # noqa: E402

OLD = 'targets:\n  roles: ["Business Analyst"]\nlimits:\n  max_prepared_per_round: 5\n'
NEW = 'targets:\n  roles: ["Business Analyst", "Product Owner"]\nlimits:\n  max_prepared_per_round: 5\n'
HEAD = ("| Job ID | Company | Role | Score | Channel | Easy Apply | Location | Applicants | Age (days) | URL | Evidence |\n"
        "|---|---|---|---|---|---|---|---|---|---|---|\n")


def cand_file(path, fp, rows):
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("# Candidates\n" + (f"Profile: {fp}\n" if fp else "") + HEAD + "\n".join(rows) + "\n")


class Fingerprint(unittest.TestCase):
    def test_changes_only_with_scoring_fields(self):
        self.assertNotEqual(cf.fingerprint(OLD), cf.fingerprint(NEW))
        self.assertEqual(cf.fingerprint(OLD), cf.fingerprint(OLD.replace("5", "9")))  # limits do not matter
        self.assertEqual(cf.fingerprint('targets:\n  roles: ["business analyst"]\n'),
                         cf.fingerprint('targets:\n  roles:\n    - "Business Analyst"   # note\n'))


class Queue(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        d = self.tmp.name
        self.jobs = os.path.join(d, "jobs")
        os.makedirs(self.jobs)
        for j in ("1", "2", "3", "5"):
            open(os.path.join(self.jobs, j + ".txt"), "w").close()
        self.tracker = os.path.join(d, "tracker.md")
        with open(self.tracker, "w", encoding="utf-8") as fh:
            fh.write("| Date | Company | Role | Posting | Status |\n|---|---|---|---|---|\n"
                     "| 2030-01-09 | Done Co | BA | https://www.linkedin.com/jobs/view/3/ | ✅ |\n")
        old, new = cf.fingerprint(OLD), cf.fingerprint(NEW)
        row = "| {id} | {c} | Product Owner | {s} | listing | yes | Remote | 5 | {age} | u | - |"
        cand_file(os.path.join(d, "candidates-2030-01-08.md"), old, [
            row.format(id=1, c="A Co", s=2.0, age=1),     # role became a target: re-score
            row.format(id=2, c="B Co", s=2.5, age=1),     # re-scored later with the new profile
            row.format(id=3, c="Done Co", s=2.0, age=1),  # already in tracker
            row.format(id=4, c="D Co", s=2.0, age=1),     # no cached text
            row.format(id=5, c="E Co", s=2.2, age=20),    # posted too long ago
        ])
        cand_file(os.path.join(d, "candidates-2030-01-09.md"), new, [row.format(id=2, c="B Co", s=4.0, age=2)])
        self.paths = [os.path.join(d, n) for n in ("candidates-2030-01-09.md", "candidates-2030-01-08.md")]
        self.new = new

    def tearDown(self):
        self.tmp.cleanup()

    def test_queue_and_skip_reasons(self):
        latest = rq.latest_scores(self.paths)
        self.assertEqual(latest["2"]["score"], 4.0)  # later file wins whatever the glob order
        q, skipped = rq.queue(latest, self.new, self.jobs, self.tracker, date(2030, 1, 10), 14)
        self.assertEqual([r["job_id"] for r in q], ["1"])
        self.assertEqual(skipped, {"same_profile": 1, "no_text": 1, "in_tracker": 1, "too_old": 1})

    def test_candidates_check_warns_on_profile_mismatch(self):
        text = open(self.paths[1], encoding="utf-8").read()
        r = cc.check(text, NEW, self.tracker, self.jobs, "2030-01-10")
        self.assertTrue(any("different or unknown profile" in w for w in r["warnings"]))
        r = cc.check(text.replace(cf.fingerprint(OLD), self.new), NEW, self.tracker, self.jobs, "2030-01-10")
        self.assertFalse(any("profile" in w for w in r["warnings"]))

    def test_cli(self):
        prof = os.path.join(self.tmp.name, "profile.yml")
        with open(prof, "w", encoding="utf-8") as fh:
            fh.write(NEW)
        fp = subprocess.run([sys.executable, SCRIPT, "--fingerprint", "--profile", prof],
                            capture_output=True, text=True).stdout.strip()
        self.assertEqual(fp, self.new)
        out = subprocess.run([sys.executable, SCRIPT, "--profile", prof, "--jobs", self.jobs, "--tracker", self.tracker,
                              "--candidates", os.path.join(self.tmp.name, "candidates-*.md"), "--date", "2030-01-10"],
                             capture_output=True, text=True)
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertIn("1 cached jobs to re-score", out.stdout)
        self.assertIn("RESCORE 1  was 2.0", out.stdout)


if __name__ == "__main__":
    unittest.main()
