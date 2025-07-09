# Canlı Ortam Deployment Rehberi

## 1. Environment Variables Ayarları

### .env Dosyası Oluşturma
```bash
# env_example.txt dosyasını .env olarak kopyalayın
cp env_example.txt .env
```

### Gerekli Environment Variables:
```env
FLASK_ENV=production
FLASK_DEBUG=False
DATABASE_URL=your_production_database_url
REDIS_URL=redis://localhost:6379/0
ALLOWED_ORIGINS=https://yourdomain.com
SECRET_KEY=your_secure_secret_key
```

## 2. Redis Kurulumu ve Konfigürasyonu

### Ubuntu/Debian:
```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

### CentOS/RHEL:
```bash
sudo yum install redis
sudo systemctl start redis
sudo systemctl enable redis
```

### Docker ile Redis:
```bash
docker run -d --name redis -p 6379:6379 redis:alpine
```

## 3. Gerekli Python Paketlerinin Kurulumu

```bash
pip install -r requirements.txt
```

## 4. Production Server Konfigürasyonu

### Gunicorn ile (Önerilen):
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 main:app
```

### Systemd Service Oluşturma:
```bash
sudo nano /etc/systemd/system/pillow-robot.service
```

Service dosyası içeriği:
```ini
[Unit]
Description=Pillow Selection Robot API
After=network.target

[Service]
User=your_user
WorkingDirectory=/path/to/your/app
Environment=PATH=/path/to/your/venv/bin
ExecStart=/path/to/your/venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 main:app
Restart=always

[Install]
WantedBy=multi-user.target
```

Service'i başlatma:
```bash
sudo systemctl daemon-reload
sudo systemctl start pillow-robot
sudo systemctl enable pillow-robot
```

## 5. Nginx Reverse Proxy (Önerilen)

### Nginx Konfigürasyonu:
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 6. SSL Sertifikası (HTTPS)

### Let's Encrypt ile:
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

## 7. Güvenlik Kontrolleri

### Firewall Ayarları:
```bash
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

### Rate Limiting Test:
```bash
# Test script'i
for i in {1..15}; do
  curl -X POST http://yourdomain.com/recommend \
    -H "Content-Type: application/json" \
    -d '{"responses":{}}'
  echo "Request $i"
done
```

## 8. Monitoring ve Logging

### Log Dosyalarını İzleme:
```bash
# Application logs
sudo journalctl -u pillow-robot -f

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

## 9. Backup Stratejisi

### Veritabanı Backup:
```bash
# Otomatik backup script'i
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump your_database > backup_$DATE.sql
```

## 10. Performance Optimizasyonu

### Redis Memory Ayarları:
```bash
# /etc/redis/redis.conf
maxmemory 256mb
maxmemory-policy allkeys-lru
```

### Gunicorn Worker Sayısı:
```bash
# CPU core sayısı * 2 + 1
# Örnek: 4 core için 9 worker
gunicorn -w 9 -b 0.0.0.0:5000 main:app
```

## 11. Troubleshooting

### Yaygın Sorunlar:

1. **Redis Bağlantı Hatası:**
   ```bash
   redis-cli ping
   # PONG dönerse Redis çalışıyor
   ```

2. **Rate Limiting Çalışmıyor:**
   ```bash
   # Redis'te rate limit verilerini kontrol et
   redis-cli keys "*limiter*"
   ```

3. **CORS Hatası:**
   - ALLOWED_ORIGINS environment variable'ını kontrol et
   - Frontend domain'inin doğru olduğundan emin ol

4. **Database Bağlantı Hatası:**
   ```bash
   # Database URL'ini test et
   python -c "from main import db; db.engine.connect()"
   ```

## 12. Health Check Endpoint

Uygulamanızda health check endpoint'i ekleyin:
```python
@app.route('/health')
def health_check():
    try:
        # Database bağlantısını test et
        db.engine.execute('SELECT 1')
        # Redis bağlantısını test et
        redis_client.ping()
        return jsonify({'status': 'healthy'}), 200
    except Exception as e:
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500
``` 