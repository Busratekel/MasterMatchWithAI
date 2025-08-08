# IIS Deployment Checklist

## 1. Dosya Hazırlığı
- [ ] `main.py` - Ana Flask uygulaması
- [ ] `wsgi.py` - WSGI entry point
- [ ] `requirements.txt` - Python bağımlılıkları
- [ ] `web.config` - IIS konfigürasyonu
- [ ] `.env` dosyası (production ayarları ile)
- [ ] `public/` klasörü (PDF dosyaları için)

## 2. IIS Sunucusunda Yapılacaklar

### Dosyaları Kopyala:
```cmd
# Backup al
xcopy "C:\inetpub\wwwroot\MasterMatchAI\backend\*" "C:\inetpub\wwwroot\MasterMatchAI\backend\backup\" /s /e /i

# Yeni dosyaları kopyala
xcopy ".\*" "C:\inetpub\wwwroot\MasterMatchAI\backend\" /s /e /y
```

### Virtual Environment Güncelle:
```cmd
cd C:\inetpub\wwwroot\MasterMatchAI\backend
venv\Scripts\activate
pip install -r requirements.txt
```

### IIS Restart:
```cmd
iisreset
```

## 3. Kontrol Edilecekler
- [ ] Backend API'leri çalışıyor mu?
- [ ] Database bağlantısı aktif mi?
- [ ] CORS ayarları doğru mu?
- [ ] Mail gönderimi çalışıyor mu?
- [ ] PDF dosyaları erişilebilir mi?

## 4. Test Endpoints
- `https://mastermatch.doquhome.com.tr/api/health`
- `https://mastermatch.doquhome.com.tr/api/questions`
- `https://mastermatch.doquhome.com.tr/api/yastiklar`

## 5. Rollback Planı
Eğer sorun çıkarsa:
```cmd
xcopy "C:\inetpub\wwwroot\MasterMatchAI\backend\backup\*" "C:\inetpub\wwwroot\MasterMatchAI\backend\" /s /e /y
iisreset
``` 