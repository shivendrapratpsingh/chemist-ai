@echo off
title Rama Chemist — PRODUCTION SERVER

echo.
echo  ================================================
echo   RAMA CHEMIST - Production Server (24/7)
echo  ================================================
echo.

python --version >nul 2>&1
if errorlevel 1 (echo [ERROR] Python not found & pause & exit /b 1)

cd /d "%~dp0"
set PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1

echo [1/2] Installing / updating dependencies...
python -m pip install fastapi "uvicorn[standard]" python-multipart Pillow "qrcode[pil]" aiofiles "passlib[bcrypt]" --quiet

echo [2/2] Starting PRODUCTION server on port 8090...
echo.
echo  ================================================
echo   Access from THIS computer : http://localhost:8090
echo   Access from LOCAL NETWORK : http://%COMPUTERNAME%:8090
echo.
echo   To find your IP address run: ipconfig
echo   Then share: http://YOUR_IP:8090
echo.
echo   Admin login : pratapsinghsivendra21@gmail.com
echo   Admin pass  : $Hivendra123
echo.
echo   Press Ctrl+C to stop.
echo  ================================================
echo.

cd /d "%~dp0backend"
python -m uvicorn main:app --host 0.0.0.0 --port 8090 --workers 2
