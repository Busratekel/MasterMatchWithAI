from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import traceback
import os
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

app = Flask(__name__)

# Geliştirme sırasında tüm kaynaklardan gelen isteklere izin ver
CORS(app, resources={r"/*": {"origins": "*"}})

# Veritabanı Yapılandırması - .env dosyasından güvenli şekilde oku
db_username = os.getenv('DB_USERNAME')
db_password = os.getenv('DB_PASSWORD')
db_server = os.getenv('DB_SERVER')
db_port = os.getenv('DB_PORT')
db_name = os.getenv('DB_NAME')
db_driver = os.getenv('DB_DRIVER')

# Veritabanı URI'sini oluştur
database_uri = f"mssql+pyodbc://{db_username}:{db_password}@{db_server},{db_port}/{db_name}?driver={db_driver}"

app.config['SQLALCHEMY_DATABASE_URI'] = database_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- Veritabanı Modelleri ---
class Yastik(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    isim = db.Column(db.String(150), nullable=False)
    gorsel = db.Column(db.String(250))
    link = db.Column(db.String(250))
    sertlik = db.Column(db.String(50))
    uyku_pozisyonu = db.Column(db.String(150))
    bmi = db.Column(db.String(50))
    dogal_malzeme = db.Column(db.String(10))
    terleme = db.Column(db.String(10))
    agri_bolge = db.Column(db.String(150))
    yas = db.Column(db.String(50))
    tempo = db.Column(db.String(50))
    mide_rahatsizligi = db.Column(db.String(10))
    nefes_problemi = db.Column(db.String(10))

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

# --- Sabit Veriler ---
SORU_AGIRLIKLARI = {
    'sertlik': 1, 'bmi': 2, 'uyku_pozisyonu': 3, 'dogal_malzeme': 4,
    'terleme': 5, 'tempo': 6, 'agri_bolge': 7, 'yas': 8,
    'mide_rahatsizligi': 9, 'nefes_problemi': 10
}

QUESTIONS = [
    {'id': 'bmi', 'question': 'Boyunuz ve Kilonuz? (BMI)', 'type': 'checkbox', 'options': ['ZAYIF', 'ORTA', 'KİLOLU', 'HEPSİ'], 'info': 'Vücut kitle indeksiniz yastık seçiminde önemlidir.', 'order': 1},
    {'id': 'yas', 'question': 'Yaşınız?', 'type': 'radio', 'options': ['0-7', '7+'], 'info': 'Yaşınız yastık seçiminde dikkate alınır.', 'order': 2},
    {'id': 'uyku_pozisyonu', 'question': 'Genellikle hangi uyku pozisyonunda uyuyorsunuz?', 'type': 'checkbox', 'options': ['SIRT ÜSTÜ', 'YÜZ ÜSTÜ UYKU POZİSYONU', 'YAN UYKU POZİSYONU', 'HEPSİ'], 'info': 'Uyku pozisyonunuz yastık seçiminde kritik öneme sahiptir.', 'order': 3},
    {'id': 'tempo', 'question': 'Gün içerisinde iş, spor vb. tempo yoğunluğunuz nasıl?', 'type': 'radio', 'options': ['NORMAL', 'YOĞUN'], 'info': 'Günlük aktivite seviyeniz yastık seçimini etkiler.', 'order': 4},
    {'id': 'terleme', 'question': 'Uyurken terleme probleminiz var mı?', 'type': 'radio', 'options': ['EVET', 'HAYIR'], 'info': 'Terleme sorunu için özel yastıklar mevcuttur.', 'order': 5},
    {'id': 'agri_bolge', 'question': 'Uyurken veya sabah uyandığınızda vücudunuzun hangi bölgelerinde ağrı hissediyorsunuz?', 'type': 'checkbox', 'options': ['HİSSETMİYORUM', 'BEL', 'OMUZ', 'BOYUN', 'HEPSİ'], 'info': 'Ağrı bölgeleriniz yastık seçiminde dikkate alınır.', 'order': 6},
    {'id': 'mide_rahatsizligi', 'question': 'Uyku düzeninizi etkileyen mide asidi veya reflü gibi bir rahatsızlığınız var mı?', 'type': 'radio', 'options': ['EVET', 'HAYIR'], 'info': 'Mide rahatsızlıkları için özel yastıklar mevcuttur.', 'order': 7},
    {'id': 'nefes_problemi', 'question': 'Uyurken nefes alıp verme düzeninizde herhangi bir zorlanma veya rahatsızlık yaşıyor musunuz?', 'type': 'radio', 'options': ['EVET', 'HAYIR'], 'info': 'Nefes problemleri için özel yastıklar mevcuttur.', 'order': 8},
    {'id': 'dogal_malzeme', 'question': 'Doğal malzemelerden yapılmış yastıklar (örneğin, pamuk, yün, bambu) sizin için önemli mi?', 'type': 'radio', 'options': ['EVET', 'HAYIR'], 'info': 'Doğal malzemeler alerjik reaksiyonları azaltabilir.', 'order': 9},
    {'id': 'sertlik', 'question': 'Son olarak size daha doğru sonuçlar verebilmemiz adına, yatağınızın sertlik derecesi nedir?', 'type': 'checkbox', 'options': ['YUMUŞAK', 'ORTA', 'SERT', 'HEPSİ'], 'info': 'Yatağınızın sertlik derecesi yastık seçiminde önemlidir.', 'order': 10}
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
        responses = request.get_json().get('responses', {})
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
                choices = [str(c).lower().strip() for c in (response if isinstance(response, list) else [response])]
                pillow_attr_lower = str(pillow_attr).lower().strip()
                if 'hepsi' in choices: return True
                choices = [c for c in choices if c and 'hissetmiyorum' not in c]
                for choice in choices:
                    if choice.split(' ')[0] in pillow_attr_lower:
                        return True
                return False

            def is_positive_match(key, pillow_attr):
                response = str(responses.get(key, 'Hayır')).lower()
                return 'evet' in response and 'evet' in str(pillow_attr).lower()

            # Puanlama
            if is_match('sertlik', yastik.sertlik): score += SORU_AGIRLIKLARI.get('sertlik', 1)
            if is_match('uyku_pozisyonu', yastik.uyku_pozisyonu): score += SORU_AGIRLIKLARI.get('uyku_pozisyonu', 1)
            if is_match('bmi', yastik.bmi): score += SORU_AGIRLIKLARI.get('bmi', 1)
            if is_match('agri_bolge', yastik.agri_bolge): score += SORU_AGIRLIKLARI.get('agri_bolge', 1)
            if is_match('yas', yastik.yas): score += SORU_AGIRLIKLARI.get('yas', 1)
            if is_match('tempo', yastik.tempo): score += SORU_AGIRLIKLARI.get('tempo', 1)
            if is_positive_match('dogal_malzeme', yastik.dogal_malzeme): score += SORU_AGIRLIKLARI.get('dogal_malzeme', 1)
            if is_positive_match('terleme', yastik.terleme): score += SORU_AGIRLIKLARI.get('terleme', 1)
            if is_positive_match('mide_rahatsizligi', yastik.mide_rahatsizligi): score += SORU_AGIRLIKLARI.get('mide_rahatsizligi', 1)
            if is_positive_match('nefes_problemi', yastik.nefes_problemi): score += SORU_AGIRLIKLARI.get('nefes_problemi', 1)

            if score > 0:
                scored_yastiklar.append({'yastik': yastik.to_dict(), 'score': score})

        if not scored_yastiklar:
            return jsonify(recommendations=[])

        sorted_yastiklar = sorted(scored_yastiklar, key=lambda x: x['score'], reverse=True)
        top_yastiklar = sorted_yastiklar[:3]
        
        # Ön yüzün beklediği format
        recommendations = [item['yastik'] for item in top_yastiklar]
        return jsonify(recommendations=recommendations)

    except Exception as e:
        print(f"Öneri sırasında hata: {e}")
        traceback.print_exc()
        return jsonify(error="Sunucu hatası."), 500

# Uygulamayı geliştirme modunda çalıştırmak için
if __name__ == '__main__':
    with app.app_context():
        # Veritabanını otomatik olarak oluşturmayın, bunu manuel olarak veya bir göç aracıyla yapın.
        pass
    app.run(debug=True, port=5000) 