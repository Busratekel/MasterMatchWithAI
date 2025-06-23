import pandas as pd
from main import app, db, Yastik

def debug_import():
    with app.app_context():
        try:
            print("1. Excel dosyası okunuyor...")
            df = pd.read_excel('YastıkSon.xlsx')
            print(f"Excel'den {len(df)} satır okundu")
            print(f"Sütunlar: {df.columns.tolist()}")
            
            print("\n2. İlk 3 satır:")
            print(df.head(3))
            
            print("\n3. Mevcut yastık sayısı kontrol ediliyor...")
            current_count = Yastik.query.count()
            print(f"Mevcut yastık sayısı: {current_count}")
            
            print("\n4. Yastıklar siliniyor...")
            deleted = db.session.query(Yastik).delete()
            db.session.commit()
            print(f"{deleted} yastık silindi")
            
            print("\n5. Yeni yastıklar ekleniyor...")
            added_count = 0
            for index, row in df.iterrows():
                if pd.notna(row['YASTIKLAR']):
                    image_url = str(row['Görsel']) if 'Görsel' in row and pd.notna(row['Görsel']) else None
                    product_url = str(row['Link']) if 'Link' in row and pd.notna(row['Link']) else None
                    
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
                    added_count += 1
                    print(f"  - {yastik.isim} eklendi")
            
            db.session.commit()
            print(f"\n6. Toplam {added_count} yastık başarıyla eklendi!")
            
            print("\n7. Son kontrol...")
            final_count = Yastik.query.count()
            print(f"Veritabanındaki toplam yastık sayısı: {final_count}")
            
        except Exception as e:
            print(f"HATA: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    debug_import() 