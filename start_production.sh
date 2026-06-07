#!/bin/bash
# Rama Chemist — Production Server (24/7)
echo ""
echo " ================================================"
echo "  RAMA CHEMIST - Production Server (24/7)"
echo " ================================================"
echo ""

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "[1/2] Installing dependencies..."
python3 -m pip install fastapi "uvicorn[standard]" python-multipart Pillow "qrcode[pil]" aiofiles "passlib[bcrypt]" --quiet

IP=$(hostname -I 2>/dev/null | awk '{print $1}' || echo "YOUR_IP")

echo "[2/2] Starting production server..."
echo ""
echo " ================================================"
echo "  Local    : http://localhost:8090"
echo "  Network  : http://$IP:8090"
echo "  Admin    : pratapsinghsivendra21@gmail.com / \$Hivendra123"
echo "  Ctrl+C   : to stop"
echo " ================================================"
echo ""

cd "$SCRIPT_DIR/backend"
python3 -m uvicorn main:app --host 0.0.0.0 --port 8090 --workers 2
