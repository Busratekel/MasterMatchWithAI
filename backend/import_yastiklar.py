import pandas as pd
from main import app, db, Yastik

def import_yastiklar_from_excel():
    """
    Flask uygulama bağlamını kullanarak Excel'den yastık verilerini
    veritabanına aktarır. Mevcut tüm yastıkları siler ve yeniden yükler.
    """
    with app.app_context():
        try:
            # 1. Mevcut tüm yastık verilerini sil
            num_deleted = db.session.query(Yastik).delete()
            db.session.commit()
            print(f"{num_deleted} adet mevcut yastık kaydı silindi.")

            # 2. Excel dosyasını oku
            df = pd.read_excel('YastıkSon.xlsx')

            # 3. DataFrame üzerinden tek tek yastıkları ekle
            for index, row in df.iterrows():
                # Sütun isimlerinin doğruluğundan emin ol
                if 'YASTIKLAR' not in row or pd.isna(row['YASTIKLAR']):
                    print(f"Satır {index+2} atlandı: 'YASTIKLAR' sütunu boş veya yok.")
                    continue

                # Gorsel ve Link alanlarını doğru şekilde ata
                image_url = str(row['Görsel']) if 'Görsel' in row and pd.notna(row['Görsel']) else None
                product_url = str(row['Link']) if 'Link' in row and pd.notna(row['Link']) else None
                
                # --- GEÇİCİ DÜZELTME: Excel'deki bozuk URL'leri düzeltmeye çalış ---
                # Bu, URL içinde URL bulunan (örn: "https://.../https://...") durumları hedefler.
                # En iyi çözüm, Excel dosyasındaki veriyi doğrudan düzeltmektir.
                if image_url:
                    # URL'de "https://" ifadesinin ikinci kez geçtiği pozisyonu bul
                    second_http_pos = image_url.lower().find("https://", 1)
                    if second_http_pos != -1:
                        # Eğer bulunduysa, URL'yi bu ikinci kısımdan itibaren al
                        original_url = image_url
                        image_url = image_url[second_http_pos:]
                        print(f"URL Düzeltildi: '{original_url}' -> '{image_url}'")
                # --- Düzeltme sonu ---

                yastik = Yastik(
                    isim=row['YASTIKLAR'],
                    gorsel=image_url,
                    link=product_url,
                    sertlik=row.get('Son olarak size daha doğru sonuçlar verebilmemiz adına, yatağınızın sertlik derecesi nedir?'),
                    uyku_pozisyonu=row.get('Genellikle hangi uyku pozisyonunda uyuyorsunuz?'),
                    bmi=row.get('Boyunuz ve Kilonuz? (BMI) (Boy ve kilo girildikten sonra çıkan değere göre)'),
                    dogal_malzeme=row.get('Doğal malzemelerden yapılmış yastıklar (örneğin, pamuk, yün, bambu) sizin için önemli mi?'),
                    terleme=row.get('Uyurken terleme probleminiz var mı?'),
                    agri_bolge=row.get('Uyurken veya sabah uyandığınızda vücudunuzun hangi bölgelerinde ağrı hissediyorsunuz?'),
                    yas=row.get('Yaşınız?'),
                    tempo=row.get('Gün içerisinde iş, spor vb. tempo yoğunluğunuz nasıl?'),
                    mide_rahatsizligi=row.get('Uyku düzeninizi etkileyen mide asidi veya reflü gibi bir rahatsızlığınız var mı?'),
                    nefes_problemi=row.get('Uyurken nefes alıp verme düzeninizde herhangi bir zorlanma veya rahatsızlık yaşıyor musunuz?')
                )
                db.session.add(yastik)

            # 4. Değişiklikleri veritabanına kaydet
            db.session.commit()
            print(f"Başarılı: {len(df)} adet yastık Excel'den veritabanına aktarıldı.")

        except Exception as e:
            db.session.rollback()
            print(f"Bir hata oluştu: {e}")
            print("Veritabanı işlemleri geri alındı.")

if __name__ == '__main__':
    import_yastiklar_from_excel()