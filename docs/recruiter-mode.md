# Recruiter mode and search limits (details)

Moved out of the README to keep it short. Safety rules: `candidate-screening-safety.md`.

## Two modes: job seeker / recruiter

| | Job seeker (`/start-job-agent`) | Recruiter (`/screen-candidates`) |
|---|---|---|
| Input | Your CV | A job description and a local folder of candidate CVs |
| First gate | You approve proposed roles | You approve must-have / nice-to-have / exclusion criteria; no CV is read before |
| Output | Tailored ATS-friendly CVs, prepared applications, drafts, tracker | Ranked, explainable shortlist (IDs only, evidence quotes, gaps, 2-3 clarifying questions, warnings) |
| Human decides | Submit, consents, sending | Everything: the agent never rejects, ranks anyone out or contacts candidates |

Recruiter mode masks protected and irrelevant attributes (age, gender, nationality, photo, name origin, address...) before scoring, marks missing information `not_stated` instead of guessing, keeps candidate data local (`screening/` and `reports/` are git-ignored), and never sends mail, InMail or messages. Read `docs/candidate-screening-safety.md` (KVKK/GDPR, retention, candidate notice, bias and fair use) first. Try it on the fictional data: `python3 scripts/screen_report.py templates/screening/criteria.example.json templates/screening/scores`. Turkish prompt: `prompts/tr/screen-candidates.md`. Platform terms apply to any LinkedIn use.


## Limits you set

After approving roles, onboarding asks: (1) max search rounds per day (suggest 1), (2) per round, max listings evaluated and max applications/drafts prepared (suggest 15 and 5), (3) approval style: one by one, or a batch summary. They are saved under `limits:` in `profile.local.yml` and the daily scan treats them as hard upper bounds: at a limit it stops and gives you a short summary. Submit, send and consent steps always need your explicit approval.


## Candidate sources (recruiter mode)

After you approve the criteria, choose one or more sources and a per-round candidate cap for each (suggest 30):

1. **Local CV folder.**
2. **Gmail:** application mails matching a filter you give. Matching threads are listed first; attachments are downloaded to the git-ignored `screening/inbox/` only after your approval. Read + create-draft only; no sending, deleting or labeling (labeling is optional, off by default, needs approval).
3. **LinkedIn:** only applicants to postings you published yourself (your Applicants screen) or profile URLs you give. No bulk collection from search results, no messages, InMail or connection requests. LinkedIn's terms restrict automation; the risk is yours.

Each candidate gets a category (strong match / possible / needs clarification / does not meet criteria) with an evidence quote. The last one is only a suggestion; the agent rejects nobody and contacts nobody. Reply drafts are drafts only. Masking applies to every source. Fictional samples: `templates/screening/`.


## LinkedIn search assistant (recruiter sub-mode)

A deliberately small, user-directed way to find leads: after you approve the criteria, the agent drafts people-search queries (keywords + location) for your approval; for each approved query it runs ONE search in your own open browser and reads only the first result page text (headline, current role line, location, connection degree; no names stored). Limits: results per round (suggest 10, hard maximum 25), queries per day (suggest 3). No paging, no profile visits, no connection requests, messages, InMail, follows or lead saving. You get a headline-level shortlist; profile deepening happens only for candidate IDs you pick in chat, one by one, with masking. It stops at once on any CAPTCHA, warning, verification or limit text. See `prompts/screening/linkedin-search-assistant.md`.

**Honest limitations.** Headline text is weak evidence: years of experience and skills are mostly invisible, so the best category is "possible / needs clarification" and "strong match" is only possible after a deepening you chose. Results depend on LinkedIn's ranking and on your network visibility, so it will miss people. LinkedIn's terms prohibit automated bulk collection and accounts can be restricted; this mode is small on purpose and the risk stays with you. Leads are third-party personal data (KVKK/GDPR): minimum fields, local git-ignored folder, no sharing, delete when done. Not tested against the live site. See `docs/candidate-screening-safety.md`. Fictional samples: `templates/screening/linkedin-search-results.example.md`, `report.linkedin-search.example.md`.

