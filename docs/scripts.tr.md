# Scriptler

`scripts/` altındaki tüm yardımcılar. Promptlar bunları senin yerine çağırır; elle de çalıştırabilirsin. Python scriptleri yalnızca standart kütüphaneyi kullanır ve proje klasöründen çalışır. Her biri `--help` yazdırır. [English](scripts.md)

## Tarayıcı scriptleri (tarayıcının JavaScript aracına yapıştırılır)

Ajan dosyanın tamamını doğru LinkedIn sayfasında tek bir JavaScript çağrısına yapıştırır. Scriptler sayfayı okur; sayfa çevirme düğmeleri dışında hiçbir şeye tıklamaz. Çıktı `MORE@n` ile bitiyorsa `OFF = n` ile tekrar çağrılır. Sayfa yapısı notları: [automation-notes.md](automation-notes.md).

| Script | Sayfa | Döndürdüğü |
|---|---|---|
| `linkedin_cards.js` | İş arama sonuçları (`/jobs/search-results/`) | Kart başına: ilan ID, başlık, şirket, yaş, rozet (Applied, Saved, Viewed) |
| `linkedin_posts.js` | #hiring gönderileri için içerik araması | Gönderi başına: gün cinsinden yaş, anahtar kelime eşleşmesi, açık e-posta, metnin başı; tekrar paylaşımlar atılır |
| `linkedin_myjobs.js` | LinkedIn'in iş takibi (`/jobs-tracker/?stage=applied`, `interview`, `draft`, `clicked_apply`, `saved`) | İlan başına: ID, yaş, aşama, sinyaller (görüntülendi, CV indirildi, kapandı), başlık, şirket |
| `linkedin_skills.js` | Profil yeteneklerin (`/in/me/details/skills/`) | Yetenek adları |

## İş arayan

| Komut | Ne yapar |
|---|---|
| `python3 scripts/card_filter.py data/cards-<tarih>.txt` | Başvurduğun, daha önce gördüğün, tracker'da olan ve rollerin dışındaki kartları eler; açılacak kartları yazar |
| `python3 scripts/candidates_check.py data/candidates-<tarih>.md [--done-only]` | Arama alt ajanının aday dosyasını denetler, limitlerin içindeki hazırlama sırasını yazar |
| `python3 scripts/rescore_queue.py [--fingerprint]` | Profilin değişince yeniden puanlanacak kayıtlı ilanları sayfa açmadan listeler |
| `python3 scripts/ats_check.py cv.md --jd ilan.txt [--pair cv_en.md]` | Uyarlanan CV için ATS kuralları ve eksik anahtar kelimeler; hiçbir şey eklemez |
| `python3 scripts/build_cv_pdf.py data/cv/Ad_Soyad_Rol_Cv.md` | CV'yi yerel Chrome ile metni seçilebilir PDF'e yazdırır; 2 sayfayı aşarsa reddeder |
| `python3 scripts/skill_gap.py --jobs data/jobs --cv cv.local.md --linkedin data/linkedin-skills.local.txt [--json]` | Kayıtlı ilan metinlerindeki yetenek talebini CV'n ve LinkedIn yeteneklerinle karşılaştırır; `--json > data/skills-report.json` Yetenekler sekmesini besler |
| `python3 scripts/skill_queries.py [--stale-only]` | Yeteneğe dayalı arama sorgusu eklemeyi ya da bırakmayı önerir; profili değiştirmez |

## Takip tablosu

| Komut | Ne yapar |
|---|---|
| `python3 scripts/linkedin_sync.py data/myjobs-<tarih>.txt [--manual data/manual-candidates.md]` | İş takibi çıktısını olaylara çevirir; kaydedilen ilanlar elle eklenen listeye girer |
| `python3 scripts/reply_reconcile.py check OLAYLAR --write-replies --inbox` | Mail ve LinkedIn olaylarını tracker satırlarıyla eşleştirir: Yanıt hücrelerini yazar, Durum düzeltmelerini ve eksik satırları onay kartı olarak önerir |
| `python3 scripts/reply_reconcile.py apply` | Onayladığın (veya düzenlediğin) tracker düzeltmelerini uygular; arada değişmiş bir satıra dokunmaz |
| `python3 scripts/tracker_stats.py [tracker.md]` | Duruma ve kanala göre sayılar, arşiv dahil |
| `python3 scripts/tracker_archive.py [--dry-run]` | 90 günden eski kapanmış satırları `tracker-archive.md`'ye taşır |
| `python3 scripts/tracker_view.py` | "Senden beklenenler" listesi olan salt okunur yerel sayfa (onay yok) |

## Yerel UI

| Komut | Ne yapar |
|---|---|
| `python3 scripts/ui_server.py [--port 8765]` | 127.0.0.1'de yerel sayfa: Bugün, Seni bekleyenler, Takip, Yetenekler, İşe alımcı |
| `python3 scripts/ui_protocol.py add / decisions / consume / compact` | Onay kutusunun ajan tarafı; `compact` dosyaları küçük tutar |

## İşe alımcı

| Komut | Ne yapar |
|---|---|
| `python3 scripts/screen_report.py KRITERLER.json PUANLAR_KLASORU [--masked MASKELI_KLASOR]` | Sıralı, tavsiye niteliğinde kısa liste; kanıt alıntıları maskeli CV'lerle doğrulanır |
| `python3 scripts/criteria_rarity.py KRITERLER.json PUANLAR_KLASORU [--masked MASKELI_KLASOR]` | Her zorunlu kriteri kaç adayın karşıladığı: RARE (çoğunda yok) ya da UNCLEAR (çoğu belirtmemiş) |

## Kurulum

| Komut | Ne yapar |
|---|---|
| `python3 scripts/install_skill.py [--uninstall]` | `/hirepair` her klasörden çalışsın diye `skills/hirepair`'i `~/.claude/skills` altına bağlar |
| `python3 -m unittest discover -s tests` | Tüm testler; Node kuruluysa tarayıcı scriptleri de test edilir |
