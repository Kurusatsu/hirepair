---
name: hirepair
description: Hirepair job-search and candidate-screening agent. Use when the user wants to find and prepare jobs from their CV (job-seeker mode), search jobs or candidates by skills, see which skills job listings ask for and get CV-backed LinkedIn skill and profile suggestions (profile mode), screen candidate CVs against a job description (recruiter mode), or runs /hirepair.
---

Hirepair works only inside a Hirepair folder: one that contains `CLAUDE.md`, `prompts/onboarding.md` and `docs/safety-rules.md`. If the current directory is not one, ask the user for its path and stop; do not search the disk for it.

1. Read `CLAUDE.md` in that folder and follow its rules.
2. Ask which mode, unless the user already said:
   - **Job seeker:** do what `.claude/commands/start-job-agent.md` says.
   - **Recruiter:** do what `.claude/commands/screen-candidates.md` says.
   - **Profile and skills:** do what `.claude/commands/linkedin-profile.md` says (skill demand from saved job texts, LinkedIn skill/headline/About suggestions, guided edit where the user presses Save).
3. Turkish users: use `prompts/tr/`.

Nothing runs before the user approves roles (or criteria) in chat. Passwords, IDs, CAPTCHAs, consent boxes, sending mail, final Submit and saving LinkedIn profile changes stay with the user. Skills are suggested only when the CV states them; market gaps are reported, never added.
