# Uyarlanan CV'ler için ATS kuralları

Ajanın bir rol için uyarladığı her CV bu kurallara UYMALIDIR. PDF'ten önce `python3 scripts/ats_check.py <cv.md> --jd <ilan.txt>` ile kontrol et, ardından PDF'i `python3 scripts/build_cv_pdf.py <cv.md>` ile üret (1, 2, 5, 6, 7 ve 11. kurallar içinde hazır). Anahtar kelime raporu yalnızca raporlar, hiçbir şey eklemez.

1. **Tek sütun.** Yan çubuk veya çok sütunlu yerleşim yok.
2. **Tablo, ikon, grafik, fotoğraf, metin kutusu yok.** Üstbilgi/altbilgide kritik bilgi yok.
3. **Standart bölüm başlıkları.** EN: Professional Summary, Work Experience, Education, Skills, Certifications, Languages. TR: Özet, İş Deneyimi, Eğitim, Beceriler, Sertifikalar, Diller. CV'yi ilanın dilinde yaz.
4. **Standart tarih:** `AA/YYYY – AA/YYYY` (veya `AA/YYYY – Present` / `Günümüz`). Her yerde tek biçim.
5. **Metni seçilebilir PDF**, taranmış veya görüntü PDF değil. Test: metni seçip kopyalayabilmelisin.
6. **Standart yazı tipi** (Arial, Calibri, Helvetica, Times New Roman), gövde 10-12 pt.
7. **Sade madde işareti** (tire veya yuvarlak). Ok, onay işareti, emoji yok.
8. **Anahtar kelime:** ilanın ifadesini yalnızca zaten doğru olan ve orijinal CV'de bulunan şeyler için kullan. CV'de olmayan beceri, araç, sertifika veya rakam asla ekleme.
9. **Unvan:** başlığı ilanın unvanına yaklaştırabilirsin, ama gerçek unvanı değiştirmeden. İşveren unvanlarını olduğu gibi bırak (açıklamayı özete yaz).
10. **Dosya adı:** `Ad_Soyad_Rol_Cv.pdf` (ASCII harf, alt çizgi), örn. `Alex_Example_Business_Analyst_Cv.pdf`.
11. **En çok 2 sayfa.**
12. **İletişim bilgisi gövdede** (ilk sayfanın üstü): şehir, e-posta, telefon, profil bağlantısı.
13. **Bölüm sırası:** Özet, Deneyim, Eğitim, Beceriler, Diller (denetleyici başka sıralarda uyarır).
14. **Seviyeye göre uzunluk:** 5 yıldan az deneyimde 1 sayfa hedefle (yaklaşık 550 kelime veya az); 2 sayfa sınırı herkes için geçerli.
15. **TR/EN çifti:** iki dil sürümünü tutuyorsan `--pair` ile kontrol et; tarih, e-posta, bölüm sırası ve sayılar eşleşmeli. Çeviri hiçbir bilgiyi değiştirmez.

Bir kural CV'nin gerçeğiyle çakışırsa gerçek kazanır: anahtar kelimeyi at, bilgiyi değil.
