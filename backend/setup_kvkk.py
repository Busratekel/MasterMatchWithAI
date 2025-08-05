import hashlib
import os
from main import app, db, KvkkMetin

# PDF'den metin çıkaran fonksiyon
def pdf_to_text(pdf_path):
    try:
        import PyPDF2
    except ImportError:
        print("PyPDF2 yüklü değil. 'pip install PyPDF2' ile yükleyin.")
        return ""
    text = ""
    with open(pdf_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text.strip()

def setup_kvkk():
    with app.app_context():
        try:
            pdf_path = os.path.join('public', 'doqu_home_kvkk_metni.pdf')
            if not os.path.exists(pdf_path):
                print("❌ PDF dosyası bulunamadı:", pdf_path)
                return

            with open(pdf_path, 'rb') as f:
                pdf_content = f.read()
                pdf_hash = hashlib.sha256(pdf_content).hexdigest()

            print(f"📄 PDF Hash: {pdf_hash}")

            # PDF'den metni çıkar
            pdf_text = pdf_to_text(pdf_path)
            if not pdf_text:
                print("❌ PDF'den metin çıkarılamadı!")
                return          

            # Mevcut aktif kayıtları pasif yap
            KvkkMetin.query.update({KvkkMetin.aktif: False})

            # Yeni KVKK kaydı oluştur
            kvkk_metin = KvkkMetin(
                dosya_adi='kvkk_v1.0.pdf',
                versiyon='1.0',
                hash=pdf_hash,
                aktif=True,
                icerik=pdf_text  # <-- yeni eklenen alan!
            )

            db.session.add(kvkk_metin)
            db.session.commit()

            print("✅ KVKK metni başarıyla eklendi!")
            print(f"   ID: {kvkk_metin.id}")
            print(f"   Dosya: {kvkk_metin.dosya_adi}")
            print(f"   Versiyon: {kvkk_metin.versiyon}")
            print(f"   Hash: {kvkk_metin.hash}")
            print(f"   Aktif: {kvkk_metin.aktif}")
            print(f"   Oluşturma Tarihi: {kvkk_metin.olusturma_tarihi}")

        except Exception as e:
            print(f"❌ Hata: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    setup_kvkk()