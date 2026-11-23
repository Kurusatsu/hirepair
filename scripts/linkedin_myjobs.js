// Read LinkedIn's own job tracker (My jobs) in ONE JavaScript call per batch of pages.
// Open https://www.linkedin.com/jobs-tracker/?stage=applied (or saved, in_progress, interview), wait ~5 s,
// paste this body. It reads the open tab page by page (newest application first) until rows are older
// than DAYS or MAX_PAGES pages were read, and keeps the rows in the page.
// Output: "N=<rows>;" then "id~days~stage~signals~title~company" rows joined by "|". If the output ends
// with "MORE@<n>", call again with OFF = n: later calls only slice the rows already read.
// days: age of the application (applied tab) in days, -1 if unknown. signals, joined by "+": viewed
// (Application viewed), downloaded (Resume downloaded), closed (No longer accepting applications),
// heard_yes / heard_no (your own answer to "Did you hear back?"). No links, no query strings.
// Then: python3 scripts/linkedin_sync.py <saved output file> (see that script).
(async () => {
  const OFF = 0;
  const DAYS = 14;
  const MAX_PAGES = 5;
  const LIMIT = 1100;
  if (OFF > 0 && window.__myjobs) {
    const out = window.__myjobs;
    return 'N=' + out.split('|').length + ';' + out.slice(OFF, OFF + LIMIT) + (OFF + LIMIT < out.length ? 'MORE@' + (OFF + LIMIT) : '');
  }
  const wait = ms => new Promise(r => setTimeout(r, ms));
  const stage = (new URLSearchParams(location.search).get('stage') || 'saved').toLowerCase();
  const UNIT = { m: 0, min: 0, dk: 0, h: 0, sa: 0, saat: 0, d: 1, g: 1, 'gün': 1, w: 7, hf: 7, hafta: 7, mo: 30, ay: 30, yr: 365, 'yıl': 365 };
  const days = s => {
    const m = (s || '').match(/(\d+)\s*(min|mo|yr|dk|saat|sa|gün|hafta|hf|ay|yıl|m|h|d|w|g)\b/i);
    return m && m[2].toLowerCase() in UNIT ? Number(m[1]) * UNIT[m[2].toLowerCase()] : -1;
  };
  const clean = s => String(s == null ? '' : s).replace(/[~|\n\r]+/g, ' ').replace(/\s+/g, ' ').trim();
  const NOISE = /^(Add note|Not ekle|Did you hear back\?|Geri dönüş aldınız mı\?|Yes|No|Evet|Hayır|·|\d+ connections?|\+\d+)$/i;
  const rows = [];
  const seen = new Set();
  let pages = 0;
  while (true) {
    pages++;
    let oldest = -1;
    for (const b of document.querySelectorAll('[componentkey^="opportunityTrackerOverflowMenuButton_table_"]')) {
      const id = b.getAttribute('componentkey').split('_').pop();
      if (!/^\d+$/.test(id) || seen.has(id)) continue;
      let r = b;
      for (let i = 0; i < 12 && r && !r.querySelector('a[href*="/jobs/view/"]'); i++) r = r.parentElement;
      if (!r) continue;
      seen.add(id);
      const lines = (r.innerText || '').split('\n').map(clean).filter(l => l && !NOISE.test(l));
      const lead = lines[0] || '';
      const plain = lead.replace(/\s*\((Verified job|Doğrulanmış iş)\)$/i, '');
      const title = lines.length > 1 && lines[1] !== lead && lead.includes(lines[1]) ? lines[1] : plain;
      const place = lines.find(l => l.includes(' · ')) || '';
      const applied = lines.find(l => /^(Applied|Başvuruldu)\b/i.test(l)) || '';
      const d = applied ? days(applied) : -1;
      if (d > oldest) oldest = d;
      const sig = [];
      if (lines.some(l => /Application viewed|Başvuru görüntülendi/i.test(l))) sig.push('viewed');
      if (lines.some(l => /Resume downloaded|Özgeçmiş indirildi/i.test(l))) sig.push('downloaded');
      if (lines.some(l => /No longer accepting|Artık başvuru kabul/i.test(l))) sig.push('closed');
      if (lines.some(l => /^(Yes, I heard back|Evet, geri dönüş)/i.test(l))) sig.push('heard_yes');
      if (lines.some(l => /^(No, I (haven't|did not|didn't) heard? back|Hayır, geri dönüş)/i.test(l))) sig.push('heard_no');
      rows.push([id, d, stage, sig.join('+'), title.slice(0, 80), place.split(' · ')[0].slice(0, 50)].map(clean).join('~'));
    }
    const next = [...document.querySelectorAll('button')].find(b => /^(Next|Sonraki)$/i.test((b.getAttribute('aria-label') || b.innerText || '').trim()));
    if (pages >= MAX_PAGES || !next || next.disabled || (stage === 'applied' && oldest > DAYS)) break;
    next.click();
    await wait(2500);
  }
  window.__myjobs = rows.join('|');
  const out = window.__myjobs;
  return 'N=' + rows.length + ';' + out.slice(0, LIMIT) + (LIMIT < out.length ? 'MORE@' + LIMIT : '');
})()
