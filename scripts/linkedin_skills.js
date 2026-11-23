// Read the skills on your own LinkedIn profile in ONE JavaScript call. Read only: it clicks nothing.
// Open https://www.linkedin.com/in/me/details/skills/ (the "All" tab), wait ~5 s, paste this body.
// It scrolls until no new skills load, then returns "N=<skills>;" and the names joined by "|"
// (if the output ends with "MORE@<n>", call again with OFF = n). Save one name per line to
// data/linkedin-skills.local.txt and run: python3 scripts/skill_gap.py --jobs data/jobs --linkedin data/linkedin-skills.local.txt
// 2026 layout: each skill is an element with componentkey "com.linkedin.sdui.profile.skill(...)";
// its first text line is the name, the next lines are where it is used (jobs, projects, endorsements).
(async () => {
  const OFF = 0;
  const LIMIT = 1100;
  const SEL = '[componentkey^="com.linkedin.sdui.profile.skill("]';
  if (OFF > 0 && window.__liskills) {
    const out = window.__liskills;
    return 'N=' + out.split('|').length + ';' + out.slice(OFF, OFF + LIMIT) + (OFF + LIMIT < out.length ? 'MORE@' + (OFF + LIMIT) : '');
  }
  const wait = ms => new Promise(r => setTimeout(r, ms));
  let last = -1;
  for (let i = 0; i < 15; i++) {
    window.scrollTo(0, document.body.scrollHeight);
    await wait(1200);
    const n = document.querySelectorAll(SEL).length;
    if (n === last) break;
    last = n;
  }
  const names = [];
  for (const e of document.querySelectorAll(SEL)) {
    const name = ((e.innerText || '').split('\n').map(s => s.trim()).filter(Boolean)[0] || '').replace(/[|~]/g, ' ').replace(/\s+/g, ' ').trim();
    if (name && !names.includes(name)) names.push(name);
  }
  window.__liskills = names.join('|');
  const out = window.__liskills;
  return 'N=' + names.length + ';' + out.slice(0, LIMIT) + (LIMIT < out.length ? 'MORE@' + LIMIT : '');
})()
