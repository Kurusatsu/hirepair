---
name: hirepair
description: Hirepair job-search and candidate-screening agent. Use when the user wants to find and prepare jobs from their CV (job-seeker mode) or screen candidate CVs against a job description (recruiter mode), or runs /hirepair.
---

Hirepair works only inside a Hirepair folder: one that contains `CLAUDE.md`, `prompts/onboarding.md` and `docs/safety-rules.md`. If the current directory is not one, ask the user for its path and stop; do not search the disk for it.

1. Read `CLAUDE.md` in that folder and follow its rules.
2. Ask which mode, unless the user already said:
   - **Job seeker:** do what `.claude/commands/start-job-agent.md` says.
   - **Recruiter:** do what `.claude/commands/screen-candidates.md` says.
3. Turkish users: use `prompts/tr/`.

Nothing runs before the user approves roles (or criteria) in chat. Passwords, IDs, CAPTCHAs, consent boxes, sending mail and final Submit stay with the user.
