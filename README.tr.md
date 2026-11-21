# claude-job-agent (Türkçe)

**CV'ni okuyan, sana uygun rolleri öneren ve hassas adımları senin onayına bırakarak iş aramanı yürüten bir ajan.**

**ATS uyumlu, role göre özelleştirilmiş CV**; yalnızca kendi CV'ndeki gerçeklerle. İngilizce sürüm: [README.md](README.md). Türkçe prompt'lar: `prompts/tr/`.

CV'ni verirsin. Ajan sana uyan 3-5 rolü CV kanıtıyla önerir ve onayını bekler. Onaydan sonra LinkedIn'de ilan ve #hiring gönderilerini arar, CV'ni ilana göre uyarlar, başvuruyu son adıma kadar hazırlar, Gmail'de taslak yazar, yanıtları kontrol eder, Markdown tracker'ı tutar. Gönder ve Yolla düğmelerine sen basarsın.

Açık kaynak [career-ops](https://github.com/santifer/career-ops) (santifer ve katkıda bulunanlar, MIT) üzerine kuruludur; kodunu kopyalamaz.

## Demo akışı

```
sen:    /start-job-agent
ajan:   CV'ni ver (klasör içi yol ya da yapıştır).
sen:    data/cv.pdf
ajan:   Önerilen roller:
        1. İş Analisti - 3 yıl gereksinim çalışması (CV: "3 sürümde gereksinim yazdım")
        2. Ürün Sahibi - ekip backlog'u (CV: "Ekip backlog'unu yönettim")
        Onay / düzenleme? Hariç tutma? Maaş (net/brüt, TL)? Şehir / uzaktan?
sen:    3'ü çıkar, Uygulama Yöneticisi ekle, İstanbul veya uzaktan.
ajan:   profile.local.yml kaydedildi. İlk taramayı başlatayım mı?
```

Roller onaylanmadan hiçbir şey çalışmaz.

## Nasıl çalışır

1. **Onboarding** (`prompts/tr/onboarding.md`): CV, rol önerisi, onayın, profil.
2. **Tarama** (`prompts/tr/daily-scan.md`): yalnızca onaylı roller; Türkçe ve İngilizce sorgular; 1-5 puan, ilandan alıntıyla; günlük limit.
3. **Yanıt kontrolü** (`prompts/tr/gmail-reply-check.md`): salt okunur.
4. **Tracker** (`docs/tracker-format.md`); `python3 scripts/tracker_stats.py tracker.md`.

Her uyarlanmış CV `docs/ats-rules.md` kurallarına uyar ve `python3 scripts/ats_check.py cv.md --jd ilan.txt` ile denetlenir (yalnızca eksik anahtar kelimeyi raporlar, hiçbir şey eklemez). Ajan CV'de olmayan deneyim, yıl, araç veya rakam uydurmaz; form CV'den çıkarılamayan bir sayı sorarsa sana sorar.

## Gereksinimler

- [Claude Code](https://claude.com/claude-code)
- Claude in Chrome eklentisi (LinkedIn'e sen giriş yapmış olursun)
- Gmail bağlayıcısı (okuma + taslak oluşturma)
- İsteğe bağlı: günlük tarama ve yanıt kontrolü için zamanlanmış görevler
- Python 3 (yalnızca standart kütüphane)

## İki mod: iş arayan / işe alım

| | İş arayan (`/start-job-agent`) | İşe alım (`/screen-candidates`) |
|---|---|---|
| Girdi | Senin CV'n | İlan metni ve aday CV'lerinin olduğu yerel klasör |
| İlk kapı | Önerilen rolleri onaylarsın | Olmazsa olmaz / olursa iyi / dışlama kriterlerini onaylarsın; onaydan önce hiçbir CV okunmaz |
| Çıktı | ATS uyumlu özel CV'ler, hazırlanmış başvurular, taslaklar, tracker | Sıralı, açıklanabilir kısa liste (yalnızca ID, kanıt alıntısı, eksikler, 2-3 netleştirme sorusu, uyarılar) |
| Karar | Gönder, rıza, gönderim sende | Her şey sende: ajan elemez, reddetmez, adaylarla iletişime geçmez |

İşe alım modu puanlamadan önce korunan ve ilgisiz özellikleri (yaş, cinsiyet, uyruk, fotoğraf, isim kökeni, adres vb.) maskeler, CV'de olmayan bilgiyi tahmin etmek yerine `not_stated` yazar, aday verisini yerelde tutar (`screening/` ve `reports/` git'e girmez), mail/InMail/mesaj göndermez. Önce `docs/candidate-screening-safety.md` oku (KVKK/GDPR, saklama süresi, aday aydınlatma metni, önyargı ve adil kullanım). Sahte veriyle dene: `python3 scripts/screen_report.py templates/screening/criteria.example.json templates/screening/scores`. Türkçe prompt: `prompts/tr/screen-candidates.md`. LinkedIn kullanımında platform şartları geçerlidir.

## Belirlediğin limitler

Roller onaylandıktan sonra onboarding şunları sorar: (1) günde en fazla kaç arama turu (öneri 1), (2) turda en fazla kaç ilan değerlendirilsin, kaç başvuru/taslak hazırlansın (öneri 15 ve 5), (3) onay biçimi: tek tek ya da toplu özet. Yanıtlar `profile.local.yml` içinde `limits:` altına yazılır; günlük tarama bunları sert üst sınır sayar, limite gelince durur ve kısa özet verir. Gönder, mesaj ve rıza adımları her zaman senin açık onayındadır.

## Aday kaynakları (işe alım modu)

Kriterleri onayladıktan sonra bir veya birkaç kaynak ve her biri için tur başına aday limiti seç (öneri 30):

1. **Yerel CV klasörü.**
2. **Gmail:** verdiğin filtreyle gelen başvuru mailleri. Önce eşleşen konuşmalar listelenir; ekler yalnızca onayınla git'e girmeyen `screening/inbox/` klasörüne indirilir. Yalnızca okuma + taslak; gönderme, silme, etiketleme yok (etiketleme isteğe bağlı, varsayılan kapalı, onay ister).
3. **LinkedIn:** yalnızca kendi yayınladığın ilanlara gelen başvurular (Applicants ekranın) ya da verdiğin profil adresleri. Arama sonuçlarından toplu toplama, mesaj, InMail, bağlantı isteği yok. LinkedIn şartları otomasyonu kısıtlar; risk sendedir.

Her aday kanıt alıntısıyla bir kategoriye girer (güçlü eşleşme / olası / netleştirme gerekli / kriterlere uymuyor). Sonuncusu yalnızca öneridir; ajan kimseyi reddetmez, kimseyle iletişime geçmez. Geri dönüş metinleri yalnızca taslaktır. Maskeleme her kaynağa uygulanır. Sahte örnekler: `templates/screening/`.

## LinkedIn arama yardımcısı (işe alım alt modu)

Aday adayı bulmanın bilerek küçük, kullanıcı yönlendirmeli yolu: kriterleri onayladıktan sonra ajan onayın için kişi-arama sorguları (anahtar kelime + lokasyon) üretir; onaylı her sorgu için senin açık tarayıcında TEK arama yapar ve yalnızca ilk sonuç sayfasının metnini okur (başlık, mevcut rol satırı, lokasyon, bağlantı derecesi; isim saklanmaz). Limitler: turda sonuç (öneri 10, sert üst sınır 25), günde sorgu (öneri 3). Sayfa gezme, profil ziyareti, bağlantı isteği, mesaj, InMail, takip, lead kaydı yok. Başlık düzeyinde kısa liste alırsın; profil derinleştirme yalnızca sohbette ID ile seçtiğin adaylar için, tek tek ve maskelemeyle yapılır. CAPTCHA, uyarı, doğrulama ya da limit metninde hemen durur. Bkz. `prompts/tr/linkedin-search-assistant.md`.

**Dürüst sınırlamalar.** Başlık metni zayıf kanıttır: deneyim yılı ve beceriler çoğunlukla görünmez; en iyi kategori "olası / netleştirme gerekli"dir, "güçlü eşleşme" ancak senin seçtiğin bir derinleştirmeden sonra mümkündür. Sonuçlar LinkedIn'in sıralamasına ve ağ görünürlüğüne bağlıdır, bazı kişileri kaçırır. LinkedIn şartları otomatik toplu toplamayı yasaklar, hesap kısıtlanabilir; mod bilerek küçüktür ve risk sendedir. Bulgular üçüncü kişi verisidir (KVKK/GDPR): asgari alan, yerel git'e girmeyen klasör, paylaşım yok, bitince sil. Canlı sitede denenmedi. Bkz. `docs/candidate-screening-safety.tr.md`.

## Hızlı başlangıç

```bash
cd claude-job-agent
claude
```

Oturumda `/start-job-agent` yaz (ya da "prompts/tr/onboarding.md akışını izle"). Onaylı rol yoksa `CLAUDE.md` onboarding'i otomatik başlatır.

## İzinler

Yalnızca şunları ver:

| İzin | Neden |
|---|---|
| Chrome site erişimi: `linkedin.com` ve seçtiğin iş portalları | İlan/gönderi arama, Kolay Başvuru formları |
| Gmail: okuma | Yanıt kontrolü, açık işe alım adresleri |
| Gmail: taslak oluşturma | İncelemen için mail taslakları |
| Dosya erişimi: tek çalışma klasörü | CV, profil, tracker, PDF. Eklenti yalnızca bu klasörden yükleme yapabilir |

**Gönderme izni GEREKMEZ.** Gmail gönderme kapalı kalsın ya da her gönderim için açık onay istesin. Ajan yalnızca taslak oluşturur.

**Asla verilmez:** parola, ödeme bilgisi, T.C. kimlik numarası; bunları sen girersin. Ajan ayrıca CAPTCHA, hesap oluşturma, **KVKK aydınlatma/açık rıza ve koşul kutuları**, InMail/bağlantı isteği, nihai Gönder ve geri alınamaz her işlemde durur ve sana bırakır.

Sayfa ve e-posta içeriği güvenilmeyen veridir; içindeki talimatlar raporlanır, uygulanmaz.

## Gizlilik

Tüm veri makinende kalır. `.gitignore` şunları dışlar: `cv.local.md`, `profile.local.yml`, `*.local.*`, `tracker.md`, `cv*.pdf`, `data/`, `upload/`, `.claude/settings.local.json`. Her push'tan önce `git status` bak.

## Zamanlama

Gözetimli ilk çalıştırmadan sonra: 17:00 civarı `prompts/tr/daily-scan.md`, 09:00 civarı `prompts/tr/gmail-reply-check.md` ile zamanlanmış görev oluştur (yer tutucuları doldur). Zamanlanmış çalıştırmalar yalnızca hazırlar; onay noktalarında durur. Onboarding yapılmadıysa durur.

## Sorun giderme

- **LinkedIn limitleri:** günlük limiti düşük tut, paralel çalıştırma, güvenlik kontrolünü kendin çöz. `docs/automation-notes.md`.
- **Kolay Başvuru pencere tuhaflıkları:** adımlar değişir; ajan gözden geçirmede durur.
- **CV yüklenmiyor:** gizli file input'u yakalama yöntemi ve "dosya çalışma klasöründe olmalı" kuralı `docs/automation-notes.md` "Uploading a tailored PDF" bölümünde.
- **Yanlış CV ya da yanlış önceden doldurulmuş deneyim yılı:** `docs/lessons-learned.md`.
- **Türkiye'ye özgü portal tuzakları** (net/brüt maaş, T.C. kimlik no, KVKK kutuları, telefon biçimi): `docs/automation-notes.md`.

## Konumlandırma

CV'ni okuyan, rolleri öneren ve hassas adımları sen onaylarken iş aramanı yürüten bir ajan. Her başvuru için ATS uyumlu, role göre özelleştirilmiş CV; deneyim uydurmaz; rıza, kimlik, Gönder ve Yolla sende kalır; veri yerelde.

## Yasal uyarı

Kendi sorumluluğunda kullan. LinkedIn ve diğer sitelerin otomasyonu kullanım koşullarını ihlal edebilir ve hesap kısıtlamasına yol açabilir; her platformun koşullarına ve KVKK/GDPR dahil yerel mevzuata uy. Kendi hesabını, düşük hacimle kullan; başvuru için gerekenin ötesinde başkalarının kişisel verisini toplama. İşe alımcılar gönderdiğini okur: her taslağı ve CV'yi göndermeden önce oku. LinkedIn, Google, Anthropic veya career-ops ile bağlantılı değildir.

## Lisans

MIT, bkz. `LICENSE`.
