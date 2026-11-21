# Lessons learned from real runs

Mistakes made in live supervised runs, turned into rules.

1. **Prefilled "years of experience" fields are not trusted.** LinkedIn Easy Apply can prefill them from the profile or an earlier application. Verify each against the CV and `form_facts`; fix or leave blank and ask the user. Never accept the prefill.
2. **Wrong CV auto-selected.** The form may preselect an older uploaded CV. On every form, read the displayed file name and confirm it is the tailored `First_Last_Role_Cv.pdf` for this job before Next.
3. **"Follow company" is ticked by default.** Untick it.
4. **File upload:** the resume input is created on click and opens a native dialog. Capture the hidden file input with the click hook and use `file_upload` (`docs/automation-notes.md`). The file must sit inside the working folder.
5. **Numeric question not derivable from the CV** (years of a tool, notice period, salary): ask the user in chat; do not estimate. Save the answer to `form_facts` if they agree.
6. **Tracker after every application:** one row plus status emoji immediately, not at the end of the run.
7. **Daily cap and short summary:** stop at `limits.daily_prepared_cap`; end with a short summary (prepared, needs you, skipped).
8. **Salary expectation only from the profile.** If the profile has no value, ask; never invent one. State whether the number is net or gross, monthly or annual, and the currency.
9. **Consent, KVKK/GDPR, IDs, passwords, CAPTCHAs** always stay with the user.
