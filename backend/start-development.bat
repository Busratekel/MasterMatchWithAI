@echo off
echo Pillow Selection Robot - Development Başlatılıyor...
echo.

REM Python kontrolü
python --version >nul 2>&1
if errorlevel 1 (
    echo HATA: Python yüklü değil!
    echo https://www.python.org/downloads/ adresinden Python'u indirin.
    pause
    exit /b 1
)

REM Virtual environment kontrolü
if not exist venv (
    echo Virtual environment oluşturuluyor...
    python -m venv venv
)

REM Virtual environment'ı aktifleştir
echo Virtual environment aktifleştiriliyor...
call venv\Scripts\activate.bat

REM Bağımlılıkları yükle
echo Bağımlılıklar yükleniyor...
pip install -r requirements.txt

REM Environment variables ayarla
set FLASK_ENV=development
set FLASK_DEBUG=True

echo.
echo Flask uygulaması başlatılıyor...
echo API: http://localhost:5000
echo Health Check: http://localhost:5000/health
echo.
echo Durdurmak için Ctrl+C
echo.

python main.py 