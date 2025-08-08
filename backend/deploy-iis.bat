@echo off
echo IIS Deployment Script for Pillow Selection Backend
echo ================================================

REM Backup mevcut dosyalar
echo Creating backup...
if exist "C:\inetpub\wwwroot\MasterMatchAI\backend\backup" (
    rmdir /s /q "C:\inetpub\wwwroot\MasterMatchAI\backend\backup"
)
mkdir "C:\inetpub\wwwroot\MasterMatchAI\backend\backup"
xcopy "C:\inetpub\wwwroot\MasterMatchAI\backend\*" "C:\inetpub\wwwroot\MasterMatchAI\backend\backup\" /s /e /i

REM Yeni dosyaları kopyala
echo Copying new files...
xcopy ".\*" "C:\inetpub\wwwroot\MasterMatchAI\backend\" /s /e /y

REM Virtual environment'ı güncelle
echo Updating virtual environment...
cd "C:\inetpub\wwwroot\MasterMatchAI\backend"
call venv\Scripts\activate
pip install -r requirements.txt

REM IIS'i restart et
echo Restarting IIS...
iisreset

echo Deployment completed!
pause 