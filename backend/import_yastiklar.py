import pandas as pd
from main import app, db, Yastik

def import_yastiklar_from_excel():
    """
    Excel'den yastık verilerini veritabanına aktarır. Mevcut tüm yastıkları siler ve yeniden yükler.
    """
    with app.app_context():
        try:
            # 1. Mevcut tüm yastık verilerini sil
            num_deleted = db.session.query(Yastik).delete()
            db.session.commit()
            print(f"{num_deleted} adet mevcut yastık kaydı silindi.")

            # 2. Excel dosyasını oku
            df = pd.read_excel('yastiklar.xlsx', header=3, sheet_name='MATRİS GÜNCEL')
            print("Excel sütunları:", list(df.columns))
            print("İlk 3 satır:")
            print(df.head(3))

            # 3. DataFrame üzerinden tek tek yastıkları ekle
            for index, row in df.iterrows():
                if not row.get('YASTIKLAR') or row['YASTIKLAR'] == 'YASTIKLAR':
                    continue
                yastik = Yastik(
                    isim=row.get('YASTIKLAR'),
                    bmi=row.get('Boyunuz Kilonuz ve Yaşınız? (BMI) (Boy, kilo ve yaş girildikten sonra çıkan değere göre)'),
                    yas=row.get('Yaş'),
                    uyku_pozisyonu=row.get('Sizin için en rahat uyku pozisyonunu seçer misiniz?'),
                    uyku_düzeni=row.get('Uyku düzeniniz genellikle nasıldır?'),
                    tempo=row.get('Gününüzün temposunu nasıl tanımlarsınız?'),
                    agri_bolge=row.get('Sabahları belirli bir bölgede ağrı hissediyor musunuz?'),
                    dogal_malzeme=row.get('Yastıkta doğal içerikler sizin için öncelikli mi?'),
                    sertlik=row.get('Yatak sertlik derecenizi belirtir misiniz?'),
                    gorsel=row.get('Görsel'),
                    link=row.get('Link')
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