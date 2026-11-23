// Read every job card on a LinkedIn job-search results page in ONE JavaScript call.
// Paste the whole body into the browser JavaScript tool (eval is blocked by the site's CSP).
// Set OFF to 0 first; if the output ends with "MORE@<n>", call again with OFF = n.
// Output: "N=<cards>;" then "id~title~company~age~badge" rows joined by "|". No links, no query strings.
// Selectors are generic on purpose (LinkedIn's class names change); check the row count against the
// visible cards on the first supervised run and note any change in docs/automation-notes.md.
(async () => {
  const OFF = 0;
  const LIMIT = 1100;
  const wait = ms => new Promise(r => setTimeout(r, ms));
  await wait(4000);
  // The results list is virtualised: scroll its pane to the bottom in steps so every card renders.
  // 2026 "search-results" layout: cards carry componentkey="job-card-component-ref-<id>" (outer and inner
  // element share it; document order puts the outer one, with the full text, first).
  const SEL = '[data-occludable-job-id], [data-job-id], [componentkey^="job-card-component-ref-"]';
  const first = document.querySelector(SEL);
  let pane = first && first.parentElement;
  while (pane && pane !== document.body && pane.scrollHeight <= pane.clientHeight + 10) pane = pane.parentElement;
  if (pane && pane !== document.body) {
    for (let y = 0; y <= pane.scrollHeight; y += 600) { pane.scrollTop = y; await wait(250); }
    pane.scrollTop = 0;
  }
  const clean = s => (s || '').replace(/[~|\n\r]+/g, ' ').replace(/\s+/g, ' ').trim();
  const seen = new Set();
  const rows = [];
  for (const el of document.querySelectorAll(SEL)) {
    const ck = (el.getAttribute('componentkey') || '').match(/^job-card-component-ref-(\d+)$/);
    let id = el.getAttribute('data-occludable-job-id') || el.getAttribute('data-job-id') || (ck ? ck[1] : '');
    if (!id) {
      const a = el.querySelector('a[href*="/jobs/view/"]');
      const m = a && a.getAttribute('href').match(/\/jobs\/view\/(\d+)/);
      id = m ? m[1] : '';
    }
    const lines = (el.innerText || '').split('\n').map(clean).filter(Boolean);
    if (!lines.length) continue;
    // The title line is often repeated with screen-reader extras ("Selected, X (Verified job)",
    // "X with verification"); when the second line is contained in the first, it is the plain title.
    const lead = lines[0].replace(/\s+with verification$/i, '');
    const title = lines.length > 1 && lines[1] !== lead && lead.includes(lines[1]) ? lines[1] : lead;
    const rest = lines.filter(l => l !== lines[0] && l !== title && !/with verification$/i.test(l));
    const company = rest[0] || '';
    const age = lines.find(l => /\b(ago|önce)\b/i.test(l)) || '';
    const badge = lines.find(l => /^(Applied|Başvuruldu|Saved|Kaydedildi|Viewed|Görüntülendi)\b/i.test(l)) || '';
    const key = id || title + '@' + company;
    if (seen.has(key)) continue;
    seen.add(key);
    rows.push([id, title.slice(0, 60), company.slice(0, 40), age.slice(0, 20), badge.split(' ')[0]].join('~'));
  }
  const out = rows.join('|');
  const part = out.slice(OFF, OFF + LIMIT);
  return 'N=' + rows.length + ';' + part + (OFF + LIMIT < out.length ? 'MORE@' + (OFF + LIMIT) : '');
})()
