import json
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(__file__)
SCRIPT = os.path.join(HERE, "..", "scripts", "reply_reconcile.py")
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
import reply_reconcile as rr  # noqa: E402
import ui_protocol as up  # noqa: E402

# Fictional rows shaped like the cases a real reply check found on 2026-11-23.
TRACKER = """# Tracker

| Date | Company | Role | Fit | Posting | CV | Cover note | Status | Channel | Reply |
|---|---|---|---|---|---|---|---|---|---|
| 2030-01-01 | Bank Hub | Senior Product Manager REQ-777 | 4.0 | Workday | - | - | ⏳ Ready: portal form, consent with the user | Company portal | - |
| 2030-01-02 | Insure Co | Retail Insurance Member (Executive) - Motor Product | 3.5 | - | - | - | 🔒 Sign-in needed | Company portal | - |
| 2030-01-03 | Big Bank | Business Analyst | 4.0 | - | - | - | ✅ Submitted 2030-01-03 | LinkedIn form | - |
| 2030-01-04 | Big Bank | Data Analyst | 3.5 | - | - | - | ✅ Submitted 2030-01-04 | LinkedIn form | - |
"""
EVENTS = [
    {"company": "Bank Hub", "role": "Senior Product Manager", "kind": "received", "date": "2030-01-05", "ref": "REQ-777"},
    {"company": "Bank Hub", "role": "Senior Product Manager", "kind": "rejected", "date": "2030-01-09", "ref": "REQ-777"},
    {"company": "Insure Co", "role": "Retail Insurance Member (Supervisor) - Motor Product", "kind": "received",
     "date": "2030-01-06", "from": "insure.example"},
    {"company": "Big Bank", "role": "Business Analyst", "kind": "interview", "date": "2030-01-07"},
    {"company": "Big Bank", "kind": "info", "date": "2030-01-07"},
    {"company": "New Co", "role": "Project Manager", "kind": "received", "date": "2030-01-08"},
    {"company": "New Co", "role": "Project Manager", "kind": "verify", "date": "2030-01-08"},
    {"company": "Bad", "kind": "maybe", "date": "soon"},
]


class Reconcile(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = self.tmp.name
        self.tracker = os.path.join(self.root, "tracker.md")
        with open(self.tracker, "w", encoding="utf-8") as f:
            f.write(TRACKER)
        self.events = os.path.join(self.root, "events.jsonl")
        with open(self.events, "w", encoding="utf-8") as f:
            f.write("\n".join(json.dumps(e) for e in EVENTS) + "\n")

    def tearDown(self):
        self.tmp.cleanup()

    def run_script(self, *args):
        return subprocess.run([sys.executable, SCRIPT, "--root", self.root, *args, "--tracker", self.tracker],
                              capture_output=True, text=True)

    def findings(self):
        return rr.check(rr.Tracker(self.tracker), up.read_jsonl(self.events))

    def test_findings_cover_reply_status_missing_and_unsure(self):
        f = self.findings()
        kinds = [x["kind"] for x in f]
        self.assertEqual(kinds.count("STATUS"), 2)  # Bank Hub once (two mails), Insure Co
        self.assertEqual(kinds.count("MISSING"), 1)  # New Co once (received + verify)
        self.assertEqual(kinds.count("SKIP"), 1)
        replies = [x["after"] for x in f if x["kind"] == "REPLY"]
        self.assertIn("Received 2030-01-05; Rejected 2030-01-09", replies)  # matched by ref, stacked
        self.assertIn("Interview invite 2030-01-07", replies)
        unsure = [x for x in f if x["kind"] == "UNSURE"]
        self.assertEqual(len(unsure[0]["rows"]), 2)  # Big Bank without a role: two rows could match
        notes = " ".join(x["why"] for x in f if x["kind"] == "NOTE")
        self.assertIn("title differs", notes)  # Supervisor vs Executive
        self.assertIn("verification mail", notes)
        status = [x for x in f if x["kind"] == "STATUS"][0]
        self.assertTrue(status["before"].startswith("⏳") and status["after"].startswith("✅"))
        missing = [x for x in f if x["kind"] == "MISSING"][0]
        self.assertEqual(len(missing["after"].strip("|").split("|")), 10)

    def test_inbox_approval_then_apply(self):
        out = self.run_script("check", self.events, "--write-replies", "--inbox")
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertIn("3 added to the inbox", out.stdout)
        text = open(self.tracker, encoding="utf-8").read()
        self.assertIn("Interview invite 2030-01-07", text)  # replies need no approval
        self.assertIn("⏳ Ready", text)  # status needs approval
        inbox_p, dec_p = up.paths(self.root)
        inbox = up.read_jsonl(inbox_p)
        items, _ = up.current_items(inbox)
        self.assertEqual({it["type"] for it in items.values()}, {"tracker_fix"})
        bank = next(it for it in items.values() if "Bank Hub" in it["title"])
        insure = next(it for it in items.values() if "Insure Co" in it["title"])
        new = next(it for it in items.values() if "New Co" in it["title"])
        self.assertTrue(bank["before"].startswith("⏳"))

        def decide(it, d, text=""):
            x = {"item": it["id"], "hash": it["hash"], "decision": d, "text": text, "at": up.now_iso()}
            ok, err = up.validate_decision(x, inbox)
            self.assertTrue(ok, err)
            up.append_jsonl(dec_p, x)

        decide(bank, "approve")
        decide(insure, "skip")
        decide(new, "edit", new["preview"].replace("| - |", "| E-mail |", 1).replace("| — | Received", "| E-mail | Received"))
        out = self.run_script("apply")
        self.assertEqual(out.returncode, 0, out.stdout)
        self.assertIn("applied 2, stale 0, problems 0", out.stdout)
        text = open(self.tracker, encoding="utf-8").read()
        self.assertIn("✅ Submitted (confirmed by mail: Received 2030-01-05)", text)
        self.assertIn("🔒 Sign-in needed", text)  # skipped
        self.assertIn("| New Co | Project Manager |", text)
        self.assertIn("| E-mail | Received 2030-01-08 |", text)  # the user's edit was used
        # nothing is proposed twice: a second check adds nothing, a second apply does nothing
        self.assertIn("0 added to the inbox", self.run_script("check", self.events, "--inbox").stdout)
        self.assertIn("applied 0", self.run_script("apply").stdout)
        statuses = {r["id"]: (r["status"], r.get("decision")) for r in up.view(up.read_jsonl(inbox_p), up.read_jsonl(dec_p))}
        self.assertEqual(statuses[insure["id"]], ("consumed", "skip"))

    def test_changed_row_is_stale_not_overwritten(self):
        self.run_script("check", self.events, "--inbox")
        inbox_p, dec_p = up.paths(self.root)
        inbox = up.read_jsonl(inbox_p)
        bank = next(it for it in up.current_items(inbox)[0].values() if "Bank Hub" in it["title"])
        up.append_jsonl(dec_p, {"item": bank["id"], "hash": bank["hash"], "decision": "approve", "text": "",
                                "at": up.now_iso()})
        with open(self.tracker, encoding="utf-8") as f:
            text = f.read().replace("⏳ Ready: portal form, consent with the user", "⛔ Dropped by the user")
        with open(self.tracker, "w", encoding="utf-8") as f:
            f.write(text)
        out = self.run_script("apply")
        self.assertIn("stale 1", out.stdout)
        self.assertIn("⛔ Dropped by the user", open(self.tracker, encoding="utf-8").read())

    def test_turkish_tracker_gets_turkish_text(self):
        with open(self.tracker, "w", encoding="utf-8") as f:
            f.write(TRACKER.replace("| Date | Company | Role | Fit | Posting | CV | Cover note | Status | Channel | Reply |",
                                    "| Tarih | Şirket | Pozisyon | Uyum | İlan | CV | Ön yazı | Durum | Kanal | Yanıt |"))
        f = self.findings()
        self.assertIn("Alındı 2030-01-05; Reddedildi 2030-01-09", [x["after"] for x in f if x["kind"] == "REPLY"])
        self.assertIn("mail ile doğrulandı", [x for x in f if x["kind"] == "STATUS"][0]["after"])
        new = [x for x in f if x["kind"] == "MISSING"][0]["after"]
        self.assertEqual(new.split("|")[5].strip(), "—")  # İlan column found (no ref for New Co)
        tr = rr.Tracker(self.tracker)
        self.assertIsNotNone(tr.col["posting"])


if __name__ == "__main__":
    unittest.main()
