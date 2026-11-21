# Browser automation notes

Lessons learned while driving a real, logged-in Chrome with the Claude in Chrome extension. They are specific to the tools and sites as they behaved at the time; sites change, so treat them as starting points.

## General mechanics

- Do not chain navigate + wait + JavaScript inside one batch call. Connections dropped and tab state lagged. Use single calls: navigate, then ONE JavaScript call that starts with `await new Promise(r => setTimeout(r, 4000))` and then reads the page. Wait about 6 seconds on LinkedIn content (post) search.
- JavaScript tool output is truncated at roughly 800-1300 characters. Return compact text (`.join('|').slice(0, 1200)`) and read long job descriptions in two slices.
- Do not return links with query strings; the tool blocks them as cookie/query data.
- String-evaluated code (`eval`) is blocked by the site's content security policy. Inline the full function in every call.
- Job IDs are not in the search-list DOM. Click the card, read the ID from the tab URL, then open the job page directly and read its text (age, applicant count, Easy Apply button).
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
