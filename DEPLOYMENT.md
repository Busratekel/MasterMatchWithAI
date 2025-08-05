# 🚀 Deployment Rehberi

## 📋 Ön Gereksinimler

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
git clone https://github.com/your-username/PillowSelectionRobotyeni.git
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

## 🔐 Environment Yapılandırması

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

## 🚀 Production Deployment

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

## 🐛 Sorun Giderme

### API Bağlantı Sorunları

```powershell
# Health kontrolü
Invoke-WebRequest -Uri "https://yourdomain.com/api/health"

# Event Viewer kontrolü
Get-EventLog -LogName Application -Source W3SVC* -Newest 10
```

### IIS Sorunları

1. **Application Pool durumunu kontrol edin**
2. **Dosya izinlerini kontrol edin**
3. **FastCGI ayarlarını kontrol edin**

### Database Sorunları

1. **ODBC Driver'ı kontrol edin**
2. **Connection string'i test edin**
3. **Firewall ayarlarını kontrol edin**

## 📊 Monitoring

### Log Dosyaları

- **Backend**: `backend/app.log`
- **IIS**: `C:\inetpub\logs\LogFiles`
- **Event Viewer**: Application logs

### Health Checks

- **API**: `GET /api/health`
- **Frontend**: Ana sayfa yükleniyor mu?
- **Database**: Bağlantı testi

## 🔄 Güncelleme Süreci

### 1. Yeni Versiyon Hazırlama

```bash
# Yeni branch oluştur
git checkout -b release/v1.1.0

# Değişiklikleri commit et
git add .
git commit -m "v1.1.0 release"

# Push et
git push origin release/v1.1.0
```

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

### 3. Restart İşlemleri

```powershell
# IIS restart
iisreset

# Application Pool restart
Import-Module WebAdministration
Restart-WebAppPool "PillowSelectionRobot"
```

## 📞 Destek

### Acil Durumlar

1. **Sistem çökmesi**: Backup'tan restore
2. **Database sorunu**: MSSQL Management Studio ile kontrol
3. **Mail sorunu**: SMTP ayarlarını kontrol et
4. **SSL sorunu**: Sertifika yenileme

### İletişim

- **Teknik Destek**: support@domain.com
- **Acil Durum**: +90 XXX XXX XX XX
- **Dokümantasyon**: [GitHub Wiki](https://github.com/your-username/PillowSelectionRobotyeni/wiki)

---

**Son Güncelleme**: 2024
**Versiyon**: 1.0 