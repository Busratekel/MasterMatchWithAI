#  Deployment Rehberi

##  Ön Gereksinimler

### Sistem Gereksinimleri
- **Python**: 3.8+
- **Node.js**: 16+
- **MSSQL Server**: 2019+
- **IIS**: 10+
- **Git**: 2.30+

### Yazılım Gereksinimleri
- **Flask**: 3.0.0+
- **React**: 18.2.0+
- **ODBC Driver**: 17 for SQL Server

## 🔧 Kurulum Adımları

### 1. Repository'yi Klonlayın

```bash
git clone https://github.com/your-username/MasterMatchWithAI.git
cd PillowSelectionRobotyeni
```

### 2. Backend Kurulumu

```bash
cd backend

# Virtual environment oluştur
python -m venv venv

# Virtual environment'ı aktifleştir
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Bağımlılıkları yükle
pip install -r requirements.txt

# Environment dosyası oluştur
copy env_example.txt .env
# .env dosyasını düzenleyin
```

### 3. Frontend Kurulumu

```bash
cd frontend

# Bağımlılıkları yükle
npm install

# Environment dosyası oluştur
copy env.example .env
# .env dosyasını düzenleyin
```

## Environment Yapılandırması

### Backend (.env)

```env
# Veritabanı
DATABASE_URL=mssql+pyodbc://username:password@server/database?driver=ODBC+Driver+17+for+SQL+Server

# Mail ayarları
MAIL_SERVER=smtp.office365.com
MAIL_PORT=587
MAIL_USERNAME=your-email@domain.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=your-email@domain.com

# Güvenlik
SECRET_KEY=your-super-secret-key-here
FLASK_ENV=production
```

### Frontend (.env)

```env
# API URL
REACT_APP_API_URL=https://yourdomain.com

# Uygulama ayarları
REACT_APP_NAME=Yastık Seçim Robotu
REACT_APP_VERSION=1.0.0
```

##  Production Deployment

### 1. Backend Deployment

```bash
cd backend

# Production build
pip install wfastcgi
wfastcgi-enable

# IIS'e kopyala
# C:\inetpub\wwwroot\PillowSelectionRobot\backend\
```

### 2. Frontend Deployment

```bash
cd frontend

# Production build
npm run build

# IIS'e kopyala
# C:\inetpub\wwwroot\PillowSelectionRobot\
```

### 3. IIS Yapılandırması

#### Ana Site
- **Site Adı**: `PillowSelectionRobot`
- **Physical Path**: `C:\inetpub\wwwroot\PillowSelectionRobot`
- **Port**: 80 (HTTP) / 443 (HTTPS)

#### API Alt Uygulaması
- **Alias**: `api`
- **Physical Path**: `C:\inetpub\wwwroot\PillowSelectionRobot\backend`
- **Application Pool**: `.NET CLR Version: No Managed Code`

## 🔒 Güvenlik Kontrolleri

### Pre-deployment Kontrolleri

- [ ] `.env` dosyaları güvenli
- [ ] Hassas bilgiler environment'da
- [ ] HTTPS sertifikası aktif
- [ ] Firewall ayarları doğru
- [ ] Database bağlantısı test edildi

### Post-deployment Kontrolleri

- [ ] API health check başarılı
- [ ] Frontend yükleniyor
- [ ] Mail gönderimi çalışıyor
- [ ] Database bağlantısı stabil
- [ ] Log dosyaları oluşuyor

## Sorun Giderme

### IIS Sorunları

1. **Application Pool durumunu kontrol edin**
2. **Dosya izinlerini kontrol edin**
3. **FastCGI ayarlarını kontrol edin**
## 📊 Monitoring

### Log Dosyaları

- **Backend**: `backend/app.log`
- **IIS**: `C:\inetpub\logs\LogFiles`
- **Event Viewer**: Application logs

### 2. Production'a Deploy

```bash
# Main branch'e merge et
git checkout main
git merge release/v1.1.0

# Production'a push et
git push origin main

# Server'da pull et
git pull origin main
```

