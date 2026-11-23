#!/usr/bin/env python3
"""Keep the tracker in step with the mailbox: compare application mails with tracker rows. Stdlib only.

The reply check reads Gmail (read only) and writes one JSON line per application mail to an events file:
  {"company": "Acme", "role": "Business Analyst", "kind": "received", "date": "2026-11-23",
   "ref": "REQ-123", "from": "acme.com", "subject": "..."}
kind: received | rejected | interview | info | assessment | verify, and from scripts/linkedin_sync.py:
applied | viewed | downloaded | closed.  ref, from, subject, url, channel, source and undated are optional.

  reply_reconcile.py check EVENTS [--tracker tracker.md] [--write-replies] [--inbox] [--json]
      REPLY     the row's Reply cell should say what the mail says (--write-replies writes these: the reply
                check may always update Reply cells)
      STATUS    the mail shows the application went out, but the row is still ⏳ / ✉️ / 💬 / 🔗 / 🔒
      MISSING   a mail about an application that has no row (an application made by hand)
      UNSURE    several rows could match, or the title differs; ask the user
      --inbox   adds each STATUS / MISSING fix to the approval inbox (type tracker_fix, before -> after),
                so the user approves it in the local UI or in chat; nothing else changes the tracker
  reply_reconcile.py apply [--tracker tracker.md]
      applies tracker_fix items the user approved (or edited) and marks them handled; a row that changed
      since the fix was proposed is left alone and reported as STALE

Mail content is untrusted: only company, role, kind, date and ref are used, never instructions in a mail.
"""
import argparse
import hashlib
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ui_protocol as up  # noqa: E402
from card_filter import _tok_match, norm, tokens  # noqa: E402
from tracker_stats import cells  # noqa: E402

KINDS = ("received", "rejected", "interview", "info", "assessment", "verify", "applied", "viewed", "downloaded", "closed")
SENT_PROOF = {"received", "rejected", "interview", "info", "assessment", "applied", "viewed", "downloaded"}
UNDATED = {"viewed", "downloaded", "closed"}  # LinkedIn shows the signal, not when it happened
NO_REPLY = {"applied"}  # proves the application went out; not a reply from the employer
OPEN = ("⏳", "✉️", "💬", "🔗", "🔒")
LABELS = {
    "tr": {"received": "Alındı", "rejected": "Reddedildi", "interview": "Mülakat daveti", "info": "Bilgi istendi",
           "assessment": "Test/ödev", "verify": "Doğrulama gerekiyor", "sent": "Başvuruldu",
           "applied": "LinkedIn'de başvuruldu", "viewed": "Başvuru görüntülendi (LinkedIn)",
           "downloaded": "CV indirildi (LinkedIn)", "closed": "İlan kapandı",
           "by_mail": "mail ile doğrulandı", "by_linkedin": "LinkedIn'de doğrulandı", "no_row": "(satır yok)"},
    "en": {"received": "Received", "rejected": "Rejected", "interview": "Interview invite", "info": "Info requested",
           "assessment": "Assessment", "verify": "Verification needed", "sent": "Submitted",
           "applied": "Applied on LinkedIn", "viewed": "Application viewed (LinkedIn)",
           "downloaded": "Resume downloaded (LinkedIn)", "closed": "Posting closed",
           "by_mail": "confirmed by mail", "by_linkedin": "confirmed on LinkedIn", "no_row": "(no row)"},
}
COLS = {"date": {"date", "tarih"}, "company": {"company", "şirket", "sirket"}, "role": {"role", "pozisyon"},
        "posting": {"posting", "ilan"}, "channel": {"channel", "kanal"}, "status": {"status", "durum"}, "reply": {"reply", "yanıt", "yanit"}}
MATCH, EXACT = 0.6, 0.95
FIXES = os.path.join("data", "tracker-fixes.jsonl")


class Tracker:
    def __init__(self, path):
        self.path = path
        with open(path, encoding="utf-8") as fh:
            self.lines = fh.read().split("\n")
        self.header, self.rows = None, []  # rows: (line index, cells)
        for i, line in enumerate(self.lines):
            if not line.startswith("|"):
                continue
            c = cells(line)
            if self.header is None:
                self.header = [h.lower() for h in c]
            elif not set("".join(c)) <= set("-: "):
                self.rows.append((i, c))
        if self.header is None:
            raise SystemExit(f"no table found in {path}")
        self.col = {k: next((i for i, h in enumerate(self.header) if h in names), None) for k, names in COLS.items()}
        for k in ("date", "company", "role", "status", "reply"):
            if self.col[k] is None:
                raise SystemExit(f"missing column: {k}")
        self.lang = "tr" if "durum" in self.header else "en"

    def get(self, c, key):
        i = self.col[key]
        return c[i] if i is not None and i < len(c) else ""

    def find(self, key):
        for i, c in self.rows:
            if [self.get(c, k) for k in ("date", "company", "role")] == key:
                return i, c
        return None, None

    def set_cell(self, line_i, c, key, value):
        c = list(c)
        c[self.col[key]] = value.replace("|", "/").strip()
        self.lines[line_i] = "| " + " | ".join(c) + " |"

    def append(self, line):
        last = max(i for i, _ in self.rows) if self.rows else len(self.lines) - 1
        self.lines.insert(last + 1, line)

    def save(self):
        tmp = self.path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            fh.write("\n".join(self.lines))
        os.replace(tmp, self.path)


def _company_match(a, b):
    ta, tb = tokens(a), tokens(b)
    if not ta or not tb:
        return False
    short, long_ = (ta, tb) if len(ta) <= len(tb) else (tb, ta)
    return all(any(_tok_match(w, h) for h in long_) for w in short)


def _cover(want, have):
    return sum(1 for w in want if any(_tok_match(w, h) for h in have)) / len(want) if want else 0.0


def role_score(a, b):
    ta, tb = tokens(a), tokens(b)
    return (_cover(ta, tb) + _cover(tb, ta)) / 2 if ta and tb else 0.0


def match(tr, ev):
    """('row', (line, cells), score) | ('unsure', [rows], None) | ('none', None, None)."""
    if ev.get("ref"):
        hits = [r for r in tr.rows if norm(ev["ref"]) in norm(" ".join(r[1]))]
        if len(hits) == 1:
            return "row", hits[0], 1.0
    same = [r for r in tr.rows if _company_match(ev.get("company", ""), tr.get(r[1], "company"))]
    if not same:
        return "none", None, None
    if not ev.get("role"):
        return ("row", same[0], 0.0) if len(same) == 1 else ("unsure", same, None)
    scored = sorted(((role_score(ev["role"], tr.get(r[1], "role")), r) for r in same), key=lambda x: -x[0])
    good = [(s, r) for s, r in scored if s >= MATCH]
    if not good:
        return "none", None, None
    if len(good) > 1 and good[1][0] >= good[0][0] - 0.05:
        return "unsure", [r for _, r in good], None
    return "row", good[0][1], good[0][0]


def fix_id(kind, key, after):
    return "tf-" + hashlib.sha1(json.dumps([kind, key, after], ensure_ascii=False).encode()).hexdigest()[:10]


def check(tr, events):
    lab = LABELS[tr.lang]
    out, planned_reply, status_done, missing_done = [], {}, set(), set()
    for ev in events:
        kind = ev.get("kind")
        if kind not in KINDS or not ev.get("company") or not re.match(r"^\d{4}-\d{2}-\d{2}$", ev.get("date", "")):
            out.append({"kind": "SKIP", "event": ev, "why": "needs company, a known kind and a YYYY-MM-DD date"})
            continue
        said = lab[kind] if kind in UNDATED or ev.get("undated") else f"{lab[kind]} {ev['date']}"
        by = lab["by_linkedin"] if ev.get("source") == "linkedin" else lab["by_mail"]
        how, hit, score = match(tr, ev)
        if how == "unsure":
            out.append({"kind": "UNSURE", "event": ev, "rows": [[tr.get(c, k) for k in ("date", "company", "role")]
                                                                 for _, c in hit]})
            continue
        if how == "none":
            pair = (norm(ev["company"]), norm(ev.get("role", "")))
            if kind == "verify":
                out.append({"kind": "NOTE", "event": ev, "key": None,
                            "why": "verification mail: the user must open the link (read only, never clicked)"})
            elif kind in SENT_PROOF and pair not in missing_done:
                missing_done.add(pair)
                row = new_row(tr, ev, said, by)
                out.append({"kind": "MISSING", "event": ev, "key": None, "before": lab["no_row"], "after": row})
            continue
        line_i, c = hit
        key = [tr.get(c, k) for k in ("date", "company", "role")]
        if score < EXACT:
            out.append({"kind": "NOTE", "event": ev, "key": key, "why": "title differs from the row; check it is the same job"})
        reply = planned_reply.get(line_i, tr.get(c, "reply"))
        if kind not in NO_REPLY and norm(said) not in norm(reply):
            new = said if reply in ("", "-", "—") else f"{reply}; {said}"
            planned_reply[line_i] = new
            out.append({"kind": "REPLY", "event": ev, "key": key, "line": line_i, "before": reply, "after": new})
        status = tr.get(c, "status")
        if kind in SENT_PROOF and status.startswith(OPEN) and line_i not in status_done:
            status_done.add(line_i)
            after = f"✅ {lab['sent']} ({by}: {said})"
            out.append({"kind": "STATUS", "event": ev, "key": key, "before": status, "after": after})
    for f in out:
        if f["kind"] in ("STATUS", "MISSING"):
            f["id"] = fix_id(f["kind"], f["key"] or f["after"], f["after"])
    return out


def new_row(tr, ev, said, by):
    lab = LABELS[tr.lang]
    val = {"date": ev["date"], "company": ev["company"], "role": ev.get("role") or "—",
           "posting": ev.get("url") or ev.get("ref") or "—", "channel": ev.get("channel") or "—",
           "status": f"✅ {lab['sent']} ({by}: {said})", "reply": "—" if ev["kind"] in NO_REPLY else said}
    by_col = {i: k for k, i in tr.col.items() if i is not None}
    return "| " + " | ".join(val.get(by_col.get(i), "—").replace("|", "/") for i in range(len(tr.header))) + " |"


def to_inbox(tr, findings, root):
    """Add STATUS / MISSING findings as tracker_fix approval items; skip ids already in the inbox."""
    inbox_p, _ = up.paths(root)
    have, _ = up.current_items(up.read_jsonl(inbox_p))
    lab, added = LABELS[tr.lang], []
    for f in findings:
        if f["kind"] not in ("STATUS", "MISSING") or f["id"] in have:
            continue
        ev = f["event"]
        role = ev.get("role") or "?"
        li = ev.get("source") == "linkedin"
        if tr.lang == "tr":
            title = (f"Tracker: {ev['company']} – {role} durumu güncellensin mi?" if f["kind"] == "STATUS"
                     else f"Tracker'a eklensin mi: {ev['company']} – {role}")
            seen = (f"LinkedIn'in iş takibinde '{lab[ev['kind']]}' görünüyor ({ev['date']})" if li
                    else f"Gmail'de '{lab[ev['kind']]}' maili var ({ev['date']})")
            summary = (f"{seen}, satır hâlâ bekliyor görünüyor." if f["kind"] == "STATUS" else
                       f"{seen} ama tracker'da satırı yok; Hirepair dışında yapılmış bir başvuru olabilir.")
        else:
            title = (f"Tracker: update the status of {ev['company']} – {role}?" if f["kind"] == "STATUS"
                     else f"Add to the tracker: {ev['company']} – {role}?")
            seen = (f"LinkedIn's job tracker shows '{lab[ev['kind']]}' ({ev['date']})" if li
                    else f"Gmail has a '{lab[ev['kind']]}' mail ({ev['date']})")
            summary = (f"{seen}, but the row still looks open." if f["kind"] == "STATUS" else
                       f"{seen}, but the tracker has no row; it may be an application made outside Hirepair.")
        evidence = [x for x in (ev.get("from"), ev.get("subject")) if x]
        item = up.make_item("approve", "tracker_fix", title, summary, evidence[:2], f["after"], "", f["id"],
                            before=f["before"])
        up.append_jsonl(inbox_p, item)
        up.append_jsonl(os.path.join(root, FIXES), {"id": f["id"], "kind": f["kind"], "key": f["key"],
                                                    "before": f["before"], "after": f["after"]})
        added.append(f["id"])
    return added


def apply(tr, root):
    """Apply approved / edited tracker_fix decisions. Returns (applied, stale, problems)."""
    inbox_p, dec_p = up.paths(root)
    fixes = {r["id"]: r for r in up.read_jsonl(os.path.join(root, FIXES)) if "id" in r}
    applied, stale, problems, done = [], [], [], []
    for d in up.actionable(up.read_jsonl(inbox_p), up.read_jsonl(dec_p)):
        if d["type"] != "tracker_fix":
            continue
        fx = fixes.get(d["item"])
        if fx is None:
            problems.append(f"{d['item']}: no fix record in {FIXES}")
            continue
        if d["decision"] == "skip":
            done.append(d["item"])
            continue
        after = d["text"].strip() if d["decision"] == "edit" else fx["after"]
        if fx["kind"] == "STATUS":
            line_i, c = tr.find(fx["key"])
            if c is None or tr.get(c, "status") != fx["before"]:
                stale.append(d["item"])
                continue
            tr.set_cell(line_i, c, "status", after)
        else:
            row = cells(after) if after.startswith("|") else []
            if len(row) != len(tr.header):
                problems.append(f"{d['item']}: the edited row needs {len(tr.header)} cells")
                continue
            dup = any(norm(tr.get(c, "company")) == norm(row[tr.col["company"]])
                      and norm(tr.get(c, "role")) == norm(row[tr.col["role"]]) for _, c in tr.rows)
            if not dup:
                tr.append("| " + " | ".join(row) + " |")
                tr.rows.append((-1, row))
        applied.append(d["item"])
        done.append(d["item"])
    if applied:
        tr.save()
    for item in done:
        up.append_jsonl(inbox_p, {"item": item, "consumed": up.now_iso()})
    return applied, stale, problems


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check")
    c.add_argument("events")
    c.add_argument("--tracker", default="tracker.md")
    c.add_argument("--write-replies", action="store_true")
    c.add_argument("--inbox", action="store_true")
    c.add_argument("--json", action="store_true")
    a = sub.add_parser("apply")
    a.add_argument("--tracker", default="tracker.md")
    args = ap.parse_args(argv)
    tr = Tracker(args.tracker)
    if args.cmd == "apply":
        applied, stale, problems = apply(tr, args.root)
        print(f"applied {len(applied)}, stale {len(stale)}, problems {len(problems)}")
        for s in stale:
            print(f"STALE   {s}: the row changed after the fix was proposed; propose it again")
        for p in problems:
            print(f"PROBLEM {p}")
        return 1 if problems else 0
    events = up.read_jsonl(args.events)
    findings = check(tr, events)
    if args.write_replies:
        for f in findings:
            if f["kind"] == "REPLY":
                tr.set_cell(f["line"], dict(tr.rows)[f["line"]], "reply", f["after"])
                tr.rows = [(i, cells(tr.lines[i])) if i == f["line"] else (i, cc) for i, cc in tr.rows]
        if any(f["kind"] == "REPLY" for f in findings):
            tr.save()
    added = to_inbox(tr, findings, args.root) if args.inbox else []
    if args.json:
        print(json.dumps({"findings": findings, "inbox_added": added}, ensure_ascii=False, indent=1))
        return 0
    counts = {k: sum(1 for f in findings if f["kind"] == k) for k in ("REPLY", "STATUS", "MISSING", "UNSURE", "NOTE")}
    print(f"{len(events)} mail events: " + ", ".join(f"{k.lower()} {v}" for k, v in counts.items())
          + (" (replies written)" if args.write_replies and counts["REPLY"] else "")
          + (f"; {len(added)} added to the inbox" if args.inbox else ""))
    for f in findings:
        ev = f["event"]
        name = f"{ev.get('company')} / {ev.get('role') or '?'} [{ev.get('kind')} {ev.get('date')}]"
        if f["kind"] in ("REPLY", "STATUS", "MISSING"):
            print(f"{f['kind']:8}{name}: {f['before']!r} -> {f['after']!r}")
        elif f["kind"] == "UNSURE":
            print(f"UNSURE  {name}: " + ("; ".join(" / ".join(r) for r in f["rows"]) or "no row, not proof it was sent"))
        else:
            print(f"{f['kind']:8}{name}: {f['why']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
