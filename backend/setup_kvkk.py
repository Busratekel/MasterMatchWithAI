import hashlib
import os
from main import app, db, KvkkMetin

def setup_kvkk():
    with app.app_context():
        try:
            # PDF dosyasının hash'ini hesapla
            pdf_path = os.path.join('public', 'kvkk_v2.0.pdf')
            
            if not os.path.exists(pdf_path):
                print("❌ PDF dosyası bulunamadı:", pdf_path)
                return
            
            with open(pdf_path, 'rb') as f:
                pdf_content = f.read()
                pdf_hash = hashlib.sha256(pdf_content).hexdigest()
            
            print(f"📄 PDF Hash: {pdf_hash}")
            
            # Mevcut aktif kayıtları pasif yap
            KvkkMetin.query.update({KvkkMetin.aktif: False})
            
            # Yeni KVKK kaydı oluştur
            kvkk_metin = KvkkMetin(
                dosya_adi='kvkk_v2.0.pdf',
                versiyon='2.0',
                hash=pdf_hash,
                aktif=True
            )
            
            db.session.add(kvkk_metin)
            db.session.commit()
            
            print("✅ KVKK metni başarıyla eklendi!")
            print(f"   ID: {kvkk_metin.id}")
            print(f"   Dosya: {kvkk_metin.dosya_adi}")
            print(f"   Versiyon: {kvkk_metin.versiyon}")
            print(f"   Hash: {kvkk_metin.hash}")
            print(f"   Aktif: {kvkk_metin.aktif}")
            print(f"   Aktif: {kvkk_metin.olusturma_tarihi}")
            
        except Exception as e:
            print(f"❌ Hata: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    setup_kvkk() 