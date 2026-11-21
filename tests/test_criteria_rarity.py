import os
import subprocess
import sys
import unittest

HERE = os.path.dirname(__file__)
SCRIPT = os.path.join(HERE, "..", "scripts", "criteria_rarity.py")
SAMPLES = os.path.join(HERE, "..", "templates", "screening")
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
import criteria_rarity as cr  # noqa: E402
import skill_gap as g  # noqa: E402

CRIT = {"must_have": [{"id": "M1", "text": "SQL"}, {"id": "M2", "text": "Payments domain"},
                      {"id": "M3", "text": "Has run UAT"}],
        "nice_to_have": [{"id": "N1", "text": "Jira"}]}


def cand(cid, **m):
    return {"candidate_id": cid, "criteria": [{"id": k, "match": v} for k, v in m.items()]}


class Rarity(unittest.TestCase):
    def test_flags_rare_vs_unclear_must_haves_only(self):
        pool = [cand(f"C{i}", M1="no", M2="not_stated", M3="yes", N1="no") for i in range(9)]
        pool.append(cand("C9", M1="partial", M3="yes"))  # missing M2 counts as not stated
        r = {c["id"]: c for c in cr.rarity(CRIT, pool)["criteria"]}
        self.assertEqual((r["M1"]["flag"], r["M1"]["met"], r["M1"]["no"]), ("RARE", 1, 9))
        self.assertEqual((r["M2"]["flag"], r["M2"]["not_stated"]), ("UNCLEAR", 10))
        self.assertEqual(r["M3"]["flag"], "")
        self.assertEqual(r["N1"]["flag"], "")  # nice-to-haves are never flagged

    def test_masked_cv_skill_counts(self):
        vocab = g.load_vocab([os.path.join(HERE, "..", "templates", "skills-vocab.txt")])
        masked = {"C1": "SQL and Jira", "C2": "Excel"}
        r = cr.rarity(CRIT, [], masked, vocab)
        self.assertEqual(r["criteria"][0]["skills"], {"SQL": 1})
        self.assertEqual(r["criteria"][0]["share"], 0)

    def test_cli_on_fictional_samples(self):
        out = subprocess.run([sys.executable, SCRIPT, os.path.join(SAMPLES, "criteria.example.json"),
                              os.path.join(SAMPLES, "scores"), "--masked", os.path.join(SAMPLES, "cvs")],
                             capture_output=True, text=True)
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertIn("in 5 scored candidates", out.stdout)
        self.assertIn("M4", out.stdout)


if __name__ == "__main__":
    unittest.main()
