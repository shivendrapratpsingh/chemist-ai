@echo off
title Rama Chemist — Pharmacy Management System

echo.
echo  ================================================
echo   RAMA CHEMIST - Pharmacy Management System
echo  ================================================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Install Python 3.10+ from python.org
    pause & exit /b 1
)

echo [1/3] Installing / updating dependencies...
cd /d "%~dp0"

set PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1
python -m pip install --upgrade pip --quiet
python -m pip install fastapi "uvicorn[standard]" python-multipart Pillow "qrcode[pil]" aiofiles "passlib[bcrypt]" httpx gradio-client --quiet
if %errorlevel% neq 0 (
    echo [WARN] Some packages may have failed. Trying without gradio-client...
    python -m pip install fastapi "uvicorn[standard]" python-multipart Pillow "qrcode[pil]" aiofiles "passlib[bcrypt]" httpx --quiet
)
echo Dependencies installed OK.

echo [2/3] Starting backend on http://localhost:8090 ...
set BACKEND=%~dp0backend
start "Rama Chemist Backend" cmd /k "cd /d "%BACKEND%" && set PYTHONPATH=%BACKEND% && set PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1 && python -m uvicorn main:app --host 0.0.0.0 --port 8090 --reload"

:: Wait for server to bind
timeout /t 4 /nobreak >nul

echo [3/3] Opening website in browser...
start "" "http://localhost:8090"
timeout /t 1 /nobreak >nul
start "" "http://localhost:8090/admin.html"

echo.
echo  ================================================
echo   Customer site : http://localhost:8090
echo   Upload order  : http://localhost:8090/order.html
echo   Track order   : http://localhost:8090/track.html
echo   Admin panel   : http://localhost:8090/admin.html
echo   QR Code       : http://localhost:8090/api/qr
echo.
echo   Admin default password: admin123
echo   Close "Rama Chemist Backend" window to stop.
echo  ================================================
echo.
