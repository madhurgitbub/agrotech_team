# AgroTech Backend — FastAPI + Supabase

This folder contains the real backend for the AgroTech frontend.

## Stack
- FastAPI REST API
- Supabase PostgreSQL
- JWT authentication
- bcrypt password hashing
- Role-based admin authorization

## 1. Create Supabase database
1. Create a project at https://supabase.com/
2. Open **SQL Editor**.
3. Paste and run `schema.sql`.
4. Open **Project Settings → API** and copy the project URL and **service_role** key.
5. Never put the service_role key inside frontend JavaScript.

## 2. Configure environment
Copy `.env.example` to `.env` and fill in:

- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`
- `JWT_SECRET`
- `CORS_ORIGINS`
- `SMTP_HOST`
- `SMTP_PORT`
- `SMTP_USERNAME`
- `SMTP_PASSWORD`
- `SMTP_FROM_EMAIL`
- `SMTP_USE_TLS`
- `SMTP_USE_SSL`

## 3. Install and run
Windows:

```powershell
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000
```

Linux/macOS:

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000
```

API docs: `http://127.0.0.1:8000/docs`

Health check:

`http://127.0.0.1:8000/api/health`

## 4. Run the frontend
From the project root:

```bash
python -m http.server 5500
```

Open:

`http://127.0.0.1:5500/`

The frontend API client defaults to:

`http://127.0.0.1:8000/api`

If your backend is deployed, run this in the browser console once before using the app:

```javascript
localStorage.setItem('agro_api_base', 'https://YOUR-BACKEND-DOMAIN/api');
```

Then reload the page.

## Frontend + backend runtime model
- Frontend (`python -m http.server ...`) and backend (`uvicorn main:app ...`) run as two separate processes.
- You must keep backend running while using authenticated app features.
- Supabase is used by backend only; service-role key never goes to browser.

## SMTP/email verification note
Signup uses email OTP verification:
1. `POST /api/auth/register` sends OTP
2. `POST /api/auth/register/verify-otp` verifies OTP and creates user

## Important
- Do not commit `.env`.
- Do not expose `SUPABASE_SERVICE_ROLE_KEY` to the frontend.
- Public farmer/seller registration is available.
- Admin registration is kept as a separate page because the existing AgroTech UI requested separate Admin Login and Admin Register buttons. In production, admin registration should be protected by an invitation/super-admin approval flow.
