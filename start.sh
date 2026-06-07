#!/bin/bash
set -e
echo ""
echo " ================================================"
echo "  RAMA CHEMIST - Pharmacy Management System"
echo " ================================================"
echo ""

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "[1/3] Installing dependencies..."
python3 -m pip install --upgrade pip --quiet
python3 -m pip install fastapi "uvicorn[standard]" python-multipart Pillow "qrcode[pil]" aiofiles "passlib[bcrypt]" --quiet

echo "[2/3] Opening browser after server starts..."
(
  sleep 4
  OPENER=""
  command -v xdg-open &>/dev/null && OPENER="xdg-open"
  command -v open &>/dev/null && OPENER="open"
  if [ -n "$OPENER" ]; then
    "$OPENER" "http://localhost:8090" &
    sleep 1
    "$OPENER" "http://localhost:8090/admin.html" &
  fi
) &

echo "[3/3] Starting server..."
echo ""
echo " ================================================"
echo "  Customer : http://localhost:8090"
echo "  Admin    : http://localhost:8090/admin.html"
echo "  Password : admin123"
echo "  Ctrl+C to stop."
echo " ================================================"
echo ""

cd "$SCRIPT_DIR/backend"
python3 -m uvicorn main:app --host 0.0.0.0 --port 8090 --reload
