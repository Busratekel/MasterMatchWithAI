# IIS FastCGI Sorun Giderme Rehberi

## Sorun: FastCGI Modülü Hatası ve API Bağlantısı Kurulamadı

### 1. Python Yolu Sorunu

**Sorun:** Web.config dosyasında belirtilen Python yolu yanlış olabilir.

**Çözüm:**
1. PowerShell'i yönetici olarak açın
2. `backend/find_python_path.ps1` scriptini çalıştırın
3. Bulunan Python yolunu web.config dosyasında güncelleyin

### 2. wfastcgi Paketi Eksik

**Sorun:** wfastcgi paketi yüklü değil.

**Çözüm:**
```bash
# Virtual environment'ı aktifleştirin
cd backend
venv\Scripts\activate

# wfastcgi'yi yükleyin
pip install wfastcgi

# wfastcgi'yi etkinleştirin
wfastcgi-enable
```

### 3. IIS FastCGI Modülü Yüklü Değil

**Sorun:** IIS'de FastCGI modülü yüklü değil.

**Çözüm:**
```powershell
# PowerShell'i yönetici olarak açın
Install-WindowsFeature -Name IIS-CGI
```

### 4. Python Handler Yapılandırması

**Sorun:** Python Handler doğru yapılandırılmamış.

**Çözüm:**
1. `backend/check_iis_modules.ps1` scriptini çalıştırın
2. Eksik modülleri yükleyin

### 5. Web.config Dosyası Güncellemeleri

**Mevcut web.config:**
```xml
<?xml version="1.0" encoding="utf-8"?>
<configuration>
  <system.webServer>
    <handlers>
      <add name="PythonHandler" path="*" verb="*" modules="FastCgiModule"
           scriptProcessor="C:\Python311\python.exe|C:\Python311\Scripts\wfastcgi.py"
           resourceType="Unspecified" requireAccess="Script" />
    </handlers>
    <appSettings>
      <add key="WSGI_HANDLER" value="main.app" />
      <add key="PYTHONPATH" value="C:\inetpub\wwwroot\MasterMatchAI\backend" />
      <add key="WSGI_LOG" value="C:\inetpub\wwwroot\MasterMatchAI\backend\logs\wsgi.log" />
    </appSettings>
    <httpErrors errorMode="Detailed" />
    <asp scriptErrorSentToBrowser="true"/>
  </system.webServer>
</configuration>
```

### 6. Alternatif Python Yolları

Eğer `C:\Python311\python.exe` çalışmazsa, şu yolları deneyin:

- `C:\Python310\python.exe`
- `C:\Python39\python.exe`
- `C:\Program Files\Python311\python.exe`
- `C:\Program Files\Python310\python.exe`

### 7. Log Dosyalarını Kontrol Etme

**IIS Logları:**
- `C:\inetpub\logs\LogFiles\W3SVC1\`

**WSGI Logları:**
- `C:\inetpub\wwwroot\MasterMatchAI\backend\logs\wsgi.log`

### 8. Test Etme

1. IIS'i yeniden başlatın:
```powershell
iisreset
```

2. Tarayıcıda test edin:
```
http://localhost/api/health
```

### 9. Yaygın Hata Kodları

- **500.19**: Web.config dosyası hatası
- **500.0**: Python script hatası
- **404.0**: Handler bulunamadı
- **502.3**: FastCGI hatası

### 10. Son Kontroller

1. Python yolu doğru mu?
2. wfastcgi yüklü mü?
3. FastCGI modülü yüklü mü?
4. Web.config dosyası doğru mu?
5. IIS Application Pool doğru yapılandırılmış mı?


