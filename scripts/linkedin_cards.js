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
  const first = document.querySelector('[data-occludable-job-id], [data-job-id]');
  let pane = first && first.parentElement;
  while (pane && pane !== document.body && pane.scrollHeight <= pane.clientHeight + 10) pane = pane.parentElement;
  if (pane && pane !== document.body) {
    for (let y = 0; y <= pane.scrollHeight; y += 600) { pane.scrollTop = y; await wait(250); }
    pane.scrollTop = 0;
  }
  const clean = s => (s || '').replace(/[~|\n\r]+/g, ' ').replace(/\s+/g, ' ').trim();
  const seen = new Set();
  const rows = [];
  for (const el of document.querySelectorAll('[data-occludable-job-id], [data-job-id]')) {
    let id = el.getAttribute('data-occludable-job-id') || el.getAttribute('data-job-id') || '';
    if (!id) {
      const a = el.querySelector('a[href*="/jobs/view/"]');
      const m = a && a.getAttribute('href').match(/\/jobs\/view\/(\d+)/);
      id = m ? m[1] : '';
    }
    const lines = (el.innerText || '').split('\n').map(clean).filter(Boolean);
    if (!lines.length) continue;
    // The title line is often repeated (visible text + "with verification"); keep the first.
    const title = lines[0].replace(/\s+with verification$/i, '');
    const rest = lines.filter(l => l !== lines[0] && !/with verification$/i.test(l));
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
