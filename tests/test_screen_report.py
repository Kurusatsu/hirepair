import json
import os
import subprocess
import sys
import tempfile
import unittest

SCRIPT = os.path.join(os.path.dirname(__file__), "..", "scripts", "screen_report.py")
CRIT = {"role": "R", "weights": {"must_have": 70, "nice_to_have": 30},
        "must_have": [{"id": "M1", "text": "SQL"}], "nice_to_have": [], "exclusions": []}


def run(evidence, cv_text, masked=True):
    with tempfile.TemporaryDirectory() as d:
        os.makedirs(os.path.join(d, "scores"))
        os.makedirs(os.path.join(d, "masked"))
        json.dump(CRIT, open(os.path.join(d, "crit.json"), "w"))
        cand = {"candidate_id": "C01", "category": "possible", "category_evidence": "q",
                "criteria": [{"id": "M1", "match": "yes", "evidence": evidence}]}
        json.dump(cand, open(os.path.join(d, "scores", "C01.json"), "w"))
        open(os.path.join(d, "masked", "C01.txt"), "w").write(cv_text)
        args = [sys.executable, SCRIPT, os.path.join(d, "crit.json"), os.path.join(d, "scores")]
        if masked:
            args += ["--masked", os.path.join(d, "masked")]
        r = subprocess.run(args, capture_output=True, text=True)
        return r.returncode, r.stderr


class Quotes(unittest.TestCase):
    def test_verbatim_quote_passes_even_with_whitespace_differences(self):
        self.assertEqual(run("Wrote SQL  queries", "Wrote SQL\nqueries daily")[0], 0)

    def test_invented_quote_is_rejected(self):
        code, err = run("Expert in SQL tuning", "Wrote SQL queries")
        self.assertEqual(code, 1)
        self.assertIn("not a verbatim quote", err)

    def test_without_masked_flag_quotes_are_not_checked(self):
        self.assertEqual(run("Expert in SQL tuning", "Wrote SQL queries", masked=False)[0], 0)


if __name__ == "__main__":
    unittest.main()
