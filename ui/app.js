(function () {
'use strict';
var T = {
tr: {
  skip:'İçeriğe geç', mode:'İş arayan modu', local:'Yalnızca yerel · 127.0.0.1 · hiçbir şey bu bilgisayardan çıkmaz',
  tab_today:'Bugün', tab_appr:'Seni bekleyenler', tab_track:'Takip', tab_rec:'İşe alımcı',
  roles_h:'Onaylı roller', limits_h:'Limitler',
  appr_intro:"İki tür madde var. Burada onayla: ajan evetinden sonra devam eder. Kendin yap: onaylar, girişler, kimlik bilgileri ve son Gönder'i ajan asla yapmaz.",
  filter_label:'Şirket, pozisyon veya duruma göre süz', filter_empty:'Eşleşen satır yok. Tümünü görmek için filtreyi temizle.',
  track_empty:'Henüz satır yok.', rec_h:'Kısa liste', rec_note:'Yalnızca tavsiye niteliğindedir. Kararı insan verir. Kimse bu sayfadan reddedilmez veya aranmaz.',
  rec_empty:'Henüz kısa liste yok.', edit_label:'Metni düzenle', cancel:'Vazgeç',
  s_wait:'Seni bekliyor', s_draft:'Taslak, gönderilmedi', s_link:'Şirket formu, bağlantı kayıtlı', s_lock:'Giriş veya onay gerekli',
  s_ok:'Gönderildi', s_skip:'Tarama atladı', s_rej:'İşveren reddetti', s_pause:'Duraklatıldı, e-posta bekleniyor', s_unk:'Bilinmiyor',
  c_date:'Tarih', c_company:'Şirket', c_role:'Pozisyon', c_fit:'Uyum', c_status:'Durum', c_reply:'Yanıt',
  k_approve:'Burada onayla', k_human:'Kendin yap', open_form:'Formu aç', view:'Bağlantıyı aç', did_it:'Yaptım', skip:'Atla', edit:'Metni düzenle',
  approve:'Onayla', a_cv_upload:"CV'yi yüklemeye onayla", a_mail_draft:'Taslak oluştur', confirm:'Onayla',
  empty_inbox:"Bekleyen bir şey yok. Sonraki tarama 17:00'de.", stale:'Bu taslak sen açtıktan sonra değişti. Yeniden incele.',
  st_decided:'Karar verildi', st_consumed:'Ajan uyguladı', st_expired:'Süresi doldu', st_stale:'Değişti, yeniden incele',
  d_approve:'Onaylandı', d_skip:'Atlandı', d_edit:'Düzenlendi', d_done:'Yaptım dendi',
  d_t_cv_upload:'Bu CV yüklemeye onaylansın mı?', d_b_cv_upload:'Ajan yükler ve gözden geçirme sayfasında durur. Göndermez.',
  d_t_mail_draft:'Bu Gmail taslağı oluşturulsun mu?', d_b_mail_draft:"Gmail'de taslak oluşur. Gönderilmez. Gmail'den kendin gönderirsin.",
  d_t_roles:'Bu roller onaylansın mı?', d_b_roles:'Ajan yalnızca bu rollere göre arar ve puanlar.',
  d_t_criteria:'Bu kriterler onaylansın mı?', d_b_criteria:'Ajan CV değerlendirmesinde bu kriterleri kullanır. Sonuçlar yalnızca tavsiyedir.',
  d_t_limits:'Bu limitler onaylansın mı?', d_b_limits:'Ajan günlük işini bu limitler içinde tutar.',
  d_t_open_question:'Bu cevap onaylansın mı?', d_b_open_question:'Ajan bu cevabı kullanarak devam eder.',
  d_t_profile_edit:'Bu LinkedIn profil değişikliği onaylansın mı?', d_b_profile_edit:'Onay tek başına hiçbir şey yazmaz: ajana sıradaki değişikliği söyler. Ajan metni düzenleme kutusuna yazar ve durur; Kaydet\'e sen basarsın.',
  d_t_gen:'Bu madde onaylansın mı?', d_b_gen:'Ajan bir sonraki çalışmasında bu onayla devam eder. Geri alınamayabilir.',
  saved:'Karar kaydedildi. Ajan çalışmıyorsa sonraki çalışmada uygulanır.', err:'Karar kaydedilemedi: ', neterr:'Sunucuya ulaşılamadı.',
  waiting_n:'{n} madde bekliyor', waiting:'seni bekliyor', scored:'takipteki ilan', submitted:'gönderildi', replies:'yanıt',
  prof_none:'Profil henüz yok. Önce onboarding tamamlanmalı.', prof_pending:'Roller henüz onaylanmadı.', roles_none:'Onaylı rol yok.',
  limits_none:'Limit tanımlı değil.', per_day:'günlük tarama', advisory:'Yalnızca tavsiye. Kararı insan verir.', load_err:'Veri yüklenemedi.',
  tab_skills:'Yetenekler', sk_note:"Kaydedilen ilan metinlerinden. Yalnızca CV'nde yazan yetenekler önerilir; LinkedIn'de Kaydet'e sen basarsın.",
  sk_demand:'İlanlarda en çok istenenler', sk_empty:'Henüz yetenek raporu yok. Ajana /linkedin-profile de veya şunu çalıştır: python3 scripts/skill_gap.py --jobs data/jobs --json > data/skills-report.json',
  sk_meta:'{n} ilan metni · rapor tarihi {d}', sk_weak:'10 ilandan az: rapor zayıf.',
  sk_add:"LinkedIn'e ekle (CV'de var, isteniyor)", sk_pin:'Öne çıkar (CV\'de var, en çok istenen)', sk_gap:'Eksikler (CV\'de yok: doğru ve kanıtlanabilir değilse ekleme)',
  sk_check:"LinkedIn'de var, CV'de yok (doğru mu kontrol et)", sk_li_none:'LinkedIn yetenekleri verilmedi.', sk_none:'-',
  sk_edits:'{n} profil değişikliği onayını bekliyor', sk_go:'Onaylara git', in_cv:'CV', on_li:'LinkedIn', not_cv:'CV\'de yok',
  sort_label:'Sırala', sort_date:'En yeni önce', sort_fit:'En uyumlu önce', prev:'Önceki', next:'Sonraki', range:'{a}–{b} / {n} satır',
  before:'Şimdi', after:'Önerilen',
  trk_fixes:'Gmail ve LinkedIn\'e göre {n} takip düzeltmesi onayını bekliyor', a_tracker_fix:'Takibi düzelt',
  d_t_tracker_fix:'Bu takip düzeltmesi uygulansın mı?', d_b_tracker_fix:'Ajan bir sonraki çalışmasında yalnızca bu satırın durumunu değiştirir ya da bu satırı ekler. Hiçbir başvuru gönderilmez, mailine dokunulmaz.'
},
en: {
  skip:'Skip to content', mode:'Job-seeker mode', local:'Local only · 127.0.0.1 · nothing leaves this computer',
  tab_today:'Today', tab_appr:'Waiting for you', tab_track:'Tracker', tab_rec:'Recruiter',
  roles_h:'Approved roles', limits_h:'Limits',
  appr_intro:'Two kinds of items. Approve here: the agent continues after your yes. Do it yourself: consents, sign-ins, IDs and the final Submit are never done by the agent.',
  filter_label:'Filter by company, role or status', filter_empty:'No rows match. Clear the filter to see all rows.',
  track_empty:'No rows yet.', rec_h:'Shortlist', rec_note:'Advisory only. A human decides. Nobody is rejected or contacted by this page.',
  rec_empty:'No shortlist yet.', edit_label:'Edit text', cancel:'Cancel',
  s_wait:'Waiting for you', s_draft:'Draft, not sent', s_link:'Company form, link saved', s_lock:'Sign-in or consent needed',
  s_ok:'Submitted', s_skip:'Skipped by scan', s_rej:'Rejected by employer', s_pause:'Paused, waiting on a mail', s_unk:'Unknown',
  c_date:'Date', c_company:'Company', c_role:'Role', c_fit:'Fit', c_status:'Status', c_reply:'Reply',
  k_approve:'Approve here', k_human:'Do it yourself', open_form:'Open the form', view:'Open link', did_it:'I did it', skip:'Skip', edit:'Edit text',
  approve:'Approve', a_cv_upload:'Approve CV for upload', a_mail_draft:'Create draft', confirm:'Approve',
  empty_inbox:'Nothing is waiting. The next scan is at 17:00.', stale:'This draft changed after you opened it. Review it again.',
  st_decided:'Decided', st_consumed:'Applied by the agent', st_expired:'Expired', st_stale:'Changed, review again',
  d_approve:'Approved', d_skip:'Skipped', d_edit:'Edited', d_done:'Marked done',
  d_t_cv_upload:'Approve this CV for upload?', d_b_cv_upload:'The agent uploads it and stops at the review page. It does not submit.',
  d_t_mail_draft:'Create this Gmail draft?', d_b_mail_draft:'A draft is created in Gmail. It is not sent. You send it yourself from Gmail.',
  d_t_roles:'Approve these roles?', d_b_roles:'The agent searches and scores only for these roles.',
  d_t_criteria:'Approve these criteria?', d_b_criteria:'The agent uses them to screen CVs. Results are advisory only.',
  d_t_limits:'Approve these limits?', d_b_limits:'The agent keeps its daily work within these limits.',
  d_t_open_question:'Approve this answer?', d_b_open_question:'The agent continues using this answer.',
  d_t_profile_edit:'Approve this LinkedIn profile change?', d_b_profile_edit:'Approving types nothing by itself: it tells the agent which change to type next. The agent types it into the edit box and stops; you press Save.',
  d_t_gen:'Approve this item?', d_b_gen:'The agent continues with this approval at its next run. It may not be reversible.',
  saved:'Decision saved. If the agent is not running, it applies at the next run.', err:'Could not save the decision: ', neterr:'Could not reach the server.',
  waiting_n:'{n} items waiting', waiting:'waiting for you', scored:'listings in tracker', submitted:'submitted', replies:'replies',
  prof_none:'No profile yet. Onboarding must be completed first.', prof_pending:'Roles are not approved yet.', roles_none:'No approved roles.',
  limits_none:'No limits set.', per_day:'scans per day', advisory:'Advisory only. A human decides.', load_err:'Could not load data.',
  tab_skills:'Skills', sk_note:'From saved job texts. Only skills your CV states are suggested; you press Save on LinkedIn.',
  sk_demand:'Most asked in listings', sk_empty:'No skill report yet. Ask the agent for /linkedin-profile or run: python3 scripts/skill_gap.py --jobs data/jobs --json > data/skills-report.json',
  sk_meta:'{n} job texts · report from {d}', sk_weak:'Fewer than 10 jobs: the report is weak.',
  sk_add:'Add to LinkedIn (in CV, asked for)', sk_pin:'Pin as top skills (in CV, most asked)', sk_gap:'Gaps (not in CV: do not add unless true and provable)',
  sk_check:'On LinkedIn, not in CV (check they are true)', sk_li_none:'No LinkedIn skills given.', sk_none:'-',
  sk_edits:'Profile changes waiting for approval: {n}', sk_go:'Go to approvals', in_cv:'CV', on_li:'LinkedIn', not_cv:'not in CV',
  sort_label:'Sort', sort_date:'Newest first', sort_fit:'Best fit first', prev:'Previous', next:'Next', range:'{a}–{b} of {n} rows',
  before:'Now', after:'Suggested',
  trk_fixes:'Tracker fixes from your mail and LinkedIn waiting for approval: {n}', a_tracker_fix:'Fix the tracker',
  d_t_tracker_fix:'Apply this tracker fix?', d_b_tracker_fix:'At its next run the agent only changes this row\'s status or adds this row. Nothing is submitted and your mail is not touched.'
}};
var lang = 'tr';
try { var sv = localStorage.getItem('hp_lang'); if (sv === 'en' || sv === 'tr') lang = sv; } catch (e) {}
function t(k) { return (T[lang][k] !== undefined) ? T[lang][k] : (T.tr[k] || k); }

var $ = function (id) { return document.getElementById(id); };
function el(tag, cls, txt) {
  var n = document.createElement(tag);
  if (cls) n.className = cls;
  if (txt !== undefined && txt !== null) n.textContent = String(txt);
  return n;
}
function add(p) { for (var i = 1; i < arguments.length; i++) if (arguments[i]) p.appendChild(arguments[i]); return p; }
function clear(n) { while (n.firstChild) n.removeChild(n.firstChild); }
function safeUrl(u) { return typeof u === 'string' && /^https?:\/\//i.test(u) ? u : null; }
function linkBtn(url, label, cls) {
  var a = el('a', cls || '', label);
  a.href = url; a.target = '_blank'; a.rel = 'noreferrer noopener';
  return a;
}
var ICON = {
  clock:'M8 2a6 6 0 1 0 0 12A6 6 0 0 0 8 2zM8 4.5V8l2.5 1.5', mail:'M2 4h12v8H2zM2 4l6 5 6-5',
  link:'M7 9a3 3 0 0 0 4 0l2-2a3 3 0 0 0-4-4l-1 1M9 7a3 3 0 0 0-4 0L3 9a3 3 0 0 0 4 4l1-1',
  lock:'M3.5 7h9v7h-9zM5.5 7V5a2.5 2.5 0 0 1 5 0v2', check:'M3 8.5l3.5 3.5L13 4.5',
  ban:'M8 2a6 6 0 1 0 0 12A6 6 0 0 0 8 2zM3.8 3.8l8.4 8.4', x:'M4 4l8 8M12 4l-8 8', pause:'M5.5 3v10M10.5 3v10',
  info:'M8 2a6 6 0 1 0 0 12A6 6 0 0 0 8 2zM8 7.5V11M8 5v.5'
};
function badge(tone, icon, text, title) {
  var b = el('span', 'badge b-' + tone);
  var s = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
  s.setAttribute('viewBox', '0 0 16 16'); s.setAttribute('aria-hidden', 'true');
  var p = document.createElementNS('http://www.w3.org/2000/svg', 'path');
  p.setAttribute('d', ICON[icon] || ICON.info); s.appendChild(p);
  b.appendChild(s); b.appendChild(document.createTextNode(text));
  if (title) b.title = title;
  return b;
}
var STATUS = [
  ['⏳', 's_wait', 'wait', 'clock'], ['✉', 's_draft', 'wait', 'mail'], ['💬', 's_draft', 'wait', 'mail'],
  ['🔗', 's_link', 'info', 'link'], ['🔒', 's_lock', 'bad', 'lock'], ['✅', 's_ok', 'ok', 'check'],
  ['⛔', 's_skip', 'info', 'ban'], ['❌', 's_rej', 'bad', 'x'], ['⏸', 's_pause', 'info', 'pause']
];
function statusOf(txt) {
  var s = String(txt || '').trim().replace(/️/g, '');
  for (var i = 0; i < STATUS.length; i++) if (s.indexOf(STATUS[i][0]) === 0) return { m: STATUS[i], rest: s.slice(STATUS[i][0].length).trim() };
  return { m: [null, 's_unk', 'info', 'info'], rest: s };
}

function announce(msg) { $('live').textContent = ''; setTimeout(function () { $('live').textContent = msg; }, 50); }
var toastTimer;
function toast(msg) { announce(msg); clearTimeout(toastTimer); toastTimer = setTimeout(function () { $('live').textContent = ''; }, 6000); }

var state = { tracker: null, inbox: null, profile: null, lastPending: null, sig: {} };
function api(path, etag) {
  return fetch(path, { cache: 'no-cache', headers: { Accept: 'application/json' } }).then(function (r) {
    if (!r.ok) throw new Error('HTTP ' + r.status);
    var tag = r.headers.get('ETag');
    if (etag && tag && tag === etag) return { unchanged: true };
    return r.json().then(function (d) { return { data: d, tag: tag }; });
  });
}

function applyI18n() {
  document.documentElement.lang = lang;
  [].forEach.call(document.querySelectorAll('[data-i18n]'), function (n) { n.textContent = t(n.getAttribute('data-i18n')); });
  $('lang').textContent = lang === 'tr' ? 'EN' : 'TR';
  $('q').placeholder = lang === 'tr' ? 'Örnek, analist, bekliyor…' : 'Example, analyst, waiting…';
  renderAll();
}

function pendingItems() { return ((state.inbox && state.inbox.items) || []).filter(function (i) { return i.status === 'pending'; }); }

function renderCount() {
  var n = pendingItems().length, c = $('count');
  c.hidden = n === 0; c.textContent = n; c.setAttribute('aria-label', t('waiting_n').replace('{n}', n));
}

function renderToday() {
  var rows = state.tracker ? colRows() : [], g = $('stats'); clear(g);
  var sub = 0, rep = 0;
  rows.forEach(function (r) {
    if (statusOf(r.status).m[0] === '✅') sub++;
    if (r.reply && !/^[-–—\s]*$/.test(r.reply)) rep++;
  });
  [[pendingItems().length, t('waiting')], [rows.length, t('scored')], [sub, t('submitted')], [rep, t('replies')]].forEach(function (s) {
    var c = el('div', 'card stat'); add(c, el('b', '', s[0]), el('span', '', s[1])); g.appendChild(c);
  });
  var r = $('roles'), l = $('limits'); clear(r); clear(l);
  var p = state.profile;
  if (!p || !p.exists) { r.appendChild(el('span', 'note', t('prof_none'))); l.appendChild(el('span', 'note', t('limits_none'))); return; }
  if (!p.approved) r.appendChild(el('span', 'note', t('prof_pending')));
  if (p.roles && p.roles.length) p.roles.forEach(function (x) { r.appendChild(el('span', 'badge b-info', x)); });
  else if (p.approved) r.appendChild(el('span', 'note', t('roles_none')));
  var keys = Object.keys(p.limits || {});
  if (!keys.length) { l.appendChild(el('span', 'note', t('limits_none'))); return; }
  var dl = el('dl', 'kv');
  keys.forEach(function (k) {
    add(dl, el('dt', '', k === 'scans_per_day' ? t('per_day') : k), el('dd', '', typeof p.limits[k] === 'object' ? JSON.stringify(p.limits[k]) : p.limits[k]));
  });
  l.appendChild(dl);
}

function colRows() {
  var h = (state.tracker.header || []).map(function (x) { return String(x).trim().toLowerCase(); });
  var names = { date:['date','tarih'], company:['company','şirket','sirket'], role:['role','pozisyon'], fit:['fit','uyum'],
    status:['status','durum'], reply:['reply','yanıt','yanit'], posting:['posting','ilan'] };
  var idx = {};
  Object.keys(names).forEach(function (k) {
    idx[k] = -1;
    names[k].forEach(function (n) { if (idx[k] < 0) idx[k] = h.indexOf(n); });
  });
  return (state.tracker.rows || []).map(function (r) {
    var o = {};
    Object.keys(idx).forEach(function (k) { o[k] = idx[k] >= 0 && r[idx[k]] != null ? String(r[idx[k]]) : ''; });
    return o;
  });
}

var PAGE = 200, view = { page: 0, sort: 'date' };
function fitNum(s) { var m = /\d+(?:[.,]\d+)?/.exec(s || ''); return m ? parseFloat(m[0].replace(',', '.')) : -1; }
// Filter, sort and slice the data, then build DOM rows for the visible page only.
function renderTracker() {
  var head = $('thead'), body = $('tbody'); clear(head); clear(body);
  if (!state.tracker) return;
  var cols = ['date', 'company', 'role', 'fit', 'status', 'reply'], tr = el('tr');
  cols.forEach(function (c) {
    var th = el('th', '', t('c_' + c));
    if ((c === 'date' && view.sort === 'date') || (c === 'fit' && view.sort === 'fit')) th.setAttribute('aria-sort', 'descending');
    tr.appendChild(th);
  });
  head.appendChild(tr);
  var all = colRows(), q = $('q').value.trim().toLowerCase();
  $('trk-empty').hidden = all.length > 0;
  var rows = all.map(function (r, i) { r.i = i; return r; }).filter(function (r) {
    return !q || [r.date, r.company, r.role, r.fit, r.status, t(statusOf(r.status).m[1]), r.reply].join(' ').toLowerCase().indexOf(q) > -1;
  });
  rows.sort(view.sort === 'fit'
    ? function (a, b) { return fitNum(b.fit) - fitNum(a.fit) || (b.date < a.date ? -1 : b.date > a.date ? 1 : 0); }
    : function (a, b) { return b.date < a.date ? -1 : b.date > a.date ? 1 : b.i - a.i; });
  $('none').hidden = rows.length > 0 || all.length === 0;
  var pages = Math.max(1, Math.ceil(rows.length / PAGE));
  if (view.page >= pages) view.page = pages - 1;
  var from = view.page * PAGE, shown = rows.slice(from, from + PAGE);
  $('pager').hidden = rows.length <= PAGE;
  $('range').textContent = t('range').replace('{a}', rows.length ? from + 1 : 0).replace('{b}', from + shown.length).replace('{n}', rows.length);
  $('prev').disabled = view.page === 0; $('next').disabled = view.page >= pages - 1;
  shown.forEach(function (r) {
    var row = el('tr');
    cols.forEach(function (c) {
      var td = el('td');
      if (c === 'status') {
        var s = statusOf(r.status);
        td.appendChild(badge(s.m[2], s.m[3], t(s.m[1]), r.status));
        if (s.rest) td.appendChild(el('div', 'note', s.rest));
      } else if (c === 'company') {
        var u = safeUrl(r.posting);
        td.appendChild(u ? linkBtn(u, r.company) : document.createTextNode(r.company));
      } else td.textContent = r[c];
      row.appendChild(td);
    });
    body.appendChild(row);
  });
}

function renderInbox() {
  var box = $('inbox'); clear(box);
  var items = (state.inbox && state.inbox.items) || [];
  if (!items.length) { box.appendChild(el('div', 'card', t('empty_inbox'))); return; }
  if (!pendingItems().length) box.appendChild(el('p', 'note', t('empty_inbox')));
  items.forEach(function (it) { box.appendChild(itemCard(it)); });
}

function itemCard(it) {
  var human = it['class'] === 'human', pend = it.status === 'pending';
  var c = el('article', 'card item' + (pend ? '' : ' done'));
  var top = el('div', 'row');
  add(top, human ? badge('bad', 'lock', t('k_human')) : badge('wait', 'clock', t('k_approve')), el('span', 'note', it.type || ''));
  if (!pend) {
    var key = 'st_' + it.status, skipped = it.status === 'consumed' && it.decision === 'skip';
    add(top, badge(it.status === 'stale' ? 'bad' : 'info', it.status === 'consumed' && !skipped ? 'check' : 'info',
      skipped ? t('d_skip') : T.tr[key] ? t(key) : String(it.status),
      it.decision && it.status !== 'consumed' ? t('d_' + it.decision) : ''));
  }
  c.appendChild(top);
  add(c, el('h3', '', it.title));
  if (it.summary) c.appendChild(el('p', 'tight', it.summary));
  (Array.isArray(it.evidence) ? it.evidence : []).forEach(function (e) { c.appendChild(el('div', 'ev', e)); });
  if (it.before && it.preview) {
    var ba = el('div', 'ba');
    add(ba, add(el('div'), el('span', '', t('before')), el('div', 'preview', it.before)),
      add(el('div'), el('span', '', t('after')), el('div', 'preview', it.preview)));
    c.appendChild(ba);
  } else if (it.preview) c.appendChild(el('div', 'preview', it.preview));
  if (it.status === 'stale') c.appendChild(el('p', 'err tight', t('stale')));
  var acts = el('div', 'row'), url = safeUrl(it.link);
  if (pend && !human) {
    var ap = el('button', 'btn primary', T.tr['a_' + it.type] ? t('a_' + it.type) : t('approve')); ap.type = 'button';
    ap.addEventListener('click', function () { openDlg(it, 'approve'); });
    var ed = el('button', 'btn', t('edit')); ed.type = 'button';
    ed.addEventListener('click', function () { openDlg(it, 'edit'); });
    add(acts, ap, ed);
    if (url) acts.appendChild(linkBtn(url, t('view'), 'btn'));
    acts.appendChild(skipBtn(it));
  } else if (pend && human) {
    if (url) acts.appendChild(linkBtn(url, t('open_form'), 'btn primary'));
    var dn = el('button', 'btn', t('did_it')); dn.type = 'button';
    dn.addEventListener('click', function () { send(it, 'done', ''); });
    add(acts, dn, skipBtn(it));
  } else if (url) acts.appendChild(linkBtn(url, t('view'), 'btn'));
  if (acts.firstChild) c.appendChild(acts);
  return c;
}
function skipBtn(it) {
  var b = el('button', 'btn', t('skip')); b.type = 'button';
  b.addEventListener('click', function () { send(it, 'skip', ''); });
  return b;
}

var dlg = $('dlg'), cur = null, busy = false;
function openDlg(it, decision) {
  cur = { it: it, decision: decision };
  var ty = T.tr['d_t_' + it.type] ? it.type : 'gen';
  $('dlg-t').textContent = decision === 'edit' ? t('edit') : t('d_t_' + ty);
  $('dlg-b').textContent = decision === 'edit' ? it.title : t('d_b_' + ty);
  var ta = $('dlg-text'); ta.hidden = $('dlg-l').hidden = decision !== 'edit';
  ta.value = decision === 'edit' ? (it.preview || '') : '';
  $('dlg-err').hidden = true;
  $('ok').textContent = decision === 'edit' ? t('edit') : t('confirm');
  dlg.showModal();
}
$('no').addEventListener('click', function () { dlg.close(); });
$('ok').addEventListener('click', function () {
  if (!cur) return;
  var txt = cur.decision === 'edit' ? $('dlg-text').value : '';
  if (cur.decision === 'edit' && !txt.trim()) { $('dlg-text').focus(); return; }
  send(cur.it, cur.decision, txt, true);
});
function send(it, decision, text, inDlg) {
  if (busy) return; busy = true;
  var csrf = document.querySelector('meta[name=csrf]');
  function fail(m) {
    busy = false;
    if (inDlg) { var e = $('dlg-err'); e.textContent = t('err') + m; e.hidden = false; } else toast(t('err') + m);
  }
  fetch('/api/decisions', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'X-CSRF': csrf ? csrf.content : '' },
    body: JSON.stringify({ item: it.id, hash: it.hash, decision: decision, text: text })
  }).then(function (r) {
    return r.json().catch(function () { return {}; }).then(function (j) {
      if (!r.ok || !j.ok) return fail(j.error || 'HTTP ' + r.status);
      busy = false; if (inDlg) dlg.close();
      toast(t('saved')); poll();
    });
  }).catch(function () { fail(t('neterr')); });
}

function renderAll() { renderCount(); renderToday(); renderTracker(); renderInbox(); renderShortlist(); renderSkills(); renderFixes(); }

function chipList(title, names, tone) {
  var c = el('div', 'card');
  c.appendChild(el('h3', '', title));
  var w = el('div', 'chips');
  if (names && names.length) names.forEach(function (n) { w.appendChild(el('span', 'badge b-' + tone, n)); });
  else w.appendChild(el('span', 'note', t('sk_none')));
  c.appendChild(w);
  return c;
}
// A card pointing to the approvals tab when items of one type are waiting (profile edits, tracker fixes).
function pendingBanner(box, type, key) {
  clear(box);
  var n = ((state.inbox && state.inbox.items) || []).filter(function (i) { return i.type === type && i.status === 'pending'; }).length;
  if (!n) return;
  var e = el('div', 'card row');
  var go = el('button', 'btn primary', t('sk_go')); go.type = 'button';
  go.addEventListener('click', function () { var x = $('t-appr'); x.focus(); show(x); });
  add(e, badge('wait', 'clock', t(key).replace('{n}', n)), go);
  box.appendChild(e);
}
function renderFixes() { pendingBanner($('trk-fixes'), 'tracker_fix', 'trk_fixes'); }
function renderSkills() {
  var r = state.skills, lists = $('sk-lists'), bars = $('sk-bars'), meta = $('sk-meta'), eds = $('sk-edits');
  clear(lists); clear(bars); clear(eds); meta.textContent = '';
  pendingBanner(eds, 'profile_edit', 'sk_edits');
  var has = !!(r && r.exists && r.jobs);
  $('sk-empty').hidden = has; bars.hidden = !has;
  if (!has) return;
  var d = r.generated ? new Date(r.generated * 1000).toLocaleDateString(lang === 'tr' ? 'tr-TR' : 'en-GB') : '-';
  meta.textContent = t('sk_meta').replace('{n}', r.jobs).replace('{d}', d) + (r.jobs < 10 ? ' · ' + t('sk_weak') : '');
  add(lists, r.linkedin_given ? chipList(t('sk_add'), r.add_to_linkedin, 'ok') : add(chipList(t('sk_add'), [], 'ok'), el('p', 'note tight', t('sk_li_none'))),
    chipList(t('sk_pin'), r.top_skills, 'info'), chipList(t('sk_gap'), r.gaps, 'wait'));
  if (r.linkedin_given && r.linkedin_not_in_cv && r.linkedin_not_in_cv.length) lists.appendChild(chipList(t('sk_check'), r.linkedin_not_in_cv, 'bad'));
  var rows = (r.demand || []).slice(0, 25), max = rows.length ? rows[0].jobs : 1;
  rows.forEach(function (x) {
    var b = el('div', 'bar'), tr = el('div', 'track'), f = el('div', 'fill' + (x.in_cv ? '' : ' gap'));
    f.style.width = Math.max(2, Math.round(100 * x.jobs / max)) + '%'; tr.appendChild(f);
    tr.setAttribute('role', 'img'); tr.setAttribute('aria-label', x.jobs + '/' + r.jobs);
    var flags = el('span', 'row');
    add(flags, el('span', 'note', x.jobs + '/' + r.jobs),
      x.in_cv ? badge('ok', 'check', t('in_cv')) : badge('wait', 'info', t('not_cv')),
      x.on_linkedin ? badge('info', 'link', t('on_li')) : null);
    add(b, el('span', '', x.skill), tr, flags);
    bars.appendChild(b);
  });
}

function renderShortlist() {
  var md = state.shortlist, pre = $('shortlist');
  pre.hidden = md == null || md === ''; $('rec-empty').hidden = !pre.hidden;
  pre.textContent = md || '';
}

// Skip JSON parsing and re-rendering when the server's per-route ETag is unchanged (most polls).
function take(key, path, done) {
  return api(path, state.sig[key]).then(function (r) {
    if (r.unchanged) return;
    state.sig[key] = r.tag || null; state[key] = r.data; state.changedAt = Date.now(); done();
  });
}
function poll() {
  if (document.visibilityState === 'hidden') return;
  take('inbox', '/api/inbox', function () {
    var n = pendingItems().length;
    if (state.lastPending !== null && n !== state.lastPending) announce(t('waiting_n').replace('{n}', n));
    state.lastPending = n; renderCount(); renderInbox(); renderToday(); renderSkills(); renderFixes();
  }).catch(function () {});
  take('tracker', '/api/tracker', function () { renderTracker(); renderToday(); }).catch(function () {});
}
function loadStatic() {
  take('profile', '/api/profile', renderToday).catch(function () {});
  take('skills', '/api/skills', renderSkills).catch(function () {});
  take('shortlistData', '/api/shortlist', function () { state.shortlist = state.shortlistData.markdown; renderShortlist(); }).catch(function () {});
}

var tabs = [].slice.call(document.querySelectorAll('[role=tab]'));
function show(tab) {
  tabs.forEach(function (x) {
    var on = x === tab; x.setAttribute('aria-selected', on); x.tabIndex = on ? 0 : -1;
    $(x.getAttribute('aria-controls')).hidden = !on;
  });
  if (tab.id === 't-rec' || tab.id === 't-today' || tab.id === 't-skills') loadStatic();
}
tabs.forEach(function (x, i) {
  x.addEventListener('click', function () { show(x); });
  x.addEventListener('keydown', function (e) {
    var n = e.key === 'ArrowRight' ? i + 1 : e.key === 'ArrowLeft' ? i - 1 : e.key === 'Home' ? 0 : e.key === 'End' ? tabs.length - 1 : null;
    if (n === null) return;
    e.preventDefault();
    var y = tabs[(n + tabs.length) % tabs.length]; y.focus(); show(y);
  });
});
$('q').addEventListener('input', function () { view.page = 0; renderTracker(); });
$('sort').addEventListener('change', function () { view.sort = $('sort').value; view.page = 0; renderTracker(); });
$('prev').addEventListener('click', function () { view.page--; renderTracker(); $('thead').scrollIntoView({ block: 'nearest' }); });
$('next').addEventListener('click', function () { view.page++; renderTracker(); $('thead').scrollIntoView({ block: 'nearest' }); });
$('lang').addEventListener('click', function () {
  lang = lang === 'tr' ? 'en' : 'tr';
  try { localStorage.setItem('hp_lang', lang); } catch (e) {}
  applyI18n();
});
document.addEventListener('visibilitychange', poll);
// Poll every 5 s while data is changing, back off to 20 s after 2 quiet minutes.
state.changedAt = Date.now();
function loop() {
  poll();
  setTimeout(loop, Date.now() - state.changedAt < 120000 ? 5000 : 20000);
}
applyI18n(); loadStatic(); loop();
})();
