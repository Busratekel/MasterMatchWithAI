# Windows'ta Canlı Ortam Deployment Rehberi

## 🚀 Hızlı Başlangıç

### 1. Docker Desktop Kurulumu
- [Docker Desktop](https://www.docker.com/products/docker-desktop) indirin ve kurun
- Windows'ta WSL2 desteğini etkinleştirin
- Docker Desktop'ı başlatın

### 2. Environment Variables Ayarları
```bash
# env_example.txt dosyasını .env olarak kopyalayın
copy env_example.txt .env
```

`.env` dosyasını düzenleyin:
```env
FLASK_ENV=production
FLASK_DEBUG=False
DATABASE_URL=your_database_url_here
REDIS_URL=redis://redis:6379/0
ALLOWED_ORIGINS=https://yourdomain.com
SECRET_KEY=your_secure_secret_key_here
```

### 3. Production Başlatma
```bash
# Otomatik script ile
start-production.bat

# Veya manuel olarak
docker-compose up -d
```

## 📋 Detaylı Adımlar

### Docker ile Deployment (Önerilen)

#### Avantajları:
- ✅ Sudo gerektirmez
- ✅ Kolay kurulum
- ✅ İzole ortam
- ✅ Taşınabilir
- ✅ Production-ready

#### Adımlar:

1. **Docker Desktop Kurulumu:**
   - [Docker Desktop](https://www.docker.com/products/docker-desktop) indirin
   - Kurulum sırasında WSL2'yi etkinleştirin
   - Docker Desktop'ı başlatın

2. **Proje Hazırlığı:**
   ```bash
   cd backend
   copy env_example.txt .env
   # .env dosyasını düzenleyin
   ```

3. **Servisleri Başlatma:**
   ```bash
   # Otomatik script
   start-production.bat
   
   # Veya manuel
   docker-compose up -d
   ```

4. **Servisleri Kontrol Etme:**
   ```bash
   # Çalışan servisleri görüntüle
   docker-compose ps
   
   # Logları görüntüle
   docker-compose logs -f api
   
   # Health check
   curl http://localhost/health
   ```

### Manuel Kurulum (Docker Olmadan)

#### Gereksinimler:
- Python 3.9+
- Redis (Windows için)
- Gunicorn

#### Adımlar:

1. **Python Kurulumu:**
   - [Python](https://www.python.org/downloads/) indirin
   - PATH'e eklemeyi unutmayın

2. **Redis Kurulumu:**
   - [Redis for Windows](https://github.com/microsoftarchive/redis/releases) indirin
   - Veya WSL2'de Redis çalıştırın

3. **Virtual Environment:**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   pip install gunicorn
   ```

4. **Environment Variables:**
   ```bash
   set FLASK_ENV=production
   set REDIS_URL=redis://localhost:6379/0
   set DATABASE_URL=your_database_url
   ```

5. **Uygulamayı Başlatma:**
   ```bash
   gunicorn -w 4 -b 0.0.0.0:5000 main:app
   ```

## 🔧 Konfigürasyon

### Docker Compose Servisleri:

- **Redis**: Rate limiting için veri saklama
- **API**: Flask uygulaması (Gunicorn ile)
- **Nginx**: Reverse proxy ve SSL termination

### Environment Variables:

| Değişken | Açıklama | Örnek |
|----------|----------|-------|
| `FLASK_ENV` | Ortam türü | `production` |
| `REDIS_URL` | Redis bağlantı URL'i | `redis://redis:6379/0` |
| `DATABASE_URL` | Veritabanı bağlantı URL'i | `sqlite:///instance/app.db` |
| `ALLOWED_ORIGINS` | CORS izin verilen domainler | `https://yourdomain.com` |
| `SECRET_KEY` | Flask secret key | `your-secret-key` |

## 🛠️ Yönetim Komutları

### Docker Komutları:
```bash
# Servisleri başlat
docker-compose up -d

# Servisleri durdur
docker-compose down

# Logları görüntüle
docker-compose logs -f

# Servisleri yeniden başlat
docker-compose restart

# Container'ları yeniden oluştur
docker-compose up -d --build
```

### Monitoring:
```bash
# Container durumları
docker-compose ps

# Kaynak kullanımı
docker stats

# Health check
curl http://localhost/health
```

## 🔒 Güvenlik

### Firewall Ayarları:
- Windows Defender Firewall'da port 80, 443, 5000'i açın
- Sadece gerekli portları açın

### SSL Sertifikası:
```bash
# Let's Encrypt ile (domain varsa)
certbot --nginx -d yourdomain.com

# Self-signed sertifika (test için)
openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout ssl/nginx.key -out ssl/nginx.crt
```

## 🐛 Troubleshooting

### Yaygın Sorunlar:

1. **Docker başlatılamıyor:**
   - Docker Desktop'ın çalıştığından emin olun
   - WSL2'nin etkin olduğunu kontrol edin

2. **Port çakışması:**
   ```bash
   # Port kullanımını kontrol et
   netstat -ano | findstr :5000
   
   # Çakışan servisi durdur
   taskkill /PID <process_id> /F
   ```

3. **Redis bağlantı hatası:**
   ```bash
   # Redis container'ını kontrol et
   docker-compose logs redis
   
   # Redis'i yeniden başlat
   docker-compose restart redis
   ```

4. **Rate limiting çalışmıyor:**
   ```bash
   # Redis'te veri var mı kontrol et
   docker exec -it pillow-robot-redis redis-cli keys "*limiter*"
   ```

### Log Analizi:
```bash
# API logları
docker-compose logs -f api

# Nginx logları
docker-compose logs -f nginx

# Redis logları
docker-compose logs -f redis
```

## 📊 Performance Monitoring

### Resource Usage:
```bash
# Container kaynak kullanımı
docker stats

# Disk kullanımı
docker system df
```

### Application Metrics:
```bash
# Health check
curl http://localhost/health

# Rate limiting durumu
curl -H "X-RateLimit-Limit" http://localhost/recommend
```

## 🔄 Backup ve Restore

### Database Backup:
```bash
# SQLite için
docker exec pillow-robot-api sqlite3 /app/instance/app.db ".backup backup.db"

# PostgreSQL için
docker exec pillow-robot-api pg_dump $DATABASE_URL > backup.sql
```

### Redis Backup:
```bash
# Redis verilerini yedekle
docker exec pillow-robot-redis redis-cli BGSAVE
docker cp pillow-robot-redis:/data/dump.rdb ./redis-backup.rdb
```

Bu rehber ile Windows'ta sudo gerektirmeden production ortamınızı kurabilirsiniz! 🚀 