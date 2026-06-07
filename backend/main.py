"""
Rama Chemist — Pharmacy Order Management Backend

LOCAL  (no env vars needed) → SQLite + local file storage
VERCEL (env vars set)       → PostgreSQL + Cloudinary

Optional environment variables for hosted deployment:
  DATABASE_URL    — Postgres connection string (Neon / Supabase)
  CLOUDINARY_URL  — cloudinary://api_key:api_secret@cloud_name
"""

import io
import os
import time
import hmac
import hashlib
import secrets
import logging
from contextlib import asynccontextmanager

import qrcode
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

import database as db

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("chemist")

# BASE_DIR = repo root, regardless of whether we're invoked from backend/ or api/
BASE_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND    = os.path.join(BASE_DIR, "frontend")

# Cloudinary — only used when CLOUDINARY_URL is set
CLOUDINARY_URL = os.environ.get("CLOUDINARY_URL", "")
USE_CLOUDINARY = bool(CLOUDINARY_URL)
if USE_CLOUDINARY:
    import cloudinary
    import cloudinary.uploader
    cloudinary.config(cloudinary_url=CLOUDINARY_URL)

# Local uploads dir — only created/used when NOT on Vercel (no Cloudinary)
if not USE_CLOUDINARY:
    UPLOADS_DIR = os.path.join(BASE_DIR, "data", "uploads")
    os.makedirs(UPLOADS_DIR, exist_ok=True)
else:
    UPLOADS_DIR = "/tmp/uploads"   # writable on Vercel, but won't be used

ALLOWED_EXT = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".heic", ".pdf"}
MAX_FILE_MB = 10

# ── Stateless admin token (HMAC-signed, survives cold starts) ─────────────────
# Token format: "admin|<expiry_unix>|<hmac_hex>"
# Signed with ADMIN_SECRET — set this as a Vercel env var for production.
ADMIN_SECRET  = os.environ.get("ADMIN_SECRET", "rama-chemist-default-secret-2024")
TOKEN_TTL     = 7 * 24 * 3600   # 7 days

def make_admin_token() -> str:
    exp     = str(int(time.time()) + TOKEN_TTL)
    payload = f"admin|{exp}"
    sig     = hmac.new(ADMIN_SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest()
    return f"{payload}|{sig}"

def verify_admin_token(token: str) -> bool:
    try:
        parts = token.split("|")
        if len(parts) != 3 or parts[0] != "admin":
            return False
        exp = int(parts[1])
        if exp < int(time.time()):
            return False                       # expired
        payload  = f"admin|{parts[1]}"
        expected = hmac.new(ADMIN_SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest()
        return hmac.compare_digest(parts[2], expected)
    except Exception:
        return False

def valid_admin(identifier: str = "", password: str = "", token: str = "") -> bool:
    if token and verify_admin_token(token):
        return True
    return db.is_admin(identifier, password)

@asynccontextmanager
async def lifespan(app: FastAPI):
    db.init_db()
    logger.info("Rama Chemist backend ready.")
    yield


app = FastAPI(title="Rama Chemist", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# Mount frontend static files only if the directory exists (it always does locally + on Vercel)
if os.path.isdir(FRONTEND):
    app.mount("/static", StaticFiles(directory=FRONTEND), name="static")

# Mount local uploads only when not using Cloudinary
if not USE_CLOUDINARY and os.path.isdir(UPLOADS_DIR):
    app.mount("/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")


# ── Health ────────────────────────────────────────────────────────────────────
@app.get("/health")
def health():
    return {"status": "ok", "shop_open": db.is_shop_open()}


# ── Shop status ───────────────────────────────────────────────────────────────
@app.get("/api/shop/status")
def shop_status():
    return {"open": db.is_shop_open(), "name": db.get_setting("shop_name") or "Rama Chemist"}


# ── QR Code ───────────────────────────────────────────────────────────────────
@app.get("/api/qr")
def get_qr(host: str = "localhost", port: int = 8090):
    url = f"http://{host}:{port}/"
    qr = qrcode.QRCode(version=2, box_size=8, border=3,
                       error_correction=qrcode.constants.ERROR_CORRECT_M)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#0a1f5e", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/png")


# ── Auth ──────────────────────────────────────────────────────────────────────
@app.post("/api/auth/register")
async def register(
    identifier: str = Form(...),
    id_type:    str = Form("phone"),
    password:   str = Form(""),
    name:       str = Form(""),
):
    identifier = identifier.strip().lower().replace(" ", "")
    if not identifier:
        return JSONResponse({"success": False, "message": "Phone number cannot be empty."}, 400)
    user = db.create_user(identifier, id_type, password, name)
    if not user:
        return JSONResponse({"success": False,
                             "message": "This number is already registered. Just sign in!"}, 409)
    return {"success": True, "message": "Account created! Welcome 🎉",
            "user": {"id": user["id"], "identifier": user["identifier"],
                     "name": user["name"], "id_type": user["identifier_type"]}}


@app.post("/api/auth/login")
async def login(
    identifier: str = Form(...),
    password:   str = Form(""),
):
    result = db.login_unified(identifier.strip().lower(), password)
    if not result:
        return JSONResponse({"success": False,
                             "message": "Not found. Check your number or create an account."}, 401)
    if result.get("role") == "admin":
        result["token"] = make_admin_token()
    return {"success": True, "user": result}


# ── Orders ────────────────────────────────────────────────────────────────────
@app.post("/api/orders/upload")
async def upload_order(
    identifier: str        = Form(...),
    name:       str        = Form(""),
    file:       UploadFile = File(...),
):
    if not db.is_shop_open():
        return JSONResponse({"success": False, "message": "🔒 Shop is currently closed."}, 503)

    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_EXT:
        return JSONResponse({"success": False, "message": "File type not allowed."}, 400)

    content = await file.read()
    if len(content) > MAX_FILE_MB * 1024 * 1024:
        return JSONResponse({"success": False, "message": f"File too large. Max {MAX_FILE_MB}MB."}, 413)

    if USE_CLOUDINARY:
        # Hosted: upload to Cloudinary, store permanent URL
        try:
            resource_type = "raw" if ext == ".pdf" else "image"
            result = cloudinary.uploader.upload(
                content,
                folder="rama-chemist/prescriptions",
                resource_type=resource_type,
            )
            image_path = result["secure_url"]
        except Exception as e:
            logger.error(f"Cloudinary upload failed: {e}")
            return JSONResponse({"success": False, "message": "File upload failed. Please try again."}, 500)
    else:
        # Local: save to disk, store filename
        ts    = int(time.time() * 1000)
        fname = f"{ts}{ext}"
        with open(os.path.join(UPLOADS_DIR, fname), "wb") as f_out:
            f_out.write(content)
        image_path = fname

    user = db.get_user(identifier.strip().lower())
    user_id = user["id"] if user else None
    order = db.create_order(user_id, identifier.strip().lower(), image_path)

    return {"success": True, "order_id": order["order_id"],
            "message": f"✅ Order placed! Your ID is {order['order_id']}.", "order": order}


@app.get("/api/orders/track/{order_id}")
def track_order(order_id: str):
    order = db.get_order(order_id.upper())
    if not order:
        return JSONResponse({"success": False, "message": "Order not found."}, 404)
    return {"success": True, "order": order}


@app.get("/api/orders/my")
def my_orders(identifier: str):
    orders = db.get_orders_for_user(identifier.strip().lower())
    return {"success": True, "orders": orders}


# ── Admin helpers ─────────────────────────────────────────────────────────────
def _auth_fail():
    return JSONResponse({"success": False, "message": "Admin access denied."}, 401)


# ── Admin endpoints ───────────────────────────────────────────────────────────
@app.get("/api/admin/orders")
def admin_orders(identifier: str = "", password: str = "", token: str = "", limit: int = 500):
    if not valid_admin(identifier, password, token):
        return _auth_fail()
    return {"success": True, "orders": db.get_all_orders(limit)}


@app.post("/api/admin/orders/{order_id}/status")
async def admin_update_status(
    order_id:   str,
    identifier: str = Form(""),
    password:   str = Form(""),
    token:      str = Form(""),
    status:     str = Form(...),
    notes:      str = Form(""),
):
    if not valid_admin(identifier, password, token):
        return _auth_fail()
    if status not in ("pending", "confirmed", "ready", "completed", "cancelled"):
        return JSONResponse({"success": False, "message": "Invalid status."}, 400)
    order = db.update_order_status(order_id.upper(), status, notes)
    if not order:
        return JSONResponse({"success": False, "message": "Order not found."}, 404)
    logger.info(f"Order {order_id} → {status}")
    return {"success": True, "order": order, "message": f"Order {order_id} → {status}"}


@app.post("/api/admin/orders/update")
async def admin_update_order(
    identifier: str = Form(""),
    password:   str = Form(""),
    token:      str = Form(""),
    order_id:   str = Form(...),
    status:     str = Form(...),
    notes:      str = Form(""),
):
    if not valid_admin(identifier, password, token):
        return _auth_fail()
    if status not in ("pending", "confirmed", "ready", "completed", "cancelled"):
        return JSONResponse({"success": False, "message": "Invalid status."}, 400)
    order = db.update_order_status(order_id.upper(), status, notes)
    if not order:
        return JSONResponse({"success": False, "message": "Order not found."}, 404)
    logger.info(f"Order {order_id} → {status}")
    return {"success": True, "order": order, "message": f"Order {order_id} → {status}"}


@app.post("/api/admin/shop/toggle")
async def admin_toggle_shop(
    identifier: str = Form(""),
    password:   str = Form(""),
    token:      str = Form(""),
):
    if not valid_admin(identifier, password, token):
        return _auth_fail()
    new_val = "0" if db.is_shop_open() else "1"
    db.set_setting("shop_open", new_val)
    state = "OPEN" if new_val == "1" else "CLOSED"
    return {"success": True, "open": new_val == "1", "message": f"Shop is now {state}"}


@app.get("/api/admin/shop/status")
def admin_shop_status(identifier: str = "", password: str = "", token: str = ""):
    if not valid_admin(identifier, password, token):
        return _auth_fail()
    return {"success": True, "open": db.is_shop_open(), "name": db.get_setting("shop_name")}


@app.get("/api/admin/stats")
def admin_stats(identifier: str = "", password: str = "", token: str = ""):
    if not valid_admin(identifier, password, token):
        return _auth_fail()
    stats = db.get_stats()
    return {"success": True, "total_orders": stats["total_orders"],
            "shop_open": db.is_shop_open(), "by_status": stats["by_status"]}


@app.get("/api/admin/dashboard")
def admin_dashboard(identifier: str = "", password: str = "", token: str = "", limit: int = 500):
    if not valid_admin(identifier, password, token):
        return _auth_fail()
    data = db.get_dashboard_data(limit)
    return {"success": True, **data}


@app.get("/api/admin/settings")
def admin_get_settings(identifier: str = "", password: str = "", token: str = ""):
    if not valid_admin(identifier, password, token):
        return _auth_fail()
    return {"success": True,
            "shop_name": db.get_setting("shop_name") or "Rama Chemist & Pharmacy"}


@app.post("/api/admin/settings")
async def admin_save_settings(
    identifier: str = Form(""),
    password:   str = Form(""),
    token:      str = Form(""),
    shop_name:  str = Form(""),
):
    if not valid_admin(identifier, password, token):
        return _auth_fail()
    if shop_name.strip():
        db.set_setting("shop_name", shop_name.strip())
    return {"success": True, "message": "✅ Settings saved!"}


# ── Frontend pages ────────────────────────────────────────────────────────────
PAGES = ["index.html", "login.html", "order.html",
         "track.html", "admin.html", "dashboard.html"]

@app.get("/")
def root():
    return FileResponse(os.path.join(FRONTEND, "index.html"))

@app.get("/{page}")
def serve_page(page: str):
    if page in PAGES:
        return FileResponse(os.path.join(FRONTEND, page))
    raise HTTPException(404, f"Page not found: {page}")
