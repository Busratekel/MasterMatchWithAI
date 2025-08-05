import os
import sys

# Proje dizinini Python path'ine ekle
sys.path.insert(0, os.path.dirname(__file__))

# Environment değişkenlerini yükle
from dotenv import load_dotenv
load_dotenv()

# Flask uygulamasını import et
from main import app

if __name__ == "__main__":
    app.run() 