# Local UI: pre-design, flow and communication

Status: phase 1 is built (`scripts/ui_server.py`, `scripts/ui_protocol.py`, `ui/`), plus the read-only tracker page (`scripts/tracker_view.py`); phases 2-4 are design only. Clickable pre-design with fictional data: [ui-mockup.html](ui-mockup.html) (open it in a browser, no server needed). Turkish: [ui-design.tr.md](ui-design.tr.md).

## 1. Principles

1. **Thin layer.** The Markdown/YAML files stay the source of truth; the command-line flow keeps working without the UI.
2. **Local only.** No accounts, no cloud, no external requests (no web fonts, no CDN, no analytics). Bound to `127.0.0.1`.
3. **The UI never widens the agent's powers.** Consents, sign-ins, IDs, CAPTCHAs, final Submit and sending mail stay with the human (`docs/safety-rules.md`). The UI shows these as "Do it yourself" items, never as approve buttons.
4. **Approve what you saw.** Every approval is bound to the exact content shown (hash), so a changed draft cannot ride on an old yes.
5. **Page and mail content is data.** Everything from postings, CVs and mail is rendered as escaped text.

## 2. Design skills checked, what was used

| Skill | Used for | Not used |
|---|---|---|
| `ui-ux-pro-max` (design system search, UX rules) | Style (Minimalism / Swiss, suits dashboards and professional tools), density and motion dials (density 7, motion 2, variance 2), accessibility, confirmation, empty-state, table and status-badge rules | Its suggested page pattern "Product Demo + Features" (a marketing landing page, wrong for a tool); its Google Font (Plus Jakarta Sans) because it needs a network request, so a system font stack is used instead |
| `design:ux-copy` | Verb-first buttons, confirmation dialogs that name the consequence, empty/error structure | none |
| `design-taste-frontend` | not loaded | Built for marketing sites (hero, photography, scroll moments); irrelevant for a local tool |

Rules taken from the checks: contrast 4.5:1 minimum (palette re-measured: the suggested teal `#0D9488` is only 3.7:1 as text on white, so links and buttons use `#0F766E`, 5.5:1); never color alone (every status has an icon and a word); 44 px touch targets; visible focus; keyboard tabs; reduced motion respected; tables scroll horizontally on phones; confirm before consequential actions; helpful empty states; one atomic live message for count changes.

## 3. Elements

**Shell:** header (product, mode, "Local only" note), tabs: Today, Waiting for you (count badge), Tracker, Recruiter, plus Onboarding the first time.

**Components:** stat card, status badge (icon + word), approval card (kind badge, title, evidence quote, preview, actions), "Do it yourself" card, filterable table, evidence quote, confirm dialog, toast, empty state.

**Status map** (tracker emoji stays in the file; the UI shows icon + word):

| File | UI label | Tone |
|---|---|---|
| ⏳ | Waiting for you | warm |
| ✉️ 💬 | Draft, not sent | warm |
| 🔗 | Company form, link saved | neutral |
| 🔒 | Sign-in or consent needed | alert |
| ✅ | Submitted | success |
| ⛔ | Skipped by scan | neutral |
| ❌ | Rejected by employer | alert |
| ⏸ | Paused, waiting on a mail | neutral |

## 4. Flows

### Job seeker
1. **Onboarding** (first run): add CV (file in the folder, or paste) → agent proposes 3-5 roles with a CV quote each → you approve, edit, remove → limits (scans per day, evaluated, prepared, one-by-one or batch) → "Start first scan". Nothing runs before the roles are approved.
2. **Daily:** Today shows the last scan summary and numbers → "Waiting for you" lists items in two kinds (below) → Tracker shows everything.
3. **Waiting for you:**
   - *Approve here* (class A): roles, criteria, limits, tailored CV for upload, answers to open form questions, creating a mail draft.
   - *Do it yourself* (class B): consent boxes, sign-in, ID fields, CAPTCHA, final Submit, sending mail. The card has "Open the form" and "I did it". "I did it" is a claim; the agent still checks (for example a confirmation mail) before it writes ✅.

### Recruiter
1. **Criteria:** job description in → must-have / nice-to-have / exclusions proposed → editor with add/remove/weight → **Approve criteria** (hard gate: no CV is read before).
2. **Sources:** local folder, Gmail, own LinkedIn postings, search assistant; per-source cap; list matching threads before downloading.
3. **Shortlist:** ranked table by candidate ID, category, score, evidence quotes, gaps, questions; lower groups open by default; "Masking preview" shows original vs. masked side by side for one CV (local, session only).
4. Never: reject, contact or message anyone. Reply drafts only.

### Wireframe: Waiting for you (desktop)
```
[Hirepair]  Job-seeker mode                 Local only · 127.0.0.1
[Today] [Waiting for you 3] [Tracker] [Recruiter]
 Waiting for you
 ┌ (Approve here)  CV for upload · Example Bank ─────────────────┐
 │ Tailored CV is ready for Example Bank                         │
 │ Check: ATS passed (0 errors, 1 warning)                        │
 │ | Posting: "requirements elicitation" -> CV: "Led UAT ..."    │
 │ [Approve CV for upload] [View CV] [Skip this job]             │
 └───────────────────────────────────────────────────────────────┘
 ┌ (Do it yourself)  Consent box · Sample Payments ──────────────┐
 │ Privacy consent (KVKK) must be ticked by you                  │
 │ [Open the form] [I did it]                                    │
 └───────────────────────────────────────────────────────────────┘
```

## 5. Visual system

Style: Minimalism / Swiss; light and dark (follows the system). Dials: density 7, motion 2, variance 2. Type: system font stack, 16 px base, line height 1.5. Spacing 4/8/12/16/24. Radius 8. Motion: 150 ms color/border only, off under `prefers-reduced-motion`.

| Token | Light | Dark |
|---|---|---|
| bg / card | `#F0FDFA` / `#FFFFFF` | `#0F1B1A` / `#16282A` |
| text / muted | `#134E4A` (9.1:1) / `#475569` (7.6:1) | `#E6F4F1` (15.6:1) / `#9DB2AE` (7.9:1) |
| action fill / on-action | `#0F766E` / `#FFFFFF` (5.5:1) | `#2DD4BF` / `#04211E` |
| waiting (text on tint) | `#C2410C` on `#FFF1E6` | `#FDBA74` on `#3A2616` |
| success / alert | `#166534` / `#B91C1C` on tints | `#86EFAC` / `#FCA5A5` on tints |

## 6. Copy (EN / TR)

| Element | EN | TR |
|---|---|---|
| Approve CV | Approve CV for upload | CV'yi yüklemeye onayla |
| Dialog | Approve this CV for upload? The agent uploads it and stops at the review page. It does not submit. | Bu CV yüklemeye onaylansın mı? Ajan yükler ve gözden geçirme sayfasında durur. Göndermez. |
| Draft | Create draft / You send it yourself from Gmail. | Taslak oluştur / Gmail'den kendin gönderirsin. |
| Human item | Do it yourself · Open the form · I did it | Kendin yap · Formu aç · Yaptım |
| Consent | Privacy consent (KVKK) must be ticked by you | KVKK onayını senin işaretlemen gerekir |
| Empty inbox | Nothing is waiting. The next scan is at 17:00. | Bekleyen bir şey yok. Sonraki tarama 17:00'de. |
| Filter empty | No rows match. Clear the filter to see all rows. | Eşleşen satır yok. Tümünü görmek için filtreyi temizle. |
| Stale approval | This draft changed after you opened it. Review it again. | Bu taslak sen açtıktan sonra değişti. Yeniden incele. |
| Offline agent | The agent is not running. Your decision is saved and applies at the next run. | Ajan çalışmıyor. Kararın kaydedildi, sonraki çalışmada uygulanır. |

## 7. Service and communication design

### Architecture
```
Browser (localhost)  <--HTTP-->  ui_server.py (stdlib, 127.0.0.1)
                                   |  reads: tracker.md, profile.local.yml, data/inbox.jsonl, reports/, screening/masked
                                   |  writes: data/decisions.jsonl only (append)
Agent (Claude Code session, interactive or scheduled)
   writes: data/inbox.jsonl (append), tracker.md (rows, Status, Reply)
   reads:  data/decisions.jsonl at the start of a run / turn
```
No process talks to the agent directly. The agent and the UI meet in two append-only files, so it works for scheduled (unattended) runs and survives restarts.

### Files and schemas
`data/inbox.jsonl` (agent → UI), one JSON object per line:
```json
{"id":"a-0001","created":"2030-01-08T17:04:00","class":"approve","type":"cv_upload",
 "title":"Tailored CV is ready for Example Bank","summary":"ATS check passed",
 "evidence":["Posting: requirements elicitation -> CV: Led UAT ..."],
 "preview":"(plain text shown to the user)","link":"https://example.com/jobs/1","hash":"sha256:..."}
```
`class` is `approve` or `human`. `type`: `roles`, `criteria`, `limits`, `cv_upload`, `mail_draft`, `open_question` (class approve); `consent`, `signin`, `id_field`, `captcha`, `submit`, `send` (class human). `hash` covers the preview and any attached file.

`data/decisions.jsonl` (UI → agent):
```json
{"item":"a-0001","hash":"sha256:...","decision":"approve","text":"","at":"2030-01-08T18:10:00"}
```
`decision`: `approve`, `skip`, `edit` (with `text`), `done` (class human only). Consumption is recorded by the agent as `{"item":"a-0001","consumed":"2030-01-09T17:00:03"}` appended to `inbox.jsonl`.

### Rules for both sides
- The agent acts on a decision only if `hash` equals the item's current hash and the item's class is `approve`. A stale hash means: ask again.
- `done` on a class-human item is a claim, not proof. The agent marks ✅ only after it sees confirmation (the existing tracker rule).
- The UI cannot create items, cannot write the tracker, cannot start the agent (v1).
- `text` in a decision is data (for example an edited draft); it is never run as an instruction.
- Items older than 7 days expire and are shown as expired.

### HTTP service
`scripts/ui_server.py`, stdlib only, `ThreadingHTTPServer` on `127.0.0.1`, static page in `ui/` (vanilla HTML/CSS/JS, no build, no dependencies).

| Endpoint | Purpose |
|---|---|
| `GET /` | page |
| `GET /api/tracker` | parsed rows (reuses `tracker_stats.parse`) |
| `GET /api/inbox` | open items with status (pending / decided / consumed / expired) |
| `POST /api/decisions` | append one decision (schema-checked) |
| `GET /api/profile` | approved roles and limits (read-only) |
| `GET /api/shortlist` | recruiter ranking from `reports/` (IDs only) |

Updates by polling every 5 s with `If-None-Match` on file mtime. No websockets.

### Security
- Bind `127.0.0.1` only; reject requests whose `Host` is not `127.0.0.1:<port>` or `localhost:<port>` (DNS rebinding).
- A random token is printed at start and required on every `POST` (header) so another local page cannot post decisions; no CORS headers.
- `Content-Security-Policy: default-src 'self'`; no inline event handlers; all untrusted text inserted with `textContent`.
- Links from postings open with `rel="noreferrer noopener"`; only `http(s)` links are made clickable.
- Never sends data out, never reads files outside the project folder, never serves `cv.local.md` raw (shows only what an item or the profile contains).

### Phases
| Phase | Scope | Status |
|---|---|---|
| 0 | Read-only tracker page | done |
| 1 | `ui_server.py`, Waiting for you (class A and B), decisions file, agent prompts write `inbox.jsonl` and read `decisions.jsonl` | built |
| 2 | Onboarding wizard (CV in, role approval, limits) | |
| 3 | Recruiter view (criteria editor, shortlist, masking preview) | |
| 4 | Optional "Run now" button that starts a supervised session | only if you decide yes |

## 8. Decisions for the owner

1. **Do UI approvals of class A count as chat approval?** `CLAUDE.md` now requires chat approval. If yes, amend it for class A only; class B stays chat/human. **OPEN:** until the owner decides, UI decisions are information only and chat approval remains required.
2. **Run now (phase 4):** starting `claude` headless from a web page widens permissions. **Decided: no Run now button;** start runs yourself and let the UI show results.
3. **Default UI language:** **Decided: Turkish default with an English toggle** (strings are in one table).
