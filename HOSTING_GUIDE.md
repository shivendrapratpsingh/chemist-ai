# Maa Gayatri Pharmacy — Hosting Guide

## Admin Credentials (NEVER SHARE)
```
Email    : pratapsinghshivendra21@gmail.com
Password : $Hivendra123
```

---

## Option 1 — Local Network (Family/Staff on same WiFi)

1. Run `start_production.bat`
2. Open Command Prompt and type: `ipconfig`
3. Find your **IPv4 Address** (e.g. `192.168.1.5`)
4. Share this link with anyone on the same WiFi:
   ```
   http://192.168.1.5:8090
   ```
5. QR code on the home page auto-updates to this address.

⚠️ Works only while your PC is ON and the server is running.

---

## Option 2 — Internet (Anyone in the World, 24/7)

### Recommended: Railway.app (Free, Easy)

1. Go to https://railway.app and sign up (free)
2. Click **New Project → Deploy from GitHub**
3. Push your `chemist-ai` folder to a GitHub repo first:
   ```bash
   git init
   git add .
   git commit -m "Maa Gayatri Pharmacy"
   git remote add origin https://github.com/YOUR_USERNAME/maa-gayatri.git
   git push -u origin main
   ```
4. On Railway, select your repo
5. Set these environment variables in Railway dashboard:
   - `PORT` = `8090`
6. Add a `Procfile` in the root folder with:
   ```
   web: cd backend && python -m uvicorn main:app --host 0.0.0.0 --port $PORT
   ```
7. Railway gives you a URL like: `https://maa-gayatri.up.railway.app`
8. Done — runs 24/7 for free!

---

### Alternative: Render.com (Also Free)

1. Go to https://render.com → New Web Service
2. Connect your GitHub repo
3. Set:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `cd backend && python -m uvicorn main:app --host 0.0.0.0 --port 10000`
   - **Environment**: `Python 3`
4. Free tier = always on (spins down after 15 min idle on free, upgrade for 24/7)

---

### Alternative: VPS (DigitalOcean / AWS / Hostinger)

```bash
# 1. Upload files to server
scp -r chemist-ai/ user@YOUR_SERVER_IP:~/

# 2. SSH into server
ssh user@YOUR_SERVER_IP

# 3. Install Python & deps
cd ~/chemist-ai
pip3 install -r requirements.txt

# 4. Run with PM2 (keeps alive 24/7, auto-restarts on crash)
npm install -g pm2
pm2 start "cd backend && python3 -m uvicorn main:app --host 0.0.0.0 --port 8090" --name maa-gayatri
pm2 save
pm2 startup   # auto-start on server reboot

# 5. Open port 8090 in your firewall
# DigitalOcean: Networking → Firewalls → add TCP 8090
# AWS: Security Groups → Inbound → add TCP 8090

# Access at: http://YOUR_SERVER_IP:8090
```

---

## Important Notes for Any Hosting

| Thing | Detail |
|---|---|
| **Database** | `data/chemist.db` — back this up regularly. All orders live here. |
| **Uploads** | `data/uploads/` — prescription photos. Back up too. |
| **Port** | Always `8090` (or set via `$PORT` env var on cloud) |
| **HTTPS** | Use a reverse proxy (Nginx/Caddy) or Railway/Render handles it automatically |
| **Admin URL** | `https://your-domain.com/admin.html` |
| **Customer URL** | `https://your-domain.com` or `https://your-domain.com/order.html` |

---

## Quick Test After Deploying

Open these URLs and confirm they work:
- `https://YOUR_DOMAIN/` → Home page loads
- `https://YOUR_DOMAIN/api/shop/status` → Returns `{"open": true, ...}`
- `https://YOUR_DOMAIN/login.html` → Login page loads
- Log in with admin email/password → Goes to admin dashboard
- `https://YOUR_DOMAIN/order.html` → Upload page (test on mobile too!)
