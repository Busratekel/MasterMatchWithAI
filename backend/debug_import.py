import pandas as pd
from main import app, db, Yastik

def debug_import():
    with app.app_context():
        try:
            print("1. Excel dosyası okunuyor...")
            df = pd.read_excel('yastiklar.xlsx', header=2, sheet_name='MATRİS GÜNCEL')
            print(f"Excel'den {len(df)} satır okundu")
            print(f"Sütunlar: {df.columns.tolist()}")
            
            print("\n2. İlk 3 satır:")
            print(df.head(3))
            
            print("\n3. Mevcut yastık sayısı kontrol ediliyor...")
            current_count = Yastik.query.count()
            print(list(df.columns))
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
                        isim=row.get('YASTIKLAR'),
                        gorsel=row.get('Görsel'),
                        link=row.get('Link'),
                        bmi=row.get('Boyunuz Kilonuz ve Yaşınız? (BMI) (Boy, kilo ve yaş girildikten sonra çıkan değere göre)'),
                        yas=row.get('Yaş?'),
                        uyku_pozisyonu=row.get('Sizin için en rahat uyku pozisyonunu seçer misiniz?'),  
                        uyku_düzeni=row.get('Uyku düzeniniz genellikle nasıldır?'),
                        tempo=row.get('Gününüzün temposunu nasıl tanımlarsınız?'),
                        agri_bolge=row.get('Sabahları belirli bir bölgede ağrı hissediyor musunuz?'),
                        dogal_malzeme=row.get('Yastıkta doğal içerikler sizin için öncelikli mi?'),
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