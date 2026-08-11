"""
Database — auto-selects backend:
  • LOCAL (no DATABASE_URL set) → SQLite
  • VERCEL / production (DATABASE_URL set) → PostgreSQL via psycopg2

Set DATABASE_URL environment variable for hosted deployments.
Example (Neon / Supabase):
  DATABASE_URL=postgresql://user:pass@host/dbname?sslmode=require
"""

import os
import hashlib
import secrets
import string
from datetime import datetime, timedelta

DATABASE_URL = os.environ.get("DATABASE_URL", "")
USE_POSTGRES = bool(DATABASE_URL)

# ── Admin credentials ─────────────────────────────────────────────────────────
ADMIN_EMAIL    = "pratapsinghshivendra21@gmail.com"
ADMIN_PASSWORD = "$Hivendra123"

# ── Connection ────────────────────────────────────────────────────────────────
if USE_POSTGRES:
    import psycopg2
    from psycopg2.extras import RealDictCursor

    def get_conn():
        return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

    def _row(r):
        return dict(r) if r else None

    def _rows(rs):
        return [dict(r) for r in rs]

    PH = "%s"   # placeholder

else:
    import sqlite3

    DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "chemist.db")
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    def get_conn():
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        return conn

    def _row(r):
        return dict(r) if r else None

    def _rows(rs):
        return [dict(r) for r in rs]

    PH = "?"   # placeholder


# ── Init DB ───────────────────────────────────────────────────────────────────
def init_db():
    conn = get_conn()
    c = conn.cursor()

    if USE_POSTGRES:
        c.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                identifier TEXT UNIQUE NOT NULL,
                identifier_type TEXT NOT NULL,
                password_hash TEXT NOT NULL DEFAULT '',
                name TEXT DEFAULT '',
                created_at TEXT NOT NULL
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id SERIAL PRIMARY KEY,
                order_id TEXT UNIQUE NOT NULL,
                user_id INTEGER,
                identifier TEXT NOT NULL,
                image_path TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                notes TEXT DEFAULT '',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        """)
        c.execute("CREATE INDEX IF NOT EXISTS idx_orders_status     ON orders(status)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_orders_created    ON orders(created_at DESC)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_orders_identifier ON orders(identifier)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_orders_updated    ON orders(updated_at DESC)")
        c.execute("INSERT INTO settings (key,value) VALUES ('shop_open','1') ON CONFLICT DO NOTHING")
        c.execute("INSERT INTO settings (key,value) VALUES ('shop_name','Maa Gayatri Pharmacy') ON CONFLICT DO NOTHING")
    else:
        c.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                identifier TEXT UNIQUE NOT NULL,
                identifier_type TEXT NOT NULL,
                password_hash TEXT NOT NULL DEFAULT '',
                name TEXT DEFAULT '',
                created_at TEXT NOT NULL
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id TEXT UNIQUE NOT NULL,
                user_id INTEGER,
                identifier TEXT NOT NULL,
                image_path TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                notes TEXT DEFAULT '',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        """)
        c.execute("CREATE INDEX IF NOT EXISTS idx_orders_status     ON orders(status)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_orders_created    ON orders(created_at DESC)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_orders_identifier ON orders(identifier)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_orders_updated    ON orders(updated_at DESC)")
        c.execute("INSERT OR IGNORE INTO settings (key,value) VALUES ('shop_open','1')")
        c.execute("INSERT OR IGNORE INTO settings (key,value) VALUES ('shop_name','Maa Gayatri Pharmacy')")

    # Rebrand: the INSERTs above are no-ops on an existing database, so the old
    # name would otherwise survive and be shown by /api/shop/status. Matched
    # loosely (lower + LIKE) because the stored value has been hand-edited via
    # the admin Settings panel — e.g. 'RAMA chemist' — so an exact match misses.
    # The LIKE patterns are bound as parameters, never inlined: psycopg2 does
    # printf-style substitution whenever params are passed, so a literal '%' in
    # the SQL is read as a format spec and raises. SQLite's '?' binding does no
    # such substitution, which is why an inlined '%rama%' passes locally and
    # only fails against Postgres.
    c.execute(
        f"UPDATE settings SET value = {PH} WHERE key = 'shop_name' "
        f"AND (LOWER(value) LIKE {PH} OR LOWER(value) LIKE {PH})",
        ("Maa Gayatri Pharmacy", "%rama%", "%chemist%")
    )

    conn.commit()
    conn.close()
    mode = "PostgreSQL" if USE_POSTGRES else "SQLite"
    print(f"Database initialised ({mode}).")


# ── Helpers ───────────────────────────────────────────────────────────────────
def hash_password(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

def verify_password(pw: str, hashed: str) -> bool:
    return hash_password(pw) == hashed

def generate_order_id() -> str:
    chars = string.ascii_uppercase + string.digits
    conn = get_conn()
    c = conn.cursor()
    while True:
        oid = ''.join(secrets.choice(chars) for _ in range(5))
        c.execute(f"SELECT 1 FROM orders WHERE order_id = {PH}", (oid,))
        if not c.fetchone():
            conn.close()
            return oid

def ist_now() -> str:
    ist = datetime.utcnow() + timedelta(hours=5, minutes=30)
    return ist.strftime("%Y-%m-%d %H:%M:%S")


# ── Unified Login ─────────────────────────────────────────────────────────────
def login_unified(identifier: str, password: str = ""):
    identifier = identifier.strip().lower()
    if identifier == ADMIN_EMAIL.lower():
        if password == ADMIN_PASSWORD:
            return {"id": 0, "identifier": ADMIN_EMAIL,
                    "name": "Admin", "id_type": "email", "role": "admin"}
        return None
    user = login_user(identifier, password)
    if user:
        return {**user, "role": "customer"}
    return None

def is_admin(identifier: str, password: str) -> bool:
    return (identifier.strip().lower() == ADMIN_EMAIL.lower()
            and password == ADMIN_PASSWORD)


# ── User operations ───────────────────────────────────────────────────────────
def create_user(identifier: str, id_type: str, password: str = "", name: str = ""):
    if identifier.strip().lower() == ADMIN_EMAIL.lower():
        return None
    conn = get_conn()
    c = conn.cursor()
    try:
        pw_hash = hash_password(password) if password else ""
        c.execute(
            f"INSERT INTO users (identifier, identifier_type, password_hash, name, created_at) "
            f"VALUES ({PH},{PH},{PH},{PH},{PH})",
            (identifier.strip().lower(), id_type, pw_hash, name.strip(), ist_now())
        )
        conn.commit()
        c.execute(f"SELECT * FROM users WHERE identifier = {PH}", (identifier.strip().lower(),))
        return _row(c.fetchone())
    except Exception:
        conn.rollback() if USE_POSTGRES else None
        return None
    finally:
        conn.close()

def get_user(identifier: str):
    conn = get_conn()
    c = conn.cursor()
    c.execute(f"SELECT * FROM users WHERE identifier = {PH}", (identifier.strip().lower(),))
    row = c.fetchone()
    conn.close()
    return _row(row)

def login_user(identifier: str, password: str = ""):
    user = get_user(identifier)
    if not user:
        return None
    if not user["password_hash"]:
        return user
    if password and verify_password(password, user["password_hash"]):
        return user
    return None


# ── Order operations ──────────────────────────────────────────────────────────
def create_order(user_id, identifier: str, image_path: str) -> dict:
    conn = get_conn()
    c = conn.cursor()
    oid = generate_order_id()
    now = ist_now()
    c.execute(
        f"INSERT INTO orders (order_id, user_id, identifier, image_path, status, created_at, updated_at) "
        f"VALUES ({PH},{PH},{PH},{PH},{PH},{PH},{PH})",
        (oid, user_id, identifier, image_path, "pending", now, now)
    )
    conn.commit()
    c.execute(f"SELECT * FROM orders WHERE order_id = {PH}", (oid,))
    row = _row(c.fetchone())
    conn.close()
    return row

def get_order(order_id: str):
    conn = get_conn()
    c = conn.cursor()
    c.execute(f"SELECT * FROM orders WHERE order_id = {PH}", (order_id.upper(),))
    row = c.fetchone()
    conn.close()
    return _row(row)

def get_orders_for_user(identifier: str) -> list:
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        f"SELECT * FROM orders WHERE identifier = {PH} ORDER BY created_at DESC",
        (identifier.strip().lower(),)
    )
    rows = c.fetchall()
    conn.close()
    return _rows(rows)

def get_all_orders(limit: int = 200) -> list:
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        f"SELECT o.*, COALESCE(u.name,'') AS customer_name "
        f"FROM orders o LEFT JOIN users u ON o.user_id = u.id "
        f"ORDER BY o.created_at DESC LIMIT {PH}",
        (limit,)
    )
    rows = c.fetchall()
    conn.close()
    return _rows(rows)

def update_order_status(order_id: str, status: str, notes: str = ""):
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        f"UPDATE orders SET status = {PH}, notes = {PH}, updated_at = {PH} WHERE order_id = {PH}",
        (status, notes, ist_now(), order_id.upper())
    )
    conn.commit()
    c.execute(f"SELECT * FROM orders WHERE order_id = {PH}", (order_id.upper(),))
    row = c.fetchone()
    conn.close()
    return _row(row)


# ── Settings ──────────────────────────────────────────────────────────────────
def get_setting(key: str):
    conn = get_conn()
    c = conn.cursor()
    c.execute(f"SELECT value FROM settings WHERE key = {PH}", (key,))
    row = c.fetchone()
    conn.close()
    return _row(row)["value"] if row else None

def set_setting(key: str, value: str):
    conn = get_conn()
    c = conn.cursor()
    if USE_POSTGRES:
        c.execute(
            "INSERT INTO settings (key,value) VALUES (%s,%s) "
            "ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value",
            (key, value)
        )
    else:
        c.execute("INSERT OR REPLACE INTO settings (key,value) VALUES (?,?)", (key, value))
    conn.commit()
    conn.close()

def is_shop_open() -> bool:
    return get_setting("shop_open") == "1"

def get_stats() -> dict:
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT status, COUNT(*) as cnt FROM orders GROUP BY status")
    rows = c.fetchall()
    conn.close()
    by_status = {r["status"]: r["cnt"] for r in _rows(rows)}
    return {"total_orders": sum(by_status.values()), "by_status": by_status}

def get_dashboard_data(limit: int = 500) -> dict:
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        f"SELECT o.order_id, o.identifier, o.image_path, o.status, "
        f"o.notes, o.created_at, o.updated_at, COALESCE(u.name,'') AS customer_name "
        f"FROM orders o LEFT JOIN users u ON o.user_id = u.id "
        f"ORDER BY o.created_at DESC LIMIT {PH}",
        (limit,)
    )
    orders_rows = c.fetchall()
    c.execute("SELECT status, COUNT(*) as cnt FROM orders GROUP BY status")
    stats_rows = c.fetchall()
    c.execute(f"SELECT value FROM settings WHERE key = {PH}", ('shop_open',))
    shop_row = c.fetchone()
    c.execute(f"SELECT value FROM settings WHERE key = {PH}", ('shop_name',))
    name_row = c.fetchone()
    conn.close()

    by_status = {r["status"]: r["cnt"] for r in _rows(stats_rows)}
    return {
        "orders":    _rows(orders_rows),
        "stats":     {"total_orders": sum(by_status.values()), "by_status": by_status},
        "shop_open": (_row(shop_row)["value"] == "1") if shop_row else True,
        "shop_name": _row(name_row)["value"] if name_row else "Maa Gayatri Pharmacy",
    }
