# ⬡ CipherVault

**Secure Notes Web Application with REST API & Token Authentication**

A production-ready Flask web application where users store and manage private notes with end-to-end Fernet encryption, JWT-based authentication, and a clean dark-themed UI.

---

## 🚀 Quick Start (Local Development)

### 1. Clone & enter
```bash
git clone https://github.com/YOUR_USERNAME/ciphervault.git
cd ciphervault
```

### 2. Create virtual environment
```bash
python -m venv venv

# Windows:
venv\Scripts\activate

# Mac/Linux:
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Generate your encryption key
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```
Copy the output — you'll need it below.

### 5. Create `.env` file
```bash
cp .env.example .env
```
Edit `.env` with your values:
```
SECRET_KEY=change-this-to-a-random-secret
JWT_SECRET_KEY=change-this-jwt-secret-too
ENCRYPTION_KEY=<paste the key from step 4>
```

### 6. Run the app
```bash
python run.py
```

Open: **http://localhost:5000**

---

## ✅ VSCode Testing Commands

```bash
# Check Python version
python --version

# Install deps
pip install -r requirements.txt

# Run app
python run.py

# Test API with curl (register)
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@test.com","password":"test123"}'

# Test API with curl (login)
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"test123"}'

# Create a note (replace TOKEN with your JWT from login)
curl -X POST http://localhost:5000/api/notes \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TOKEN" \
  -d '{"title":"My Secret","content":"This is encrypted"}'
```

---

## 👑 Default Admin Account

```
Username: admin
Password: Admin@123
```

Access admin panel at: **http://localhost:5000/admin-panel**

> ⚠️ Change admin password immediately in production!

---

## 📤 GitHub Upload

```bash
# Initialize git
git init
git add .
git commit -m "Initial commit: CipherVault"

# Create repo on github.com, then:
git remote add origin https://github.com/YOUR_USERNAME/ciphervault.git
git branch -M main
git push -u origin main
```

---

## 🌐 Deploy on Render

1. Push code to GitHub (above)
2. Go to [render.com](https://render.com) → **New → Web Service**
3. Connect your GitHub repo
4. Settings:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn run:app`
   - **Python version:** `3.11`
5. Add Environment Variables:
   | Key | Value |
   |-----|-------|
   | `SECRET_KEY` | (generate random string) |
   | `JWT_SECRET_KEY` | (generate random string) |
   | `ENCRYPTION_KEY` | (generate with Fernet) |
6. Click **Deploy**

> For PostgreSQL: Add a Render Postgres database, copy the `DATABASE_URL`, and add it as an env var.

---

## 📁 Project Structure

```
ciphervault/
├── app/
│   ├── __init__.py       # App factory
│   ├── extensions.py     # DB + JWT init
│   ├── models.py         # User & Note models
│   ├── routes.py         # Web pages + REST API
│   ├── services.py       # Fernet encryption
│   ├── utils.py          # JWT decorators
│   ├── templates/        # Jinja2 HTML pages
│   └── static/           # CSS + JS
├── run.py
├── requirements.txt
├── Procfile
└── runtime.txt
```

---

## 🔐 Security Features

- **Fernet Encryption** — AES-128-CBC + HMAC-SHA256 on all note content
- **JWT Authentication** — Stateless token-based auth
- **Password Hashing** — PBKDF2-SHA256 via Werkzeug
- **Role-Based Access** — Admin panel hidden from navigation
- **Environment Variables** — No secrets in source code

---

## 🌐 Pages

| URL | Description |
|-----|-------------|
| `/` | Landing page |
| `/about` | About the project |
| `/features` | Features + API docs |
| `/contact` | Contact form |
| `/login` | Login |
| `/register` | Register |
| `/dashboard` | User vault (JWT required) |
| `/admin-panel` | Admin panel (admin JWT required, not in nav) |

---

## 📡 REST API

| Method | Endpoint | Auth |
|--------|----------|------|
| POST | `/api/auth/register` | — |
| POST | `/api/auth/login` | — |
| GET | `/api/auth/me` | JWT |
| GET | `/api/notes` | JWT |
| POST | `/api/notes` | JWT |
| DELETE | `/api/notes/<id>` | JWT |
| PATCH | `/api/notes/<id>/favorite` | JWT |
| GET | `/api/admin/users` | Admin JWT |
| GET | `/api/admin/notes` | Admin JWT |
| DELETE | `/api/admin/users/<id>` | Admin JWT |
