# Aday tarama: güvenlik ve adil kullanım (Türkçe özet)

Ayrıntılı ve bağlayıcı sürüm: `docs/candidate-screening-safety.md`. Bu sayfa LinkedIn arama yardımcısı için Türkçe özettir.

## Karar insanındır
Ajan kimseyi elemez, reddetmez, aday adına işlem yapmaz. `not_matching` yalnızca öneridir. Korunan özellikler (yaş, cinsiyet, uyruk, medeni hâl, din, sağlık, fotoğraf, isim kökeni, adres vb.) puana girmez, raporda yazılmaz; maskeleme zorunludur.

## LinkedIn arama yardımcısı
- LinkedIn şartları otomatik toplu veri toplamayı yasaklar; hesap kısıtlanabilir. Bu mod bu yüzden bilerek küçük ve kullanıcı yönlendirmelidir: yalnızca onaylı sorgular, sorgu başına TEK arama, yalnızca ilk sonuç sayfası metni, tur başına sonuç limiti (öneri 10, sert üst sınır 25), günde sorgu limiti (öneri 3). Çok sayfa gezme, profil ziyareti (kullanıcının seçtiği derinleştirme hariç), bağlantı isteği, mesaj, InMail, takip, lead kaydı yok.
- LinkedIn CAPTCHA, güvenlik uyarısı, giriş doğrulaması ya da limit/kısıtlama metni gösterirse **hemen dur**, kullanıcıya bildir, asla aşmaya çalışma.
- Üçüncü kişi verisi (KVKK/GDPR): adaylar bu veriyi sana vermedi. Asgari alan (başlık, mevcut rol satırı, lokasyon, bağlantı derecesi), isim saklanmaz, yalnızca git'e girmeyen yerel `screening/` klasöründe, amaç bitince silinir (saklama süresi), paylaşılmaz ve satılmaz; aday ile iletişime geçildiğinde aydınlatma metni verilir.
- Kullanıcı olmadan adaylarla iletişim yok; her mesajı kullanıcı gönderir.
- Başlık kanıtı zayıftır: en iyi kategori `possible` (bakmaya değer) / `needs_clarification` (netleştirme gerekli); `strong_match` yalnızca kullanıcının ID ile açıkça seçtiği profil derinleştirmesinden sonra.
- Derinleştirme: yalnızca seçilen ID'ler, onaylanan sayıyı geçmeden, tek tek ve aralıklı, yalnızca görünen herkese açık bölümler, maskeleme uygulanır, puanlayıp durur.

## Adil kullanım
Sıralama araçları önyargı taşıyabilir (CV yazım tarzı, kariyer boşlukları, tanıdık işveren/okul). Kriterleri iş ile sınırlı tut, puanı tek karar dayanağı yapma, listenin alt grubunu da incele, örnekleme ile kontrol et.
