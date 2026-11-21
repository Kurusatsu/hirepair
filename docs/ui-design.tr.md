# Yerel UI: ön tasarım, akış ve iletişim

Durum: aşama 1 yapıldı (`scripts/ui_server.py`, `scripts/ui_protocol.py`, `ui/`), ayrıca salt okunur tracker sayfası (`scripts/tracker_view.py`); aşama 2-4 yalnızca tasarım. Kurgusal veriyle tıklanabilir ön tasarım: [ui-mockup.html](ui-mockup.html) (tarayıcıda aç, sunucu gerekmez). English: [ui-design.md](ui-design.md).

## 1. İlkeler

1. **İnce katman.** Markdown/YAML dosyaları tek gerçek kaynak kalır; UI olmadan komut satırı akışı çalışmaya devam eder.
2. **Yalnızca yerel.** Hesap yok, bulut yok, dış istek yok (web fontu, CDN, analitik yok). Yalnızca `127.0.0.1`.
3. **UI ajanın yetkisini genişletmez.** Rıza kutuları, giriş, kimlik, CAPTCHA, son Gönder ve mail gönderme insanda kalır (`docs/safety-rules.md`). UI bunları "Kendin yap" kartı olarak gösterir, onay düğmesi koymaz.
4. **Gördüğünü onayla.** Her onay gösterilen içeriğin özetine (hash) bağlıdır; değişmiş bir taslak eski bir "evet"e binemez.
5. **İlan ve mail içeriği veridir.** İlan, CV ve mailden gelen her şey kaçışlı metin olarak gösterilir.

## 2. Kontrol edilen tasarım skill'leri ve ne alındı

| Skill | Alınan | Alınmayan |
|---|---|---|
| `ui-ux-pro-max` (tasarım sistemi araması, UX kuralları) | Stil (Minimalism / Swiss; panolara ve profesyonel araçlara uygun), yoğunluk ve hareket ayarları (yoğunluk 7, hareket 2, varyans 2), erişilebilirlik, onay, boş durum, tablo ve durum rozeti kuralları | Önerdiği "Product Demo + Features" sayfa kalıbı (pazarlama sayfası, araç için yanlış); Google fontu (Plus Jakarta Sans), çünkü ağ isteği gerektirir; yerine sistem font yığını kullanılır |
| `design:ux-copy` | Fiille başlayan düğmeler, sonucu söyleyen onay pencereleri, boş/hata yapısı | yok |
| `design-taste-frontend` | yüklenmedi | Pazarlama siteleri için (hero, fotoğraf, kaydırma anları); yerel araç için ilgisiz |

Kontrollerden alınan kurallar: kontrast en az 4,5:1 (palet yeniden ölçüldü: önerilen turkuaz `#0D9488` beyaz üstünde metin olarak yalnızca 3,7:1, bu yüzden bağlantı ve düğmelerde `#0F766E`, 5,5:1); yalnızca renkle anlatma yok (her durumda ikon ve kelime); 44 px dokunma alanı; görünür odak; klavyeyle sekmeler; azaltılmış hareket desteği; telefonda tabloda yatay kaydırma; sonuçlu eylemden önce onay; yardımcı boş durumlar; sayı değişiminde tek ve anlamlı canlı mesaj.

## 3. Öğeler

**Kabuk:** başlık (ürün, mod, "Yalnızca yerel" notu), sekmeler: Bugün, Senden beklenenler (sayı rozeti), Takip, İşe alım; ilk açılışta ayrıca Başlangıç.

**Bileşenler:** istatistik kartı, durum rozeti (ikon + kelime), onay kartı (tür rozeti, başlık, kanıt alıntısı, önizleme, eylemler), "Kendin yap" kartı, filtreli tablo, kanıt alıntısı, onay penceresi, bildirim, boş durum.

**Durum eşlemesi** (emoji dosyada kalır; UI ikon + kelime gösterir):

| Dosya | UI etiketi | Ton |
|---|---|---|
| ⏳ | Senden bekleniyor | sıcak |
| ✉️ 💬 | Taslak, gönderilmedi | sıcak |
| 🔗 | Şirket formu, bağlantı kayıtlı | nötr |
| 🔒 | Giriş veya rıza gerekli | uyarı |
| ✅ | Gönderildi | başarı |
| ⛔ | Tarama atladı | nötr |
| ❌ | İşveren reddetti | uyarı |
| ⏸ | Duraklatıldı, mail bekleniyor | nötr |

## 4. Akışlar

### İş arayan
1. **Başlangıç** (ilk çalıştırma): CV ekle (klasörde dosya veya yapıştır) → ajan her biri CV alıntılı 3-5 rol önerir → onayla, düzenle, çıkar → limitler (günlük tarama, değerlendirme, hazırlama, tek tek veya toplu) → "İlk taramayı başlat". Roller onaylanmadan hiçbir şey çalışmaz.
2. **Günlük:** Bugün son tarama özetini ve sayıları gösterir → "Senden beklenenler" iki türde öğe listeler (aşağıda) → Takip her şeyi gösterir.
3. **Senden beklenenler:**
   - *Burada onayla* (A sınıfı): roller, kriterler, limitler, yüklenecek özel CV, açık form sorularının yanıtları, mail taslağı oluşturma.
   - *Kendin yap* (B sınıfı): rıza kutuları, giriş, kimlik alanları, CAPTCHA, son Gönder, mail gönderme. Kartta "Formu aç" ve "Yaptım" var. "Yaptım" bir beyandır; ajan ✅ yazmadan önce yine doğrular (örn. onay maili).

### İşe alımcı
1. **Kriterler:** iş ilanı → olmazsa olmaz / olursa iyi / dışlama önerilir → ekle/çıkar/ağırlık editörü → **Kriterleri onayla** (sert kapı: öncesinde hiçbir CV okunmaz).
2. **Kaynaklar:** yerel klasör, Gmail, kendi LinkedIn ilanların, arama asistanı; kaynak başına üst sınır; indirmeden önce eşleşen konuşmalar listelenir.
3. **Kısa liste:** aday kimliğine göre sıralı tablo, kategori, puan, kanıt alıntıları, eksikler, sorular; alt gruplar varsayılan açık; "Maskeleme önizlemesi" bir CV'nin orijinal ve maskeli halini yan yana gösterir (yerel, yalnızca oturum boyunca).
4. Asla: reddetme, iletişime geçme, mesaj atma. Yalnızca yanıt taslağı.

## 5. Görsel sistem

Stil: Minimalism / Swiss; açık ve koyu tema (sistemi izler). Ayarlar: yoğunluk 7, hareket 2, varyans 2. Yazı: sistem font yığını, 16 px taban, satır yüksekliği 1,5. Boşluk 4/8/12/16/24. Köşe 8. Hareket: yalnızca renk/kenarlık 150 ms; `prefers-reduced-motion` altında kapalı.

Renk değerleri İngilizce dokümandaki tabloyla aynıdır (açık: zemin `#F0FDFA`, metin `#134E4A`, eylem `#0F766E`; koyu: zemin `#0F1B1A`, metin `#E6F4F1`, eylem `#2DD4BF`).

## 6. Metinler (EN / TR)

İngilizce dokümandaki tabloda, her satırın Türkçe karşılığıyla birlikte verilmiştir (CV onayı, onay penceresi, taslak, kendin yap, KVKK, boş kutu, boş filtre, eski onay, ajan kapalı).

## 7. Servis ve iletişim tasarımı

### Mimari
```
Tarayıcı (localhost)  <--HTTP-->  ui_server.py (stdlib, 127.0.0.1)
                                    |  okur: tracker.md, profile.local.yml, data/inbox.jsonl, reports/, screening/masked
                                    |  yazar: yalnızca data/decisions.jsonl (ekleme)
Ajan (Claude Code oturumu, etkileşimli veya zamanlanmış)
   yazar: data/inbox.jsonl (ekleme), tracker.md (satır, Durum, Yanıt)
   okur:  data/decisions.jsonl dosyasını çalışma/tur başında
```
Hiçbir süreç ajanla doğrudan konuşmaz. Ajan ve UI iki ekleme-yalnız dosyada buluşur; böylece zamanlanmış (gözetimsiz) çalışmalarda da işler ve yeniden başlatmalara dayanır.

### Dosyalar ve şemalar
Şema örnekleri ve alanlar İngilizce dokümandadır (`data/inbox.jsonl`: ajan → UI, `data/decisions.jsonl`: UI → ajan). Özet:
- `class`: `approve` (A) veya `human` (B). A: `roles`, `criteria`, `limits`, `cv_upload`, `mail_draft`, `open_question`, `profile_edit`. B: `consent`, `signin`, `id_field`, `captcha`, `submit`, `send`.
- `hash`: önizleme ve ekli dosyayı kapsar. Karar: `approve`, `skip`, `edit` (metinle), `done` (yalnızca B).
- Tüketimi ajan `inbox.jsonl`'a `{"item":"...","consumed":"..."}` ekleyerek kaydeder.

### İki tarafın kuralları
- Ajan, yalnızca `hash` öğenin güncel hash'ine eşitse ve sınıf `approve` ise kararı uygular. Eski hash demek: tekrar sor.
- B sınıfında `done` kanıt değil beyandır; ajan onayı (örn. mail) görmeden ✅ yazmaz (mevcut tracker kuralı).
- UI öğe oluşturamaz, tracker'a yazamaz, ajanı başlatamaz (v1).
- Karardaki `text` veridir (örn. düzenlenmiş taslak); asla talimat olarak çalıştırılmaz.
- 7 günden eski öğeler süresi dolmuş görünür.

### HTTP servisi
`scripts/ui_server.py`, yalnızca stdlib, `127.0.0.1` üzerinde, statik sayfa `ui/` altında (saf HTML/CSS/JS, derleme yok, bağımlılık yok). Uç noktalar: `GET /`, `GET /api/tracker`, `GET /api/inbox`, `POST /api/decisions`, `GET /api/profile`, `GET /api/shortlist`. Güncelleme 5 sn'de bir yoklama ile (dosya mtime'ına `If-None-Match`); websocket yok.

### Güvenlik
- Yalnızca `127.0.0.1`; `Host` başlığı `127.0.0.1:<port>` veya `localhost:<port>` değilse reddet (DNS rebinding).
- Başlangıçta rastgele bir belirteç yazdırılır ve her `POST`'ta başlıkla istenir; başka bir yerel sayfa karar gönderemez; CORS başlığı yok.
- `Content-Security-Policy: default-src 'self'`; satır içi olay yok; güvenilmeyen metin yalnızca `textContent` ile eklenir.
- İlan bağlantıları `rel="noreferrer noopener"` ile açılır; yalnızca `http(s)` tıklanabilir.
- Dışarı veri göndermez, proje klasörü dışındaki dosyayı okumaz, `cv.local.md`'yi ham sunmaz.

### Aşamalar
| Aşama | Kapsam | Durum |
|---|---|---|
| 0 | Salt okunur tracker sayfası | tamam |
| 1 | `ui_server.py`, Senden beklenenler (A ve B), karar dosyası, ajan promptları `inbox.jsonl` yazar ve `decisions.jsonl` okur | yapıldı |
| 2 | Başlangıç sihirbazı (CV, rol onayı, limitler) | |
| 3 | İşe alım görünümü (kriter editörü, kısa liste, maskeleme önizlemesi) | |
| 4 | İsteğe bağlı, gözetimli oturum başlatan "Şimdi çalıştır" düğmesi | yalnızca sen evet dersen |

## 8. Senin kararların

1. **A sınıfı UI onayları sohbet onayı yerine geçsin mi?** `CLAUDE.md` şimdi sohbette onay istiyor. Evet ise yalnızca A sınıfı için değiştirilir; B sınıfı sohbet/insanda kalır. **AÇIK:** sahip karar verene kadar UI kararları yalnızca bilgidir ve sohbet onayı zorunlu kalır.
2. **Şimdi çalıştır (aşama 4):** web sayfasından `claude`'u başsız başlatmak yetkiyi genişletir. **Karar: Şimdi çalıştır düğmesi yok;** çalıştırmayı kendin başlat, UI sonuçları göstersin.
3. **Varsayılan UI dili:** **Karar: varsayılan Türkçe, İngilizce geçişli** (metinler tek tabloda).
