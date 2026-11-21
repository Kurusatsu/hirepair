# Roadmap

Order matters: finish what is below "Now" before starting "Next".

## Now (done in this repo)
- Job-seeker mode: CV in, roles proposed and approved, limits, ATS-compliant role-tailored CV, LinkedIn + Gmail + tracker loop
- Recruiter mode: approved criteria, evidence-based categories, masking, CV folder / Gmail / own-postings sources, small LinkedIn search assistant
- Turkish prompts and README, safety and privacy docs, example mail drafts

## Next: tidy and harden
- Run every mode end to end on a real account and fix what breaks (LinkedIn search assistant and Gmail source are only tested on fictional data)
- Package the commands as an installable Claude skill

## Done in "tidy and harden"
- More ATS checks: section order, length by experience level, bilingual CV pair (TR/EN) check, with unit tests (`python3 -m unittest discover -s tests`)

## Later: small local web UI
A minimal local dashboard (no accounts, no cloud, data stays on your machine):
- Onboarding screen: upload CV, review proposed roles, approve or edit
- Tracker board: status columns, replies, tailored CV per row
- Recruiter view: criteria editor, ranked shortlist with evidence, candidate masking preview
- Approval inbox: every consent, send and submit step waiting for you, in one list

Keep it a thin layer over the same Markdown/YAML files so the command-line flow keeps working.
