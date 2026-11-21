import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(__file__)
SCRIPT = os.path.join(HERE, "..", "scripts", "candidates_check.py")
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
import candidates_check as c  # noqa: E402

HEAD = ("| Job ID | Company | Role | Score | Channel | Easy Apply | Location | Applicants | Age (days) | URL | Evidence |\n"
        "|---|---|---|---|---|---|---|---|---|---|---|\n")
GOOD = [
    '| 101 | A Co | Business Analyst | 4.2 | listing | yes | Remote | 12 | 1 | https://x/101 | "UAT", "SQL" |',
    '| 102 | B Co | Business Analyst | 4.2 | listing | no | Istanbul | 80 | 1 | https://x/102 | "Jira" |',
    '| 103 | C Co | Product Owner | 3.4 | post | no | Remote | 5 | 3 | https://x/103 | backlog work |',
    '| 104 | D Co | Analyst | 2.5 | listing | ? | ? | ? | ? | https://x/104 | - |',
]
COVERAGE = "\n## Coverage\n| Query | Kind | Result |\n|---|---|---|\n| business analyst | jobs | working |\n| po | jobs | empty |\n"
PROFILE = "limits:\n  max_prepared_per_round: 2\n  daily_prepared_cap: 3\n"
TRACKER = ("| Date | Company | Role | Posting | Status |\n|---|---|---|---|---|\n"
           "| 2030-01-05 | Z Co | Analyst | - | ⏳ Ready |\n"
           "| 2030-01-05 | Y Co | Analyst | - | ⛔ Rejected by scan |\n")


def doc(rows, coverage=COVERAGE, done=True):
    return "# Candidates 2030-01-05\n" + HEAD + "\n".join(rows) + "\n" + coverage + ("SUBAGENT_DONE 2030-01-05\n" if done else "")


class CandidatesCheck(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.tracker = os.path.join(self.tmp.name, "tracker.md")
        with open(self.tracker, "w", encoding="utf-8") as fh:
            fh.write(TRACKER)
        self.jobs = os.path.join(self.tmp.name, "jobs")
        os.makedirs(self.jobs)
        for j in ("101", "102", "103"):
            open(os.path.join(self.jobs, j + ".txt"), "w").close()

    def tearDown(self):
        self.tmp.cleanup()

    def run_check(self, text, profile=PROFILE):
        return c.check(text, profile, self.tracker, self.jobs, "2030-01-05")

    def test_queue_respects_cap_and_ranking(self):
        r = self.run_check(doc(GOOD))
        self.assertEqual(r["problems"], [])
        # cap 3, one non-rejected row already today -> room 2 (also the per-round limit)
        self.assertEqual(r["room"], 2)
        self.assertEqual([i["job_id"] for i in r["queue"]], ["101", "102"])  # same score: fewer applicants first
        self.assertEqual([i["job_id"] for i in r["next"]], ["103"])

    def test_unknown_fields_and_unquoted_high_score_are_problems(self):
        rows = GOOD + ['| 105 | E Co | BA | 3.8 | listing | ? | Remote | 3 | 1 | https://x/105 | requirements |']
        probs = self.run_check(doc(rows))["problems"]
        self.assertTrue(any("'easy apply' is required" in p for p in probs))
        self.assertTrue(any("needs a quoted job requirement" in p for p in probs))

    def test_failed_query_makes_scan_incomplete(self):
        cov = COVERAGE + "| release manager | jobs | failed |\n"
        r = self.run_check(doc(GOOD, cov))
        self.assertTrue(any("queries failed" in p and "release manager" in p for p in r["problems"]))

    def test_missing_coverage_and_cache_warning(self):
        os.remove(os.path.join(self.jobs, "101.txt"))
        r = self.run_check(doc(GOOD, coverage=""))
        self.assertTrue(any("no 'Coverage' table" in p for p in r["problems"]))
        self.assertTrue(any("101.txt" in w for w in r["warnings"]))

    def test_rows_already_in_tracker_are_not_queued(self):
        with open(self.tracker, "a", encoding="utf-8") as fh:
            fh.write("| 2030-01-04 | A Co | Business Analyst | https://www.linkedin.com/jobs/view/101/ | ✅ |\n")
        r = self.run_check(doc(GOOD))
        self.assertNotIn("101", [i["job_id"] for i in r["queue"] + r["next"]])

    def test_done_only_exit_codes(self):
        p = os.path.join(self.tmp.name, "cand.md")
        run = lambda: subprocess.run([sys.executable, SCRIPT, p, "--done-only"]).returncode  # noqa: E731
        self.assertEqual(run(), 2)  # file missing
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(doc(GOOD, done=False))
        self.assertEqual(run(), 2)
        with open(p, "a", encoding="utf-8") as fh:
            fh.write("SUBAGENT_DONE 2030-01-05T17:40\n")
        self.assertEqual(run(), 0)


if __name__ == "__main__":
    unittest.main()
