// Read the posts on a LinkedIn content-search page ("#hiring" scan) in ONE JavaScript call.
// Open /search/results/content/?keywords=<unquoted words>&sortBy=%22date_posted%22, wait ~6 s, paste this body.
// Set KW to the role words to look for. Scrolls to the bottom twice, then returns
// "N=<posts>;" + rows "days~kw~emails~snippet" joined by "|", newest first as the page shows them.
// days: post age in days (-1 = unknown); kw: 1 if a KW word is in the post; emails: public addresses
// the poster published, comma separated; snippet: start of the post text. Reposts of the same text are
// dropped (the same opening was reposted by several recruiters on 2026-11-23). No links, no query strings.
(async () => {
  const KW = ['iş analist', 'business analyst'];
  const wait = ms => new Promise(r => setTimeout(r, ms));
  for (let i = 0; i < 2; i++) { window.scrollTo(0, document.body.scrollHeight); await wait(3000); }
  const low = s => (s || '').replace(/İ/g, 'i').replace(/I/g, 'ı').toLowerCase();
  const kws = KW.map(low);
  const UNIT = { m: 0, h: 0, sa: 0, dk: 0, d: 1, g: 1, w: 7, hf: 7, mo: 30, ay: 30, yr: 365, y: 365 };
  // 2026 layout: one element per post with componentkey "expanded<id>FeedType_..."
  const posts = [...document.querySelectorAll('[componentkey^="expanded"]')]
    .filter(e => /FeedType_/.test(e.getAttribute('componentkey')));
  const seen = new Set();
  const rows = [];
  for (const p of posts) {
    const text = (p.innerText || '').replace(/\s+/g, ' ').trim();
    const m = text.match(/(?:^|\s)(\d+)\s?(mo|yr|dk|sa|hf|ay|m|h|d|w|g|y)\s?•/);
    const days = m && m[2] in UNIT ? Number(m[1]) * UNIT[m[2]] : -1;
    // The post body starts after "<age> •" (optionally "Edited •") and the Follow / Connect button.
    const rest = m ? text.slice(m.index + m[0].length) : text;
    const body = rest.replace(/^\s*(Edited\s*•|Düzenlendi\s*•)?\s*(Follow|Connect|Takip et|Bağlantı kur)?\s*/i, '').trim();
    const key = low(body).replace(/[^a-zçğıöşü0-9]/g, '').slice(0, 120);
    if (!key || seen.has(key)) continue;
    seen.add(key);
    const emails = [...new Set(text.match(/[\w.+-]+@[\w-]+(?:\.[\w-]+)+/g) || [])].join(',');
    const kw = kws.some(k => low(text).includes(k)) ? 1 : 0;
    rows.push([days, kw, emails, body.replace(/[~|]/g, ' ').slice(0, 90)].join('~'));
  }
  return 'N=' + rows.length + ';' + rows.join('|');
})()
