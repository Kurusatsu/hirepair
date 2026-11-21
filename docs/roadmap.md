# Roadmap

Order matters: finish what is below "Now" before starting "Next".

## Now (done in this repo)
- Job-seeker mode: CV in, roles proposed and approved, limits, ATS-compliant role-tailored CV, LinkedIn + Gmail + tracker loop
- Recruiter mode: approved criteria, evidence-based categories, masking, CV folder / Gmail / own-postings sources, small LinkedIn search assistant
- Turkish prompts and README, safety and privacy docs, example mail drafts

## Next: tidy and harden
- Run every mode end to end on a real account and fix what breaks (LinkedIn search assistant and Gmail source are only tested on fictional data)

## Done in "tidy and harden"
- More ATS checks: section order, length by experience level, bilingual CV pair (TR/EN) check, with unit tests (`python3 -m unittest discover -s tests`)
- Installable `hirepair` skill (`skills/hirepair`, `scripts/install_skill.py`). It is a thin entry point over this repo, not a self-contained bundle

- Read-only local tracker page with a "waiting for you" list (`scripts/tracker_view.py`); recruiter score reports verify evidence quotes against the masked CVs (`--masked`)

## Later: small local web UI
The read-only tracker page above is the first step. A minimal local dashboard (no accounts, no cloud, data stays on your machine):
- Onboarding screen: upload CV, review proposed roles, approve or edit
- Tracker board: status columns, replies, tailored CV per row
- Recruiter view: criteria editor, ranked shortlist with evidence, candidate masking preview
- Approval inbox: every consent, send and submit step waiting for you, in one list

Design, flow, mockup and the communication protocol: [ui-design.md](ui-design.md) ([TR](ui-design.tr.md)), clickable preview [ui-mockup.html](ui-mockup.html).

Keep it a thin layer over the same Markdown/YAML files so the command-line flow keeps working.
