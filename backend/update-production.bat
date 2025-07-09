@echo off
echo Pillow Selection Robot - Canlı Ortam Güncelleme
echo.

REM Domain bilgisini al
set /p DOMAIN="Domain adresinizi girin (örn: yastikrobotu.com): "

REM Güvenli secret key oluştur
echo Güvenli secret key oluşturuluyor...
python -c "import secrets; print('SECRET_KEY=' + secrets.token_hex(32))" > temp_secret.txt
set /p SECRET_KEY=<temp_secret.txt
del temp_secret.txt

REM .env dosyasını güncelle
echo FLASK_ENV=production > .env
echo FLASK_DEBUG=False >> .env
echo DATABASE_URL=mssql+pyodbc://sa:YourPassword@localhost:1433/pillow_robot?driver=ODBC+Driver+17+for+SQL+Server >> .env
echo REDIS_URL=redis://redis:6379/0 >> .env
echo ALLOWED_ORIGINS=https://%DOMAIN% >> .env
echo %SECRET_KEY% >> .env

echo.
echo Canlı ortam ayarları güncellendi!
echo Domain: https://%DOMAIN%
echo.
echo Uygulamayı yeniden başlatmak için:
echo docker-compose down
echo docker-compose up -d
echo.
pause 