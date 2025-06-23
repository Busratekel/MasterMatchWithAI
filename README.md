# Pillow Selection Robot

Yastık seçimi için akıllı öneri sistemi. Bu proje, kullanıcıların ihtiyaçlarına göre en uygun yastığı öneren bir web uygulamasıdır.

## 🚀 Özellikler

- **Akıllı Soru Sistemi**: Kullanıcının uyku alışkanlıklarını analiz eden adım adım soru sistemi
- **Kişiselleştirilmiş Öneriler**: Makine öğrenmesi tabanlı yastık önerileri
- **Modern UI/UX**: React ile geliştirilmiş kullanıcı dostu arayüz
- **Responsive Tasarım**: Tüm cihazlarda mükemmel görünüm
- **İlerleme Takibi**: Test sürecinde ilerleme göstergesi
- **Otomatik Kaydetme**: Test durumunu otomatik olarak kaydetme

## 🛠️ Teknolojiler

### Backend
- **Python 3.11**
- **Flask** - Web framework
- **SQLAlchemy** - ORM
- **scikit-learn** - Makine öğrenmesi
- **pandas** - Veri işleme
- **openpyxl** - Excel dosya işleme

### Frontend
- **React 18**
- **CSS3** - Styling
- **HTML5** - Markup

## 📦 Kurulum

### Gereksinimler
- Python 3.11+
- Node.js 16+
- npm veya yarn
- SQL Server (veya başka bir veritabanı)

### Backend Kurulumu

1. Backend klasörüne gidin:
```bash
cd backend
```

2. Virtual environment oluşturun:
```bash
python -m venv venv
```

3. Virtual environment'ı aktifleştirin:
```bash
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

4. Gerekli paketleri yükleyin:
```bash
pip install -r requirements.txt
```

5. **ÖNEMLİ**: Veritabanı yapılandırması için `.env` dosyası oluşturun:
```bash
# .env.example dosyasını .env olarak kopyalayın
cp .env.example .env
```

6. `.env` dosyasını düzenleyin ve kendi veritabanı bilgilerinizi girin:
```env
DB_USERNAME=your_username
DB_PASSWORD=your_password
DB_SERVER=your_server_name
DB_PORT=1433
DB_NAME=your_database_name
DB_DRIVER=ODBC+Driver+17+for+SQL+Server
```

7. Uygulamayı çalıştırın:
```bash
python main.py
```

Backend `http://localhost:5000` adresinde çalışacaktır.

### Frontend Kurulumu

1. Frontend klasörüne gidin:
```bash
cd frontend
```

2. Bağımlılıkları yükleyin:
```bash
npm install
```

3. Uygulamayı çalıştırın:
```bash
npm start
```

Frontend `http://localhost:3000` adresinde çalışacaktır.

## 🔒 Güvenlik

- **Veritabanı bilgileri** `.env` dosyasında saklanır ve GitHub'a yüklenmez
- **Hassas bilgiler** kod içinde hardcode edilmemiştir
- **Environment variables** kullanılarak güvenlik sağlanmıştır

## 🎯 Kullanım

1. Tarayıcınızda `http://localhost:3000` adresine gidin
2. "Teste Başla" butonuna tıklayın
3. Soruları adım adım cevaplayın
4. Sonuçlarınızı görüntüleyin

## 📁 Proje Yapısı

```
PillowSelectionRobot/
├── backend/                 # Flask backend
│   ├── main.py             # Ana uygulama dosyası
│   ├── import_yastiklar.py # Veri import scripti
│   ├── check_excel_columns.py # Excel kontrol scripti
│   ├── .env                # Veritabanı bilgileri (GitHub'a yüklenmez)
│   ├── .env.example        # Örnek .env dosyası
│   ├── requirements.txt    # Python bağımlılıkları
│   ├── venv/               # Python virtual environment
│   └── instance/           # SQLite veritabanı
├── frontend/               # React frontend
│   ├── src/
│   │   ├── App.js          # Ana React bileşeni
│   │   ├── components/     # React bileşenleri
│   │   └── assets/         # Statik dosyalar
│   ├── package.json        # Node.js bağımlılıkları
│   └── public/             # Public dosyalar
├── .gitignore              # Git ignore dosyası
└── README.md               # Bu dosya
```

## 🔧 Geliştirme

### Backend Geliştirme
- Flask debug modu aktif
- SQLite veritabanı kullanılıyor
- CORS desteği mevcut
- Environment variables ile güvenli yapılandırma

### Frontend Geliştirme
- Hot reload aktif
- ESLint kuralları uygulanıyor
- Modern React hooks kullanılıyor

## 📝 API Endpoints

- `GET /questions` - Soruları getir
- `POST /recommend` - Yastık önerisi al
- `GET /health` - Sağlık kontrolü

## 🤝 Katkıda Bulunma

1. Bu repository'yi fork edin
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Değişikliklerinizi commit edin (`git commit -m 'Add amazing feature'`)
4. Branch'inizi push edin (`git push origin feature/amazing-feature`)
5. Pull Request oluşturun

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

## 👥 İletişim

Proje Sahibi - [@busra_tekel](https://github.com/busra_tekel)

Proje Linki: [https://github.com/busra_tekel/PillowSelectionRobot](https://github.com/busra_tekel/PillowSelectionRobot) 