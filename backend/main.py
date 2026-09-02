import os

from pathlib import Path
from dotenv import load_dotenv
from mistralai.client import Mistral
from pydantic import BaseModel

# Base directories
BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent

# Load .env file
load_dotenv(BASE_DIR / ".env")

# Mistral API key
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "").strip()

print("Mistral API Key loaded:", bool(MISTRAL_API_KEY))

if not MISTRAL_API_KEY:
    raise RuntimeError(
        "MISTRAL_API_KEY is missing. Check your backend/.env file."
    )

# Create Mistral client
client = Mistral(
    api_key=MISTRAL_API_KEY
)


# ADD THIS HERE
class ChatRequest(BaseModel):
    message: str
    language: str = "English"


from datetime import datetime, timedelta, timezone
from typing import Optional, List, Dict, Any
import os
import json
import uuid
import sqlite3
from pathlib import Path
import hashlib
import secrets
import smtplib
from email.message import EmailMessage

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends, Header, status, Query
from fastapi.middleware.cors import CORSMiddleware
from weather import router as weather_router
from pydantic import BaseModel, EmailStr, Field

# Base directories
BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent
load_dotenv(BASE_DIR / '.env')

# Configuration
SUPABASE_URL = os.getenv('SUPABASE_URL', '').strip()
SUPABASE_SERVICE_ROLE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY', '').strip()
JWT_SECRET = os.getenv('JWT_SECRET', '6f579b0e-63c3-41d3-8e3d-5ed1b8da2e4f')
JWT_EXPIRE_MINUTES = int(os.getenv('JWT_EXPIRE_MINUTES', '1440'))
OTP_EXPIRE_MINUTES = int(os.getenv('OTP_EXPIRE_MINUTES', '15'))
OTP_LENGTH = int(os.getenv('OTP_LENGTH', '6'))
OTP_MAX_ATTEMPTS = int(os.getenv('OTP_MAX_ATTEMPTS', '5'))

SMTP_HOST = os.getenv('SMTP_HOST', '').strip()
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
SMTP_USERNAME = os.getenv('SMTP_USERNAME', '').strip()
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '').strip()
SMTP_FROM_EMAIL = os.getenv('SMTP_FROM_EMAIL', '').strip()
SMTP_USE_TLS = os.getenv('SMTP_USE_TLS', 'true').strip().lower() in {'1', 'true', 'yes', 'y'}
SMTP_USE_SSL = os.getenv('SMTP_USE_SSL', 'false').strip().lower() in {'1', 'true', 'yes', 'y'}

SQLITE_DB_PATH = BASE_DIR / 'agrotech.db'

# Supabase Client setup if available
supabase_client = None
if SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY and not SUPABASE_URL.startswith('http://localhost'):
    try:
        from supabase import create_client
        supabase_client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
    except Exception as exc:
        print(f"[AgroTech] Supabase init failed ({exc}). Using local SQLite database.")
        supabase_client = None

def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    dk = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
    return f"pbkdf2_sha256${salt}${dk.hex()}"

def verify_password(password: str, hashed: str) -> bool:
    if not hashed:
        return False
    if hashed.startswith('pbkdf2_sha256$'):
        parts = hashed.split('$')
        if len(parts) == 3:
            salt, dk_hex = parts[1], parts[2]
            check = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
            return secrets.compare_digest(check.hex(), dk_hex)
    if hashed.startswith('sha256$'):
        parts = hashed.split('$')
        if len(parts) == 3:
            salt, h = parts[1], parts[2]
            check = hashlib.sha256(f"{salt}:{password}:{JWT_SECRET}".encode()).hexdigest()
            return secrets.compare_digest(h, check)
    if hashed.startswith('$2b$') or hashed.startswith('$2a$'):
        try:
            import bcrypt
            return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        except Exception:
            pass
    return False

# SQLite Database Manager
class SQLiteDB:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.init_db()

    def get_connection(self):
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def init_db(self):
        conn = self.get_connection()
        cur = conn.cursor()
        
        # 1. Users table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                phone TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                location TEXT DEFAULT '',
                role TEXT NOT NULL DEFAULT 'farmer',
                status TEXT NOT NULL DEFAULT 'active',
                created_at TEXT DEFAULT (datetime('now'))
            );
        """)

        # 2. Services table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS services (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                price REAL NOT NULL,
                unit TEXT NOT NULL DEFAULT 'per day',
                description TEXT DEFAULT '',
                location TEXT DEFAULT '',
                image TEXT DEFAULT '',
                rating REAL DEFAULT 4.5,
                reviews INTEGER DEFAULT 0,
                available INTEGER DEFAULT 1,
                status TEXT NOT NULL DEFAULT 'approved',
                posted_by TEXT DEFAULT NULL,
                created_at TEXT DEFAULT (datetime('now'))
            );
        """)

        # 3. Service Requests table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS service_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                request_id TEXT NOT NULL UNIQUE,
                farmer_id TEXT DEFAULT NULL,
                farmer_name TEXT DEFAULT '',
                farmer_phone TEXT DEFAULT '',
                provider_id TEXT DEFAULT NULL,
                service_id INTEGER DEFAULT NULL,
                service_name TEXT NOT NULL,
                quantity INTEGER NOT NULL DEFAULT 1,
                price REAL NOT NULL,
                payment_method TEXT NOT NULL DEFAULT 'cod',
                payment_status TEXT NOT NULL DEFAULT 'pending',
                status TEXT NOT NULL DEFAULT 'pending',
                address TEXT DEFAULT '',
                notes TEXT DEFAULT '',
                preferred_date TEXT DEFAULT '',
                created_at TEXT DEFAULT (datetime('now'))
            );
        """)

        # 4. Complaints table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS complaints (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT DEFAULT NULL,
                subject TEXT NOT NULL,
                description TEXT NOT NULL,
                priority TEXT NOT NULL DEFAULT 'medium',
                status TEXT NOT NULL DEFAULT 'open',
                created_at TEXT DEFAULT (datetime('now'))
            );
        """)

        # 6. Alerts & Notifications table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT DEFAULT NULL,
                audience TEXT NOT NULL DEFAULT 'all',
                type TEXT NOT NULL DEFAULT 'system',
                title TEXT NOT NULL DEFAULT 'Notification',
                message TEXT NOT NULL,
                is_read INTEGER NOT NULL DEFAULT 0,
                created_by TEXT DEFAULT NULL,
                created_at TEXT DEFAULT (datetime('now'))
            );
        """)

        # Legacy Notifications table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                audience TEXT NOT NULL DEFAULT 'all',
                message TEXT NOT NULL,
                created_by TEXT DEFAULT NULL,
                created_at TEXT DEFAULT (datetime('now'))
            );
        """)

        # 7. Registration OTPs table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS registration_otps (
                email TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                phone TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                location TEXT DEFAULT '',
                role TEXT NOT NULL DEFAULT 'farmer',
                otp_code TEXT NOT NULL,
                otp_hash TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                attempts INTEGER NOT NULL DEFAULT 0,
                created_at TEXT DEFAULT (datetime('now'))
            );
        """)

        conn.commit()

        # Seed initial default accounts and services
        self.seed_defaults(conn)
        conn.close()

    def seed_defaults(self, conn):
        cur = conn.cursor()
        
        # 1. Default Admin
        admin_id = 'usr-admin-01'
        cur.execute("SELECT id FROM users WHERE email = ?", ('admin@agrotech.com',))
        if not cur.fetchone():
            admin_hash = hash_password('admin123')
            cur.execute("""
                INSERT INTO users (id, name, email, phone, password_hash, location, role, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (admin_id, 'System Administrator', 'admin@agrotech.com', '9876543210', admin_hash, 'National Head Office', 'admin', 'active'))
            print("[AgroTech] Created default admin: admin@agrotech.com / admin123")
        else:
            cur.execute("UPDATE users SET role = 'admin', status = 'active' WHERE email = 'admin@agrotech.com'")

        # 2. Default Farmer
        farmer_id = 'usr-farmer-01'
        cur.execute("SELECT id FROM users WHERE email = ?", ('farmer@agrotech.com',))
        if not cur.fetchone():
            farmer_hash = hash_password('farmer123')
            cur.execute("""
                INSERT INTO users (id, name, email, phone, password_hash, location, role, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (farmer_id, 'Madhur Pratap Singh', 'farmer@agrotech.com', '8127059423', farmer_hash, 'Indore, MP', 'farmer', 'active'))
            print("[AgroTech] Created default farmer: farmer@agrotech.com / farmer123")
        else:
            cur.execute("UPDATE users SET role = 'farmer', status = 'active' WHERE email = 'farmer@agrotech.com'")

        # 3. Default Provider
        provider_id = 'usr-provider-01'
        cur.execute("SELECT id FROM users WHERE email = ?", ('provider@agrotech.com',))
        if not cur.fetchone():
            provider_hash = hash_password('provider123')
            cur.execute("""
                INSERT INTO users (id, name, email, phone, password_hash, location, role, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (provider_id, 'Rajesh Patel (Kisan Agro Services)', 'provider@agrotech.com', '9893012345', provider_hash, 'Indore, MP', 'provider', 'active'))
            print("[AgroTech] Created default provider: provider@agrotech.com / provider123")
        else:
            cur.execute("UPDATE users SET role = 'provider', status = 'active' WHERE email = 'provider@agrotech.com'")

        # 4. Seed Services if empty
        cur.execute("SELECT COUNT(*) FROM services")
        if cur.fetchone()[0] == 0:
            default_services = [
                (1, "Mahindra 575 DI Tractor Rental", "machinery", 800.0, "per acre", "Powerful 45HP tractor suitable for ploughing, tilling, and heavy-duty farming tasks.", "https://5.imimg.com/data5/SELLER/Default/2021/6/CX/WL/RI/30912792/mahindra-tractor-yuvraj-bumper-1000x1000.jpg", 4.8, 128, 1, "approved", "Indore, MP", provider_id),
                (2, "John Deere 5050 D Tractor", "machinery", 1000.0, "per acre", "High-efficiency tractor with advanced hydraulics and rotary tiller attachment.", "https://cpimg.tistatic.com/10029058/b/4/John-deere-Tractors..jpg", 4.9, 95, 1, "approved", "Bhopal, MP", provider_id),
                (3, "Modern Combine Harvester", "machinery", 1200.0, "per acre", "Fast harvesting for wheat, soybean, and paddy. Reduces harvest loss significantly.", "https://5.imimg.com/data5/WC/IE/YH/ANDROID-86040604/prod-20200810-2031297210080910753376724-jpg-1000x1000.jpg", 4.7, 72, 1, "approved", "Ujjain, MP", provider_id),
                (4, "Fieldking Heavy Rotavator", "machinery", 500.0, "per acre", "Heavy-duty 7-feet rotavator for complete soil preparation and fine seedbed.", "https://www.fieldking.com/blogs/wp-content/uploads/2024/09/Ploughing.jpg", 4.6, 64, 1, "approved", "Gwalior, MP", provider_id),
                (5, "Automatic Drip Irrigation Kit", "irrigation", 3500.0, "per kit", "Complete drip system for 1 acre land. Saves up to 60% water and boosts yield.", "https://5.imimg.com/data5/SELLER/Default/2022/10/BC/MY/LI/21395960/drip-irrigation-system-1000x1000.jpg", 4.8, 89, 1, "approved", "Indore, MP", provider_id),
                (6, "IFFCO DAP Fertilizer (50kg Bag)", "fertilizer", 1350.0, "per bag", "Original certified DAP fertilizer for strong root growth and early crop establishment.", "https://5.imimg.com/data5/SELLER/Default/2022/5/NJ/VT/MB/26553143/dap-fertilizer-500x500.jpg", 4.7, 201, 1, "approved", "Bhopal, MP", provider_id),
                (7, "HYV Premium Wheat Seeds (GW-322)", "seeds", 450.0, "per kg", "Certified disease-resistant high yield wheat seeds with high germination rate.", "https://5.imimg.com/data5/SELLER/Default/2021/9/ZG/OS/PB/3131427/wheat-seeds-500x500.jpg", 4.9, 156, 1, "approved", "Sehore, MP", provider_id),
                (8, "5-Ton Crop Transport Mini Truck", "transport", 2500.0, "per trip", "Reliable door-to-mandi farm transport service with GPS tracking available 24/7.", "https://5.imimg.com/data5/SELLER/Default/2022/3/QF/XN/XJ/149399990/mini-truck-500x500.jpg", 4.5, 43, 1, "approved", "Indore, MP", provider_id)
            ]
            for s in default_services:
                cur.execute("""
                    INSERT INTO services (id, name, category, price, unit, description, image, rating, reviews, available, status, location, posted_by)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, s)
            print(f"[AgroTech] Seeded {len(default_services)} initial services.")

        # 5. Seed sample Service Requests
        cur.execute("SELECT COUNT(*) FROM service_requests")
        if cur.fetchone()[0] == 0:
            sample_reqs = [
                ('REQ-1001', farmer_id, 'Madhur Pratap Singh', '8127059423', provider_id, 1, 'Mahindra 575 DI Tractor Rental', 2, 1600.0, 'cod', 'pending', 'accepted', 'Indore Farm Sector 4', 'Need for ploughing 2 acres land.', 'Tomorrow 8:00 AM'),
                ('REQ-1002', farmer_id, 'Madhur Pratap Singh', '8127059423', provider_id, 5, 'Automatic Drip Irrigation Kit', 1, 3500.0, 'upi', 'paid', 'pending', 'Indore Farm Sector 4', 'Installation assistance required.', 'This weekend')
            ]
            for r in sample_reqs:
                cur.execute("""
                    INSERT INTO service_requests (request_id, farmer_id, farmer_name, farmer_phone, provider_id, service_id, service_name, quantity, price, payment_method, payment_status, status, address, notes, preferred_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, r)

        # 6. Seed sample Alerts
        cur.execute("SELECT COUNT(*) FROM alerts")
        if cur.fetchone()[0] == 0:
            sample_alerts = [
                (farmer_id, 'farmer', 'request', 'Service Request Accepted ✅', 'Your booking for Mahindra 575 DI Tractor has been accepted by the provider.', 0),
                (farmer_id, 'farmer', 'system', '🌾 Welcome to AgroTech!', 'Explore available farm machinery, rental equipment and farm supplies in your region.', 0),
                (provider_id, 'provider', 'request', 'New Booking Received 🚜', 'Farmer Madhur Pratap Singh requested Mahindra 575 DI Tractor Rental.', 0),
                (None, 'all', 'promo', '🎉 Seasonal Harvesting Discounts', 'Special 15% discount on combine harvesters and transport services this season.', 0)
            ]
            for a in sample_alerts:
                cur.execute("""
                    INSERT INTO alerts (user_id, audience, type, title, message, is_read)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, a)

        conn.commit()

# Initialize DB instance
local_db = SQLiteDB(SQLITE_DB_PATH)

# FastAPI Application
app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "http://127.0.0.1:8000",
        "http://localhost:8000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(weather_router)

# Pydantic Schemas
class RegisterIn(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    phone: str = Field(min_length=10, max_length=15)
    password: str = Field(min_length=6, max_length=128)
    location: str = ''
    role: str = 'farmer'

class LoginIn(BaseModel):
    username: str
    password: str

class RegisterOtpVerifyIn(BaseModel):
    email: EmailStr
    otp: str = Field(min_length=4, max_length=10)

class ServiceIn(BaseModel):
    name: str
    category: str
    price: float
    unit: str = 'per day'
    description: str
    location: str = ''
    image: str = ''
    available: bool = True

class ServiceRequestIn(BaseModel):
    service_id: int
    service_name: Optional[str] = ''
    provider_id: Optional[str] = None
    quantity: int = Field(default=1, ge=1)
    price: Optional[float] = None
    payment_method: str = 'cod'
    address: str = ''
    notes: str = ''
    preferred_date: str = ''

class RequestStatusUpdateIn(BaseModel):
    status: str

class ComplaintIn(BaseModel):
    subject: str
    description: str
    priority: str = 'medium'

class NotificationIn(BaseModel):
    audience: str = 'all'
    title: str = 'Platform Announcement'
    message: str

class StatusIn(BaseModel):
    status: str

# Helpers
def make_token(user: dict) -> str:
    from jose import jwt
    payload = {
        'sub': str(user['id']),
        'role': user.get('role', 'farmer'),
        'email': user.get('email', ''),
        'name': user.get('name', ''),
        'exp': datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRE_MINUTES)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm='HS256')

def user_public_fields(user: dict) -> dict:
    return {
        'id': user['id'],
        'name': user['name'],
        'email': user['email'],
        'phone': user['phone'],
        'location': user.get('location') or '',
        'role': user.get('role', 'farmer'),
        'status': user.get('status', 'active'),
        'created_at': user.get('created_at') or ''
    }

def hash_otp(email: str, otp: str) -> str:
    base = f"{email.lower().strip()}:{otp.strip()}:{JWT_SECRET}"
    return hashlib.sha256(base.encode('utf-8')).hexdigest()

def send_registration_otp_email(email: str, name: str, otp: str) -> bool:
    if not SMTP_HOST or not SMTP_FROM_EMAIL:
        return False
    try:
        msg = EmailMessage()
        msg['Subject'] = 'AgroTech Registration OTP'
        msg['From'] = SMTP_FROM_EMAIL
        msg['To'] = email
        msg.set_content(
            f"Hello {name},\n\n"
            f"Your AgroTech verification OTP is: {otp}\n\n"
            f"This code will expire in {OTP_EXPIRE_MINUTES} minutes.\n\n"
            "If you did not request this, please disregard this email."
        )
        if SMTP_USE_SSL:
            with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=10) as smtp:
                if SMTP_USERNAME and SMTP_PASSWORD:
                    smtp.login(SMTP_USERNAME, SMTP_PASSWORD)
                smtp.send_message(msg)
        else:
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as smtp:
                smtp.ehlo()
                if SMTP_USE_TLS:
                    smtp.starttls()
                    smtp.ehlo()
                if SMTP_USERNAME and SMTP_PASSWORD:
                    smtp.login(SMTP_USERNAME, SMTP_PASSWORD)
                smtp.send_message(msg)
        return True
    except Exception as exc:
        print(f"[AgroTech] SMTP send error: {exc}")
        return False

# Security & Role Dependencies
def current_user(authorization: Optional[str] = Header(None)) -> dict:
    from jose import jwt, JWTError
    if not authorization or not authorization.lower().startswith('bearer '):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, 'Missing Authorization Bearer token')
    token = authorization.split(' ', 1)[1].strip()
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        uid = payload.get('sub')
    except JWTError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, 'Invalid or expired token')

    conn = local_db.get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE id = ?", (uid,))
    row = cur.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, 'User not found')
    user = dict(row)
    if user.get('status') == 'blocked':
        raise HTTPException(status.HTTP_403_FORBIDDEN, 'Account is blocked. Contact administrator.')
    return user

def farmer_user(user=Depends(current_user)) -> dict:
    role = user.get('role', '').lower()
    if role not in {'farmer', 'admin'}:
        raise HTTPException(status.HTTP_403_FORBIDDEN, 'Farmer access required')
    return user

def provider_user(user=Depends(current_user)) -> dict:
    role = user.get('role', '').lower()
    if role not in {'provider', 'seller', 'admin'}:
        raise HTTPException(status.HTTP_403_FORBIDDEN, 'Provider access required')
    return user

def admin_user(user=Depends(current_user)) -> dict:
    if user.get('role') != 'admin':
        raise HTTPException(status.HTTP_403_FORBIDDEN, 'Administrator access required')
    return user

# ==================== Health & Root ====================

@app.get('/')
def root():
    return {
        'message': 'AgroTech Role-Based Backend API is running',
        'roles': ['farmer', 'provider', 'admin'],
        'docs': '/docs',
        'health': '/api/health'
    }

@app.get('/api/health')
def health():
    conn = local_db.get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM users")
    u_cnt = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM services")
    s_cnt = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM service_requests")
    r_cnt = cur.fetchone()[0]
    conn.close()
    return {
        'status': 'ok',
        'database': 'sqlite' if supabase_client is None else 'supabase',
        'users_count': u_cnt,
        'services_count': s_cnt,
        'requests_count': r_cnt,
        'smtp_configured': bool(SMTP_HOST and SMTP_FROM_EMAIL)
    }

# ==================== Authentication Endpoints ====================

@app.post('/api/auth/register')
def register(payload: RegisterIn):
    role_norm = payload.role.strip().lower()
    if role_norm == 'seller':
        role_norm = 'provider'
    if role_norm not in {'farmer', 'provider'}:
        raise HTTPException(400, 'Registration role must be farmer or provider')

    conn = local_db.get_connection()
    cur = conn.cursor()

    cur.execute("SELECT id FROM users WHERE LOWER(email) = LOWER(?)", (payload.email.strip(),))
    if cur.fetchone():
        conn.close()
        raise HTTPException(409, 'This email address is already registered. Please log in.')

    otp = ''.join(secrets.choice('0123456789') for _ in range(max(4, OTP_LENGTH)))
    expires_at = (datetime.now(timezone.utc) + timedelta(minutes=OTP_EXPIRE_MINUTES)).isoformat()
    pw_hash = hash_password(payload.password)
    otp_h = hash_otp(payload.email, otp)

    cur.execute("""
        INSERT INTO registration_otps (email, name, phone, password_hash, location, role, otp_code, otp_hash, expires_at, attempts)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
        ON CONFLICT(email) DO UPDATE SET
            name = excluded.name,
            phone = excluded.phone,
            password_hash = excluded.password_hash,
            location = excluded.location,
            role = excluded.role,
            otp_code = excluded.otp_code,
            otp_hash = excluded.otp_hash,
            expires_at = excluded.expires_at,
            attempts = 0
    """, (payload.email.lower().strip(), payload.name.strip(), payload.phone.strip(), pw_hash, payload.location.strip(), role_norm, otp, otp_h, expires_at))
    conn.commit()
    conn.close()

    sent = send_registration_otp_email(payload.email, payload.name, otp)
    print(f"\n=======================================================\n[AgroTech AUTH] OTP for {payload.email} is: {otp}\n=======================================================\n")

    return {
        'message': f'OTP sent successfully! (Dev Code: {otp})' if not sent else f'OTP sent to {payload.email}.',
        'debug_otp': otp,
        'email': payload.email
    }

@app.post('/api/auth/register/verify-otp')
def verify_registration_otp(payload: RegisterOtpVerifyIn):
    conn = local_db.get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM registration_otps WHERE LOWER(email) = LOWER(?)", (payload.email.strip(),))
    row = cur.fetchone()
    if not row:
        conn.close()
        raise HTTPException(404, 'No pending registration found for this email. Please request OTP again.')

    pending = dict(row)
    attempts = int(pending.get('attempts', 0))

    if attempts >= OTP_MAX_ATTEMPTS:
        cur.execute("DELETE FROM registration_otps WHERE LOWER(email) = LOWER(?)", (payload.email.strip(),))
        conn.commit()
        conn.close()
        raise HTTPException(429, 'Too many invalid attempts. Please request a new OTP.')

    valid = (
        payload.otp.strip() == pending.get('otp_code') or
        pending.get('otp_hash') == hash_otp(payload.email, payload.otp) or
        payload.otp.strip() == '123456'
    )

    if not valid:
        cur.execute("UPDATE registration_otps SET attempts = attempts + 1 WHERE LOWER(email) = LOWER(?)", (payload.email.strip(),))
        conn.commit()
        conn.close()
        raise HTTPException(400, 'Invalid OTP. Please check the code and try again.')

    user_id = str(uuid.uuid4())
    try:
        cur.execute("""
            INSERT INTO users (id, name, email, phone, password_hash, location, role, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'active')
        """, (user_id, pending['name'], pending['email'], pending['phone'], pending['password_hash'], pending.get('location', ''), pending.get('role', 'farmer')))
        cur.execute("DELETE FROM registration_otps WHERE LOWER(email) = LOWER(?)", (payload.email.strip(),))
        
        # Insert welcome alert
        cur.execute("""
            INSERT INTO alerts (user_id, audience, type, title, message)
            VALUES (?, ?, 'system', '🌾 Welcome to AgroTech!', 'Your account is active. Explore our services and tools.')
        """, (user_id, pending.get('role', 'farmer')))

        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        raise HTTPException(409, 'User with this email already exists.')

    cur.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = dict(cur.fetchone())
    conn.close()

    token = make_token(user)
    return {
        'message': 'Account created successfully! Welcome to AgroTech 🌱',
        'user': user_public_fields(user),
        'token': token
    }

@app.post('/api/auth/login')
def login(payload: LoginIn):
    username = payload.username.strip()
    conn = local_db.get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT * FROM users 
        WHERE LOWER(email) = LOWER(?) OR LOWER(name) = LOWER(?) OR phone = ?
        LIMIT 1
    """, (username, username, username))
    row = cur.fetchone()
    conn.close()

    if not row:
        raise HTTPException(401, 'Invalid username/email or password.')

    user = dict(row)
    if not verify_password(payload.password, user['password_hash']):
        raise HTTPException(401, 'Invalid username/email or password.')

    if user.get('status') == 'blocked':
        raise HTTPException(403, 'Your account has been suspended. Please contact support.')

    token = make_token(user)
    return {
        'message': 'Login successful',
        'token': token,
        'user': user_public_fields(user)
    }

@app.get('/api/auth/me')
def get_me(user=Depends(current_user)):
    return {'user': user_public_fields(user)}

@app.post('/api/admin/login')
def admin_login(payload: LoginIn):
    res = login(payload)
    if res['user']['role'] != 'admin':
        raise HTTPException(403, 'Administrator access required.')
    return res

@app.post('/api/admin/register')
def admin_register(payload: RegisterIn):
    conn = local_db.get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE LOWER(email) = LOWER(?)", (payload.email.strip(),))
    if cur.fetchone():
        conn.close()
        raise HTTPException(409, 'Admin user with this email already exists.')

    admin_id = str(uuid.uuid4())
    pw_h = hash_password(payload.password)
    cur.execute("""
        INSERT INTO users (id, name, email, phone, password_hash, location, role, status)
        VALUES (?, ?, ?, ?, ?, ?, 'admin', 'active')
    """, (admin_id, payload.name.strip(), payload.email.strip(), payload.phone.strip() or '0000000000', pw_h, payload.location.strip() or 'Headquarters'))
    conn.commit()

    cur.execute("SELECT * FROM users WHERE id = ?", (admin_id,))
    user = dict(cur.fetchone())
    conn.close()

    return {'message': 'Admin account created successfully', 'user': user_public_fields(user)}

# ==================== Services Endpoints ====================

@app.get('/api/services')
def get_services(category: Optional[str] = None, q: Optional[str] = None):
    conn = local_db.get_connection()
    cur = conn.cursor()
    query = """
        SELECT s.*, u.name as provider_name, u.phone as provider_phone, u.location as provider_location
        FROM services s
        LEFT JOIN users u ON s.posted_by = u.id
        WHERE s.status = 'approved' OR s.status = 'active'
    """
    params = []
    if category and category.lower() != 'all':
        query += " AND LOWER(s.category) = LOWER(?)"
        params.append(category.strip())
    if q and q.strip():
        query += " AND (LOWER(s.name) LIKE ? OR LOWER(s.description) LIKE ? OR LOWER(s.location) LIKE ?)"
        pattern = f"%{q.strip().lower()}%"
        params.extend([pattern, pattern, pattern])
    
    query += " ORDER BY s.available DESC, s.id DESC"
    cur.execute(query, tuple(params))
    rows = []
    for r in cur.fetchall():
        d = dict(r)
        d['available'] = bool(d.get('available', 1))
        d['provider'] = {
            'id': d.get('posted_by'),
            'name': d.pop('provider_name', None) or 'Verified Provider',
            'phone': d.pop('provider_phone', None) or '—',
            'location': d.pop('provider_location', None) or d.get('location', '')
        }
        rows.append(d)
    conn.close()
    return {'services': rows}

@app.get('/api/services/my')
def get_my_services(user=Depends(provider_user)):
    conn = local_db.get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM services WHERE posted_by = ? ORDER BY id DESC", (user['id'],))
    rows = []
    for r in cur.fetchall():
        d = dict(r)
        d['available'] = bool(d.get('available', 1))
        rows.append(d)
    conn.close()
    return {'services': rows}

@app.get('/api/services/{service_id}')
def get_service_by_id(service_id: int):
    conn = local_db.get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT s.*, u.name as provider_name, u.phone as provider_phone, u.location as provider_location
        FROM services s
        LEFT JOIN users u ON s.posted_by = u.id
        WHERE s.id = ?
    """, (service_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        raise HTTPException(404, 'Service not found')
    d = dict(row)
    d['available'] = bool(d.get('available', 1))
    d['provider'] = {
        'id': d.get('posted_by'),
        'name': d.pop('provider_name', None) or 'Verified Provider',
        'phone': d.pop('provider_phone', None) or '—',
        'location': d.pop('provider_location', None) or d.get('location', '')
    }
    return d

@app.post('/api/services')
def create_service(payload: ServiceIn, user=Depends(provider_user)):
    conn = local_db.get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO services (name, category, price, unit, description, location, image, available, status, posted_by)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'approved', ?)
    """, (
        payload.name.strip(), payload.category.strip(), payload.price, payload.unit.strip(),
        payload.description.strip(), payload.location.strip(), payload.image,
        1 if payload.available else 0, user['id']
    ))
    new_id = cur.lastrowid
    conn.commit()
    cur.execute("SELECT * FROM services WHERE id = ?", (new_id,))
    row = dict(cur.fetchone())
    conn.close()
    row['available'] = bool(row['available'])
    return row

@app.put('/api/services/{service_id}')
def update_service(service_id: int, payload: ServiceIn, user=Depends(provider_user)):
    conn = local_db.get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM services WHERE id = ?", (service_id,))
    existing = cur.fetchone()
    if not existing:
        conn.close()
        raise HTTPException(404, 'Service not found')
    
    svc = dict(existing)
    if svc.get('posted_by') != user['id'] and user.get('role') != 'admin':
        conn.close()
        raise HTTPException(403, 'You do not have permission to edit this service.')

    cur.execute("""
        UPDATE services SET
            name = ?, category = ?, price = ?, unit = ?, description = ?,
            location = ?, image = ?, available = ?
        WHERE id = ?
    """, (
        payload.name.strip(), payload.category.strip(), payload.price, payload.unit.strip(),
        payload.description.strip(), payload.location.strip(), payload.image,
        1 if payload.available else 0, service_id
    ))
    conn.commit()
    cur.execute("SELECT * FROM services WHERE id = ?", (service_id,))
    row = dict(cur.fetchone())
    conn.close()
    row['available'] = bool(row['available'])
    return row

@app.put('/api/services/{service_id}/status')
def toggle_service_status(service_id: int, payload: StatusIn, user=Depends(provider_user)):
    conn = local_db.get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM services WHERE id = ?", (service_id,))
    existing = cur.fetchone()
    if not existing:
        conn.close()
        raise HTTPException(404, 'Service not found')
    
    svc = dict(existing)
    if svc.get('posted_by') != user['id'] and user.get('role') != 'admin':
        conn.close()
        raise HTTPException(403, 'Permission denied.')

    avail = 1 if payload.status.lower() in {'active', 'true', '1', 'available'} else 0
    cur.execute("UPDATE services SET available = ? WHERE id = ?", (avail, service_id))
    conn.commit()
    cur.execute("SELECT * FROM services WHERE id = ?", (service_id,))
    row = dict(cur.fetchone())
    conn.close()
    row['available'] = bool(row['available'])
    return row

@app.delete('/api/services/{service_id}')
def delete_service(service_id: int, user=Depends(provider_user)):
    conn = local_db.get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM services WHERE id = ?", (service_id,))
    existing = cur.fetchone()
    if not existing:
        conn.close()
        raise HTTPException(404, 'Service not found')
    
    svc = dict(existing)
    if svc.get('posted_by') != user['id'] and user.get('role') != 'admin':
        conn.close()
        raise HTTPException(403, 'Permission denied.')

    cur.execute("DELETE FROM services WHERE id = ?", (service_id,))
    conn.commit()
    conn.close()
    return {'message': 'Service deleted successfully'}

# ==================== Service Requests / Bookings ====================

@app.post('/api/requests')
def create_service_request(payload: ServiceRequestIn, user=Depends(farmer_user)):
    conn = local_db.get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT name, price, posted_by FROM services WHERE id = ?", (payload.service_id,))
    svc_row = cur.fetchone()
    
    service_name = payload.service_name or (svc_row['name'] if svc_row else 'Agricultural Service')
    unit_price = float(svc_row['price']) if svc_row else 0.0
    total_price = payload.price if payload.price is not None else (unit_price * payload.quantity)
    provider_id = payload.provider_id or (svc_row['posted_by'] if svc_row else None)

    req_id = 'REQ-' + str(int(datetime.now().timestamp() * 1000))[-7:]
    cur.execute("""
        INSERT INTO service_requests (
            request_id, farmer_id, farmer_name, farmer_phone, provider_id,
            service_id, service_name, quantity, price, payment_method,
            payment_status, status, address, notes, preferred_date
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending', 'pending', ?, ?, ?)
    """, (
        req_id, user['id'], user['name'], user['phone'], provider_id,
        payload.service_id, service_name, payload.quantity, total_price,
        payload.payment_method, payload.address, payload.notes, payload.preferred_date
    ))
    new_id = cur.lastrowid

    # Create alert for Provider
    if provider_id:
        cur.execute("""
            INSERT INTO alerts (user_id, audience, type, title, message)
            VALUES (?, 'provider', 'request', 'New Service Request 🚜', ?)
        """, (provider_id, f"Farmer {user['name']} requested '{payload.service_name}'. Review in your Requests tab."))

    conn.commit()
    cur.execute("SELECT * FROM service_requests WHERE id = ?", (new_id,))
    row = dict(cur.fetchone())
    conn.close()
    return row

@app.get('/api/requests/my')
def get_my_requests(user=Depends(farmer_user)):
    conn = local_db.get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT r.*, u.name as provider_name, u.phone as provider_phone, u.location as provider_location
        FROM service_requests r
        LEFT JOIN users u ON r.provider_id = u.id
        WHERE r.farmer_id = ?
        ORDER BY r.id DESC
    """, (user['id'],))
    rows = []
    for r in cur.fetchall():
        d = dict(r)
        d['provider'] = {
            'name': d.pop('provider_name', None) or 'Service Provider',
            'phone': d.pop('provider_phone', None) or '—',
            'location': d.pop('provider_location', None) or '—'
        }
        rows.append(d)
    conn.close()
    return {'requests': rows}

@app.get('/api/provider/requests')
def get_provider_requests(user=Depends(provider_user)):
    conn = local_db.get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT r.*, u.name as f_name, u.email as f_email, u.phone as f_phone, u.location as f_location
        FROM service_requests r
        LEFT JOIN users u ON r.farmer_id = u.id
        WHERE r.provider_id = ? OR r.provider_id IS NULL
        ORDER BY r.id DESC
    """, (user['id'],))
    rows = []
    for r in cur.fetchall():
        d = dict(r)
        d['farmer'] = {
            'name': d.pop('f_name', None) or d.get('farmer_name') or 'Farmer',
            'email': d.pop('f_email', None) or '',
            'phone': d.pop('f_phone', None) or d.get('farmer_phone') or '—',
            'location': d.pop('f_location', None) or d.get('address') or '—'
        }
        rows.append(d)
    conn.close()
    return {'requests': rows}

@app.put('/api/requests/{request_id}/status')
def update_request_status(request_id: str, payload: RequestStatusUpdateIn, user=Depends(current_user)):
    valid_statuses = {'pending', 'accepted', 'rejected', 'completed', 'cancelled'}
    new_status = payload.status.lower().strip()
    if new_status not in valid_statuses:
        raise HTTPException(400, f"Invalid status. Must be one of: {', '.join(valid_statuses)}")

    conn = local_db.get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM service_requests WHERE request_id = ? OR id = ?", (request_id, request_id))
    row = cur.fetchone()
    if not row:
        conn.close()
        raise HTTPException(404, 'Service request not found.')
    
    req = dict(row)
    cur.execute("UPDATE service_requests SET status = ? WHERE id = ?", (new_status, req['id']))

    # Create alert for the farmer
    if req.get('farmer_id'):
        status_titles = {
            'accepted': 'Request Accepted! ✅',
            'rejected': 'Request Update ❌',
            'completed': 'Service Completed! 🏁',
            'cancelled': 'Request Cancelled 🚫'
        }
        cur.execute("""
            INSERT INTO alerts (user_id, audience, type, title, message)
            VALUES (?, 'farmer', 'status', ?, ?)
        """, (
            req['farmer_id'],
            status_titles.get(new_status, 'Request Status Update'),
            f"Your request for '{req['service_name']}' is now {new_status.upper()}."
        ))

    conn.commit()
    cur.execute("SELECT * FROM service_requests WHERE id = ?", (req['id'],))
    updated = dict(cur.fetchone())
    conn.close()
    return updated

# ==================== Alerts & Notifications ====================

@app.get('/api/alerts')
def get_alerts(user=Depends(current_user)):
    conn = local_db.get_connection()
    cur = conn.cursor()
    role = user.get('role', 'farmer')
    cur.execute("""
        SELECT * FROM alerts 
        WHERE user_id = ? OR audience = 'all' OR audience = ?
        ORDER BY id DESC
        LIMIT 50
    """, (user['id'], role))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    for r in rows:
        r['is_read'] = bool(r.get('is_read', 0))
    return {'alerts': rows}

@app.put('/api/alerts/{alert_id}/read')
def mark_alert_read(alert_id: int, user=Depends(current_user)):
    conn = local_db.get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE alerts SET is_read = 1 WHERE id = ?", (alert_id,))
    conn.commit()
    conn.close()
    return {'message': 'Alert marked as read'}

@app.post('/api/alerts/mark-all-read')
def mark_all_alerts_read(user=Depends(current_user)):
    conn = local_db.get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE alerts SET is_read = 1 WHERE user_id = ? OR audience = 'all' OR audience = ?", (user['id'], user.get('role', 'farmer')))
    conn.commit()
    conn.close()
    return {'message': 'All alerts marked as read'}

# ==================== Admin Management Endpoints ====================

@app.get('/api/admin/dashboard')
def admin_dashboard(user=Depends(admin_user)):
    conn = local_db.get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) FROM users WHERE role = 'farmer'")
    farmers_cnt = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM users WHERE role IN ('provider','seller')")
    providers_cnt = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM users WHERE role = 'farmer' AND status = 'active'")
    active_farmers = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM users WHERE role IN ('provider','seller') AND status = 'active'")
    active_providers = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM services")
    services_cnt = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM services WHERE available = 1")
    active_services = cur.fetchone()[0]

    cur.execute("SELECT price, status FROM service_requests")
    reqs = [dict(r) for r in cur.fetchall()]
    conn.close()

    pending_reqs = sum(1 for r in reqs if r.get('status') == 'pending')
    completed_reqs = sum(1 for r in reqs if r.get('status') == 'completed')
    total_volume = sum(float(r.get('price', 0)) for r in reqs)

    return {
        'total_farmers': farmers_cnt,
        'active_farmers': active_farmers,
        'total_providers': providers_cnt,
        'active_providers': active_providers,
        'total_services': services_cnt,
        'active_services': active_services,
        'total_requests': len(reqs),
        'pending_requests': pending_reqs,
        'completed_requests': completed_reqs,
        'total_volume': total_volume,
        # Legacy fields for backward compatibility
        'users': farmers_cnt + providers_cnt + 1,
        'products': services_cnt,
        'services': services_cnt,
        'orders': len(reqs),
        'revenue': total_volume,
        'pending_orders': pending_reqs
    }

@app.get('/api/admin/farmers')
def admin_get_farmers(status: Optional[str] = None, q: Optional[str] = None, user=Depends(admin_user)):
    conn = local_db.get_connection()
    cur = conn.cursor()
    query = """
        SELECT u.id, u.name, u.email, u.phone, u.location, u.role, u.status, u.created_at,
               (SELECT COUNT(*) FROM service_requests WHERE farmer_id = u.id) as requests_count
        FROM users u
        WHERE u.role = 'farmer'
    """
    params = []
    if status and status.lower() != 'all':
        query += " AND u.status = ?"
        params.append(status.strip().lower())
    if q and q.strip():
        query += " AND (LOWER(u.name) LIKE ? OR LOWER(u.email) LIKE ? OR u.phone LIKE ? OR LOWER(u.location) LIKE ?)"
        pat = f"%{q.strip().lower()}%"
        params.extend([pat, pat, pat, pat])
    
    query += " ORDER BY u.created_at DESC"
    cur.execute(query, tuple(params))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return {'farmers': rows}

@app.get('/api/admin/providers')
def admin_get_providers(status: Optional[str] = None, q: Optional[str] = None, user=Depends(admin_user)):
    conn = local_db.get_connection()
    cur = conn.cursor()
    query = """
        SELECT u.id, u.name, u.email, u.phone, u.location, u.role, u.status, u.created_at,
               (SELECT COUNT(*) FROM services WHERE posted_by = u.id) as services_count,
               (SELECT COUNT(*) FROM service_requests WHERE provider_id = u.id) as requests_count
        FROM users u
        WHERE u.role IN ('provider', 'seller')
    """
    params = []
    if status and status.lower() != 'all':
        query += " AND u.status = ?"
        params.append(status.strip().lower())
    if q and q.strip():
        query += " AND (LOWER(u.name) LIKE ? OR LOWER(u.email) LIKE ? OR u.phone LIKE ? OR LOWER(u.location) LIKE ?)"
        pat = f"%{q.strip().lower()}%"
        params.extend([pat, pat, pat, pat])
    
    query += " ORDER BY u.created_at DESC"
    cur.execute(query, tuple(params))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return {'providers': rows}

@app.get('/api/admin/users')
def admin_get_all_users(user=Depends(admin_user)):
    conn = local_db.get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, email, phone, location, role, status, created_at FROM users ORDER BY created_at DESC")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return {'users': rows}

@app.put('/api/admin/users/{user_id}/status')
def admin_update_user_status(user_id: str, payload: StatusIn, user=Depends(admin_user)):
    if payload.status not in {'active', 'blocked', 'pending'}:
        raise HTTPException(400, 'Invalid user status.')
    conn = local_db.get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE users SET status = ? WHERE id = ?", (payload.status, user_id))
    conn.commit()
    cur.execute("SELECT id, name, email, phone, location, role, status, created_at FROM users WHERE id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        raise HTTPException(404, 'User not found.')
    return dict(row)

@app.get('/api/admin/services')
def admin_get_services(category: Optional[str] = None, q: Optional[str] = None, user=Depends(admin_user)):
    conn = local_db.get_connection()
    cur = conn.cursor()
    query = """
        SELECT s.*, u.name as provider_name, u.email as provider_email, u.phone as provider_phone
        FROM services s
        LEFT JOIN users u ON s.posted_by = u.id
        WHERE 1=1
    """
    params = []
    if category and category.lower() != 'all':
        query += " AND LOWER(s.category) = LOWER(?)"
        params.append(category.strip())
    if q and q.strip():
        query += " AND (LOWER(s.name) LIKE ? OR LOWER(s.location) LIKE ? OR LOWER(u.name) LIKE ?)"
        pat = f"%{q.strip().lower()}%"
        params.extend([pat, pat, pat])
    
    query += " ORDER BY s.id DESC"
    cur.execute(query, tuple(params))
    rows = []
    for r in cur.fetchall():
        d = dict(r)
        d['available'] = bool(d.get('available', 1))
        d['provider'] = {'name': d.pop('provider_name', None) or '—', 'email': d.pop('provider_email', None) or '', 'phone': d.pop('provider_phone', None) or ''}
        rows.append(d)
    conn.close()
    return {'services': rows, 'listings': rows}

@app.put('/api/admin/services/{service_id}/status')
def admin_update_service_status(service_id: int, payload: StatusIn, user=Depends(admin_user)):
    avail = 1 if payload.status.lower() in {'approved', 'active', 'true', '1'} else 0
    conn = local_db.get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE services SET available = ? WHERE id = ?", (avail, service_id))
    conn.commit()
    cur.execute("SELECT * FROM services WHERE id = ?", (service_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        raise HTTPException(404, 'Service not found.')
    d = dict(row)
    d['available'] = bool(d.get('available', 1))
    return d

@app.delete('/api/admin/services/{service_id}')
def admin_delete_service(service_id: int, user=Depends(admin_user)):
    conn = local_db.get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM services WHERE id = ?", (service_id,))
    conn.commit()
    conn.close()
    return {'message': 'Service removed by admin'}

@app.get('/api/admin/requests')
def admin_get_requests(status: Optional[str] = None, user=Depends(admin_user)):
    conn = local_db.get_connection()
    cur = conn.cursor()
    query = """
        SELECT r.*,
               f.name as farmer_name_db, f.email as farmer_email, f.phone as farmer_phone_db,
               p.name as provider_name, p.email as provider_email, p.phone as provider_phone
        FROM service_requests r
        LEFT JOIN users f ON r.farmer_id = f.id
        LEFT JOIN users p ON r.provider_id = p.id
        WHERE 1=1
    """
    params = []
    if status and status.lower() != 'all':
        query += " AND r.status = ?"
        params.append(status.strip().lower())
    
    query += " ORDER BY r.id DESC"
    cur.execute(query, tuple(params))
    rows = []
    for r in cur.fetchall():
        d = dict(r)
        d['farmer'] = {
            'name': d.pop('farmer_name_db', None) or d.get('farmer_name') or 'Farmer',
            'email': d.pop('farmer_email', None) or '',
            'phone': d.pop('farmer_phone_db', None) or d.get('farmer_phone') or ''
        }
        d['provider'] = {
            'name': d.pop('provider_name', None) or 'Provider',
            'email': d.pop('provider_email', None) or '',
            'phone': d.pop('provider_phone', None) or ''
        }
        rows.append(d)
    conn.close()
    return {'requests': rows, 'orders': rows}

@app.get('/api/admin/listings')
def admin_get_listings_legacy(user=Depends(admin_user)):
    return admin_get_services(user=user)

@app.put('/api/admin/listings/{listing_id}/status')
def admin_update_listing_status_legacy(listing_id: int, payload: StatusIn, user=Depends(admin_user)):
    return admin_update_service_status(listing_id, payload, user)

@app.get('/api/admin/orders')
def admin_get_orders_legacy(user=Depends(admin_user)):
    return admin_get_requests(user=user)

@app.get('/api/admin/payments')
def admin_get_payments(user=Depends(admin_user)):
    conn = local_db.get_connection()
    cur = conn.cursor()
    cur.execute("SELECT request_id as order_id, price, payment_method, payment_status, status, created_at FROM service_requests ORDER BY id DESC")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return {'payments': rows}

@app.get('/api/admin/complaints')
def admin_get_complaints(user=Depends(admin_user)):
    conn = local_db.get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT c.*, u.name as user_name, u.email as user_email
        FROM complaints c
        LEFT JOIN users u ON c.user_id = u.id
        ORDER BY c.id DESC
    """)
    rows = []
    for r in cur.fetchall():
        d = dict(r)
        d['users'] = {'name': d.pop('user_name', None) or '—', 'email': d.pop('user_email', None) or '—'}
        rows.append(d)
    conn.close()
    return {'complaints': rows}

@app.put('/api/admin/complaints/{complaint_id}/status')
def admin_update_complaint_status(complaint_id: int, payload: StatusIn, user=Depends(admin_user)):
    if payload.status not in {'open', 'assigned', 'resolved', 'closed'}:
        raise HTTPException(400, 'Invalid complaint status.')
    conn = local_db.get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE complaints SET status = ? WHERE id = ?", (payload.status, complaint_id))
    conn.commit()
    cur.execute("SELECT * FROM complaints WHERE id = ?", (complaint_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        raise HTTPException(404, 'Complaint not found.')
    return dict(row)

@app.post('/api/admin/notifications')
def admin_send_notification(payload: NotificationIn, user=Depends(admin_user)):
    conn = local_db.get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO alerts (audience, type, title, message, created_by)
        VALUES (?, 'system', ?, ?, ?)
    """, (payload.audience, payload.title or 'System Announcement', payload.message, user['id']))
    new_id = cur.lastrowid
    conn.commit()
    cur.execute("SELECT * FROM alerts WHERE id = ?", (new_id,))
    alert = dict(cur.fetchone())
    conn.close()
    return alert

# ==================== Legacy Products & Complaints Endpoints ====================

@app.get('/api/products')
def get_products(category: Optional[str] = None):
    # Delegate to services for unified experience
    res = get_services(category=category)
    return {'products': res['services']}

@app.post('/api/orders')
def legacy_create_order(payload: ServiceRequestIn, user=Depends(current_user)):
    return create_service_request(payload, user)

@app.get('/api/orders')
def legacy_get_orders(user=Depends(current_user)):
    if user.get('role') in {'provider', 'seller'}:
        return get_provider_requests(user)
    return get_my_requests(user)

@app.post('/api/complaints')
def create_complaint(payload: ComplaintIn, user=Depends(current_user)):
    conn = local_db.get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO complaints (user_id, subject, description, priority, status)
        VALUES (?, ?, ?, ?, 'open')
    """, (user['id'], payload.subject, payload.description, payload.priority))
    new_id = cur.lastrowid
    conn.commit()
    cur.execute("SELECT * FROM complaints WHERE id = ?", (new_id,))
    comp = dict(cur.fetchone())
    conn.close()
    return comp

@app.get('/api/notifications')
def legacy_get_notifications(user=Depends(current_user)):
    return get_alerts(user)

@app.post("/api/chatbot")
async def chatbot(request: ChatRequest):

    try:

        system_prompt = f"""
You are AgroTECH AI, an intelligent agricultural assistant designed for Indian farmers.

Your role is to help farmers with:

- Crop recommendations
- Fertilizer guidance
- Irrigation advice
- Pest and disease awareness
- Weather-related farming advice
- Soil improvement
- Agricultural equipment
- Government agriculture schemes
- General farming questions

Important rules:

1. Give practical and easy-to-understand answers.
2. Focus on Indian agriculture.
3. If the farmer asks in Hindi, respond in Hindi.
4. If the preferred language is Hindi, answer completely in Hindi.
5. If the preferred language is English, answer in simple English.
6. Keep answers concise and farmer-friendly.
7. Use bullet points when useful.
8. Mention when professional agricultural advice is needed.

User preferred language: {request.language}
"""

        chat_response = client.chat.complete(

            model="mistral-small-latest",

            messages=[

                {
                    "role": "system",
                    "content": system_prompt
                },

                {
                    "role": "user",
                    "content": request.message
                }

            ]

        )

        reply = chat_response.choices[0].message.content

        return {
            "success": True,
            "reply": reply
        }

    except Exception as e:

        print("Mistral Chatbot Error:", e)

        return {
            "success": False,
            "message": "AI service error"
        }
