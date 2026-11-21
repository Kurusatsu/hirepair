#!/usr/bin/env python3
"""Approval inbox protocol between the agent and the local UI (see docs/ui-design.md). Stdlib only.

Files (under data/, git-ignored, append-only JSON lines):
  inbox.jsonl      agent -> UI   items, and {"item": id, "consumed": ts} records
  decisions.jsonl  UI -> agent   {"item", "hash", "decision", "text", "at"}

Agent CLI:
  ui_protocol.py add --class approve|human --type TYPE --title T [--summary S] [--evidence E ...]
                     [--preview P] [--link URL] [--id ID]      append an item, print "id hash"
  ui_protocol.py decisions                                       print actionable decisions as JSON lines
  ui_protocol.py consume ITEM_ID                                 mark an item as handled
  ui_protocol.py compact [--keep-days 30]                        rewrite both files without items consumed or
                                                                 expired over 30 days ago, superseded definitions
                                                                 and older decisions (status stays the same)
Run from the project folder or pass --root.
"""
import argparse
import hashlib
import json
import os
import sys
import time
from datetime import datetime, timedelta

CLASSES = {"approve": {"approve", "skip", "edit"}, "human": {"done", "skip"}}
TYPES = {"approve": {"roles", "criteria", "limits", "cv_upload", "mail_draft", "open_question", "profile_edit"},
         "human": {"consent", "signin", "id_field", "captcha", "submit", "send"}}
EXPIRY = timedelta(days=7)
MAX_TEXT = 4000
HASH_FIELDS = ("title", "summary", "evidence", "preview", "link")


def paths(root):
    d = os.path.join(root, "data")
    return os.path.join(d, "inbox.jsonl"), os.path.join(d, "decisions.jsonl")


def read_jsonl(path):
    out = []
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except ValueError:
                    continue
                if isinstance(obj, dict):
                    out.append(obj)
    except FileNotFoundError:
        pass
    return out


def append_jsonl(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")


def item_hash(item):
    body = {k: item.get(k, [] if k == "evidence" else "") for k in HASH_FIELDS}
    raw = json.dumps(body, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def now_iso():
    return datetime.now().isoformat(timespec="seconds")


def parse_ts(s):
    try:
        return datetime.fromisoformat(s)
    except (TypeError, ValueError):
        return None


def make_item(cls, typ, title, summary="", evidence=None, preview="", link="", item_id=None, created=None):
    if cls not in CLASSES:
        raise ValueError(f"class must be one of {sorted(CLASSES)}")
    if typ not in TYPES[cls]:
        raise ValueError(f"type '{typ}' is not allowed for class '{cls}': {sorted(TYPES[cls])}")
    if not title.strip():
        raise ValueError("title is required")
    if link and not link.startswith(("http://", "https://")):
        raise ValueError("link must start with http:// or https://")
    item = {"id": item_id or f"a-{int(time.time())}-{os.getpid() % 1000}", "created": created or now_iso(),
            "class": cls, "type": typ, "title": title.strip(), "summary": summary, "evidence": list(evidence or []),
            "preview": preview, "link": link}
    item["hash"] = item_hash(item)
    return item


def current_items(inbox):
    """Latest definition per id (re-adding an id supersedes it) plus the consumed map."""
    items, consumed = {}, {}
    for r in inbox:
        if "consumed" in r and "item" in r:
            consumed[r["item"]] = r["consumed"]
        elif "id" in r and r.get("class") in CLASSES:
            items[r["id"]] = r
    return items, consumed


def latest_decisions(decisions):
    """Last decision per item in one pass (the files are append-only and grow over time)."""
    last = {}
    for d in decisions:
        if "item" in d:
            last[d["item"]] = d
    return last


def latest_decision(item_id, decisions):
    return latest_decisions(decisions).get(item_id)


def view(inbox, decisions, now=None):
    """Items with a computed status: pending | decided | stale | consumed | expired."""
    now = now or datetime.now()
    items, consumed = current_items(inbox)
    last = latest_decisions(decisions)
    out = []
    for it in items.values():
        d = last.get(it["id"])
        if it["id"] in consumed:
            status = "consumed"
        elif d and d.get("hash") == it.get("hash") and d.get("decision") in CLASSES[it["class"]]:
            status = "decided"
        elif d and d.get("hash") != it.get("hash"):
            status = "stale"
        else:
            status = "pending"
        created = parse_ts(it.get("created"))
        if status in ("pending", "stale") and created and now - created > EXPIRY:
            status = "expired"
        row = dict(it)
        row["status"] = status
        if d and status in ("decided", "stale"):
            row["decision"] = d.get("decision")
        out.append(row)
    out.sort(key=lambda r: r.get("created", ""))
    return out


def validate_decision(d, inbox, decisions=None):
    """Return (ok, error). Checks the item exists, hash is current, decision fits the class."""
    if not isinstance(d, dict):
        return False, "decision must be an object"
    items, consumed = current_items(inbox)
    it = items.get(d.get("item"))
    if it is None:
        return False, "unknown item"
    if d.get("item") in consumed:
        return False, "item already handled"
    if d.get("hash") != it.get("hash"):
        return False, "stale: the item changed after you opened it"
    if d.get("decision") not in CLASSES[it["class"]]:
        return False, f"decision not allowed for class {it['class']}"
    text = d.get("text", "")
    if not isinstance(text, str) or len(text) > MAX_TEXT:
        return False, "text too long"
    if d.get("decision") == "edit" and not text.strip():
        return False, "edit needs text"
    return True, ""


def actionable(inbox, decisions):
    """Decisions the agent may act on: decided items only, with the matching hash."""
    last = latest_decisions(decisions)
    out = []
    for row in view(inbox, decisions):
        if row["status"] == "decided":
            d = last[row["id"]]
            out.append({"item": row["id"], "type": row["type"], "class": row["class"], "decision": d["decision"],
                        "text": d.get("text", ""), "at": d.get("at", "")})
    return out


def compact(inbox, decisions, now=None, keep_days=30):
    """(inbox rows, decision rows, dropped ids) keeping only what view() and actionable() still need.

    Items consumed or expired more than keep_days ago are dropped with their records; for the rest only
    the latest definition, the consumed record and the last decision are kept.
    """
    now = now or datetime.now()
    items, consumed = current_items(inbox)
    last = latest_decisions(decisions)
    status = {r["id"]: r["status"] for r in view(inbox, decisions, now)}
    old = now - timedelta(days=keep_days)
    drop = set()
    for i, it in items.items():
        ref = None
        if status[i] == "consumed":
            ref = parse_ts(consumed.get(i))
        elif status[i] == "expired":
            ref = parse_ts(it.get("created")) + EXPIRY
        if ref and ref < old:
            drop.add(i)
    keep_inbox = [it for i, it in sorted(items.items(), key=lambda kv: kv[1].get("created", "")) if i not in drop]
    keep_inbox += [{"item": i, "consumed": ts} for i, ts in consumed.items() if i in items and i not in drop]
    keep_dec = sorted((d for i, d in last.items() if i in items and i not in drop), key=lambda d: d.get("at", ""))
    return keep_inbox, keep_dec, sorted(drop)


def _rewrite(path, rows, expect_size):
    """Atomically replace path unless it grew since it was read (the UI may have appended a decision)."""
    try:
        if os.path.getsize(path) != expect_size:
            return False
    except FileNotFoundError:
        if expect_size:
            return False
        return True
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    os.replace(tmp, path)
    return True


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("add")
    a.add_argument("--class", dest="cls", required=True, choices=sorted(CLASSES))
    a.add_argument("--type", required=True)
    a.add_argument("--title", required=True)
    a.add_argument("--summary", default="")
    a.add_argument("--evidence", action="append", default=[])
    a.add_argument("--preview", default="")
    a.add_argument("--link", default="")
    a.add_argument("--id")
    sub.add_parser("decisions")
    c = sub.add_parser("consume")
    c.add_argument("item")
    k = sub.add_parser("compact")
    k.add_argument("--keep-days", type=int, default=30)
    args = ap.parse_args(argv)
    inbox_p, dec_p = paths(args.root)
    if args.cmd == "compact":
        sizes = [os.path.getsize(p) if os.path.exists(p) else 0 for p in (inbox_p, dec_p)]
        inbox, decs = read_jsonl(inbox_p), read_jsonl(dec_p)
        new_inbox, new_dec, dropped = compact(inbox, decs, keep_days=args.keep_days)
        # decisions first: if the inbox rewrite is then skipped, every kept decision still matches its item
        if not (_rewrite(dec_p, new_dec, sizes[1]) and _rewrite(inbox_p, new_inbox, sizes[0])):
            print("error: a file changed while compacting; run again", file=sys.stderr)
            return 1
        print(f"compacted: inbox {len(inbox)} -> {len(new_inbox)} rows, decisions {len(decs)} -> {len(new_dec)}; "
              f"dropped {len(dropped)} old items")
        return 0
    if args.cmd == "add":
        try:
            item = make_item(args.cls, args.type, args.title, args.summary, args.evidence, args.preview, args.link, args.id)
        except ValueError as e:
            print("error:", e, file=sys.stderr)
            return 1
        append_jsonl(inbox_p, item)
        print(item["id"], item["hash"])
    elif args.cmd == "decisions":
        for row in actionable(read_jsonl(inbox_p), read_jsonl(dec_p)):
            print(json.dumps(row, ensure_ascii=False))
    elif args.cmd == "consume":
        items, _ = current_items(read_jsonl(inbox_p))
        if args.item not in items:
            print("error: unknown item", file=sys.stderr)
            return 1
        append_jsonl(inbox_p, {"item": args.item, "consumed": now_iso()})
    return 0


if __name__ == "__main__":
    sys.exit(main())
