import os
import subprocess
import sys
import tempfile
import time
import unittest
from datetime import date

HERE = os.path.dirname(__file__)
SCRIPT = os.path.join(HERE, "..", "scripts", "skill_queries.py")
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
import skill_gap as g  # noqa: E402
import skill_queries as sq  # noqa: E402

VOCAB = g.load_vocab([os.path.join(HERE, "..", "templates", "skills-vocab.txt")])
CV = "## Skills\nSQL, Jira, UAT, Scrum\n"
PROFILE = 'queries:\n  skills: ["Jira", "UAT", "Kubernetes"]\n'
TODAY = date(2030, 1, 20)


def cov_file(d, name, rows):
    with open(os.path.join(d, name), "w", encoding="utf-8") as fh:
        fh.write("# Candidates\n| Job ID | Company | Role | Score |\n|---|---|---|---|\n"
                 "## Coverage\n| Query | Kind | Result |\n|---|---|---|\n"
                 + "".join(f"| {q} | {k} | {r} |\n" for q, k, r in rows))


class SkillQueries(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        d = self.tmp.name
        cov_file(d, "candidates-2030-01-10.md", [("Jira", "skills", "empty"), ("UAT", "skills", "working"),
                                                 ("jira", "jobs", "working")])
        cov_file(d, "candidates-2030-01-18.md", [("jira", "skills", "empty"), ("UAT", "skills", "empty"),
                                                 ("Kubernetes", "skills", "failed")])
        self.paths = [os.path.join(d, n) for n in os.listdir(d)]
        self.jobs = os.path.join(d, "jobs")
        os.makedirs(self.jobs)
        fresh = time.mktime(date(2030, 1, 15).timetuple())
        for i in range(4):
            p = os.path.join(self.jobs, f"{i}.txt")
            with open(p, "w", encoding="utf-8") as fh:
                fh.write("Need SQL and Jira")
            os.utime(p, (fresh, fresh))
        old = os.path.join(self.jobs, "old.txt")
        with open(old, "w", encoding="utf-8") as fh:
            fh.write("Scrum Scrum")
        t = time.mktime(date(2029, 11, 1).timetuple())
        os.utime(old, (t, t))

    def tearDown(self):
        self.tmp.cleanup()

    def test_stale_counts_only_skill_runs_since_last_new_result(self):
        runs = sq.skill_runs(self.paths)
        self.assertEqual(sq.stale("Jira", runs, TODAY, 7), 10)  # empty since first run; jobs-kind row ignored
        self.assertEqual(sq.stale("UAT", runs, TODAY, 7), 10)   # last new result 10 days ago, empty since
        self.assertIsNone(sq.stale("UAT", runs, date(2030, 1, 16), 7))
        self.assertIsNone(sq.stale("Kubernetes", runs, TODAY, 7))  # failed only: unknown, not stale
        self.assertIsNone(sq.stale("Jira", runs, date(2030, 1, 14), 7))  # not 7 days yet

    def test_suggest_add_drop_check(self):
        jobs = sq.recent_jobs(self.jobs, TODAY, 30)
        self.assertNotIn("old.txt", jobs)
        r = sq.suggest(PROFILE, jobs, CV, sq.skill_runs(self.paths), VOCAB, TODAY)
        self.assertEqual([x["skill"] for x in r["add"]], ["SQL"])  # Scrum only in an old text; Jira already a query
        self.assertEqual([x["query"] for x in r["drop"]], ["Jira", "UAT"])
        self.assertEqual(r["check"], ["Kubernetes"])
        r = sq.suggest(PROFILE, jobs, CV, {}, VOCAB, TODAY, stale_only=True)
        self.assertEqual((r["add"], r["drop"]), ([], []))

    def test_cli_never_writes_profile(self):
        prof = os.path.join(self.tmp.name, "profile.yml")
        cv = os.path.join(self.tmp.name, "cv.md")
        for p, t in ((prof, PROFILE), (cv, CV)):
            with open(p, "w", encoding="utf-8") as fh:
                fh.write(t)
        out = subprocess.run([sys.executable, SCRIPT, "--profile", prof, "--cv", cv, "--jobs", self.jobs,
                              "--candidates", os.path.join(self.tmp.name, "candidates-*.md"),
                              "--date", TODAY.isoformat()], capture_output=True, text=True)
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertIn("ADD   SQL", out.stdout)
        self.assertIn("DROP  Jira  (nothing new for 10 days)", out.stdout)
        self.assertIn("CHECK Kubernetes", out.stdout)
        self.assertEqual(open(prof, encoding="utf-8").read(), PROFILE)


if __name__ == "__main__":
    unittest.main()
