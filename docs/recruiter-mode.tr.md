# İşe alım modu ve arama limitleri (ayrıntılar)

README kısa kalsın diye buraya taşındı. Güvenlik kuralları: `candidate-screening-safety.tr.md`.

## İki mod: iş arayan / işe alım

| | İş arayan (`/start-job-agent`) | İşe alım (`/screen-candidates`) |
|---|---|---|
| Girdi | Senin CV'n | İlan metni ve aday CV'lerinin olduğu yerel klasör |
| İlk kapı | Önerilen rolleri onaylarsın | Olmazsa olmaz / olursa iyi / dışlama kriterlerini onaylarsın; onaydan önce hiçbir CV okunmaz |
| Çıktı | ATS uyumlu özel CV'ler, hazırlanmış başvurular, taslaklar, tracker | Sıralı, açıklanabilir kısa liste (yalnızca ID, kanıt alıntısı, eksikler, 2-3 netleştirme sorusu, uyarılar) |
| Karar | Gönder, rıza, gönderim sende | Her şey sende: ajan elemez, reddetmez, adaylarla iletişime geçmez |

İşe alım modu puanlamadan önce korunan ve ilgisiz özellikleri (yaş, cinsiyet, uyruk, fotoğraf, isim kökeni, adres vb.) maskeler, CV'de olmayan bilgiyi tahmin etmek yerine `not_stated` yazar, aday verisini yerelde tutar (`screening/` ve `reports/` git'e girmez), mail/InMail/mesaj göndermez. Önce `docs/candidate-screening-safety.md` oku (KVKK/GDPR, saklama süresi, aday aydınlatma metni, önyargı ve adil kullanım). Sahte veriyle dene: `python3 scripts/screen_report.py templates/screening/criteria.example.json templates/screening/scores`. `python3 scripts/criteria_rarity.py` (aynı argümanlar, artı `--masked`) hangi zorunlu kriterlerin havuzda nadir veya belirtilmemiş olduğunu gösterir; kriterleri gözden geçirmek için yalnızca ipucudur. Türkçe prompt: `prompts/tr/screen-candidates.md`. LinkedIn kullanımında platform şartları geçerlidir.


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

