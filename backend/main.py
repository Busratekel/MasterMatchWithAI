from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import traceback
from datetime import datetime, UTC
import json
import hashlib
import os
import warnings
from dotenv import load_dotenv
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import redis

# Flask-Limiter uyarısını bastır (geliştirme ortamı için)
warnings.filterwarnings("ignore", message="Using the in-memory storage")

load_dotenv()

app = Flask(__name__)
# Static folder ayarı - PDF dosyaları için
app = Flask(__name__, static_folder='public', static_url_path='/public')

# CORS Ayarları - Ortama göre
def configure_cors():
    """Ortama göre CORS ayarlarını yapılandırır"""
    environment = os.getenv('FLASK_ENV', 'development')
    # Eğer FLASK_ENV tanımlıysa: environment = 'production' veya 'development'
    # Eğer tanımlı değilse: environment = 'development'
    
    if environment == 'production':
        # Canlı ortam - Sadece belirli domainler
        allowed_origins = os.getenv('ALLOWED_ORIGINS', 'https://yourdomain.com')
        origins = [origin.strip() for origin in allowed_origins.split(',')]
        CORS(app, origins=origins, supports_credentials=True)
    else:
        # Geliştirme ortamı - Localhost
        CORS(app, origins=["http://localhost:3000"])

configure_cors()

# Veritabanı Yapılandırması
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Rate Limiting Konfigürasyonu - Canlı/Geliştirme ortamına göre
def create_limiter():
    """Ortama göre rate limiter oluşturur"""
    environment = os.getenv('FLASK_ENV', 'development')
    
    if environment == 'production':
        # Canlı ortam - Redis kullan
        redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
        try:
            redis_client = redis.from_url(redis_url)
            redis_client.ping()  # Redis bağlantısını test et
            
            return Limiter(
                app=app,
                key_func=get_remote_address,
                storage_uri=redis_url,
                default_limits=["1000 per day", "100 per hour", "10 per minute"],
                strategy="fixed-window-elastic-expiry"
            )
        except Exception as e:
            print(f"Redis bağlantı hatası: {e}")
            print("In-memory storage'a geri dönülüyor...")
            # Redis bağlantısı başarısız olursa in-memory kullan
            return Limiter(
                app=app,
                key_func=get_remote_address,
                default_limits=["500 per day", "50 per hour", "5 per minute"]
            )
    else:
        # Geliştirme ortamı - Rate limiting devre dışı
        return Limiter(
            app=app,
            key_func=get_remote_address,
            enabled=False  # Rate limiting tamamen kapalı
        )

limiter = create_limiter()

# --- Veritabanı Modelleri ---
class KvkkMetin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dosya_adi = db.Column(db.String(200), nullable=False)
    versiyon = db.Column(db.String(20), nullable=False)
    hash = db.Column(db.String(64), nullable=False)  # SHA256 hash
    aktif = db.Column(db.Boolean, default=True)
    olusturma_tarihi = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    icerik = db.Column(db.UnicodeText, nullable=False)

class KvkkOnay(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    log_id = db.Column(db.Integer, nullable=False)
    kvkk_metin_id = db.Column(db.Integer, nullable=False)
    ip_adresi = db.Column(db.String(50))
    onay_tarihi = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
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
    tarih = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
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
    {'id': 'uyku_düzeni', 'question': 'Uyku düzeniniz genellikle nasıldır?', 'type': 'radio', 'options': ['Uykum terleme nedeniyle bölünüyor.', 'Hiçbir problem yaşamıyorum, sabahları dinlenmiş uyanıyorum.','Nefes almakta zorlanıyorum, zaman zaman horlama problemi yaşıyorum','Reflü nedeniyle geceleri sık sık uyanıyorum.'], 'info': 'Terleme sorunu için özel yastıklar mevcuttur.', 'order': 3},
    {'id': 'tempo', 'question': 'Gününüzün temposunu nasıl tanımlarsınız?', 'type': 'radio', 'options': ['Oldukça sakin bir tempom var.','Genelde orta tempoda, dengeli bir günüm oluyor.', 'Yoğun tempolu bir gün geçiriyorum.'], 'info': 'Yoğun tempolu yaşamda vücut daha fazla destek ve dinlenmeye ihtiyaç duyar. Doğru yastık, günün yorgunluğunu hafifletir.', 'order': 4},
    {'id': 'agri_bolge', 'question': 'Sabahları belirli bir bölgede ağrı hissediyor musunuz?', 'type': 'checkbox', 'options': ['Hiçbir ağrı hissetmiyorum', 'Bel', 'Omuz', 'Boyun', 'Hepsi'], 'info': 'Boyun, omuz veya bel ağrısı; yanlış yastık seçiminden kaynaklanıyor olabilir. Vücudunuzu dinleyin, ihtiyacınıza uygun yastığı seçin.', 'order': 5},
    {'id': 'dogal_malzeme', 'question': 'Uyku sırasında sizin için daha önemli olan nedir?', 'type': 'radio', 'options': ['Doğal malzemelerin sunduğu doğallık ve nefes alabilirlik', 'Modern teknolojili yastıkların sağladığı konfor ve destek'], 'info': 'Doğal içerikler nefes alabilirlik sağlar, hassas ciltler için daha uygundur. Bambu, pamuk ve yün gibi malzemeler konfor sunar.', 'order': 6},
    {'id': 'sertlik', 'question': 'Yatak sertlik derecenizi belirtir misiniz?', 'type': 'radio', 'options': ['Yumuşak', 'Orta', 'Sert'], 'info': 'Yatak sertliği, yastığın yüksekliği ve dolgunluğu ile uyumlu olmalı. Uyumlu ikili, daha sağlıklı bir uyku sağlar.', 'order': 7}
]

# --- API Endpoint'leri ---
@app.route('/')
def home():
    return jsonify({
        'message': 'Pillow Selection Robot API',
        'version': '1.0',
        'endpoints': [
            '/questions',
            '/yastiklar', 
            '/recommend',
            '/kvkk_metin',
            '/kvkk_onay_ekle',
            '/health'
        ]
    })

@app.route('/health')
def health_check():
    """Sistem sağlık kontrolü endpoint'i"""
    try:
        # Database bağlantısını test et
        with db.engine.connect() as conn:
            conn.execute(db.text('SELECT 1'))
        
        # Redis bağlantısını test et (sadece production'da)
        environment = os.getenv('FLASK_ENV', 'development')
        if environment == 'production':
            try:
                redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
                redis_client = redis.from_url(redis_url)
                redis_client.ping()
                redis_status = 'healthy'
            except Exception as e:
                redis_status = f'unhealthy: {str(e)}'
        else:
            redis_status = 'not_configured'
        
        return jsonify({
            'status': 'healthy',
            'database': 'healthy',
            'redis': redis_status,
            'environment': environment,
            'timestamp': datetime.now(UTC).isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now(UTC).isoformat()
        }), 500

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
@limiter.limit("10 per minute")  # Her IP için dakikada 10 istek
def recommend():
    try:
        data = request.get_json()
        if not data or 'responses' not in data or not isinstance(data['responses'], dict):
            return jsonify({'error': 'Eksik veya hatalı veri: responses alanı zorunlu ve dict olmalı!'}), 400
        responses = data['responses']
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
        
        # BASİT ALGORİTMA - Her yastık için puan hesapla
        yastik_puanlari = []
        

        
        for yastik in yastiklar:
            toplam_puan = 0
            # Her soru için puan hesapla
            for soru_key, agirlik in SORU_AGIRLIKLARI.items():
                # Kullanıcı cevabını al
                kullanici_cevap = None
                if soru_key == 'yas':
                    yas_gercek = responses.get('bmi_age', {}).get('yas_gercek')
                    if yas_gercek:
                        yas_int = int(yas_gercek)
                        if yas_int >= 7:
                            kullanici_cevap = "7+"
                        else:
                            kullanici_cevap = "0-7"
                    else:
                        kullanici_cevap = None
                else:
                    kullanici_cevap = responses.get(soru_key)
                
                if not kullanici_cevap:
                    continue
                
                # Yastık özelliğini al
                yastik_ozellik = getattr(yastik, soru_key, None)
                if not yastik_ozellik:
                    continue
                
                # Eşleşme kontrolü - Türkçe karakterleri normalize et
                kullanici_cevap_str = str(kullanici_cevap).lower().strip()
                yastik_ozellik_str = str(yastik_ozellik).lower().strip()
                
                # Türkçe karakterleri normalize et
                def normalize_turkish(text):
                    replacements = {
                        'ı': 'i', 'ğ': 'g', 'ü': 'u', 'ş': 's', 'ö': 'o', 'ç': 'c',
                        'İ': 'I', 'Ğ': 'G', 'Ü': 'U', 'Ş': 'S', 'Ö': 'O', 'Ç': 'C'
                    }
                    for old, new in replacements.items():
                        text = text.replace(old, new)
                    return text
                
                kullanici_cevap_normalized = normalize_turkish(kullanici_cevap_str)
                yastik_ozellik_normalized = normalize_turkish(yastik_ozellik_str)
                
                # Eşleşme kontrolü - normalize edilmiş metinlerle
                if kullanici_cevap_normalized in yastik_ozellik_normalized:
                    toplam_puan += agirlik
            
            # BMI için özel kontrol
            bmi_cevap = responses.get('bmi')
            if bmi_cevap and yastik.bmi:
                bmi_cevap_str = str(bmi_cevap).lower().strip()
                bmi_yastik_str = str(yastik.bmi).lower().strip()
                
                # Türkçe karakterleri normalize et
                def normalize_turkish(text):
                    replacements = {
                        'ı': 'i', 'ğ': 'g', 'ü': 'u', 'ş': 's', 'ö': 'o', 'ç': 'c',
                        'İ': 'I', 'Ğ': 'G', 'Ü': 'U', 'Ş': 'S', 'Ö': 'O', 'Ç': 'C'
                    }
                    for old, new in replacements.items():
                        text = text.replace(old, new)
                    return text
                
                bmi_cevap_normalized = normalize_turkish(bmi_cevap_str)
                bmi_yastik_normalized = normalize_turkish(bmi_yastik_str)
                
                if bmi_cevap_normalized in bmi_yastik_normalized:
                    toplam_puan += SORU_AGIRLIKLARI.get('bmi', 2)
            
            # Yastık ve puanını listeye ekle
            yastik_puanlari.append({
                'yastik': yastik.to_dict(),
                'puan': toplam_puan
            })
        
        # Yaş kontrolü - 0-7 yaş seçildiyse özel algoritma
        yas_cevap = responses.get('bmi_age', {}).get('yas_gercek')
        if yas_cevap and int(yas_cevap) < 7:
            # 0-7 yaş için özel algoritma
            bebek_yastiklar = []  # Bebek yastıkları listesi
            onemli_eslesenler = []  # Önemli eşleşen (bebek olmayan) yastıklar
            diger_yastiklar = []  # Diğer yastıklar
            
            for item in yastik_puanlari:
                yastik_yas = item['yastik'].get('yas', '')
                yastik_isim = item['yastik'].get('isim', '').lower()
                # Bebek yastığı kontrolü
                if yastik_yas and ('0-7' in str(yastik_yas).lower() or 'bebek' in yastik_isim):
                    bebek_yastiklar.append(item)
                else:
                    # Önemli sorularda (ağırlık 5+) tam eşleşme var mı kontrolü
                    onemli_eslesme_var = False
                    for soru_key, agirlik in SORU_AGIRLIKLARI.items():
                        if agirlik >= 5:  # Önemli sorular
                            kullanici_cevap = responses.get(soru_key)
                            if kullanici_cevap:
                                yastik_ozellik = item['yastik'].get(soru_key, '')
                                if yastik_ozellik:
                                    # Türkçe karakterleri normalize et
                                    def normalize_turkish(text):
                                        replacements = {
                                            'ı': 'i', 'ğ': 'g', 'ü': 'u', 'ş': 's', 'ö': 'o', 'ç': 'c',
                                            'İ': 'I', 'Ğ': 'G', 'Ü': 'U', 'Ş': 'S', 'Ö': 'O', 'Ç': 'C'
                                        }
                                        for old, new in replacements.items():
                                            text = text.replace(old, new)
                                        return text
                                    kullanici_normalized = normalize_turkish(str(kullanici_cevap).lower().strip())
                                    yastik_normalized = normalize_turkish(str(yastik_ozellik).lower().strip())
                                    if kullanici_normalized in yastik_normalized:
                                        onemli_eslesme_var = True
                                        break
                    if onemli_eslesme_var:
                        onemli_eslesenler.append(item)
                    else:
                        diger_yastiklar.append(item)
            # Her grubu puanına göre sırala
            bebek_yastiklar.sort(key=lambda x: x['puan'], reverse=True)
            onemli_eslesenler.sort(key=lambda x: x['puan'], reverse=True)
            diger_yastiklar.sort(key=lambda x: x['puan'], reverse=True)
            # Sonuç listesi: 2 bebek + 2 önemli eşleşen + 1 diğer
            sonuc_listesi = []
            sonuc_listesi.extend(bebek_yastiklar[:2])
            sonuc_listesi.extend(onemli_eslesenler[:2])
            sonuc_listesi.extend(diger_yastiklar[:1])
            # Toplamda 5 yastık olacak şekilde kırp
            yastik_puanlari = sonuc_listesi[:5]
            # Debug için puanları yazdır
            print("=== 0-7 YAŞ ALGORİTMASI (2 bebek + 2 önemli + 1 diğer) ===")
            for i, item in enumerate(yastik_puanlari):
                print(f"{i+1}. {item['yastik']['isim']} - Puan: {item['puan']}")
        else:
            # 7+ yaş için normal puan sıralaması
            yastik_puanlari.sort(key=lambda x: x['puan'], reverse=True)
        
        # İlk 5 yastığı öner
        recommendations = [item['yastik'] for item in yastik_puanlari[:5]]
        
        return jsonify(recommendations=recommendations, log_id=log.id)

    except Exception as e:
        print(f"Öneri sırasında hata: {e}")
        traceback.print_exc()
        return jsonify(error="Sunucu hatası."), 500

@app.route('/kvkk_onay_ekle', methods=['POST'])
@limiter.limit("20 per minute")  # Her IP için dakikada 20 istek
def kvkk_onay_ekle():
    try:
        data = request.get_json()
        if not data or not data.get('log_id') or not data.get('kvkk_metin_id'):
            return jsonify({'error': 'Eksik parametre: log_id ve kvkk_metin_id zorunlu!'}), 400
        log_id = data['log_id']
        kvkk_metin_id = data['kvkk_metin_id']
        ip_adresi = data.get('ip_adresi', request.remote_addr)
        onay_durumu = data.get('onay_durumu', 'kabul')
        onay_yontemi = data.get('onay_yontemi', 'popup')
        onay_tarihi = datetime.now(UTC)
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

@app.route('/kvkk_metin', methods=['GET'])
def get_kvkk_metin():
    kvkk = KvkkMetin.query.filter_by(aktif=True).first()
    if not kvkk:
        return jsonify({'error': 'KVKK metni bulunamadı'}), 404
    return jsonify({
        'id': kvkk.id,
        'versiyon': kvkk.versiyon,
        'icerik': kvkk.icerik
    })

# Uygulamayı geliştirme modunda çalıştırmak için
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    print("🚀 Backend başlatılıyor... http://localhost:5000")
    app.run(debug=True, port=5000, host='0.0.0.0') 