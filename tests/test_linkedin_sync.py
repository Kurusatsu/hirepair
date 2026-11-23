import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from datetime import date

HERE = os.path.dirname(__file__)
SCRIPTS = os.path.join(HERE, "..", "scripts")
FIXTURE = os.path.join(HERE, "fixtures", "linkedin_myjobs_2026.json")
sys.path.insert(0, SCRIPTS)
import linkedin_sync as ls  # noqa: E402
import reply_reconcile as rr  # noqa: E402
import ui_protocol as up  # noqa: E402

# Runs linkedin_myjobs.js in node against a fake job tracker with two pages and a "Next" button.
RUNNER = r"""
const fs = require('fs'), vm = require('vm');
const [script, fixture] = process.argv.slice(1);
const fx = JSON.parse(fs.readFileSync(fixture, 'utf8'));
let page = 0;
const row = r => {
  const link = { getAttribute: () => '/jobs/view/' + r.id + '/' };
  const box = { innerText: r.text, querySelector: s => (s.includes('/jobs/view/') ? link : null), parentElement: null };
  return { getAttribute: () => 'opportunityTrackerOverflowMenuButton_table_' + r.id, parentElement: box,
           querySelector: () => null };
};
const next = { getAttribute: () => null, innerText: 'Next', get disabled() { return page >= fx.pages.length - 1; },
               click() { page++; } };
const document = {
  querySelectorAll: s => s.includes('opportunityTracker') ? fx.pages[page].map(row) : s === 'button' ? [next] : [],
};
const ctx = vm.createContext({ document, location: { search: '?stage=applied' }, URLSearchParams,
                               window: {}, setTimeout: f => f() });
vm.runInContext(fs.readFileSync(script, 'utf8'), ctx).then(out => console.log(out));
"""

TRACKER = """| Date | Company | Role | Fit | Posting | CV | Cover note | Status | Channel | Reply |
|---|---|---|---|---|---|---|---|---|---|
| 2030-01-01 | Example Pay | Technical Product Manager | 4.0 | https://www.linkedin.com/jobs/view/4000000011/ | - | - | ⏳ Easy Apply draft saved | LinkedIn form | - |
| 2030-01-01 | Example Consulting | Data Governance Consultant | 3.5 | https://www.linkedin.com/jobs/view/4000000013 | - | - | ✅ Submitted | LinkedIn form | - |
"""


@unittest.skipUnless(shutil.which("node"), "node not installed")
class Reader(unittest.TestCase):
    def test_pages_signals_and_titles(self):
        out = subprocess.run(["node", "-e", RUNNER, os.path.join(SCRIPTS, "linkedin_myjobs.js"), FIXTURE],
                             capture_output=True, text=True)
        self.assertEqual(out.returncode, 0, out.stderr)
        with open(FIXTURE, encoding="utf-8") as f:
            expected = json.load(f)["expected"]
        self.assertEqual(out.stdout.strip(), f"N={len(expected)};" + "|".join(expected))


class Sync(unittest.TestCase):
    RAW = ("N=4;4000000011~0~applied~~Technical Product Manager~Example Pay|4000000012~0~applied~~Project Ma"
           "MORE@100\nN=4;nager~Example Data|4000000013~4~applied~viewed+closed~Data Governance Consultant~Example Consulting"
           "|4000000099~30~applied~~Old Job~Old Co\nN=2;4000000020~-1~saved~~Saved Role~Saved Co|4000000021~-1~interview~~Interview Role~Int Co")

    def test_rows_and_events(self):
        rows = ls.rows_from(self.RAW)
        self.assertEqual([r["id"] for r in rows], ["4000000011", "4000000012", "4000000013", "4000000099",
                                                   "4000000020", "4000000021"])
        self.assertEqual(rows[1]["title"], "Project Manager")  # stitched across MORE@
        ev, listed = ls.events(rows, date(2030, 1, 10), 14)
        kinds = [(e["ref"], e["kind"]) for e in ev]
        self.assertIn(("4000000013", "viewed"), kinds)
        self.assertIn(("4000000013", "closed"), kinds)
        self.assertIn(("4000000021", "interview"), kinds)
        self.assertNotIn("4000000099", [e["ref"] for e in ev])  # older than 14 days
        self.assertEqual(next(e for e in ev if e["ref"] == "4000000013" and e["kind"] == "applied")["date"], "2030-01-06")
        self.assertEqual([r["id"] for r in listed], ["4000000020"])

    def test_saved_jobs_go_to_manual_list_once(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "manual.md")
            saved = [r for r in ls.rows_from(self.RAW) if r["stage"] == "saved"]
            self.assertEqual(ls.add_saved(p, saved, date(2030, 1, 10)), 1)
            self.assertEqual(ls.add_saved(p, saved, date(2030, 1, 11)), 0)
            text = open(p, encoding="utf-8").read()
            self.assertIn("## LinkedIn saved jobs", text)
            self.assertEqual(text.count("/jobs/view/4000000020/"), 1)

    def test_events_flow_into_reconcile(self):
        with tempfile.TemporaryDirectory() as d:
            tracker = os.path.join(d, "tracker.md")
            with open(tracker, "w", encoding="utf-8") as f:
                f.write(TRACKER)
            ev, _ = ls.events(ls.rows_from(self.RAW), date(2030, 1, 10), 14)
            tr = rr.Tracker(tracker)
            found = rr.check(tr, ev)
            by = {(f["kind"], f["event"]["ref"], f["event"]["kind"]): f for f in found}
            status = by[("STATUS", "4000000011", "applied")]
            self.assertIn("confirmed on LinkedIn: Applied on LinkedIn 2030-01-10", status["after"])
            self.assertNotIn(("REPLY", "4000000011", "applied"), by)  # applying is not a reply
            self.assertEqual(by[("REPLY", "4000000013", "closed")]["after"],
                             "Application viewed (LinkedIn); Posting closed")  # undated, stacked
            missing = by[("MISSING", "4000000012", "applied")]["after"]
            self.assertIn("| https://www.linkedin.com/jobs/view/4000000012/ |", missing)
            self.assertIn("| LinkedIn form |", missing)
            # an interview on LinkedIn proves the application too: a missing row is proposed, reply undated
            self.assertIn("| Interview invite |", by[("MISSING", "4000000021", "interview")]["after"])
            # a second sync after the replies were written proposes nothing new for them
            for f in found:
                if f["kind"] == "REPLY":
                    tr.set_cell(f["line"], dict(tr.rows)[f["line"]], "reply", f["after"])
                    tr.rows = [(i, rr.cells(tr.lines[i])) if i == f["line"] else (i, c) for i, c in tr.rows]
            tr.save()
            again = rr.check(rr.Tracker(tracker), ev)
            self.assertFalse([f for f in again if f["kind"] == "REPLY"])
            inbox_added = rr.to_inbox(rr.Tracker(tracker), again, d)
            items, _ = up.current_items(up.read_jsonl(up.paths(d)[0]))
            self.assertTrue(any("LinkedIn's job tracker" in items[i]["summary"] for i in inbox_added))


class OpenApplications(unittest.TestCase):
    RAW = ("N=3;4000000011~0~draft~~Technical Product Manager~Example Pay|4000000031~1~draft~~New Draft~Draft Co"
           "|4000000032~-1~draft~closed~Dead Draft~Gone Co\n"
           "N=2;4000000033~3~clicked_apply~~Portal Role~Portal Co|4000000034~40~clicked_apply~~Old Portal Role~Old Co")

    def test_drafts_and_company_forms(self):
        with tempfile.TemporaryDirectory() as d:
            tracker = os.path.join(d, "tracker.md")
            with open(tracker, "w", encoding="utf-8") as f:
                f.write(TRACKER)
            ev, listed = ls.events(ls.rows_from(self.RAW), date(2030, 1, 10), 14)
            self.assertEqual(listed, [])
            self.assertEqual({(e["ref"], e["kind"]) for e in ev},
                             {("4000000011", "draft"), ("4000000031", "draft"), ("4000000032", "closed"),
                              ("4000000033", "clicked")})  # the 40-day-old posting is skipped
            found = rr.check(rr.Tracker(tracker), ev)
            rows = {f["event"]["ref"]: f for f in found if f["kind"] == "MISSING"}
            self.assertEqual(set(rows), {"4000000031", "4000000033"})  # the known draft and the dead one add none
            self.assertIn("| ⏳ Easy Apply draft waiting on LinkedIn |", rows["4000000031"]["after"])
            self.assertIn("| 🔗 Company form opened from LinkedIn |", rows["4000000033"]["after"])
            self.assertFalse([f for f in found if f["kind"] in ("STATUS", "REPLY")])  # a draft proves nothing


@unittest.skipUnless(shutil.which("node"), "node not installed")
class Skills(unittest.TestCase):
    def test_reads_names_once(self):
        runner = r"""
const fs = require('fs'), vm = require('vm');
const el = t => ({ innerText: t });
const items = [el('SQL\nUsed at Example Co'), el('Jira\n1 endorsement'), el('SQL\nagain'), el('Agile | Scrum')];
const document = { body: { scrollHeight: 0 }, querySelectorAll: s => s.includes('profile.skill(') ? items : [] };
const ctx = vm.createContext({ document, window: { scrollTo() {} }, setTimeout: f => f() });
vm.runInContext(fs.readFileSync(process.argv[1], 'utf8'), ctx).then(out => console.log(out));
"""
        out = subprocess.run(["node", "-e", runner, os.path.join(SCRIPTS, "linkedin_skills.js")],
                             capture_output=True, text=True)
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertEqual(out.stdout.strip(), "N=3;SQL|Jira|Agile Scrum")


if __name__ == "__main__":
    unittest.main()
