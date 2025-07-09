@echo off
echo Pillow Selection Robot - Production Başlatılıyor...
echo.

REM Environment variables kontrolü
if not exist .env (
    echo HATA: .env dosyası bulunamadı!
    echo env_example.txt dosyasını .env olarak kopyalayın ve düzenleyin.
    pause
    exit /b 1
)

REM Docker kontrolü
docker --version >nul 2>&1
if errorlevel 1 (
    echo HATA: Docker yüklü değil!
    echo https://www.docker.com/products/docker-desktop adresinden Docker Desktop'ı indirin.
    pause
    exit /b 1
)

REM Docker Compose kontrolü
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo HATA: Docker Compose yüklü değil!
    pause
    exit /b 1
)

echo Docker servisleri başlatılıyor...
docker-compose up -d

echo.
echo Servisler başlatıldı!
echo.
echo API: http://localhost:5000
echo Nginx: http://localhost:80
echo Health Check: http://localhost/health
echo.
echo Servisleri durdurmak için: docker-compose down
echo Logları görmek için: docker-compose logs -f
echo.
pause 