# LMS Academy API — Documentation & Deployment Guide

## 1. Executive Summary

The LMS System is a modular REST API for managing educational content, student enrollments, and live sessions. The system is split into a **React Frontend** (Vite) and this **Django + DRF Backend**. The backend uses **PostgreSQL** for data storage and **SimpleJWT** for stateless authentication. Role-Based Access Control (RBAC) separates operations among Students, Trainers, Supporters, and Administrators.

**Repository:** [github.com/aseemfaras/lms-academy-api](https://github.com/aseemfaras/lms-academy-api)

---

## 2. Tech Stack

| Layer | Technology |
| :--- | :--- |
| Backend Runtime | Python 3.10+ |
| Backend Framework | Django 6.0.2 + Django REST Framework |
| Database | PostgreSQL (production) / SQLite (local fallback) |
| Authentication | `djangorestframework-simplejwt` (JWT) |
| CORS | `django-cors-headers` |
| Environment Config | `django-environ` (reads `.env`) |
| Production Server | Gunicorn (WSGI) managed by PM2 |
| Frontend | React + Vite (separate repo, e.g. deployed on Vercel) |

---

## 3. Project Structure

```text
lms-academy-api/
│
├── apps/                        # Domain logic, separated by role
│   ├── users/                   # Auth, JWT login, user registration
│   ├── trainers/                # Courses, modules, live sessions
│   ├── students/                # Enrollments
│   ├── admins/                  # Admin logic
│   └── supporters/              # Support portal logic
│
├── config/                      # Django project settings
│   ├── settings.py              # DB, CORS, JWT, logging
│   ├── urls.py                  # Root URL router
│   └── wsgi.py                  # WSGI entry point (used by Gunicorn)
│
├── media/                       # Uploaded files (course images, notes)
├── manage.py                    # Django CLI (migrate, runserver, etc.)
├── erp_setup.sql                # Reference SQL schema (optional)
├── error.log                    # Application error log
└── .env                         # Environment variables (NOT in git)
```

---

## 4. How the Three Layers Connect

```text
┌─────────────────┐       HTTPS/HTTP        ┌─────────────────────┐
│  React Frontend │  ──────────────────────▶  │  Django API (PM2)   │
│  (Vite / Vercel)│  ◀──────────────────────  │  Port 8000          │
│  VITE_API_URL   │       JSON + JWT          │  /api/users/login/  │
└─────────────────┘                           └──────────┬──────────┘
                                                         │
                                                         │ psycopg2
                                                         ▼
                                              ┌─────────────────────┐
                                              │  PostgreSQL          │
                                              │  DB credentials      │
                                              │  from .env           │
                                              └─────────────────────┘
```

### A. Frontend → Backend

The React app sends HTTP requests to the backend API. Every authenticated request includes:

```http
Authorization: Bearer <access_token>
```

**Frontend `.env` (Vite):**

```env
VITE_API_URL=http://YOUR_SERVER_IP:8000/api/
```

**Frontend usage:**

```javascript
const apiUrl = import.meta.env.VITE_API_URL || "http://localhost:8000/api/";
const response = await axios.post(`${apiUrl}users/login/`, {
  username: "student@example.com",  // backend maps this to email
  password: "yourpassword",
});
```

**Backend CORS (`config/settings.py`):**

The backend only accepts requests from origins listed in `CORS_ALLOWED_ORIGINS`. When deploying, you **must** add your frontend URL here:

```python
CORS_ALLOWED_ORIGINS = [
    "https://your-frontend-domain.vercel.app",   # production frontend
    "http://localhost:5173",                      # local dev frontend
]
CSRF_TRUSTED_ORIGINS = [
    "https://your-frontend-domain.vercel.app",
]
```

Without this, the browser will block API calls with a CORS error.

### B. Backend → Database

Database credentials are loaded from the `.env` file via `django-environ` and `os.getenv`:

```python
# config/settings.py
DATABASES = {
    'default': {
        'ENGINE': os.getenv('DB_ENGINE', 'django.db.backends.sqlite3'),
        'NAME': os.getenv('DB_NAME', BASE_DIR / 'db.sqlite3'),
        'USER': os.getenv('DB_USER', ''),
        'PASSWORD': os.getenv('DB_PASSWORD', ''),
        'HOST': os.getenv('DB_HOST', ''),
        'PORT': os.getenv('DB_PORT', ''),
    }
}
```

If `DB_ENGINE` is not set, Django falls back to SQLite (`db.sqlite3`). For production, always configure PostgreSQL in `.env`.

### C. API Route Map

| Endpoint Prefix | App | Example |
| :--- | :--- | :--- |
| `/api/users/` | users | `POST /api/users/login/` |
| `/api/students/` | students | `GET /api/students/enrollments/` |
| `/api/` | trainers | `GET /api/courses/` |
| `/admin/` | Django admin | `http://server:8000/admin/` |

---

## 5. Server Deployment Guide (Step-by-Step)

This section walks through deploying the backend on a Linux VPS (Ubuntu 22.04/24.04). The same steps apply to AWS EC2, DigitalOcean Droplets, or any cloud VM.

### Prerequisites

- A Linux server with SSH access (root or sudo user)
- Your server's public IP address (e.g. `203.0.113.10`)
- Git installed on the server
- The React frontend repo URL (for CORS configuration)

---

### Step 1 — Connect to Your Server

From your local machine:

```bash
ssh username@YOUR_SERVER_IP
```

Replace `username` with your server user (often `ubuntu` on AWS/DigitalOcean).

---

### Step 2 — Install System Dependencies

```bash
sudo apt update && sudo apt upgrade -y

# Python 3, pip, venv, and build tools
sudo apt install -y python3 python3-pip python3-venv python3-dev \
  build-essential libpq-dev git curl

# PostgreSQL
sudo apt install -y postgresql postgresql-contrib

# Node.js (required for PM2 process manager)
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# PM2 — keeps the backend running after you disconnect from SSH
sudo npm install -g pm2
```

Verify installations:

```bash
python3 --version    # should be 3.10+
node --version
pm2 --version
psql --version
```

---

### Step 3 — Set Up PostgreSQL Database

Switch to the PostgreSQL admin user and create a database:

```bash
sudo -u postgres psql
```

Inside the PostgreSQL shell, run (change the password to something secure):

```sql
CREATE DATABASE lms_academy;
CREATE USER lms_user WITH PASSWORD 'YourStrongPassword123';
ALTER ROLE lms_user SET client_encoding TO 'utf8';
ALTER ROLE lms_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE lms_user SET timezone TO 'Asia/Kolkata';
GRANT ALL PRIVILEGES ON DATABASE lms_academy TO lms_user;

-- PostgreSQL 15+ requires explicit schema grants
\c lms_academy
GRANT ALL ON SCHEMA public TO lms_user;

\q
```

Test the connection:

```bash
psql -h localhost -U lms_user -d lms_academy -W
```

---

### Step 4 — Clone the Repository

```bash
cd ~
git clone https://github.com/aseemfaras/lms-academy-api.git
cd lms-academy-api
```

---

### Step 5 — Create Python Virtual Environment & Install Packages

```bash
python3 -m venv env
source env/bin/activate

pip install --upgrade pip

pip install django djangorestframework djangorestframework-simplejwt \
  django-cors-headers psycopg2-binary django-environ gunicorn
```

> **Note:** There is no `requirements.txt` in the repo yet. Run the command above, or generate one after installing:
> `pip freeze > requirements.txt`

---

### Step 6 — Create the `.env` File

Create a `.env` file in the project root (`lms-academy-api/.env`). This file is git-ignored and holds all secrets.

```bash
nano .env
```

Paste and edit the following template:

```env
# ── Database (PostgreSQL) ──────────────────────────────────────
DB_ENGINE=django.db.backends.postgresql
DB_NAME=lms_academy
DB_USER=lms_user
DB_PASSWORD=YourStrongPassword123
DB_HOST=localhost
DB_PORT=5432

# ── Email (optional — for password reset / notifications) ──────
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=support@yourdomain.com
```

Save and exit (`Ctrl+O`, `Enter`, `Ctrl+X` in nano).

**Verify Django can read the `.env`:**

```bash
source env/bin/activate
python manage.py check
```

If the database connection fails, double-check `DB_NAME`, `DB_USER`, `DB_PASSWORD`, and that PostgreSQL is running:

```bash
sudo systemctl status postgresql
```

---

### Step 7 — Run Database Migrations

Django migrations create all tables (`users`, `trainers_course`, `students_enrollment`, etc.) automatically. You do **not** need to run the `.sql` files manually unless you want a reference.

```bash
source env/bin/activate
python manage.py makemigrations
python manage.py migrate
```

Create an admin superuser (for Django admin panel):

```bash
python manage.py createsuperuser
```

Follow the prompts (email is the login field).

---

### Step 8 — Configure CORS for Your Frontend

Edit `config/settings.py` on the server:

```bash
nano config/settings.py
```

Find `CORS_ALLOWED_ORIGINS` and `CSRF_TRUSTED_ORIGINS` and add your frontend URL:

```python
CORS_ALLOWED_ORIGINS = [
    "https://your-frontend.vercel.app",   # your deployed frontend
    "http://localhost:5173",               # local frontend dev
    "http://YOUR_SERVER_IP:5173",          # if frontend runs on same server
]

CSRF_TRUSTED_ORIGINS = [
    "https://your-frontend.vercel.app",
]
```

Save the file.

---

### Step 9 — Test the Server Manually (Before PM2)

Quick smoke test before setting up PM2:

```bash
source env/bin/activate
python manage.py runserver 0.0.0.0:8000
```

From your local machine, open a browser or run:

```bash
curl http://YOUR_SERVER_IP:8000/api/users/
```

You should get a JSON response (likely `401 Unauthorized` without a token — that means the API is running).

Press `Ctrl+C` to stop the dev server.

---

### Step 10 — Run the Backend with PM2 + Gunicorn

Django's `runserver` is for development only. In production, use **Gunicorn** as the WSGI server and **PM2** to keep it alive, restart on crash, and start on boot.

**Create a PM2 ecosystem file:**

```bash
nano ecosystem.config.js
```

Paste:

```javascript
module.exports = {
  apps: [
    {
      name: "lms-api",
      script: "gunicorn",
      args: "config.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 120",
      cwd: "/home/ubuntu/lms-academy-api",
      interpreter: "/home/ubuntu/lms-academy-api/env/bin/python",
      env: {
        DJANGO_SETTINGS_MODULE: "config.settings",
      },
      error_file: "/home/ubuntu/lms-academy-api/logs/pm2-error.log",
      out_file: "/home/ubuntu/lms-academy-api/logs/pm2-out.log",
      autorestart: true,
      watch: false,
      max_memory_restart: "500M",
    },
  ],
};
```

> **Important:** Update `cwd` and `interpreter` paths to match your actual server username and project location.

Create the logs directory and start PM2:

```bash
mkdir -p logs
pm2 start ecosystem.config.js
pm2 save
pm2 startup
```

Run the command that `pm2 startup` prints (it looks like `sudo env PATH=... pm2 startup systemd -u ubuntu --hp /home/ubuntu`). This ensures the API restarts automatically if the server reboots.

**Useful PM2 commands:**

```bash
pm2 status              # check if lms-api is running
pm2 logs lms-api        # live log stream
pm2 restart lms-api     # restart after code changes
pm2 stop lms-api        # stop the process
pm2 delete lms-api      # remove from PM2
```

---

### Step 11 — Open the Firewall Port

Allow inbound traffic on port 8000:

```bash
sudo ufw allow OpenSSH
sudo ufw allow 8000
sudo ufw enable
sudo ufw status
```

Test from your browser: `http://YOUR_SERVER_IP:8000/api/users/`

---

### Step 12 — Connect the Frontend

#### Option A: Frontend deployed on Vercel (recommended)

1. In your **frontend repo**, create or edit `.env.production`:

   ```env
   VITE_API_URL=http://YOUR_SERVER_IP:8000/api/
   ```

   Or, if you set up a domain with Nginx (Step 13):

   ```env
   VITE_API_URL=https://api.yourdomain.com/api/
   ```

2. Redeploy the frontend on Vercel so the env variable is baked into the build.

3. Add the Vercel URL to `CORS_ALLOWED_ORIGINS` in `config/settings.py` (Step 8) and restart PM2:

   ```bash
   pm2 restart lms-api
   ```

#### Option B: Frontend running locally during development

**Frontend `.env`:**

```env
VITE_API_URL=http://YOUR_SERVER_IP:8000/api/
```

**Backend `config/settings.py`:** ensure `http://localhost:5173` is in `CORS_ALLOWED_ORIGINS`.

#### Verify the connection

Open the frontend, try logging in. If you see a CORS error in the browser console:

- Confirm the frontend origin exactly matches an entry in `CORS_ALLOWED_ORIGINS` (including `https` vs `http`, no trailing slash).
- Restart PM2 after any settings change.

Test login directly with curl:

```bash
curl -X POST http://YOUR_SERVER_IP:8000/api/users/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin@example.com", "password": "yourpassword"}'
```

Expected response:

```json
{
  "access": "eyJ...",
  "refresh": "eyJ...",
  "role": "ADMIN"
}
```

---

### Step 13 — (Optional) Nginx Reverse Proxy + HTTPS

For production, put Nginx in front of Gunicorn and use a domain with SSL.

```bash
sudo apt install -y nginx certbot python3-certbot-nginx
```

Create an Nginx site config:

```bash
sudo nano /etc/nginx/sites-available/lms-api
```

```nginx
server {
    listen 80;
    server_name api.yourdomain.com;

    client_max_body_size 50M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /media/ {
        alias /home/ubuntu/lms-academy-api/media/;
    }
}
```

Enable the site and get SSL:

```bash
sudo ln -s /etc/nginx/sites-available/lms-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
sudo certbot --nginx -d api.yourdomain.com
```

Update firewall (close 8000 publicly, open 80/443):

```bash
sudo ufw delete allow 8000
sudo ufw allow 'Nginx Full'
```

Update frontend `VITE_API_URL` to `https://api.yourdomain.com/api/` and add the HTTPS frontend URL to CORS.

---

## 6. Environment Variables Reference

| Variable | Required | Default | Description |
| :--- | :---: | :--- | :--- |
| `DB_ENGINE` | Yes (prod) | `sqlite3` | `django.db.backends.postgresql` for production |
| `DB_NAME` | Yes (prod) | `db.sqlite3` | PostgreSQL database name |
| `DB_USER` | Yes (prod) | — | PostgreSQL username |
| `DB_PASSWORD` | Yes (prod) | — | PostgreSQL password |
| `DB_HOST` | Yes (prod) | — | `localhost` or remote DB host |
| `DB_PORT` | No | `5432` | PostgreSQL port |
| `EMAIL_BACKEND` | No | console | SMTP backend for sending emails |
| `EMAIL_HOST` | No | smtp.gmail.com | SMTP server |
| `EMAIL_PORT` | No | `587` | SMTP port |
| `EMAIL_USE_TLS` | No | `True` | Enable TLS |
| `EMAIL_HOST_USER` | No | — | SMTP username |
| `EMAIL_HOST_PASSWORD` | No | — | SMTP password / app password |
| `DEFAULT_FROM_EMAIL` | No | — | Sender address |

**Frontend (Vite) variable:**

| Variable | Description |
| :--- | :--- |
| `VITE_API_URL` | Full base URL to the API, e.g. `http://203.0.113.10:8000/api/` |

---

## 7. Local Development Setup

For working on your laptop before deploying:

```bash
# Clone and enter project
git clone https://github.com/aseemfaras/lms-academy-api.git
cd lms-academy-api

# Virtual environment
python -m venv env

# Activate (Linux/Mac)
source env/bin/activate

# Activate (Windows PowerShell)
env\Scripts\Activate.ps1

# Install dependencies
pip install django djangorestframework djangorestframework-simplejwt \
  django-cors-headers psycopg2-binary django-environ gunicorn

# Create .env (use SQLite by omitting DB_ENGINE, or point to local PostgreSQL)
# See Step 6 above for the .env template

# Apply migrations
python manage.py migrate

# Run dev server
python manage.py runserver 0.0.0.0:8000
```

API available at: `http://localhost:8000/api/`

---

## 8. System Workflow (Request Lifecycle)

Using login as an example:

1. **URL Routing** — `POST /api/users/login/` hits `config/urls.py` → `users.urls`
2. **View** — `CustomTokenObtainPairView` validates credentials against PostgreSQL
3. **Response** — Returns JWT tokens + user role: `{ "access": "...", "refresh": "...", "role": "STUDENT" }`
4. **Authenticated requests** — Client sends `Authorization: Bearer <access_token>` on all subsequent API calls

---

## 9. Core Modules

| App | Purpose |
| :--- | :--- |
| `users` | Identity, JWT auth, registration, role assignment (`ADMIN`, `TRAINER`, `STUDENT`, `SUPPORTER`) |
| `trainers` | Courses, modules, live sessions, trainer activity logs |
| `students` | Enrollments linking students to courses/batches |
| `admins` | Administrative oversight |
| `supporters` | Support portal |

---

## 10. Database Schema (Key Tables)

| Table | Model | Purpose |
| :--- | :--- | :--- |
| `users` | `users.User` | Identity (email as login) |
| `trainers_course` | `trainers.Course` | Course catalog |
| `trainers_module` | `trainers.Module` | Course syllabus / content |
| `students_enrollment` | `students.Enrollment` | Student ↔ course enrollment |

Tables are created automatically by `python manage.py migrate`. The `.sql` files in the repo (`erp_setup.sql`, `erp_clean_setup.sql`) are reference scripts only.

---

## 11. Troubleshooting

| Problem | Likely Cause | Fix |
| :--- | :--- | :--- |
| `FATAL: password authentication failed` | Wrong `.env` DB credentials | Verify `DB_USER`, `DB_PASSWORD`, re-run `migrate` |
| `django.db.utils.OperationalError: could not connect` | PostgreSQL not running | `sudo systemctl start postgresql` |
| CORS error in browser | Frontend origin not in `CORS_ALLOWED_ORIGINS` | Add exact URL to `config/settings.py`, `pm2 restart lms-api` |
| `502 Bad Gateway` (Nginx) | Gunicorn not running | `pm2 status`, check `pm2 logs lms-api` |
| API returns HTML instead of JSON | Wrong URL path | Ensure URL ends with `/api/` prefix |
| Login returns 401 | Wrong email/password | Use email (not username) — frontend sends `username` field which backend maps to email |
| PM2 process keeps restarting | Import error or bad path in ecosystem file | Check `pm2 logs lms-api --lines 50`, verify `interpreter` path |
| Media files (images) not loading | DEBUG=False without Nginx media config | Add `/media/` location block in Nginx (Step 13) |

**Log files to check:**

```bash
pm2 logs lms-api              # Gunicorn / application output
cat error.log                 # Django error log (project root)
cat sql_queries.log           # SQL query log (project root)
sudo tail -f /var/log/nginx/error.log   # Nginx errors (if using Nginx)
```

---

## 12. Deploying Code Updates

When you push new code to the server:

```bash
cd ~/lms-academy-api
git pull origin main
source env/bin/activate
pip install django djangorestframework djangorestframework-simplejwt \
  django-cors-headers psycopg2-binary django-environ gunicorn
python manage.py migrate
pm2 restart lms-api
```

---

## 13. Security Checklist for Production

Before going live with real users:

- [ ] Change `SECRET_KEY` in `config/settings.py` to a random string (use `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`)
- [ ] Set `DEBUG = False` in `config/settings.py`
- [ ] Restrict `ALLOWED_HOSTS` to your domain/IP instead of `['*']`
- [ ] Use strong PostgreSQL passwords
- [ ] Never commit `.env` to git
- [ ] Set up HTTPS via Nginx + Certbot
- [ ] Restrict PostgreSQL to localhost only (default)
