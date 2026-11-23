# Roadmap

Order matters: finish what is below "Now" before starting "Next".

## Now (done in this repo)
- Job-seeker mode: CV in, roles proposed and approved, limits, ATS-compliant role-tailored CV, LinkedIn + Gmail + tracker loop
- Recruiter mode: approved criteria, evidence-based categories, masking, CV folder / Gmail / own-postings sources, small LinkedIn search assistant
- Turkish prompts and README, safety and privacy docs, example mail drafts

## Next: tidy and harden
- Run every mode end to end on a real account and fix what breaks. Done on a supervised run (2026-11-23): job search and card filter, job-text cache and scoring, skill report, Easy Apply up to Review with the resume upload, #hiring post search, Gmail reply check and a mail draft. Still untested on a real account: the scheduled run (search subagent + `candidates_check.py --done-only`), `/linkedin-profile` guided edit, company portals (Workday sign-in stop), recruiter mode sources.
- Done: CV PDF build step (`scripts/build_cv_pdf.py`): Markdown to a single-column HTML page printed by the local headless Chrome; fails on more than 2 pages or no text layer. Before it, tailored CVs stopped at Markdown and forms got the general CV.
- Reply check: it only updates the Reply cell. Applications made by hand never get a row, and a row stays ⏳ after a "received" or rejection mail. List both in the report as tracker mismatches.
- Skill matching: a tool name such as "Azure DevOps" also counts as the practice "DevOps" (overlapping vocabulary entries).

## Found and fixed on the first real run (2026-11-23)
- LinkedIn's 2026 search-results layout: `linkedin_cards.js` read 0 cards (no `data-job-id`); it now reads `componentkey`. Posts have a new layout too: `linkedin_posts.js` replaces the ad hoc filter (Turkish `İ` matching, reposts).
- Skill report: company names and benefit sections (health insurance, training budget) counted as demand; "requirements analysis" did not map to Requirements Gathering.
- ATS check: `MM/YYYY – Günümüz` was flagged as a year-only date; two tests passed `--lang` wrongly and checked nothing.

## Done in "tidy and harden"
- More ATS checks: section order, length by experience level, bilingual CV pair (TR/EN) check, with unit tests (`python3 -m unittest discover -s tests`)
- Installable `hirepair` skill (`skills/hirepair`, `scripts/install_skill.py`). It is a thin entry point over this repo, not a self-contained bundle

- Read-only local tracker page with a "waiting for you" list (`scripts/tracker_view.py`); recruiter score reports verify evidence quotes against the masked CVs (`--masked`)
- Local UI phase 1: approval inbox + local server (`scripts/ui_server.py`, `scripts/ui_protocol.py`, `ui/`)

- Skills and profile: job texts cached in `data/jobs/`, `scripts/skill_gap.py` (market demand vs CV vs LinkedIn skills, CV-backed suggestions only), skill-based job search (`queries.skills`), skill-cluster queries in the recruiter LinkedIn assistant, `/linkedin-profile` (drafts + guided edit, the human presses Save), `profile_edit` inbox type
- UI performance: per-route ETags (a tracker change no longer invalidates the inbox), the page skips JSON parsing and re-rendering when the ETag is unchanged, polling backs off from 5 s to 20 s after 2 quiet minutes, the inbox view indexes decisions in one pass instead of one scan per item

## Next: performance, UI and flow (planned 2026-11)
Ordered by expected gain. The slowest part of a run is browser round trips and tokens, not the local code.

**Agent flow**
1. Done: `scripts/linkedin_cards.js` reads a results page in one call; `scripts/card_filter.py` drops handled cards before any click. Verified on a real supervised run (2026-11-23) after adapting to the new layout; a node test with the observed card shapes guards it.
2. Done: title prefilter in `card_filter.py` (exclusions, role phrases, `queries.jobs`, `queries.skills`, always-include companies bypass it); skipped titles are reported, not hidden.
3. Done: the read-only search subagent is the default in scheduled runs, with a fixed candidate-file format; `scripts/candidates_check.py` waits for it (`--done-only`), checks rows and query coverage, and prints the prepare queue within the limits.
4. Done: candidate files carry a profile hash; `scripts/rescore_queue.py` lists cached jobs scored with an older profile, and the search subagent re-scores them from `data/jobs/` without opening pages; `candidates_check.py` warns when a file was scored with a different profile.
5. Done (`scripts/skill_queries.py`: daily `--stale-only`, full report monthly; suggestions only). Monthly: `skill_gap.py` over the last 30 days of `data/jobs/`, propose `queries.skills` changes; drop skill queries that found nothing new for 7 days (same tally as #hiring queries).

**Local files**
6. Done: `ui_protocol.py compact`: rewrite `data/inbox.jsonl` / `decisions.jsonl` without consumed or expired items older than 30 days (the files are append-only and every poll reads them).
7. Done (`scripts/tracker_archive.py`; dedupe reads the archive too). Tracker archive: move rows older than 90 days with a final status to `tracker-archive.md`; stats read both.

**UI**
8. Done: Skills tab (read-only): `/api/skills` serves `data/skills-report.json` (written by `skill_gap.py --json`); demand bars with CV / LinkedIn flags, the three suggestion lists, and a link to each `profile_edit` item.
9. Done (`ui_protocol.py add --before`): profile drafts in the inbox show before → after with the CV evidence line; approving types nothing by itself, it only tells the agent which change to type next.
10. Done: tracker sort by date / fit, paginate above 200 rows, render only the visible page.
11. Done (`scripts/criteria_rarity.py`: per-criterion match counts from the score files, RARE vs UNCLEAR, vocabulary skills in masked CVs). Recruiter: run `skill_gap.py` over the masked CV pool to show which must-have skills are rare in the pool, as a hint to relax criteria (advisory, the human edits criteria).

## Later: small local web UI
The read-only tracker page above is the first step. A minimal local dashboard (no accounts, no cloud, data stays on your machine):
- Onboarding screen: upload CV, review proposed roles, approve or edit
- Tracker board: status columns, replies, tailored CV per row
- Recruiter view: criteria editor, ranked shortlist with evidence, candidate masking preview
- Approval inbox: every consent, send and submit step waiting for you, in one list

Design, flow, mockup and the communication protocol: [ui-design.md](ui-design.md) ([TR](ui-design.tr.md)), clickable preview [ui-mockup.html](ui-mockup.html).

Keep it a thin layer over the same Markdown/YAML files so the command-line flow keeps working.
