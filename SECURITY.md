# 🔒 Güvenlik Politikası

## 🛡️ Güvenlik Önlemleri

Bu proje güvenlik standartlarına uygun olarak geliştirilmiştir. Aşağıdaki önlemler alınmıştır:

### 🔐 Hassas Bilgilerin Korunması

- **Environment Dosyaları**: Tüm hassas bilgiler `.env` dosyalarında saklanır
- **Gitignore**: `.env` dosyaları `.gitignore`'da tanımlıdır ve GitHub'a yüklenmez
- **Örnek Dosyalar**: `env_example.txt` ve `env.example` dosyaları güvenli şekilde paylaşılır

### 🚫 Yüklenmemesi Gereken Dosyalar

Aşağıdaki dosyalar **ASLA** GitHub'a yüklenmemelidir:

```
❌ .env
❌ .env.local
❌ .env.production
❌ backend/.env
❌ frontend/.env
❌ *.key
❌ *.pem
❌ *.p12
❌ credentials.json
❌ service-account.json
❌ database.db
❌ *.log
❌ node_modules/
❌ venv/
❌ __pycache__/
```

### ✅ Güvenli Dosyalar

Aşağıdaki dosyalar güvenle yüklenebilir:

```
✅ env_example.txt
✅ env.example
✅ requirements.txt
✅ package.json
✅ README.md
✅ SECURITY.md
✅ .gitignore
```

## 🔍 Güvenlik Kontrol Listesi

### Pre-commit Kontrolleri

GitHub'a yüklemeden önce şunları kontrol edin:

- [ ] `.env` dosyaları yok
- [ ] Hassas bilgiler kod içinde yok
- [ ] Database dosyaları yok
- [ ] Log dosyaları yok
- [ ] Node modules yok
- [ ] Virtual environment yok

### Environment Dosyası Kontrolü

```bash
# Backend için
cp backend/env_example.txt backend/.env
# .env dosyasını düzenleyin

# Frontend için
cp frontend/env.example frontend/.env
# .env dosyasını düzenleyin
```

## 🚨 Güvenlik Uyarıları

### ⚠️ Önemli Notlar

1. **Environment Dosyaları**: Gerçek `.env` dosyalarını asla commit etmeyin
2. **API Anahtarları**: Tüm API anahtarları environment değişkenlerinde saklanmalı
3. **Veritabanı Bağlantıları**: Connection string'ler environment'da olmalı
4. **Mail Şifreleri**: SMTP şifreleri environment'da olmalı

### 🔧 Güvenlik Ayarları

#### Backend Güvenlik
- Rate limiting aktif
- CORS koruması aktif
- Input validation aktif
- SQL injection koruması (SQLAlchemy)

#### Frontend Güvenlik
- HTTPS zorunlu (production)
- XSS koruması
- CSRF koruması
- Content Security Policy

## 📞 Güvenlik İletişimi

Güvenlik açığı bulursanız:

1. **Özel Issue açın**: GitHub'da private issue oluşturun
2. **Açıklayın**: Açığı detaylı açıklayın
3. **Bekleyin**: Yanıt için bekleyin
4. **Yayınlamayın**: Açığı public olarak paylaşmayın

## 🔄 Güvenlik Güncellemeleri

- Düzenli dependency güncellemeleri
- Güvenlik yamaları takibi
- Vulnerability scanning
- Code review süreci

## 📋 Güvenlik Checklist

### Development Ortamı
- [ ] Environment dosyaları güvenli
- [ ] Hassas bilgiler kod dışında
- [ ] .gitignore doğru yapılandırılmış
- [ ] Dependencies güncel

### Production Ortamı
- [ ] HTTPS aktif
- [ ] Environment değişkenleri güvenli
- [ ] Database bağlantısı güvenli
- [ ] Log dosyaları korunuyor
- [ ] Backup stratejisi mevcut

---

**Son Güncelleme**: 2024
**Versiyon**: 1.0 