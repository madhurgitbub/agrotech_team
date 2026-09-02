# AgroTech — Quick Start & Run Guide

## 🚀 1-Click Startup (Recommended)

### 1. Start Backend API Server
Double-click `start_backend.bat` or run in terminal:
```bash
.\venv\Scripts\python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```
- Backend runs on `http://127.0.0.1:8000`
- Interactive API Swagger docs available at `http://127.0.0.1:8000/docs`
- Self-contained SQLite database (`backend/agrotech.db`) is automatically initialized and seeded with all products, demo farmer, and admin users on first run!

### 2. Start Frontend
Double-click `start_frontend.bat` or run in terminal:
```bash
python -m http.server 5500
```
Then open `http://127.0.0.1:5500/` in your browser.

---

## 🔑 Pre-Configured Demo Accounts

| Role | Username / Email | Password | Access Portal |
| :--- | :--- | :--- | :--- |
| **Farmer** | `farmer@agrotech.com` | `farmer123` | [Farmer Login](pages/login.html) |
| **Admin** | `admin@agrotech.com` | `admin123` | [Admin Portal](pages/admin-login.html) |

---

## 🌾 Registration & OTP Flow

1. Go to [Register Page](pages/register.html).
2. Enter your details and click **Send OTP →**.
3. The verification OTP is automatically generated and logged to the backend console. For quick testing and offline mode, the OTP code is auto-provided in the input field.
4. Click **Verify OTP & Create Account →** to instantly access the platform!

---

## 🛡️ Offline-Resilient Dual Mode
- **Connected Mode**: When FastAPI backend is running on `http://127.0.0.1:8000`, the frontend communicates with the server via REST API + JWT authentication.
- **Local Fallback Mode**: If the backend is not started, the frontend automatically falls back to an offline localStorage bridge so you can test and explore pages without console errors.
