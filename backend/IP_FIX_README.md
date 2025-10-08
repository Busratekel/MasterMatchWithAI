# 🔧 IP Adresi Düzeltme Kılavuzu

## 🎯 Sorun
IIS proxy/load balancer arkasında çalışırken, tüm kullanıcı IP adresleri aynı görünüyordu (172.16.130.252). Bu IIS'in internal IP adresiydi.

## ✅ Çözüm

### 1. Backend'de `get_client_ip()` Fonksiyonu Eklendi
```python
def get_client_ip():
    """
    Gerçek kullanıcı IP adresini al
    IIS/Proxy arkasındaki gerçek IP'yi header'lardan oku
    """
    # X-Forwarded-For header'ı kontrol et (en yaygın)
    if request.headers.get('X-Forwarded-For'):
        ip = request.headers.get('X-Forwarded-For').split(',')[0].strip()
        return ip
    
    # X-Real-IP header'ı kontrol et
    if request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP').strip()
    
    # HTTP_X_FORWARDED_FOR (bazı proxy'ler bu formatı kullanır)
    if request.environ.get('HTTP_X_FORWARDED_FOR'):
        ip = request.environ.get('HTTP_X_FORWARDED_FOR').split(',')[0].strip()
        return ip
    
    # Hiçbir header yoksa request.remote_addr kullan (fallback)
    return request.remote_addr
```

### 2. Tüm `request.remote_addr` Kullanımları Değiştirildi
- `/api/recommend` endpoint: `ip_adresi = get_client_ip()`
- `/api/kvkk_onay_ekle` endpoint: `ip_adresi = data.get('ip_adresi', get_client_ip())`

### 3. IIS `web.config` Güncellendi
IP header'larını Flask'e iletmek için rewrite rule eklendi:

```xml
<rewrite>
  <rules>
    <rule name="AddForwardedHeaders">
      <match url=".*" />
      <serverVariables>
        <set name="HTTP_X_FORWARDED_FOR" value="{REMOTE_ADDR}" />
        <set name="HTTP_X_REAL_IP" value="{REMOTE_ADDR}" />
      </serverVariables>
      <action type="None" />
    </rule>
  </rules>
</rewrite>
```

### 4. Debug Endpoint Eklendi
`/api/health` endpoint'i artık IP debug bilgisi döndürüyor:

```json
{
  "status": "healthy",
  "client_ip": "185.x.x.x",
  "remote_addr": "172.16.130.252",
  "x_forwarded_for": "185.x.x.x",
  "x_real_ip": "185.x.x.x"
}
```

## 🚀 IIS'de Gerekli Ayarlar

### 1. URL Rewrite Module Yüklü Olmalı
- IIS Manager → URL Rewrite modülü yüklü değilse: [Web Platform Installer](https://www.microsoft.com/web/downloads/platform.aspx) ile yükleyin

### 2. Server Variables Unlock Edilmeli
PowerShell (Administrator) olarak çalıştırın:

```powershell
# URL Rewrite modülünü kur (gerekirse)
# Web Platform Installer ile yükleyin veya:
# https://www.iis.net/downloads/microsoft/url-rewrite

# Server variables'ı unlock et
cd C:\Windows\System32\inetsrv
.\appcmd.exe unlock config -section:system.webServer/rewrite/allowedServerVariables

# HTTP_X_FORWARDED_FOR ekle
.\appcmd.exe set config -section:system.webServer/rewrite/allowedServerVariables /+"[name='HTTP_X_FORWARDED_FOR']" /commit:apphost

# HTTP_X_REAL_IP ekle
.\appcmd.exe set config -section:system.webServer/rewrite/allowedServerVariables /+"[name='HTTP_X_REAL_IP']" /commit:apphost

# IIS'i restart et
iisreset
```

### 3. Application Pool Restart
```powershell
# Application pool'u restart et
.\appcmd.exe recycle apppool "MasterMatchAI"
```

## 🧪 Test

### 1. Local Test (Geliştirme)
```bash
curl http://localhost:5001/api/health
```

### 2. Canlı Test
```bash
curl https://mastermatch.doquhome.com.tr/api/health
```

Yanıtta görmeli:
```json
{
  "client_ip": "GERÇEK_IP",
  "remote_addr": "172.16.130.252",
  "x_forwarded_for": "GERÇEK_IP"
}
```

## 📊 Beklenen Akış

```
Kullanıcı (Gerçek IP: 185.x.x.x)
    ↓
IIS (Proxy IP: 172.16.130.252)
    ↓ (Header: X-Forwarded-For: 185.x.x.x)
Flask Backend
    → get_client_ip() = "185.x.x.x" ✅
```

## ⚠️ Dikkat

- `web.config` değişikliği sonrası **mutlaka IIS restart** yapın
- Server Variables unlock edilmemişse rewrite rule çalışmaz
- Firewall/WAF kullanıyorsanız, onlar da header'ları geçirmelidir

## 🔍 Sorun Giderme

### Hala aynı IP geliyor mu?
1. `/api/health` endpoint'ini çağırın, header'ları kontrol edin
2. IIS Manager'da URL Rewrite rule'u göründüğünü doğrulayın
3. PowerShell komutlarını tekrar çalıştırın
4. IIS'i restart edin: `iisreset`

### Header'lar NULL geliyor mu?
- Server Variables unlock edilmemiş olabilir
- `appcmd.exe` komutlarını kontrol edin
- IIS Manager → Application Pool → Advanced Settings → Load User Profile = True

### Hala çözülmedi mi?
- IIS Application Pool'u restart edin
- `web.config` dosyasının UTF-8 (without BOM) ile kaydedildiğinden emin olun
- Event Viewer'da IIS loglarına bakın

