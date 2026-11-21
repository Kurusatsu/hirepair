#!/usr/bin/env python3
"""Drop already-handled job cards before any card is clicked. Stdlib only.

Input: the raw output(s) of scripts/linkedin_cards.js, one call per file or all pasted in one file,
in call order ("N=..;rows...MORE@n" parts are stitched back together).

Usage:
  python3 scripts/card_filter.py cards.txt [more.txt ...] [--seen data/seen-ids.txt] [--tracker tracker.md]
                                 [--profile profile.local.yml] [--json]
  ... | python3 scripts/card_filter.py - [...]

Drops: Applied/Başvuruldu badge, job ID in the seen-ID list or in a tracker Posting link,
company + role already in the tracker, duplicates on the page. Saved cards are kept and flagged.
Title prefilter (needs the profile): drops titles that match exclusions.roles, and titles that match
no approved/target/adjacent role, no queries.jobs phrase and no queries.skills keyword. Cards from
always_include_companies are never dropped by title. Skipped titles are printed so the report can
list them; nothing is dropped by title when the profile has no role phrases.
Prints the cards to open, then one line of counts. Does not write any file.
"""
import argparse
import json
from collections import defaultdict
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tracker_stats import parse  # noqa: E402

APPLIED = {"applied", "başvuruldu"}
SAVED = {"saved", "kaydedildi"}
COMPANY = {"company", "şirket", "sirket"}
ROLE = {"role", "pozisyon"}
POSTING = {"posting", "ilan"}
TITLE_MAX, COMPANY_MAX = 60, 40  # must match the slices in linkedin_cards.js


def norm(s, n=None):
    s = s.replace("İ", "i").lower()
    s = re.sub(r"[^\w]+", " ", s).strip()
    s = re.sub(r"\s+", " ", s)
    return s[:n] if n else s


def _unquote(v):
    v = v.strip()
    return v[1:-1] if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'" else v


def _strip_comment(line):
    out, q = [], None
    for i, ch in enumerate(line):
        if q:
            q = None if ch == q else q
        elif ch in "\"'":
            q = ch
        elif ch == "#" and (i == 0 or line[i - 1] in " \t"):
            break
        out.append(ch)
    return "".join(out).rstrip()


def mini_yaml(text):
    """Collect scalar and list values by dotted key path. Enough for profile.local.yml; not general YAML."""
    out, stack = defaultdict(list), []
    for raw in text.splitlines():
        line = _strip_comment(raw)
        if not line.strip():
            continue
        ind, s = len(line) - len(line.lstrip()), line.strip()
        is_item = s.startswith("- ") or s == "-"
        while stack and (stack[-1][0] > ind or (stack[-1][0] == ind and not is_item)):
            stack.pop()
        path = [k for _, k in stack]
        if is_item:
            s = s[2:].strip()
            m = re.match(r"^([\w-]+):\s*(.*)$", s)
            if m:
                path, s = path + [m.group(1)], m.group(2)
            if s:
                out[".".join(path)].append(_unquote(s))
            continue
        m = re.match(r"^([\w-]+):\s*(.*)$", s)
        if not m:
            continue
        key, val = m.group(1), m.group(2).strip()
        if not val:
            stack.append((ind, key))
        elif val.startswith("[") and val.endswith("]"):
            out[".".join(path + [key])].extend(_unquote(x) for x in val[1:-1].split(",") if x.strip())
        else:
            out[".".join(path + [key])].append(_unquote(val))
    return out


FILLER = {"and", "or", "ve", "veya", "of", "for", "the", "&", "-"}


def tokens(s):
    return [t for t in norm(s).split() if t not in FILLER]


def phrases(entry):
    """'Release / Change Manager' -> [['release', 'manager'], ['change', 'manager']]."""
    alts = [tokens(a) for a in entry.split("/")]
    alts = [a for a in alts if a]
    if len(alts) > 1 and len(alts[-1]) > 1:
        tail = alts[-1][-1]
        alts = [a + [tail] if len(a) == 1 else a for a in alts]
    return alts


def _tok_match(want, have):
    return have == want or (min(len(want), len(have)) >= 4 and (have.startswith(want) or want.startswith(have)))


def title_has(title_tokens, phrase):
    return all(any(_tok_match(w, h) for h in title_tokens) for w in phrase)


class TitleRules:
    def __init__(self, profile_text):
        y = mini_yaml(profile_text or "")
        real = lambda xs: [x for x in xs if x and not x.startswith("<")]  # noqa: E731
        self.positive = [p for e in real(y["approved_roles.roles.title"] + y["targets.roles"]
                                         + y["targets.adjacent_roles"] + y["queries.jobs"]) for p in phrases(e)]
        self.skills = [p for e in real(y["queries.skills"]) for p in phrases(e)]
        self.excluded = [p for e in real(y["exclusions.roles"]) for p in phrases(e)]
        self.always = {norm(c) for c in real(y["always_include_companies"])}

    def active(self):
        return bool(self.positive)

    def decide(self, card):
        """Return (keep, reason) where reason is a drop reason or a keep flag ('' for a role match)."""
        if norm(card["company"]) in self.always:
            return True, "always"
        tt = tokens(card["title"])
        if any(title_has(tt, p) for p in self.excluded):
            return False, "excluded_title"
        if any(title_has(tt, p) for p in self.positive):
            return True, ""
        if any(title_has(tt, p) for p in self.skills):
            return True, "skill"
        return False, "off_target"


def stitch(parts):
    """Join the parts of one or more calls; a row may be cut across a MORE@ boundary."""
    out = ""
    for p in parts:
        p = p.strip()
        p = re.sub(r"^N=\d+;", "", p)
        p = re.sub(r"MORE@\d+$", "", p)
        out += p
    return out


def rows_from(text):
    cards = []
    for raw in text.split("|"):
        f = raw.split("~")
        if len(f) < 2 or not f[1].strip():
            continue
        f += [""] * (5 - len(f))
        cards.append({"id": f[0].strip(), "title": f[1].strip(), "company": f[2].strip(),
                      "age": f[3].strip(), "badge": f[4].strip()})
    return cards


def read_seen(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return {line.strip() for line in fh if line.strip()}
    except FileNotFoundError:
        return set()


def tracker_keys(path):
    """Return ({company|role keys}, {job ids found in posting links})."""
    try:
        with open(path, encoding="utf-8") as fh:
            header, rows = parse(fh.read())
    except FileNotFoundError:
        return set(), set()
    if header is None:
        return set(), set()

    def idx(names):
        return next((i for i, h in enumerate(header) if h in names), -1)

    ci, ri, pi = idx(COMPANY), idx(ROLE), idx(POSTING)
    keys, ids = set(), set()
    for r in rows:
        if len(r) != len(header):
            continue
        if ci >= 0 and ri >= 0:
            keys.add(norm(r[ci], COMPANY_MAX) + "|" + norm(r[ri], TITLE_MAX))
        if pi >= 0:
            ids.update(re.findall(r"(?:/jobs/view/|currentJobId=)(\d+)", r[pi]))
    return keys, ids


def filter_cards(cards, seen, keys, tracker_ids, rules=None):
    keep, page = [], set()
    counts = {"applied": 0, "seen_id": 0, "in_tracker": 0, "duplicate": 0, "excluded_title": 0, "off_target": 0}
    skipped = []
    for c in cards:
        key = norm(c["company"], COMPANY_MAX) + "|" + norm(c["title"], TITLE_MAX)
        badge = norm(c["badge"])
        dedupe = c["id"] or key
        if dedupe in page:
            counts["duplicate"] += 1
            continue
        page.add(dedupe)
        if badge in APPLIED:
            counts["applied"] += 1
        elif c["id"] and (c["id"] in seen or c["id"] in tracker_ids):
            counts["seen_id"] += 1
        elif key in keys:
            counts["in_tracker"] += 1
        else:
            ok, why = rules.decide(c) if rules and rules.active() else (True, "")
            if not ok:
                counts[why] += 1
                skipped.append(dict(c, reason=why))
                continue
            keep.append(dict(c, saved=badge in SAVED, needs_click=not c["id"], via=why))
    return keep, counts, skipped


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("inputs", nargs="+")
    ap.add_argument("--seen", default=os.path.join("data", "seen-ids.txt"))
    ap.add_argument("--tracker", default="tracker.md")
    ap.add_argument("--profile", default="profile.local.yml")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    parts = []
    for p in a.inputs:
        if p == "-":
            parts.append(sys.stdin.read())
        else:
            with open(p, encoding="utf-8") as fh:
                parts.append(fh.read())
    cards = rows_from(stitch(parts))
    keys, tids = tracker_keys(a.tracker)
    try:
        with open(a.profile, encoding="utf-8") as fh:
            rules = TitleRules(fh.read())
    except FileNotFoundError:
        rules = TitleRules("")
    keep, counts, skipped = filter_cards(cards, read_seen(a.seen), keys, tids, rules)
    if a.json:
        print(json.dumps({"cards": len(cards), "open": keep, "dropped": counts, "skipped_by_title": skipped,
                          "title_filter": rules.active()}, ensure_ascii=False, indent=1))
        return 0
    if not rules.active():
        print("note: no role phrases in the profile; title prefilter is off", file=sys.stderr)
    for c in keep:
        flags = ("SAVED " if c["saved"] else "") + ("CLICK-FOR-ID " if c["needs_click"] else "")
        flags += {"always": "ALWAYS-INCLUDE ", "skill": "SKILL-MATCH "}.get(c["via"], "")
        print(f"{c['id'] or '-':>12}  {c['title']} @ {c['company']}  [{c['age'] or '?'}] {flags}".rstrip())
    dropped = ", ".join(f"{k} {v}" for k, v in counts.items() if v) or "none"
    print(f"{len(cards)} cards: open {len(keep)}; dropped {dropped}")
    if skipped:
        print("Skipped by title: " + "; ".join(f"{c['title']} @ {c['company']} ({c['reason']})" for c in skipped))
    return 0


if __name__ == "__main__":
    sys.exit(main())
