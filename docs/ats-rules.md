# ATS rules for tailored CVs

Every CV the agent tailors for a role MUST follow these rules. Check with `python3 scripts/ats_check.py <cv.md> --jd <job.txt>` before building the PDF. The keyword report only reports; it never adds anything.

1. **Single column.** No side bars, no multi-column layouts.
2. **No tables, icons, charts, graphics, photos or text boxes.** No critical information in headers or footers.
3. **Standard section headings.** EN: Professional Summary, Work Experience, Education, Skills, Certifications, Languages. TR: Özet, İş Deneyimi, Eğitim, Beceriler, Sertifikalar, Diller. Write the CV in the language of the posting.
4. **Standard dates:** `MM/YYYY – MM/YYYY` (or `MM/YYYY – Present` / `Günümüz`). One format everywhere.
5. **Selectable-text PDF**, not a scanned or image PDF. Test: you can select and copy the text.
6. **Standard font** (Arial, Calibri, Helvetica, Times New Roman), body 10-12 pt.
7. **Plain bullets** (a simple hyphen or round bullet). No arrows, check marks or emoji.
8. **Keywords:** use the posting's exact wording only for things that are already true and already stated in the original CV (for example "stakeholder management" instead of "working with business people", if the CV supports it). Never add a skill, tool, certificate or number that is not in the CV.
9. **Job title:** you may order or phrase the headline to match the posting's title only if it does not change the real title. Keep real employer titles exactly as they were (add a descriptor in the summary instead).
10. **File name:** `First_Last_Role_Cv.pdf` (ASCII letters, underscores), for example `Alex_Example_Business_Analyst_Cv.pdf`.
11. **Maximum 2 pages.**
12. **Contact details in the body** (top of page one): city, e-mail, phone, profile link.

13. **Section order:** Summary, Experience, Education, Skills, Languages (the checker warns on other orders).
14. **Length by level:** under 5 years of experience aim for 1 page (about 550 words or fewer); the 2-page cap applies to everyone.
15. **TR/EN pair:** if you keep both language versions, check them with `--pair`; dates, e-mail, section sequence and numbers must match. A translation never changes a fact.

If a rule conflicts with the truth of the CV, the truth wins: drop the keyword, not the fact.
