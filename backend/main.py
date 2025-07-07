from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import traceback
from datetime import datetime
import json
import hashlib
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
# Static folder ayarı - PDF dosyaları için
app = Flask(__name__, static_folder='public', static_url_path='/public')

# CORS ayarlarını daha güvenli hale getir
CORS(app, resources={r"/*": {"origins": ["http://localhost:3000", "http://127.0.0.1:3000"]}}, supports_credentials=True)

# Veritabanı Yapılandırması
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- Veritabanı Modelleri ---
class KvkkMetin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dosya_adi = db.Column(db.String(200), nullable=False)
    versiyon = db.Column(db.String(20), nullable=False)
    hash = db.Column(db.String(64), nullable=False)  # SHA256 hash
    aktif = db.Column(db.Boolean, default=True)
    olusturma_tarihi = db.Column(db.DateTime, default=datetime.utcnow)

class KvkkOnay(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    log_id = db.Column(db.Integer, nullable=False)
    kvkk_metin_id = db.Column(db.Integer, nullable=False)
    ip_adresi = db.Column(db.String(50))
    onay_tarihi = db.Column(db.DateTime, default=datetime.utcnow)
    onay_durumu = db.Column(db.String(10), default='1')
    onay_yontemi = db.Column(db.String(50), default='popup')

class Yastik(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    isim = db.Column(db.String(150), nullable=False)
    gorsel = db.Column(db.String(250))
    link = db.Column(db.String(250))
    sertlik = db.Column(db.String(50))
    uyku_pozisyonu = db.Column(db.String(350))
    bmi = db.Column(db.String(50))
    dogal_malzeme = db.Column(db.String(350))
    uyku_düzeni = db.Column(db.String(350))
    agri_bolge = db.Column(db.String(350))
    yas = db.Column(db.String(50))
    tempo = db.Column(db.String(350))

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in Yastik.__table__.columns}

class KullaniciLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ad = db.Column(db.String(100))
    soyad = db.Column(db.String(100))
    ip_adresi = db.Column(db.String(50))
    yas = db.Column(db.String(10))
    boy = db.Column(db.String(10))
    kilo = db.Column(db.String(10))
    vki = db.Column(db.String(10))
    cevaplar = db.Column(db.Text)  # Tüm cevaplar JSON olarak
    tarih = db.Column(db.DateTime, default=datetime.utcnow)
    incelendi_mi = db.Column(db.Boolean, default=False)
    incelenen_urunler = db.Column(db.Text, nullable=True)

# --- Sabit Veriler ---
SORU_AGIRLIKLARI = {
    'sertlik': 1, 'bmi': 2, 'yas': 2, 'uyku_pozisyonu': 3, 'dogal_malzeme': 4, 'tempo': 5, 'agri_bolge': 6, 'uyku_düzeni': 7,
}

QUESTIONS = [
    {
        'id': 'bmi_age',
        'question': 'Yaşınızı, boyunuzu ve kilonuzu giriniz.',
        'type': 'bmi_age',
        'info': 'Yaş, boy ve kilo gibi fiziksel bilgiler; ideal yastık yüksekliği ve destek düzeyini belirlememize yardımcı olur. Bu bilgiler yalnızca daha doğru bir öneri sunmak amacıyla kullanılacaktır.',
        'order': 1
    },
    {'id': 'uyku_pozisyonu', 'question': 'Sizin için en rahat uyku pozisyonunu seçer misiniz?', 'type': 'checkbox', 'options': ['Sırt üstü uyku pozisyonu', 'Yüz üstü uyku pozisyonu', 'Yan uyku pozisyonu', 'Pozisyonum değişken'], 'info': 'Uyku pozisyonu, boyun ve omurga sağlığınızı doğrudan etkiler. Doğru yastık, uyku tarzınıza uyum sağlamalıdır.', 'order': 2},
    {'id': 'uyku_düzeni', 'question': 'Uyku düzeniniz genellikle nasıldır?', 'type': 'checkbox', 'options': ['Uykum terleme nedeniyle bölünüyor.', 'Hiçbir problem yaşamıyorum, sabahları dinlenmiş uyanıyorum.','Nefes almakta zorlanıyorum, zaman zaman horlama problemi yaşıyorum','Reflü nedeniyle geceleri sık sık uyanıyorum.'], 'info': 'Terleme sorunu için özel yastıklar mevcuttur.', 'order': 3},
    {'id': 'tempo', 'question': 'Gününüzün temposunu nasıl tanımlarsınız?', 'type': 'radio', 'options': ['Genelde orta tempoda, dengeli bir günüm oluyor.', 'Yoğun tempolu bir gün geçiriyorum.','Oldukça sakin bir tempom var.'], 'info': 'Yoğun tempolu yaşamda vücut daha fazla destek ve dinlenmeye ihtiyaç duyar. Doğru yastık, günün yorgunluğunu hafifletir.', 'order': 4},
    {'id': 'agri_bolge', 'question': 'Sabahları belirli bir bölgede ağrı hissediyor musunuz?', 'type': 'checkbox', 'options': ['Hiçbir ağrı hissetmiyorum', 'Bel', 'Omuz', 'Boyun', 'Hepsi'], 'info': 'Boyun, omuz veya bel ağrısı; yanlış yastık seçiminden kaynaklanıyor olabilir. Vücudunuzu dinleyin, ihtiyacınıza uygun yastığı seçin.', 'order': 5},
    {'id': 'dogal_malzeme', 'question': 'Uyku sırasında sizin için daha önemli olan nedir?', 'type': 'radio', 'options': ['Doğal malzemelerin sunduğu doğallık ve nefes alabilirlik', 'Modern teknolojili yastıkların sağladığı konfor ve destek'], 'info': 'Doğal içerikler nefes alabilirlik sağlar, hassas ciltler için daha uygundur. Bambu, pamuk ve yün gibi malzemeler konfor sunar.', 'order': 6},
    {'id': 'sertlik', 'question': 'Yatak sertlik derecenizi belirtir misiniz?', 'type': 'checkbox', 'options': ['Yumuşak', 'Orta', 'Sert', 'Hepsi'], 'info': 'Yatak sertliği, yastığın yüksekliği ve dolgunluğu ile uyumlu olmalı. Uyumlu ikili, daha sağlıklı bir uyku sağlar.', 'order': 7}
]

# --- API Endpoint'leri ---
@app.route('/questions')
def get_questions():
    try:
        sorted_questions = sorted(QUESTIONS, key=lambda x: x['order'])
        return jsonify(questions=sorted_questions)
    except Exception as e:
        print(f"Soru getirme hatası: {e}")
        return jsonify(error="Sorular yüklenirken bir hata oluştu."), 500

@app.route('/yastiklar')
def get_yastiklar():
    try:
        yastiklar = Yastik.query.all()
        return jsonify(yastiklar=[y.to_dict() for y in yastiklar])
    except Exception as e:
        print(f"Yastık getirme hatası: {e}")
        return jsonify(error="Yastıklar yüklenirken bir hata oluştu."), 500

@app.route('/recommend', methods=['POST'])
def recommend():
    try:
        data = request.get_json()
        responses = data.get('responses', {})
        user_info = data.get('user', {})

        yas = responses.get('bmi_age', {}).get('yas_gercek')
        boy = responses.get('bmi_age', {}).get('boy')
        kilo = responses.get('bmi_age', {}).get('kilo')
        vki = responses.get('bmi_age', {}).get('vki')
        ad = user_info.get('ad')
        soyad = user_info.get('soyad')
        ip_adresi = request.remote_addr if not (ad and soyad) else None

        log = KullaniciLog(
            ad=ad,
            soyad=soyad,
            ip_adresi=ip_adresi,
            yas=str(yas),
            boy=str(boy),
            kilo=str(kilo),
            vki=str(vki),
            cevaplar=json.dumps(responses, ensure_ascii=False)
        )
        db.session.add(log)
        db.session.commit()

        if not responses:
            return jsonify(error="Cevaplar alınamadı."), 400

        yastiklar = Yastik.query.all()
        if not yastiklar:
            return jsonify(error="Veritabanında yastık bulunamadı."), 500
        
        scored_yastiklar = []
        for yastik in yastiklar:
            score = 0
            
            def is_match(key, pillow_attr):
                response = responses.get(key)
                if not response or not pillow_attr: return False
                
                # Response'u array'e çevir (eğer değilse)
                if isinstance(response, list):
                    choices = [str(c).lower().strip() for c in response if c]
                else:
                    choices = [str(response).lower().strip()]
                
                pillow_attr_lower = str(pillow_attr).lower().strip()
                
                # Pozisyonum değişken seçildiyse, her şeyle eşleşir
                if key == 'uyku_pozisyonu' and 'pozisyonum değişken' in choices:
                    return True
                
                # HEPSİ seçildiyse, her şeyle eşleşir
                if 'hepsi' in choices:
                    return True
                
                # Hiçbir ağrı hissetmiyorum seçildiyse, sadece o seçenekle eşleşir
                if key == 'agri_bolge' and 'hiçbir ağrı hissetmiyorum' in choices:
                    return 'hiçbir ağrı hissetmiyorum' in pillow_attr_lower
                
                # Uyku pozisyonu için özel kontrol
                if key == 'uyku_pozisyonu':
                    # Kullanıcının seçtiği pozisyonları kontrol et
                    for choice in choices:
                        if choice in pillow_attr_lower:
                            return True
                    return False
                
                # Diğer alanlar için genel kontrol
                for choice in choices:
                    if choice in pillow_attr_lower:
                        return True
                
                return False

            def is_positive_match(key, pillow_attr):
                response = str(responses.get(key, 'Hayır')).lower()
                return 'evet' in response and 'evet' in str(pillow_attr).lower()

            # YAŞ ALGORİTMASI (0-7 ve 7+)
            yas_cevap = responses.get('yas')  # "0-7" veya "7+"
            pillow_yas = (yastik.yas or '').lower()
            if yas_cevap and pillow_yas and yas_cevap.lower().strip() == pillow_yas.strip():
                score += SORU_AGIRLIKLARI.get('yas', 1)

            # BMI karşılaştırması - kategori olarak geliyor
            bmi_cevap = responses.get('bmi')  # Kategori olarak geliyor
            pillow_bmi = (yastik.bmi or '').lower().strip()
            tam_bmi_eslesme = bmi_cevap and pillow_bmi and bmi_cevap.lower().strip() == pillow_bmi
            icinde_bmi_eslesme = bmi_cevap and pillow_bmi and bmi_cevap.lower() in pillow_bmi
            if tam_bmi_eslesme:
                score += SORU_AGIRLIKLARI.get('bmi', 1) + 1  # Tam eşleşmeye ekstra puan
            elif icinde_bmi_eslesme:
                score += SORU_AGIRLIKLARI.get('bmi', 1)  # İçinde geçen eşleşmeye normal puan

            # Diğer kriterler
            if is_match('sertlik', yastik.sertlik): score += SORU_AGIRLIKLARI.get('sertlik', 1)
            if is_match('uyku_pozisyonu', yastik.uyku_pozisyonu): score += SORU_AGIRLIKLARI.get('uyku_pozisyonu', 1)
            if is_positive_match('dogal_malzeme', yastik.dogal_malzeme): score += SORU_AGIRLIKLARI.get('dogal_malzeme', 1)
            if is_match('tempo', yastik.tempo): score += SORU_AGIRLIKLARI.get('tempo', 1)
            if is_match('agri_bolge', yastik.agri_bolge): score += SORU_AGIRLIKLARI.get('agri_bolge', 1)
            if is_match('uyku_düzeni', yastik.uyku_düzeni): score += SORU_AGIRLIKLARI.get('uyku_düzeni', 1)

            if score > 0:
                scored_yastiklar.append({'yastik': yastik.to_dict(), 'score': score})

        if not scored_yastiklar:
            return jsonify(recommendations=[], log_id=log.id)

        sorted_yastiklar = sorted(scored_yastiklar, key=lambda x: x['score'], reverse=True)
        top_yastiklar = sorted_yastiklar[:5]
        
        recommendations = [item['yastik'] for item in top_yastiklar]
        return jsonify(recommendations=recommendations, log_id=log.id)

    except Exception as e:
        print(f"Öneri sırasında hata: {e}")
        traceback.print_exc()
        return jsonify(error="Sunucu hatası."), 500

@app.route('/kvkk_onay_ekle', methods=['POST'])
def kvkk_onay_ekle():
    try:
        data = request.get_json()
        log_id = data.get('log_id')
        kvkk_metin_id = data.get('kvkk_metin_id')
        ip_adresi = data.get('ip_adresi', request.remote_addr)
        onay_durumu = data.get('onay_durumu', 'kabul')
        onay_yontemi = data.get('onay_yontemi', 'popup')
        onay_tarihi = datetime.utcnow()
        if not log_id or not kvkk_metin_id:
            return jsonify({'error': 'log_id ve kvkk_metin_id zorunlu!'}), 400
        onay = KvkkOnay(
            log_id=log_id,
            kvkk_metin_id=kvkk_metin_id,
            ip_adresi=ip_adresi,
            onay_tarihi=onay_tarihi,
            onay_durumu=onay_durumu,
            onay_yontemi=onay_yontemi
        )
        db.session.add(onay)
        db.session.commit()
        return jsonify({'success': True, 'onay_id': onay.id})
    except Exception as e:
        print(f"KVKK onay ekleme hatası: {e}")
        traceback.print_exc()
        return jsonify({'error': 'Sunucu hatası'}), 500

@app.route('/kvkk_aktif_pdf')
def kvkk_aktif_pdf():
    try:
        # Aktif KVKK metnini bul
        aktif_kvkk = KvkkMetin.query.filter_by(aktif=True).first()
        
        if not aktif_kvkk:
            return jsonify({'error': 'Aktif KVKK metni bulunamadı'}), 404
        
        # PDF dosya yolunu oluştur
        pdf_path = os.path.join('public', aktif_kvkk.dosya_adi)
        
        # Dosyanın var olup olmadığını kontrol et
        if not os.path.exists(pdf_path):
            return jsonify({'error': 'PDF dosyası bulunamadı'}), 404
        
        # Dosya URL'ini oluştur
        pdf_url = f"/public/{aktif_kvkk.dosya_adi}"
        
        return jsonify({
            'id': aktif_kvkk.id,
            'dosya_adi': aktif_kvkk.dosya_adi,
            'versiyon': aktif_kvkk.versiyon,
            'hash': aktif_kvkk.hash,
            'url': pdf_url,
            'aktif': aktif_kvkk.aktif
        })
        
    except Exception as e:
        print(f"KVKK PDF getirme hatası: {e}")
        traceback.print_exc()
        return jsonify({'error': 'Sunucu hatası'}), 500

@app.route('/log_urun_inceleme', methods=['POST'])
def log_urun_inceleme():
    try:
        data = request.get_json()
        log_id = data.get('log_id')
        urun_ismi = data.get('urun_ismi')
        if not log_id or not urun_ismi:
            return jsonify({'error': 'log_id ve urun_ismi zorunlu!'}), 400
        log = KullaniciLog.query.get(log_id)
        if not log:
            return jsonify({'error': 'Log bulunamadı!'}), 404
        log.incelendi_mi = True
        if log.incelenen_urunler:
            urunler = log.incelenen_urunler.split(',')
            if urun_ismi not in urunler:
                urunler.append(urun_ismi)
            log.incelenen_urunler = ','.join(urunler)
        else:
            log.incelenen_urunler = urun_ismi
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        print(f"Ürün inceleme logu ekleme hatası: {e}")
        traceback.print_exc()
        return jsonify({'error': 'Sunucu hatası'}), 500

# Uygulamayı geliştirme modunda çalıştırmak için
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    print("🚀 Backend başlatılıyor... http://localhost:5000")
    app.run(debug=True, port=5000, host='0.0.0.0') 