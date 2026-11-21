import os
import sys
import unittest
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import ui_protocol as p  # noqa: E402


def item(cls="approve", typ="cv_upload", **kw):
    return p.make_item(cls, typ, kw.pop("title", "T"), preview=kw.pop("preview", "x"), **kw)


def dec(it, decision="approve", **kw):
    d = {"item": it["id"], "hash": it["hash"], "decision": decision, "text": "", "at": "t"}
    d.update(kw)
    return d


class Protocol(unittest.TestCase):
    def test_class_and_type_must_match(self):
        with self.assertRaises(ValueError):
            p.make_item("approve", "consent", "T")
        with self.assertRaises(ValueError):
            p.make_item("human", "cv_upload", "T")

    def test_link_must_be_http(self):
        with self.assertRaises(ValueError):
            p.make_item("approve", "cv_upload", "T", link="javascript:alert(1)")

    def test_human_items_cannot_be_approved(self):
        h = item("human", "consent", item_id="h1")
        ok, err = p.validate_decision(dec(h, "approve"), [h])
        self.assertFalse(ok)
        self.assertIn("not allowed", err)
        self.assertTrue(p.validate_decision(dec(h, "done"), [h])[0])

    def test_stale_hash_is_rejected(self):
        a = item(item_id="a1")
        ok, err = p.validate_decision(dec(a, hash="sha256:old"), [a])
        self.assertFalse(ok)
        self.assertIn("stale", err)

    def test_readding_an_id_supersedes_and_makes_old_decision_stale(self):
        a = item(item_id="a1", preview="v1")
        decisions = [dec(a)]
        a2 = item(item_id="a1", preview="v2")
        rows = p.view([a, a2], decisions)
        self.assertEqual(rows[0]["status"], "stale")
        self.assertEqual(p.actionable([a, a2], decisions), [])

    def test_decided_then_consumed(self):
        a = item(item_id="a1")
        self.assertEqual(p.view([a], [dec(a)])[0]["status"], "decided")
        self.assertEqual(len(p.actionable([a], [dec(a)])), 1)
        inbox = [a, {"item": "a1", "consumed": "t"}]
        self.assertEqual(p.view(inbox, [dec(a)])[0]["status"], "consumed")
        self.assertEqual(p.actionable(inbox, [dec(a)]), [])
        self.assertFalse(p.validate_decision(dec(a), inbox)[0])

    def test_pending_items_expire_after_seven_days(self):
        old = item(item_id="a1", created=(datetime.now() - timedelta(days=8)).isoformat(timespec="seconds"))
        self.assertEqual(p.view([old], [])[0]["status"], "expired")

    def test_edit_needs_text_and_text_is_capped(self):
        a = item(item_id="a1")
        self.assertFalse(p.validate_decision(dec(a, "edit", text=" "), [a])[0])
        self.assertTrue(p.validate_decision(dec(a, "edit", text="new draft"), [a])[0])
        self.assertFalse(p.validate_decision(dec(a, "edit", text="x" * 4001), [a])[0])

    def test_unknown_item_and_bad_shapes(self):
        self.assertFalse(p.validate_decision({"item": "nope"}, [])[0])
        self.assertFalse(p.validate_decision("string", [])[0])

    def test_read_jsonl_skips_bad_lines(self):
        import tempfile
        with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False, encoding="utf-8") as f:
            f.write('{"a":1}\nnot json\n\n[1]\n{"b":2}\n')
        try:
            self.assertEqual(p.read_jsonl(f.name), [{"a": 1}, {"b": 2}])
        finally:
            os.unlink(f.name)
        self.assertEqual(p.read_jsonl(f.name), [])


if __name__ == "__main__":
    unittest.main()
