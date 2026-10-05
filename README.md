# 🛏️ Yastık Seçim Robotu

Flask backend ve React frontend ile geliştirilmiş yastık öneri sistemi.

### Geliştirme Ortamı

1. **Backend'i başlat:**
   ```powershell
   cd backend
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   python main.py
   ```

2. **Frontend'i başlat:**
   ```powershell
   cd frontend
   npm install
   npm start
   ```

### Canlı Ortam Deployment

1. **Backend environment dosyası oluştur:**
   ```powershell
   cd backend
   copy env_production.txt .env
   ```

2. **Frontend production build al:**
   ```powershell
   cd frontend
   npm install
   npm run build
   ```

3. **IIS'e manuel deploy et**

## 📁 Proje Yapısı

```
PillowSelectionRobot/
├── backend/                 # Flask API
│   ├── main.py             # Ana uygulama
│   ├── requirements.txt    # Python bağımlılıkları
│   ├── web.config         # IIS yapılandırması
│   ├── env_example.txt    # Geliştirme environment örneği
│   └── env_production.txt # Canlı ortam ayarları
├── frontend/               # React uygulaması
│   ├── src/
│   │   ├── config.js      # API konfigürasyonu (otomatik domain)
│   │   └── components/    # React bileşenleri
│   └── build/             # Production build
└── PRODUCTION_CHECKLIST.md # Canlı ortam kontrol listesi
```

## ⚙️ Environment Dosyaları

### Backend (.env)
```env
# Veritabanı
DATABASE_URL=mssql+pyodbc://username:password@server/database?driver=ODBC+Driver+17+for+SQL+Server

# Mail ayarları
MAIL_SERVER=smtp.office365.com
MAIL_PORT=587
MAIL_USERNAME=your-email@domain.com
MAIL_PASSWORD=your-password
MAIL_DEFAULT_SENDER=your-email@domain.com

# Ortam
FLASK_ENV=production
ALLOWED_ORIGINS=https://mastermatch.doquhome.com.tr
```

### Frontend (Otomatik)
```javascript
// config.js otomatik olarak ortamı algılar:
// Development: http://localhost:5000
// Production: https://mastermatch.doquhome.com.tr
```

## 🔗 API Endpoint'leri

- `GET /api/health` - Sistem sağlık kontrolü
- `GET /api/questions` - Sorular listesi
- `GET /api/yastiklar` - Yastık listesi
- `POST /api/recommend` - Yastık önerisi
- `POST /api/kvkk_onay_ekle` - KVKK onayı
- `GET /api/kvkk_metin` - KVKK metni
- `POST /api/log_urun_inceleme` - Ürün inceleme logu
- `POST /api/save-mail` - Mail gönderme

## 🌐 URL'ler

### Geliştirme Ortamı
- **Frontend:** http://localhost:3000
- **Backend:** http://localhost:5001
- **API Health:** http://localhost:5001/api/health

### Canlı Ortam
- **Site:** https://mastermatch.doquhome.com.tr
- **API:** https://mastermatch.doquhome.com.tr/api


### 3. IIS Yapılandırması
- **Ana Site:** `PillowSelectionRobot` → `C:\inetpub\wwwroot\PillowSelectionRobot`
- **API Alt Uygulaması:** `api` → `C:\inetpub\wwwroot\PillowSelectionRobot\backend`
- **Application Pool:** `.NET CLR Version: No Managed Code`

## 📋 Kontrol Listesi

Detaylı kontrol listesi için [PRODUCTION_CHECKLIST.md](PRODUCTION_CHECKLIST.md) dosyasını inceleyin.

## 🚨 Sorun Giderme

### FastCGI Sorunları
```powershell
pip uninstall wfastcgi
pip install wfastcgi
wfastcgi-enable
``` 
