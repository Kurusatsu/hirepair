# Scripts

Every helper in `scripts/`. The prompts call them for you; you can also run them by hand. Python scripts use the standard library only and run from the project folder. Each prints `--help`. [Türkçe](scripts.tr.md)

## Browser scripts (paste into the browser JavaScript tool)

The agent pastes the whole file body into one JavaScript call on the right LinkedIn page. They read the page and click nothing except paging buttons. When the output ends with `MORE@n`, call again with `OFF = n`. Layout notes: [automation-notes.md](automation-notes.md).

| Script | Page | Returns |
|---|---|---|
| `linkedin_cards.js` | Job search results (`/jobs/search-results/`) | One row per card: job ID, title, company, age, badge (Applied, Saved, Viewed) |
| `linkedin_posts.js` | Content search for #hiring posts | Per post: age in days, keyword match, public e-mail, start of text; reposts dropped |
| `linkedin_myjobs.js` | LinkedIn's job tracker (`/jobs-tracker/?stage=applied`, `interview`, `draft`, `clicked_apply`, `saved`) | Per job: ID, age, stage, signals (viewed, downloaded, closed), title, company |
| `linkedin_skills.js` | Your profile skills (`/in/me/details/skills/`) | Skill names |

## Job seeker

| Command | What it does |
|---|---|
| `python3 scripts/card_filter.py data/cards-<date>.txt` | Drops cards you applied to, saw before or track already, and titles outside your roles; prints the cards to open |
| `python3 scripts/candidates_check.py data/candidates-<date>.md [--done-only]` | Checks the search subagent's candidate file and prints the prepare queue within your limits |
| `python3 scripts/rescore_queue.py [--fingerprint]` | Lists cached jobs to re-score after your profile changed, without opening pages |
| `python3 scripts/ats_check.py cv.md --jd job.txt [--pair cv_en.md]` | ATS rules and missing keywords for a tailored CV; never adds anything |
| `python3 scripts/build_cv_pdf.py data/cv/First_Last_Role_Cv.md` | Prints the CV to a selectable-text PDF with your local Chrome; refuses more than 2 pages |
| `python3 scripts/skill_gap.py --jobs data/jobs --cv cv.local.md --linkedin data/linkedin-skills.local.txt [--json]` | Skill demand in saved job texts vs your CV and LinkedIn skills; `--json > data/skills-report.json` feeds the Skills tab |
| `python3 scripts/skill_queries.py [--stale-only]` | Suggests adding or dropping skill-based search queries; never edits the profile |

## Tracker

| Command | What it does |
|---|---|
| `python3 scripts/linkedin_sync.py data/myjobs-<date>.txt [--manual data/manual-candidates.md]` | Turns the job tracker output into events; saved jobs join the manual list |
| `python3 scripts/reply_reconcile.py check EVENTS --write-replies --inbox` | Matches mail and LinkedIn events with tracker rows: writes Reply cells, proposes Status fixes and missing rows as approval cards |
| `python3 scripts/reply_reconcile.py apply` | Applies the tracker fixes you approved (or edited); a row that changed meanwhile is left alone |
| `python3 scripts/tracker_stats.py [tracker.md]` | Counts by status and channel, archive included |
| `python3 scripts/tracker_archive.py [--dry-run]` | Moves closed rows older than 90 days to `tracker-archive.md` |
| `python3 scripts/tracker_view.py` | A read-only local page with a "waiting for you" list (no approvals) |

## Local UI

| Command | What it does |
|---|---|
| `python3 scripts/ui_server.py [--port 8765]` | The local page on 127.0.0.1: Today, Waiting for you, Tracker, Skills, Recruiter |
| `python3 scripts/ui_protocol.py add / decisions / consume / compact` | The agent's side of the approval inbox; `compact` keeps the files small |

## Recruiter

| Command | What it does |
|---|---|
| `python3 scripts/screen_report.py CRITERIA.json SCORES_DIR [--masked MASKED_DIR]` | Ranked, advisory shortlist; evidence quotes checked against the masked CVs |
| `python3 scripts/criteria_rarity.py CRITERIA.json SCORES_DIR [--masked MASKED_DIR]` | How many candidates meet each must-have: RARE (most lack it) or UNCLEAR (most do not say) |

## Setup

| Command | What it does |
|---|---|
| `python3 scripts/install_skill.py [--uninstall]` | Links `skills/hirepair` into `~/.claude/skills` so `/hirepair` works from any folder |
| `python3 -m unittest discover -s tests` | All tests; the browser scripts are tested in Node when it is installed |
