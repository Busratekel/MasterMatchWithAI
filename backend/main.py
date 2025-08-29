# -*- coding: utf-8 -*-
import sys
import os

# Python encoding ayarları
if sys.platform.startswith('win'):
    # Windows'ta encoding ayarları
    import locale
    try:
        locale.setlocale(locale.LC_ALL, 'Turkish_Turkey.1254')
    except:
        try:
            locale.setlocale(locale.LC_ALL, 'tr_TR.UTF-8')
        except:
            pass
    
    # Console encoding'i UTF-8 yap
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8')

# Environment variables for encoding
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['PYTHONUTF8'] = '1'

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import traceback
from datetime import datetime, timezone
import json
import hashlib
import warnings
from dotenv import load_dotenv
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
# Redis import'u kaldırıldı - artık kullanılmıyor
from flask_mail import Mail, Message

# Flask-Limiter uyarısını bastır (geliştirme ortamı için)
warnings.filterwarnings("ignore", message="Using the in-memory storage")

load_dotenv()

app = Flask(__name__)
# Static folder ayarı - PDF dosyaları için
app = Flask(__name__, static_folder='public', static_url_path='/public')

# CORS Ayarları - Ortama göre
from flask_cors import CORS
import os

def configure_cors():
    environment = os.getenv('FLASK_ENV', 'development')
    if environment == 'production':
        # Canlı domainler izinli
        CORS(app, origins=[
            'https://mastermatch.doquhome.com.tr',
            'https://devmastermatch.doquhome.com.tr'
        ], supports_credentials=True)
    else:
        # Geliştirme ortamı - localhost ve dev domain izinli
        CORS(app, origins=[
            'http://localhost:3000',
            'https://devmastermatch.doquhome.com.tr'
        ], supports_credentials=True)

configure_cors()

# Veritabanı Yapılandırması
database_url = os.getenv('DATABASE_URL')
if not database_url:
    # Eğer DATABASE_URL yoksa SQLite kullan (geliştirme için)
    database_url = 'sqlite:///app.db'
print(f"Kullanılan veritabanı URL: {database_url}")
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Rate Limiting Konfigürasyonu - In-memory storage kullan
def create_limiter():
    """In-memory rate limiter oluşturur"""
    environment = os.getenv('FLASK_ENV', 'development')
    
    if environment == 'production':
        # Canlı ortam - In-memory storage kullan
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

# .env'den SMTP ve mail ayarlarını oku
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.office365.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')
MAIL_BCC_LIST = os.getenv('MAIL_BCC_LIST', '')
MAIL_REPLY_TO = os.getenv('MAIL_REPLY_TO', app.config['MAIL_DEFAULT_SENDER'])

mail = Mail(app)

# Mail gönderme fonksiyonu
def send_analysis_email(email, mail_content, from_address=None, bcc_emails=None):
    try:
        msg = Message(
            subject='Yastık Analiz Raporunuz - DoquHome',
            sender=from_address or app.config['MAIL_DEFAULT_SENDER'],
            recipients=[email]
        )
        msg.reply_to = MAIL_REPLY_TO
        # BCC env'den veya parametreden
        bcc_final = bcc_emails or MAIL_BCC_LIST
        if bcc_final:
            msg.bcc = [e.strip() for e in bcc_final.split(';') if e.strip()]
        
        # Direkt gelen HTML içeriği kullan
        msg.html = mail_content
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Mail gönderme hatası: {e}")
        return False

# --- Veritabanı Modelleri ---
class KvkkMetin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dosya_adi = db.Column(db.String(200), nullable=False)
    versiyon = db.Column(db.String(20), nullable=False)
    hash = db.Column(db.String(64), nullable=False)  # SHA256 hash
    aktif = db.Column(db.Boolean, default=True)
    olusturma_tarihi = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    icerik = db.Column(db.UnicodeText, nullable=False)

class KvkkOnay(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    log_id = db.Column(db.Integer, nullable=False)
    kvkk_metin_id = db.Column(db.Integer, nullable=False)
    ip_adresi = db.Column(db.String(50))
    onay_tarihi = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
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
    email = db.Column(db.String(100))
    ip_adresi = db.Column(db.String(50))
    yas = db.Column(db.String(10))
    boy = db.Column(db.String(10))
    kilo = db.Column(db.String(10))
    vki = db.Column(db.String(10))
    cevaplar = db.Column(db.Text)  # Tüm cevaplar JSON olarak
    tarih = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    incelendi_mi = db.Column(db.Boolean, default=False)
    incelenen_urunler = db.Column(db.Text, nullable=True)
    analiz_sonucu_alindi_mi = db.Column(db.Boolean, default=False)  # Analiz sonucu popup ile alındı mı

# --- Sabit Veriler ---
SORU_AGIRLIKLARI = {
    'sertlik': 1, 'bmi': 2, 'yas': 2, 'uyku_pozisyonu': 3, 'ideal_sertlik': 4,'dogal_malzeme': 5, 'tempo': 6, 'agri_bolge': 7, 'uyku_düzeni': 8,
}

# --- Yardımcı Fonksiyonlar ---
def normalize_turkish(text):
    """Türkçe karakterleri normalize eder"""
    replacements = {
        'ı': 'i', 'ğ': 'g', 'ü': 'u', 'ş': 's', 'ö': 'o', 'ç': 'c',
        'İ': 'I', 'Ğ': 'G', 'Ü': 'U', 'Ş': 'S', 'Ö': 'O', 'Ç': 'C'
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text

def calculate_pillow_recommendations(responses):
    """Yastık önerilerini hesaplar - tekrar kullanılabilir fonksiyon"""
    yastiklar = Yastik.query.all()
    if not yastiklar:
        return []
    
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
                if yas_gercek is not None:
                    yas_int = int(yas_gercek)
                    if yas_int <= 7:
                        kullanici_cevap = "0-7"
                    else:
                        kullanici_cevap = "7+"
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
            
            # Eşleşme kontrolü
            if isinstance(kullanici_cevap, list):
                # Çoklu seçim için
                for cevap in kullanici_cevap:
                    if str(cevap).lower() in str(yastik_ozellik).lower():
                        toplam_puan += agirlik
                        break
            else:
                # Tek seçim için
                kullanici_cevap_str = str(kullanici_cevap).lower().strip()
                yastik_ozellik_str = str(yastik_ozellik).lower().strip()
                
                kullanici_cevap_normalized = normalize_turkish(kullanici_cevap_str)
                yastik_ozellik_normalized = normalize_turkish(yastik_ozellik_str)
                
                if kullanici_cevap_normalized in yastik_ozellik_normalized:
                    toplam_puan += agirlik
        
        # BMI için özel kontrol
        bmi_cevap = responses.get('bmi')
        if bmi_cevap and yastik.bmi:
            bmi_cevap_str = str(bmi_cevap).lower().strip()
            bmi_yastik_str = str(yastik.bmi).lower().strip()
            
            bmi_cevap_normalized = normalize_turkish(bmi_cevap_str)
            bmi_yastik_normalized = normalize_turkish(bmi_yastik_str)
            
            if bmi_cevap_normalized in bmi_yastik_normalized:
                toplam_puan += SORU_AGIRLIKLARI.get('bmi', 2)

        # İdeal sertlik için özel kontrol
        ideal_sertlik_cevap = responses.get('ideal_sertlik')
        if ideal_sertlik_cevap and yastik.sertlik:
            ideal_sertlik_str = str(ideal_sertlik_cevap).lower().strip()
            yastik_sertlik_str = str(yastik.sertlik).lower().strip()
            
            ideal_sertlik_normalized = normalize_turkish(ideal_sertlik_str)
            yastik_sertlik_normalized = normalize_turkish(yastik_sertlik_str)
            
            # Direkt eşleşme kontrolü
            if ideal_sertlik_normalized in yastik_sertlik_normalized:
                toplam_puan += agirlik
            else:
                # İçinde geçen kelimelere göre eşleşme
                if ideal_sertlik_cevap == 'Sert' and ('sert' in yastik_sertlik_normalized or 'orta-sert' in yastik_sertlik_normalized):
                    toplam_puan += agirlik
                elif ideal_sertlik_cevap == 'Orta' and ('orta' in yastik_sertlik_normalized or 'orta-sert' in yastik_sertlik_normalized or 'yumusak-orta' in yastik_sertlik_normalized):
                    toplam_puan += agirlik
                elif ideal_sertlik_cevap == 'Yumuşak' and ('yumusak' in yastik_sertlik_normalized or 'yumusak-orta' in yastik_sertlik_normalized):
                    toplam_puan += agirlik
                elif ideal_sertlik_cevap == 'Orta-Sert' and ('orta-sert' in yastik_sertlik_normalized or 'sert' in yastik_sertlik_normalized or 'orta' in yastik_sertlik_normalized):
                    toplam_puan += agirlik

        # Doğal malzeme alerjisi için özel kontrol
        dogal_malzeme_cevap = responses.get('dogal_malzeme')
        if dogal_malzeme_cevap:
            # Kullanıcı alerjisi varsa
            if 'evet' in str(dogal_malzeme_cevap).lower():
                # Yastık doğal malzemeli mi kontrol et
                yastik_dogal_malzeme = yastik.dogal_malzeme or ''
                dogal_malzemeler = ['kaz tüyü', 'yün', 'bambu', 'pamuk', 'doğal', 'organik']
                
                # Yastık doğal malzemeli ise puanı sıfırla
                for malzeme in dogal_malzemeler:
                    if malzeme.lower() in yastik_dogal_malzeme.lower():
                        toplam_puan = 0  # Alerjik kullanıcı için doğal malzemeli yastık uygun değil
                        break

        # Yastık ve puanını listeye ekle
        yastik_puanlari.append({
            'yastik': yastik.to_dict(),
            'puan': toplam_puan
        })
    
    # Yaş kontrolü - 0-7 yaş seçildiyse özel algoritma
    yas_cevap = responses.get('bmi_age', {}).get('yas_gercek')
    if yas_cevap and int(yas_cevap) < 7:
        # 0-7 yaş için özel algoritma
        bebek_yastiklar = []
        onemli_eslesenler = []
        diger_yastiklar = []
        
        for item in yastik_puanlari:
            yastik_yas = item['yastik'].get('yas', '')
            yastik_isim = item['yastik'].get('isim', '').lower()
            if yastik_yas and ('0-7' in str(yastik_yas).lower() or 'bebek' in yastik_isim):
                bebek_yastiklar.append(item)
            else:
                onemli_eslesme_var = False
                for soru_key, agirlik in SORU_AGIRLIKLARI.items():
                    if agirlik >= 5:
                        kullanici_cevap = responses.get(soru_key)
                        if kullanici_cevap:
                            yastik_ozellik = item['yastik'].get(soru_key, '')
                            if yastik_ozellik:
                                kullanici_normalized = normalize_turkish(str(kullanici_cevap).lower().strip())
                                yastik_normalized = normalize_turkish(str(yastik_ozellik).lower().strip())
                                if kullanici_normalized in yastik_normalized:
                                    onemli_eslesme_var = True
                                    break
                if onemli_eslesme_var:
                    onemli_eslesenler.append(item)
                else:
                    diger_yastiklar.append(item)
        
        bebek_yastiklar.sort(key=lambda x: x['puan'], reverse=True)
        onemli_eslesenler.sort(key=lambda x: x['puan'], reverse=True)
        diger_yastiklar.sort(key=lambda x: x['puan'], reverse=True)
        
        sonuc_listesi = []
        sonuc_listesi.extend(bebek_yastiklar[:2])
        sonuc_listesi.extend(onemli_eslesenler[:2])
        sonuc_listesi.extend(diger_yastiklar[:1])
        yastik_puanlari = sonuc_listesi[:5]
        
        # Debug için puanları yazdır
        print("=== 0-7 YAŞ ALGORİTMASI (2 bebek + 2 önemli + 1 diğer) ===")
        for i, item in enumerate(yastik_puanlari):
            print(f"{i+1}. {item['yastik']['isim']} - Puan: {item['puan']}")
    else:
        # 7+ yaş için: bebek yastıkları hariç, normal puan sıralaması
        yastiklar_yas_bebek_haric = []
        for item in yastik_puanlari:
            yastik_yas = item['yastik'].get('yas', '')
            yastik_isim = item['yastik'].get('isim', '').lower()
            if not (yastik_yas and ('0-7' in str(yastik_yas).lower() or 'bebek' in yastik_isim)):
                yastiklar_yas_bebek_haric.append(item)
        yastiklar_yas_bebek_haric.sort(key=lambda x: x['puan'], reverse=True)
        yastik_puanlari = yastiklar_yas_bebek_haric
    
    # İlk 5 yastığı döndür
    return [item['yastik'] for item in yastik_puanlari[:5]]

QUESTIONS = [
    {
        'id': 'bmi_age',
        'question': 'Yaşınızı, boyunuzu ve kilonuzu giriniz.',
        'type': 'bmi_age',
        'info': 'Yaş, boy ve kilo gibi fiziksel bilgiler; ideal yastık yüksekliği ve destek düzeyini belirlememize yardımcı olur. Bu bilgiler yalnızca daha doğru bir öneri sunmak amacıyla kullanılacaktır.',
        'order': 1
    },
    {'id': 'uyku_pozisyonu', 'question': 'Sizin için en rahat uyku pozisyonunu seçer misiniz?', 'type': 'checkbox', 'options': ['Sırt üstü uyku pozisyonu', 'Yüz üstü uyku pozisyonu', 'Yan uyku pozisyonu', 'Hareketli Uyku Pozisyonu'], 'info': 'Uyku pozisyonu, boyun ve omurga sağlığınızı doğrudan etkiler. Doğru yastık, uyku tarzınıza uyum sağlamalıdır.', 'order': 2},
    {'id': 'ideal_sertlik', 'question': 'Sizin için ideal yastık sertliği nedir?', 'type': 'radio', 'options': ['Yumuşak', 'Orta', 'Sert', 'Orta-Sert'], 'info': 'Yastık sertliği, baş ve boynunuza ne kadar destek verdiğini belirler. Yumuşak yastıklar daha çok batarken, sert yastıklar daha sıkı bir yapı sunar. Konforunuz için size en uygun olanı seçin.', 'order': 3},
    {'id': 'uyku_düzeni', 'question': 'Uyku düzeniniz genellikle nasıldır?', 'type': 'radio', 'options': ['Uykum terleme nedeniyle bölünüyor.', 'Hiçbir problem yaşamıyorum, sabahları dinlenmiş uyanıyorum.','Nefes almakta zorlanıyorum, zaman zaman horlama problemi yaşıyorum','Reflü nedeniyle geceleri sık sık uyanıyorum.'], 'info': 'Terleme sorunu için özel yastıklar mevcuttur.', 'order': 4},
    {'id': 'tempo', 'question': 'Günlük yaşam temponuzu nasıl tanımlarsınız?', 'type': 'radio', 'options': ['Oldukça sakin bir tempom var.','Genelde orta tempoda, dengeli bir günüm oluyor.', 'Yoğun tempolu bir gün geçiriyorum.'], 'info': 'Yoğun tempolu yaşamda vücut daha fazla destek ve dinlenmeye ihtiyaç duyar. Doğru yastık, günün yorgunluğunu hafifletir.', 'order': 5},
    {'id': 'agri_bolge', 'question': 'Sabahları belirli bir bölgede ağrı hissediyor musunuz?', 'type': 'checkbox', 'options': ['Hiçbir ağrı hissetmiyorum', 'Bel', 'Omuz', 'Boyun', 'Hepsi'], 'info': 'Boyun, omuz veya bel ağrısı; yanlış yastık seçiminden kaynaklanıyor olabilir. Vücudunuzu dinleyin, ihtiyacınıza uygun yastığı seçin.', 'order': 6},
    {'id': 'dogal_malzeme', 'question': 'Doğal malzemelere (kaz tüyü,yün,bambu,pamuk gibi) karşı alerjiniz veya hassasiyetiniz var mı ?', 'type': 'checkbox', 'options': ['Evet,bu tür doğal malzemelere karşı alerjim,hassasiyetim var', 'Hayır,yok'], 'info': 'Bazı kişiler doğal dolgu malzemelerine (kaz tüyü,yün,bambu,pamuk gibi) karşı alerjik reaksiyon veya hassasiyet gösterebilir.Bu kişiler için,elyaf dolgulu veya visco sünger dolgulu ürünlerin kullanımı daha sağlıklı ve konforlu bir tercih olabilir', 'order': 7},
    
    {'id': 'sertlik', 'question': 'Yatak sertlik derecenizi belirtir misiniz?', 'type': 'radio', 'options': ['Yumuşak Yatak', 'Orta Yatak', 'Sert Yatak'], 'info': 'Yatak sertliği, yastığın yüksekliği ve dolgunluğu ile uyumlu olmalı. Uyumlu ikili, daha sağlıklı bir uyku sağlar.', 'order': 8}
]

# --- API Endpoint'leri ---
@app.route('/')
def home():
    return jsonify({
        'message': 'Pillow Selection Robot API',
        'version': '1.0',
        'endpoints': [
            '/api/questions',
            '/api/yastiklar', 
            '/api/recommend',
            '/api/kvkk_metin',
            '/api/kvkk_onay_ekle',
            '/api/health'
        ]
    })

@app.route('/api/health')
def health_check():
    """Sistem sağlık kontrolü endpoint'i"""
    try:
        # Database bağlantısını test et
        with db.engine.connect() as conn:
            conn.execute(db.text('SELECT 1'))
        
        # Redis artık kullanılmıyor - in-memory storage kullanılıyor
        environment = os.getenv('FLASK_ENV', 'development')
        redis_status = 'not_used'
        
        return jsonify({
            'status': 'healthy',
            'database': 'healthy',
            'redis': redis_status,
            'environment': environment,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 500

@app.route('/api/questions')
def get_questions():
    try:
        sorted_questions = sorted(QUESTIONS, key=lambda x: x['order'])
        return jsonify(questions=sorted_questions)
    except Exception as e:
        print(f"Soru getirme hatası: {e}")
        return jsonify(error="Sorular yüklenirken bir hata oluştu."), 500

@app.route('/api/yastiklar')
def get_yastiklar():
    try:
        yastiklar = Yastik.query.all()
        return jsonify(yastiklar=[y.to_dict() for y in yastiklar])
    except Exception as e:
        print(f"Yastık getirme hatası: {e}")
        return jsonify(error="Yastıklar yüklenirken bir hata oluştu."), 500



@app.route('/api/recommend', methods=['POST'])
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

        # Yeni fonksiyonu kullanarak önerileri hesapla
        recommendations = calculate_pillow_recommendations(responses)
        
        if not recommendations:
            return jsonify(error="Veritabanında yastık bulunamadı."), 500
        
        return jsonify(recommendations=recommendations, log_id=log.id)

    except Exception as e:
        print(f"Öneri sırasında hata: {e}")
        traceback.print_exc()
        return jsonify(error="Sunucu hatası."), 500

@app.route('/api/kvkk_onay_ekle', methods=['POST'])
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
        onay_tarihi = datetime.now(timezone.utc)
        onay = KvkkOnay(
            log_id=log_id,
            kvkk_metin_id=kvkk_metin_id,
            ip_adresi=ip_adresi,
            onay_tarihi=onay_tarihi,
            onay_durumu=onay_durumu,
            onay_yontemi=onay_yontemi,
        )
        db.session.add(onay)
        db.session.commit()
        return jsonify({'success': True, 'onay_id': onay.id})
    except Exception as e:
        print(f"KVKK onay ekleme hatası: {e}")
        traceback.print_exc()
        return jsonify({'error': 'Sunucu hatası'}), 500

@app.route('/api/kvkk_aktif_pdf')
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

@app.route('/api/log_urun_inceleme', methods=['POST'])
def log_urun_inceleme():
    try:
        data = request.get_json()
        log_id = data.get('log_id')
        urun_ismi = data.get('urun_ismi')
        if not log_id or not urun_ismi:
            return jsonify({'error': 'log_id ve urun_ismi zorunlu!'}), 400
        log = db.session.get(KullaniciLog, log_id)
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

@app.route('/api/kvkk_metin', methods=['GET'])
def get_kvkk_metin():
    kvkk = KvkkMetin.query.filter_by(aktif=True).first()
    if not kvkk:
        return jsonify({'error': 'KVKK metni bulunamadı'}), 404
    return jsonify({
        'id': kvkk.id,
        'versiyon': kvkk.versiyon,
        'icerik': kvkk.icerik
    })

@app.route('/api/save-mail', methods=['POST'])
def save_mail():
    data = request.json
    email = data.get('email')
    log_id = data.get('logId')
    analiz_alindi_mi = data.get('analizAlindiMi', False)
    from_address = data.get('from_address')
    bcc_emails = data.get('bcc_emails')
    analysis_html = data.get('analysisHtml')

    if not log_id:
        return jsonify({'error': 'logId zorunlu!'}), 400

    log = db.session.get(KullaniciLog, log_id)
    if not log:
        return jsonify({'error': 'Log bulunamadı!'}), 404

    if email:
        log.email = email
        
        # Kullanıcı cevaplarını al
        responses = json.loads(log.cevaplar) if log.cevaplar else {}
        
        # Frontend'den öneri listesi geldiyse onu kullan, yoksa hesapla
        incoming_recs = data.get('recommendations')
        recommendations = None
        if isinstance(incoming_recs, list) and len(incoming_recs) > 0:
            recommendations = incoming_recs
        else:
            recommendations = calculate_pillow_recommendations(responses)
        
        if recommendations:
            # Frontend mantığıyla aynı: Diz Arası Yastık ana listede görünmesin
            def normalize(s: str) -> str:
                try:
                    return s.lower().encode('utf-8').decode('utf-8')
                except Exception:
                    return (s or '').lower()

            def is_knee_pillow(name: str) -> bool:
                if not name:
                    return False
                n = normalize(name)
                return ('diz arası' in n) or ('diz arasi' in n)

            cards_html = []
            for yastik in recommendations:
                name = yastik.get('isim') or 'Yastık'
                if is_knee_pillow(name):
                    continue  # ana listede göstermiyoruz
                img = yastik.get('gorsel') or ''
                href = yastik.get('link') or ''
                uyku_poz = normalize(yastik.get('uyku_pozisyonu') or '')
                is_perfect_match = 'yan' in uyku_poz

                # Kart: İsim + Görsel (tıklanabilir) + Ürünü İncele + (opsiyonel rozet)
                piece = '<div style="display:inline-block;vertical-align:top;margin:10px;padding:12px;border:1px solid #eee;border-radius:10px;text-align:center;max-width:240px;position:relative;">'
                if is_perfect_match:
                    piece += '<div style="position:absolute;top:8px;right:8px;background:#ff6f00;color:#fff;font-size:11px;font-weight:700;padding:6px 8px;border-radius:999px;line-height:1;">⭐ Mükemmel Eşleşme</div>'
                piece += f'<div style="font-weight:600;margin-bottom:8px;color:#333;">{name}</div>'
                if img:
                    if href:
                        piece += f'<a href="{href}" target="_blank" rel="noopener noreferrer"><img src="{img}" alt="{name}" style="max-width:220px;height:auto;border-radius:8px;border:1px solid #f0f0f0;"/></a>'
                    else:
                        piece += f'<img src="{img}" alt="{name}" style="max-width:220px;height:auto;border-radius:8px;border:1px solid #f0f0f0;"/>'
                if href:
                    piece += f'<div style="margin-top:10px;"><a href="{href}" target="_blank" rel="noopener noreferrer" style="display:inline-block;padding:8px 14px;border-radius:6px;background:#1976d2;color:#fff;text-decoration:none;">Ürünü İncele</a></div>'

                # Mükemmel Eşleşme ise aynı kutu içinde "+" ikonu ve Diz Arası Yastık mini-kartı
                if is_perfect_match:
                    knee_href = 'https://www.doquhome.com.tr/urun/diz-arasi-yastik-26-x-21-x-16-5-cm-beyaz'
                    knee_img = 'https://www.doquhome.com.tr/idea/kl/05/myassets/products/672/diz-arasi-yastik04.jpg?revision=1751466969'
                    piece += '<div style="margin-top:12px;border-top:1px dashed #e5e5e5;padding-top:10px;text-align:center;">'
                    piece += '<div style="display:inline-flex;align-items:center;gap:6px;color:#444;font-weight:600;font-size:12px;margin-bottom:6px;">'
                    piece += '<span style="display:inline-block;width:18px;height:18px;border-radius:50%;background:#2e7d32;color:#fff;line-height:18px;text-align:center;font-weight:700;">+</span>'
                    piece += 'Diz Arası Yastık</div>'
                    piece += f'<a href="{knee_href}" target="_blank" rel="noopener noreferrer" style="display:inline-block;">'
                    piece += f'<img src="{knee_img}" alt="Diz Arası Yastık" style="max-width:180px;height:auto;border-radius:8px;border:1px solid #f0f0f0;"/>'
                    piece += '</a>'
                    piece += f'<div style="margin-top:8px;"><a href="{knee_href}" target="_blank" rel="noopener noreferrer" style="display:inline-block;padding:6px 12px;border-radius:6px;background:#455a64;color:#fff;text-decoration:none;font-size:12px;">Ürünü İncele</a></div>'
                    piece += '</div>'

                piece += '</div>'
                cards_html.append(piece)

            yastik_html = f'''<div style="text-align:center;">{''.join(cards_html)}</div>'''

            complete_mail_content = f'''
            {analysis_html or ''}
            <hr style="margin: 24px 0; border: 1px solid #ddd;">
            {yastik_html}
            '''
        else:
            complete_mail_content = analysis_html or log.cevaplar
        
        mail_sent = send_analysis_email(email, complete_mail_content, from_address, bcc_emails)
        if not mail_sent:
            return jsonify({'error': 'Mail gönderilemedi!'}), 500
    
    log.analiz_sonucu_alindi_mi = analiz_alindi_mi
    db.session.commit()
    
    return jsonify({'success': True})
# Uygulamayı çalıştırmak için
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    environment = os.getenv('FLASK_ENV', 'development')
    if environment != 'production':
        print("🚀 Backend geliştirme modunda başlatılıyor... http://localhost:5001")
        app.run(debug=True, host='0.0.0.0', port=5001)
    else:
        print("Production ortamı: Lütfen bir WSGI sunucusu ile başlatın (örn. waitress, IIS, vs.)") 