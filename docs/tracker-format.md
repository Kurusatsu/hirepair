# Tracker format

The tracker is a single Markdown table. It is the shared memory between the daily scan, the reply check, and the human. Keep your real tracker out of git (`tracker.md` is in `.gitignore`); `templates/tracker.example.md` shows the shape with fake rows.

## Columns

| Column | Meaning |
|---|---|
| Date | ISO date the row was created (`YYYY-MM-DD`). |
| Company | Employer name. |
| Role | Job title as posted. |
| Fit | Score 1-5 plus a one-line reason with a quoted requirement that matches the CV. |
| Posting | Link to the listing or post. |
| CV | File name of the tailored PDF. |
| Cover note | File name of the short e-mail / message draft, or `-`. |
| Status | Emoji + short text, see legend. |
| Channel | How the application goes out, see below. |
| Reply | `-` for new rows; updated by the reply-check task (`Received <date>`, `Interview invite <date>`, `Rejected`, `Info requested`). |

The original author's tracker used Turkish column names (`Tarih | Şirket | Pozisyon | Uyum | İlan | CV | Ön yazı | Durum | Kanal | Yanıt`). The prompts and `scripts/` accept either; see the header handling in `scripts/tracker_stats.py`.

## Status legend

| Emoji | Meaning |
|---|---|
| ⏳ | Ready, waiting for the human's approval. |
| ✉️ | Mail draft created, not sent. |
| 💬 | Message draft written, not sent. |
| 🔗 | Company form exists; link recorded. |
| 🔒 | Sign-in or account needed; the human must do it. |
| ✅ | Submitted by the human (or confirmed received). |
| ⛔ | Rejected by the scan (hard exclusion) or dropped by the human. |

An agent never writes ✅ on its own for an application it did not see confirmed. For portals that send a confirmation mail, ✅ is set only after that mail was seen.

## Channel values

`LinkedIn form`, `Company form`, `Company portal`, `E-mail`, `LinkedIn message`, `Funding news`. If two channels are prepared, write both, for example `LinkedIn form + E-mail`.

## Rules

- One row per company + role. Deduplicate by company + role before adding a row.
- The agent only appends rows and edits the Status and Reply cells of existing rows.
- Never put passwords, ID numbers or full personal data in the tracker.

## Archive

`python3 scripts/tracker_archive.py` (`--dry-run` first) moves rows older than 90 days whose Status is ✅ or ⛔ to `tracker-archive.md` next to the tracker (git-ignored, same header). Rows waiting for the human never move. Dedupe (`card_filter.py`, `candidates_check.py`, `rescore_queue.py`) and `tracker_stats.py` read both files. The human runs it, or the agent after a yes in chat, since it rewrites the tracker.
