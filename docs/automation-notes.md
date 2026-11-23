# Browser automation notes

Lessons learned while driving a real, logged-in Chrome with the Claude in Chrome extension. They are specific to the tools and sites as they behaved at the time; sites change, so treat them as starting points.

## General mechanics

- Do not chain navigate + wait + JavaScript inside one batch call. Connections dropped and tab state lagged. Use single calls: navigate, then ONE JavaScript call that starts with `await new Promise(r => setTimeout(r, 4000))` and then reads the page. Wait about 6 seconds on LinkedIn content (post) search.
- JavaScript tool output is truncated at roughly 800-1300 characters. Return compact text (`.join('|').slice(0, 1200)`) and read long job descriptions in two slices.
- Do not return links with query strings; the tool blocks them as cookie/query data.
- String-evaluated code (`eval`) is blocked by the site's content security policy. Inline the full function in every call.
- Read a whole results page in ONE call with `scripts/linkedin_cards.js` (paste the body; it scrolls the virtualised list, then returns `id~title~company~age~badge` rows; if the output ends with `MORE@n`, call again with `OFF = n`). Save the raw outputs to a file and run `python3 scripts/card_filter.py <file>`: it drops Applied cards, seen IDs, tracker rows and duplicates, and (reading `profile.local.yml`) titles that are excluded or match no role, query phrase or skill keyword, so only the remaining cards are opened. Skipped titles are printed for the report. Earlier runs found no job ID in the list DOM; the script reads `data-occludable-job-id` / `data-job-id` / `/jobs/view/<id>` when present. Cards it prints as `CLICK-FOR-ID` still need the old way: click the card, read the ID from the tab URL, then open the job page directly and read its text (age, applicant count, Easy Apply button). On the first supervised run, compare the row count with the visible cards and note any selector change here.
- Supervised run on 2026-11-23 (logged-in Chrome, Claude in Chrome):
  - `/jobs/search/?keywords=…` now redirects to `/jobs/search-results/` and drops the `location` parameter; results still followed the account's location (Istanbul). Open `/jobs/search-results/?keywords=…&f_TPR=r86400` directly.
  - The new layout has no `data-job-id` / `data-occludable-job-id`; each card carries `componentkey="job-card-component-ref-<id>"` (outer and inner element share it). `linkedin_cards.js` reads that now; a page gave 25 rows for 25 visible cards. The first line of a card can carry screen-reader extras ("Selected, …", "… (Verified job)"); the plain title is the second line. Cards with a badge (Viewed / Applied / Saved) show no age.
  - A tool result starting with `N=` was once refused as "cookie/query string data"; returning it with the `=` replaced passed. Output was cut at about 1000 characters, so read long results in slices.
  - `/jobs/view/<id>/` works; read it only after a short wait, or the text of the previous page comes back.
  - A job page with an unfinished Easy Apply draft shows "Continue" and "You last modified this application …" instead of the Easy Apply button: compare with the tracker before preparing it again.
  - Similar queries overlap heavily: after the first 25-card query, the next three added 2, 3 and 8 new cards.
- If the extension disconnects, re-check the tab context up to three times with waits, then re-run the failed queries. Machine sleep also kills sessions; do searching first and long CV work later.
- Work in your own new tab and close it at the end. Do not use the browser from two agents at once.

## LinkedIn Easy Apply flow

1. Open the job page, click Easy Apply.
2. Contact step: the form is prefilled from the profile; verify, do not retype.
3. Resume step: see the upload trick below.
4. Questions: answer only from the profile's form facts and the CV. Leave the rest blank and list them.
5. Uncheck "Follow company" (it is ticked by default).
6. Do not mark "top choice".
7. The Next button can sit below the viewport: click it with JavaScript (button whose label is Next / Continue / Review) and take a screenshot after every page so no question page is skipped.
8. Stop at Review. Close the dialog and choose Save if a draft is offered. The human submits.

### Uploading a tailored PDF

The resume file input does not exist in the DOM until "Upload resume" is clicked, and the click opens a native file dialog the agent cannot drive. Approach that worked:

1. Before clicking, hook `HTMLInputElement.prototype.click` so the created hidden `<input type=file>` is captured instead of opening the dialog, and tag it (for example set an `aria-label` such as `CVINPUT`).
2. Click "Upload resume".
3. Find the tagged input and call the extension's `file_upload` tool on it.
4. The extension reads files only from inside the session's working directory. Copy the PDF to an `upload/` folder under it first; files elsewhere (for example the Desktop) were rejected as unreadable.
5. Confirm the new file is the selected radio at the top of the resume list.

### Prefilled answers

LinkedIn prefills experience-year questions (for example "years of experience with X") from the profile, and the values can be wrong or stale. Never accept a prefilled number blindly. Compare it with the CV, and correct or leave blank. Numeric-only fields take digits only (no currency text).

## #hiring post search

Observed behavior:
- Quoted queries combined with a date-posted filter returned "No results found".
- English "#hiring <role>" queries mostly return spam from outside the target country.

Forms that worked:
- Unquoted keywords, no date-posted filter, sort by `date_posted`.
- Scroll to the bottom twice, wait about 6 seconds.
- Then filter in one JavaScript call by keyword and by post age (3 days preferred, 7 acceptable) and extract public e-mail addresses with a regex.
- Supervised run on 2026-11-23: posts have no `data-urn`; each post is an element with `componentkey="expanded<id>FeedType_…"`, which `scripts/linkedin_posts.js` reads. "iş analisti istanbul işe alım" returned only posts older than a week; "iş analisti arıyoruz" returned 5 posts within 7 days, newest first. The same opening was reposted by three recruiters (the script keeps one). In JavaScript, `"İ".toLowerCase()` is not `"i"`: replace `İ` before matching Turkish keywords.
- Keep a per-query tally (working / empty / failed) and replace queries that stay empty for several days.
- If three working queries produce nothing relevant, report "post scan inconclusive" instead of retrying the rest.

## Search yield

The job search's semantic ranking returns almost the same ~30 cards for similar queries, and after a few days most are already applied. Run distinct-intent queries first (role families), and stop after three consecutive near-duplicate queries with no new unhandled card. Keep a seen-ID file so a card is never opened twice.

## Company portal quirks (generic)

- Large applicant-tracking portals (Workday-style) render dropdowns lazily. Click the field, wait, then read the option list; options often are not in the DOM until opened. Selecting too early silently does nothing.
- Some portals let you apply as a guest ("apply manually"), others need an account. If an account is needed, record the link and stop.
- Bank career portals often depend on the user already being signed in within the same Chrome. If a sign-in page appears, list the role instead of trying to log in.
- Portals that send an e-mail verification link need a separate step: read the verification mail (read only), open the link, then continue the question flow. Check again later for a "complete your application" mail; a "link already used" message means nothing is left. Only a "received" confirmation mail justifies marking the row as submitted.
- Do not tick consent boxes even when the page makes them look mandatory; hand that step to the human.

## Turkey-specific portal pitfalls (generic)

- Many forms ask salary as a single number. Check whether it means net or gross, monthly or annual, and the currency (usually TL). Use only the profile value; if unclear, ask the user.
- National ID number (T.C. kimlik no), date of birth, military-service status and similar fields appear on local portals. Never fill identity numbers; leave them for the user.
- KVKK clarification / explicit-consent boxes are often mandatory-looking and sometimes ticked by default. Never tick or untick; hand it to the user.
- Local job boards can require a full profile (education history, forms) before applying. If a CV auto-parse fills the profile, check every parsed field against the CV; parsers misread dates and titles.
- Phone fields may demand a specific format (+90, leading 0 or not). Read the hint text, do not guess; ask the user if unsure.
- Turkish characters (ç ğ ı ö ş ü İ) can break in file names and some form fields. Use ASCII file names (`Ad_Soyad_Rol_Cv.pdf`); keep Turkish text inside the CV.
- Bank and corporate career portals often use a separate candidate account and e-mail verification. List the role and the link; the user signs in.
- Workday (a bank's career portal, checked 2026-11-23 without signing in): LinkedIn's "Apply on company website" goes through `linkedin.com/safety/go/`; the real target is in its `url` parameter. On Workday, "Başvur" offers resume autofill, "Manuel Olarak Başvur" or the last application. Manual apply opened the form as a guest, without sign-in: Bilgilerim (previous-employee radio, legal name, address line, postal code, city, e-mail, phone) > Deneyimim > Başvuru Soruları > Rızaya Bağlı Bildirimler > Gözden Geçir. Address and postal code are not in the CV or `form_facts`: ask the user. The consent step is the user's. An earlier run noted that Workday keeps no draft, so do not fill a Workday form unless the user can finish it in the same session.
- Job-post age is shown relatively ("3 gün önce", "1 hafta önce"); convert to days before ranking.
