import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
import skill_gap as g  # noqa: E402

VOCAB = g.load_vocab([os.path.join(HERE, "..", "templates", "skills-vocab.txt")])
CV = "## Skills\nSQL, Jira, Confluence, UAT, Scrum\n## Eğitim\nLisans"
JOBS = {
    "1.txt": "We need SQL (PostgreSQL), Jira and Power BI. Agile team.",
    "2.txt": "Business analyst: requirements elicitation, user acceptance testing, Jira, Power BI.",
    "3.txt": "İş analisti arıyoruz. SQL bilgisi, Jira, kullanıcı kabul testi.",
}


class SkillGap(unittest.TestCase):
    def test_aliases_and_turkish_match(self):
        s = g.skills_in("İŞ ANALİZİ ve kullanıcı kabul testi", VOCAB)
        self.assertIn("Business Analysis", s)
        self.assertIn("User Acceptance Testing", s)

    def test_whole_words_only(self):
        self.assertNotIn("SAP", g.skills_in("We are a sapphire company", VOCAB))
        self.assertIn("C#", g.skills_in("Backend in C# and .NET", VOCAB))
        self.assertIn(".NET", g.skills_in("Backend in C# and .NET", VOCAB))

    def test_education_heading_is_not_training(self):
        self.assertNotIn("Training", g.skills_in(CV, VOCAB))

    def test_gap_never_suggested_for_linkedin(self):
        r = g.analyse(JOBS, CV, ["Jira"], VOCAB, min_share=0.3)
        self.assertIn("Microsoft Power BI", r["gaps"])
        self.assertNotIn("Microsoft Power BI", r["add_to_linkedin"])
        self.assertIn("SQL", r["add_to_linkedin"])
        self.assertNotIn("Jira", r["add_to_linkedin"])

    def test_linkedin_skill_without_cv_evidence_is_flagged(self):
        r = g.analyse(JOBS, CV, ["Python", "Jira", "Underwater Basket Weaving"], VOCAB)
        self.assertEqual(r["linkedin_not_in_cv"], ["Python"])
        self.assertEqual(r["linkedin_unmatched"], ["Underwater Basket Weaving"])

    def test_demand_counts_each_job_once(self):
        r = g.analyse({"a": "SQL SQL SQL", "b": "nothing"}, "", None, VOCAB)
        row = next(x for x in r["demand"] if x["skill"] == "SQL")
        self.assertEqual((row["jobs"], row["share"]), (1, 0.5))
        self.assertEqual(r["add_to_linkedin"], [])

    def test_empty_jobs_folder(self):
        with tempfile.TemporaryDirectory() as d:
            out = subprocess.run([sys.executable, os.path.join(HERE, "..", "scripts", "skill_gap.py"),
                                  "--jobs", d, "--cv", os.path.join(d, "none.md")],
                                 capture_output=True, text=True)
        self.assertEqual(out.returncode, 0)
        self.assertIn("No job descriptions found", out.stdout)


if __name__ == "__main__":
    unittest.main()
