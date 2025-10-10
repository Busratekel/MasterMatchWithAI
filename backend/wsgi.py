# -*- coding: utf-8 -*-
import os
import sys

# Proje dizinini Python path'ine ekle
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Windows encoding ayarları (IIS için)
if sys.platform.startswith('win'):
    if hasattr(sys.stdout, 'reconfigure'):
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except:
            pass
    if hasattr(sys.stderr, 'reconfigure'):
        try:
            sys.stderr.reconfigure(encoding='utf-8')
        except:
            pass

os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['PYTHONUTF8'] = '1'

# .env dosyasını yükle - Detaylı logging ile
from dotenv import load_dotenv
env_path = os.path.join(current_dir, '.env')

print(f"=== WSGI Başlatılıyor ===")
print(f"Current directory: {current_dir}")
print(f".env path: {env_path}")
print(f".env exists: {os.path.exists(env_path)}")

if os.path.exists(env_path):
    load_dotenv(env_path)
    print(f"✓ .env dosyası yüklendi")
    # Environment variables yüklendi mi kontrol et
    admin_user = os.getenv('ADMIN_USERNAME')
    ad_enabled = os.getenv('AD_ENABLED')
    print(f"ADMIN_USERNAME: {admin_user}")
    print(f"AD_ENABLED: {ad_enabled}")
else:
    print(f"⚠ .env dosyası bulunamadı!")

# Flask uygulamasını import et
try:
    from main import app
    print("✓ Flask uygulaması başarıyla yüklendi")
except Exception as e:
    print(f"✗ Flask uygulaması yüklenemedi: {e}")
    import traceback
    traceback.print_exc()
    raise

# IIS için application nesnesi
application = app

if __name__ == "__main__":
    # Geliştirme ortamı
    app.run(debug=False, host='0.0.0.0', port=5001) 