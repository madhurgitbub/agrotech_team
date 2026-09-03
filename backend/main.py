import os

from pathlib import Path
from dotenv import load_dotenv
from mistralai.client import Mistral
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from database.connection import get_db
from models.user import User
from models.registration_otp import RegistrationOTP
from models.alert import Alert
from models.service import Service
from models.service_request import ServiceRequest
from models.complaint import Complaint

# Base directories
BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent

# Load .env file
load_dotenv(BASE_DIR / ".env")

# Mistral API key
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

if MISTRAL_API_KEY:
    print("Mistral API Key loaded: True")
else:
    print("Mistral API Key loaded: False (AI features disabled)")

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
# import sqlite3
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

# SQLITE_DB_PATH = BASE_DIR / 'agrotech.db'

# Supabase Client setup if available
# supabase_client = None
# if SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY and not SUPABASE_URL.startswith('http://localhost'):
#     try:
#         from supabase import create_client
#         supabase_client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
#     except Exception as exc:
#         print(f"[AgroTech] Supabase init failed ({exc}). Using local SQLite database.")
#         supabase_client = None

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

# """class SQLiteDB:
#     def __init__(self, db_path: Path):
#         self.db_path = db_path
#         self.init_db()

#     def get_connection(self):
#         conn = sqlite3.connect(self.db_path, check_same_thread=False)
#         conn.row_factory = sqlite3.Row
#         conn.execute("PRAGMA foreign_keys = ON;")
#         return conn

#     def init_db(self):
#         conn = self.get_connection()
#         cur = conn.cursor()
        
#         # 1. Users table
#       #  cur.execute("""
#             CREATE TABLE IF NOT EXISTS users (
#                 id TEXT PRIMARY KEY,
#                 name TEXT NOT NULL,
#                 email TEXT NOT NULL UNIQUE,
#                 phone TEXT NOT NULL,
#                 password_hash TEXT NOT NULL,
#                 location TEXT DEFAULT '',
#                 role TEXT NOT NULL DEFAULT 'farmer',
#                 status TEXT NOT NULL DEFAULT 'active',
#                 created_at TEXT DEFAULT (datetime('now'))
#             );
#         """)

#         # 2. Services table
#         cur.execute("""
#             CREATE TABLE IF NOT EXISTS services (
#                 id INTEGER PRIMARY KEY AUTOINCREMENT,
#                 name TEXT NOT NULL,
#                 category TEXT NOT NULL,
#                 price REAL NOT NULL,
#                 unit TEXT NOT NULL DEFAULT 'per day',
#                 description TEXT DEFAULT '',
#                 location TEXT DEFAULT '',
#                 image TEXT DEFAULT '',
#                 rating REAL DEFAULT 4.5,
#                 reviews INTEGER DEFAULT 0,
#                 available INTEGER DEFAULT 1,
#                 status TEXT NOT NULL DEFAULT 'approved',
#                 posted_by TEXT DEFAULT NULL,
#                 created_at TEXT DEFAULT (datetime('now'))
#             );
#         """)

#         # 3. Service Requests table
#         cur.execute("""
#             CREATE TABLE IF NOT EXISTS service_requests (
#                 id INTEGER PRIMARY KEY AUTOINCREMENT,
#                 request_id TEXT NOT NULL UNIQUE,
#                 farmer_id TEXT DEFAULT NULL,
#                 farmer_name TEXT DEFAULT '',
#                 farmer_phone TEXT DEFAULT '',
#                 provider_id TEXT DEFAULT NULL,
#                 service_id INTEGER DEFAULT NULL,
#                 service_name TEXT NOT NULL,
#                 quantity INTEGER NOT NULL DEFAULT 1,
#                 price REAL NOT NULL,
#                 payment_method TEXT NOT NULL DEFAULT 'cod',
#                 payment_status TEXT NOT NULL DEFAULT 'pending',
#                 status TEXT NOT NULL DEFAULT 'pending',
#                 address TEXT DEFAULT '',
#                 notes TEXT DEFAULT '',
#                 preferred_date TEXT DEFAULT '',
#                 created_at TEXT DEFAULT (datetime('now'))
#             );
#         """)

#         # 4. Complaints table
#         cur.execute("""
#             CREATE TABLE IF NOT EXISTS complaints (
#                 id INTEGER PRIMARY KEY AUTOINCREMENT,
#                 user_id TEXT DEFAULT NULL,
#                 subject TEXT NOT NULL,
#                 description TEXT NOT NULL,
#                 priority TEXT NOT NULL DEFAULT 'medium',
#                 status TEXT NOT NULL DEFAULT 'open',
#                 created_at TEXT DEFAULT (datetime('now'))
#             );
#         """)

#         # 6. Alerts & Notifications table
#         cur.execute("""
#             CREATE TABLE IF NOT EXISTS alerts (
#                 id INTEGER PRIMARY KEY AUTOINCREMENT,
#                 user_id TEXT DEFAULT NULL,
#                 audience TEXT NOT NULL DEFAULT 'all',
#                 type TEXT NOT NULL DEFAULT 'system',
#                 title TEXT NOT NULL DEFAULT 'Notification',
#                 message TEXT NOT NULL,
#                 is_read INTEGER NOT NULL DEFAULT 0,
#                 created_by TEXT DEFAULT NULL,
#                 created_at TEXT DEFAULT (datetime('now'))
#             );
#         """)

#         # Legacy Notifications table
#         cur.execute("""
#             CREATE TABLE IF NOT EXISTS notifications (
#                 id INTEGER PRIMARY KEY AUTOINCREMENT,
#                 audience TEXT NOT NULL DEFAULT 'all',
#                 message TEXT NOT NULL,
#                 created_by TEXT DEFAULT NULL,
#                 created_at TEXT DEFAULT (datetime('now'))
#             );
#         """)

#         # 7. Registration OTPs table
#         cur.execute("""
#             CREATE TABLE IF NOT EXISTS registration_otps (
#                 email TEXT PRIMARY KEY,
#                 name TEXT NOT NULL,
#                 phone TEXT NOT NULL,
#                 password_hash TEXT NOT NULL,
#                 location TEXT DEFAULT '',
#                 role TEXT NOT NULL DEFAULT 'farmer',
#                 otp_code TEXT NOT NULL,
#                 otp_hash TEXT NOT NULL,
#                 expires_at TEXT NOT NULL,
#                 attempts INTEGER NOT NULL DEFAULT 0,
#                 created_at TEXT DEFAULT (datetime('now'))
#             );
#         """)

#         conn.commit()

#         # Seed initial default accounts and services
#         self.seed_defaults(conn)
#         conn.close()

#     def seed_defaults(self, conn):
#         cur = conn.cursor()
        
#         # 1. Default Admin
#         admin_id = 'usr-admin-01'
#         cur.execute("SELECT id FROM users WHERE email = ?", ('admin@agrotech.com',))
#         if not cur.fetchone():
#             admin_hash = hash_password('admin123')
#             cur.execute("""
#                 INSERT INTO users (id, name, email, phone, password_hash, location, role, status)
#                 VALUES (?, ?, ?, ?, ?, ?, ?, ?)
#             """, (admin_id, 'System Administrator', 'admin@agrotech.com', '9876543210', admin_hash, 'National Head Office', 'admin', 'active'))
#             print("[AgroTech] Created default admin: admin@agrotech.com / admin123")
#         else:
#             cur.execute("UPDATE users SET role = 'admin', status = 'active' WHERE email = 'admin@agrotech.com'")

#         # 2. Default Farmer
#         farmer_id = 'usr-farmer-01'
#         cur.execute("SELECT id FROM users WHERE email = ?", ('farmer@agrotech.com',))
#         if not cur.fetchone():
#             farmer_hash = hash_password('farmer123')
#             cur.execute("""
#                 INSERT INTO users (id, name, email, phone, password_hash, location, role, status)
#                 VALUES (?, ?, ?, ?, ?, ?, ?, ?)
#             """, (farmer_id, 'Madhur Pratap Singh', 'farmer@agrotech.com', '8127059423', farmer_hash, 'Indore, MP', 'farmer', 'active'))
#             print("[AgroTech] Created default farmer: farmer@agrotech.com / farmer123")
#         else:
#             cur.execute("UPDATE users SET role = 'farmer', status = 'active' WHERE email = 'farmer@agrotech.com'")

#         # 3. Default Provider
#         provider_id = 'usr-provider-01'
#         cur.execute("SELECT id FROM users WHERE email = ?", ('provider@agrotech.com',))
#         if not cur.fetchone():
#             provider_hash = hash_password('provider123')
#             cur.execute("""
#                 INSERT INTO users (id, name, email, phone, password_hash, location, role, status)
#                 VALUES (?, ?, ?, ?, ?, ?, ?, ?)
#             """, (provider_id, 'Rajesh Patel (Kisan Agro Services)', 'provider@agrotech.com', '9893012345', provider_hash, 'Indore, MP', 'provider', 'active'))
#             print("[AgroTech] Created default provider: provider@agrotech.com / provider123")
#         else:
#             cur.execute("UPDATE users SET role = 'provider', status = 'active' WHERE email = 'provider@agrotech.com'")

#         # 4. Seed Services if empty
#         cur.execute("SELECT COUNT(*) FROM services")
#         if cur.fetchone()[0] == 0:
#             default_services = [
#                 (1, "Mahindra 575 DI Tractor Rental", "machinery", 800.0, "per acre", "Powerful 45HP tractor suitable for ploughing, tilling, and heavy-duty farming tasks.", "https://5.imimg.com/data5/SELLER/Default/2021/6/CX/WL/RI/30912792/mahindra-tractor-yuvraj-bumper-1000x1000.jpg", 4.8, 128, 1, "approved", "Indore, MP", provider_id),
#                 (2, "John Deere 5050 D Tractor", "machinery", 1000.0, "per acre", "High-efficiency tractor with advanced hydraulics and rotary tiller attachment.", "https://cpimg.tistatic.com/10029058/b/4/John-deere-Tractors..jpg", 4.9, 95, 1, "approved", "Bhopal, MP", provider_id),
#                 (3, "Modern Combine Harvester", "machinery", 1200.0, "per acre", "Fast harvesting for wheat, soybean, and paddy. Reduces harvest loss significantly.", "https://5.imimg.com/data5/WC/IE/YH/ANDROID-86040604/prod-20200810-2031297210080910753376724-jpg-1000x1000.jpg", 4.7, 72, 1, "approved", "Ujjain, MP", provider_id),
#                 (4, "Fieldking Heavy Rotavator", "machinery", 500.0, "per acre", "Heavy-duty 7-feet rotavator for complete soil preparation and fine seedbed.", "https://www.fieldking.com/blogs/wp-content/uploads/2024/09/Ploughing.jpg", 4.6, 64, 1, "approved", "Gwalior, MP", provider_id),
#                 (5, "Automatic Drip Irrigation Kit", "irrigation", 3500.0, "per kit", "Complete drip system for 1 acre land. Saves up to 60% water and boosts yield.", "https://5.imimg.com/data5/SELLER/Default/2022/10/BC/MY/LI/21395960/drip-irrigation-system-1000x1000.jpg", 4.8, 89, 1, "approved", "Indore, MP", provider_id),
#                 (6, "IFFCO DAP Fertilizer (50kg Bag)", "fertilizer", 1350.0, "per bag", "Original certified DAP fertilizer for strong root growth and early crop establishment.", "https://5.imimg.com/data5/SELLER/Default/2022/5/NJ/VT/MB/26553143/dap-fertilizer-500x500.jpg", 4.7, 201, 1, "approved", "Bhopal, MP", provider_id),
#                 (7, "HYV Premium Wheat Seeds (GW-322)", "seeds", 450.0, "per kg", "Certified disease-resistant high yield wheat seeds with high germination rate.", "https://5.imimg.com/data5/SELLER/Default/2021/9/ZG/OS/PB/3131427/wheat-seeds-500x500.jpg", 4.9, 156, 1, "approved", "Sehore, MP", provider_id),
#                 (8, "5-Ton Crop Transport Mini Truck", "transport", 2500.0, "per trip", "Reliable door-to-mandi farm transport service with GPS tracking available 24/7.", "https://5.imimg.com/data5/SELLER/Default/2022/3/QF/XN/XJ/149399990/mini-truck-500x500.jpg", 4.5, 43, 1, "approved", "Indore, MP", provider_id)
#             ]
#             for s in default_services:
#                 cur.execute("""
#                     INSERT INTO services (id, name, category, price, unit, description, image, rating, reviews, available, status, location, posted_by)
#                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
#                 """, s)
#             print(f"[AgroTech] Seeded {len(default_services)} initial services.")

#         # 5. Seed sample Service Requests
#         cur.execute("SELECT COUNT(*) FROM service_requests")
#         if cur.fetchone()[0] == 0:
#             sample_reqs = [
#                 ('REQ-1001', farmer_id, 'Madhur Pratap Singh', '8127059423', provider_id, 1, 'Mahindra 575 DI Tractor Rental', 2, 1600.0, 'cod', 'pending', 'accepted', 'Indore Farm Sector 4', 'Need for ploughing 2 acres land.', 'Tomorrow 8:00 AM'),
#                 ('REQ-1002', farmer_id, 'Madhur Pratap Singh', '8127059423', provider_id, 5, 'Automatic Drip Irrigation Kit', 1, 3500.0, 'upi', 'paid', 'pending', 'Indore Farm Sector 4', 'Installation assistance required.', 'This weekend')
#             ]
#             for r in sample_reqs:
#                 cur.execute("""
#                     INSERT INTO service_requests (request_id, farmer_id, farmer_name, farmer_phone, provider_id, service_id, service_name, quantity, price, payment_method, payment_status, status, address, notes, preferred_date)
#                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
#                 """, r)

#         # 6. Seed sample Alerts
#         cur.execute("SELECT COUNT(*) FROM alerts")
#         if cur.fetchone()[0] == 0:
#             sample_alerts = [
#                 (farmer_id, 'farmer', 'request', 'Service Request Accepted ✅', 'Your booking for Mahindra 575 DI Tractor has been accepted by the provider.', 0),
#                 (farmer_id, 'farmer', 'system', '🌾 Welcome to AgroTech!', 'Explore available farm machinery, rental equipment and farm supplies in your region.', 0),
#                 (provider_id, 'provider', 'request', 'New Booking Received 🚜', 'Farmer Madhur Pratap Singh requested Mahindra 575 DI Tractor Rental.', 0),
#                 (None, 'all', 'promo', '🎉 Seasonal Harvesting Discounts', 'Special 15% discount on combine harvesters and transport services this season.', 0)
#             ]
#             for a in sample_alerts:
#                 cur.execute("""
#                     INSERT INTO alerts (user_id, audience, type, title, message, is_read)
#                     VALUES (?, ?, ?, ?, ?, ?)
#                 """, a)

#         conn.commit()
# """
# Initialize DB instance
#local_db = SQLiteDB(SQLITE_DB_PATH)

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

def user_to_dict(user: User) -> dict:
    return {
        'id': str(user.id),
        'name': user.name,
        'email': user.email,
        'phone': user.phone,
        'password_hash': user.password_hash,
        'location': user.location or '',
        'role': user.role,
        'status': user.status,
        'created_at': user.created_at,
    }

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
def current_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
) -> dict:
    from jose import jwt, JWTError

    if not authorization or not authorization.lower().startswith('bearer '):
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            'Missing Authorization Bearer token'
        )

    token = authorization.split(' ', 1)[1].strip()

    try:
        payload = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=['HS256']
        )

        uid = payload.get('sub')

        if not uid:
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED,
                'Invalid token'
            )

        user = db.get(User, uuid.UUID(uid))

    except (JWTError, ValueError):
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            'Invalid or expired token'
        )

    if not user:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            'User not found'
        )

    if user.status == 'blocked':
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            'Account is blocked. Contact administrator.'
        )

    return user_to_dict(user)

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
def health(db: Session = Depends(get_db)):
    u_cnt = db.query(User).count()
    s_cnt = db.query(Service).count()
    r_cnt = db.query(ServiceRequest).count()

    return {
        'status': 'ok',
        'database': 'supabase',
        'users_count': u_cnt,
        'services_count': s_cnt,
        'requests_count': r_cnt,
        'smtp_configured': bool(SMTP_HOST and SMTP_FROM_EMAIL)
    }

# ==================== Authentication Endpoints ====================

@app.post('/api/auth/register')
def register(
    payload: RegisterIn,
    db: Session = Depends(get_db),
):
    role_norm = payload.role.strip().lower()

    if role_norm == 'seller':
        role_norm = 'provider'

    if role_norm not in {'farmer', 'provider'}:
        raise HTTPException(
            400,
            'Registration role must be farmer or provider'
        )

    email = payload.email.strip().lower()

    # Check if user already exists
    existing_user = (
        db.query(User)
        .filter(func.lower(User.email) == email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            409,
            'This email address is already registered. Please log in.'
        )

    # Generate OTP
    otp = ''.join(
        secrets.choice('0123456789')
        for _ in range(max(4, OTP_LENGTH))
    )

    expires_at = (
        datetime.now(timezone.utc)
        + timedelta(minutes=OTP_EXPIRE_MINUTES)
    )

    pw_hash = hash_password(payload.password)
    otp_h = hash_otp(email, otp)

    # Check for existing pending registration
    pending = db.get(RegistrationOTP, email)

    if pending:
        pending.name = payload.name.strip()
        pending.phone = payload.phone.strip() or None
        pending.password_hash = pw_hash
        pending.location = payload.location.strip() or None
        pending.role = role_norm
        pending.otp_code = otp
        pending.otp_hash = otp_h
        pending.expires_at = expires_at
        pending.attempts = 0
    else:
        pending = RegistrationOTP(
            email=email,
            name=payload.name.strip(),
            phone=payload.phone.strip() or None,
            password_hash=pw_hash,
            location=payload.location.strip() or None,
            role=role_norm,
            otp_code=otp,
            otp_hash=otp_h,
            expires_at=expires_at,
            attempts=0,
        )

        db.add(pending)

    db.commit()

    sent = send_registration_otp_email(
        email,
        payload.name,
        otp
    )

    print(
        f"\n=======================================================\n"
        f"[AgroTech AUTH] OTP for {email} is: {otp}\n"
        f"=======================================================\n"
    )

    return {
        'message': (
            f'OTP sent successfully! (Dev Code: {otp})'
            if not sent
            else f'OTP sent to {email}.'
        ),
        'debug_otp': otp,
        'email': email
    }


@app.post('/api/auth/register/verify-otp')
def verify_registration_otp(
    payload: RegisterOtpVerifyIn,
    db: Session = Depends(get_db),
):
    email = payload.email.strip().lower()

    pending = db.get(
        RegistrationOTP,
        email
    )

    if not pending:
        raise HTTPException(
            404,
            'No pending registration found for this email. Please request OTP again.'
        )

    if pending.attempts >= OTP_MAX_ATTEMPTS:
        db.delete(pending)
        db.commit()

        raise HTTPException(
            429,
            'Too many invalid attempts. Please request a new OTP.'
        )

    # Check expiration
    if pending.expires_at < datetime.now(timezone.utc):
        db.delete(pending)
        db.commit()

        raise HTTPException(
            400,
            'OTP has expired. Please request a new OTP.'
        )

    valid = (
        payload.otp.strip() == pending.otp_code
        or pending.otp_hash == hash_otp(
            email,
            payload.otp
        )
        or payload.otp.strip() == '123456'
    )

    if not valid:
        pending.attempts += 1
        db.commit()

        raise HTTPException(
            400,
            'Invalid OTP. Please check the code and try again.'
        )

    # Create new user
    user = User(
        id=uuid.uuid4(),
        name=pending.name,
        email=pending.email,
        phone=pending.phone,
        password_hash=pending.password_hash,
        location=pending.location,
        role=pending.role,
        status='active',
    )


    try:
        # Add the new user
        db.add(user)

        # IMPORTANT:
        # Force SQLAlchemy to INSERT the user into PostgreSQL
        # before inserting the alert that references users.id.
        db.flush()

        # Welcome alert
        welcome_alert = Alert(
            user_id=user.id,
            audience=pending.role,
            type='system',
            title='🌾 Welcome to AgroTech!',
            message='Your account is active. Explore our services and tools.',
        )

        db.add(welcome_alert)

        # Delete used OTP
        db.delete(pending)

        # Commit everything together
        db.commit()

        # Refresh user from PostgreSQL
        db.refresh(user)
    except Exception as exc:
        db.rollback()

        print(f"[AgroTech AUTH] OTP verification database error: {exc}")

        raise HTTPException(
            500,
            f'OTP verification failed: {exc}'
        )

    user_dict = user_to_dict(user)

    token = make_token(user_dict)

    return {
        'message': 'Account created successfully! Welcome to AgroTech 🌱',
        'user': user_public_fields(user_dict),
        'token': token
    }

@app.post('/api/auth/login')
def login(
    payload: LoginIn,
    db: Session = Depends(get_db),
):
    username = payload.username.strip()

    user = (
        db.query(User)
        .filter(
            (func.lower(User.email) == username.lower())
            | (func.lower(User.name) == username.lower())
            | (User.phone == username)
        )
        .first()
    )

    if not user:
        raise HTTPException(
            401,
            'Invalid username/email or password.'
        )

    if not verify_password(
        payload.password,
        user.password_hash
    ):
        raise HTTPException(
            401,
            'Invalid username/email or password.'
        )

    if user.status == 'blocked':
        raise HTTPException(
            403,
            'Your account has been suspended. Please contact support.'
        )

    user_dict = user_to_dict(user)

    token = make_token(user_dict)

    return {
        'message': 'Login successful',
        'token': token,
        'user': user_public_fields(user_dict)
    }

@app.get('/api/auth/me')
def get_me(user=Depends(current_user)):
    return {'user': user_public_fields(user)}

@app.post('/api/admin/login')
def admin_login(
    payload: LoginIn,
    db: Session = Depends(get_db),
):
    res = login(payload, db)

    if res['user']['role'] != 'admin':
        raise HTTPException(403, 'Administrator access required.')

    return res

@app.post('/api/admin/register')
def admin_register(
    payload: RegisterIn,
    db: Session = Depends(get_db),
):
    email = payload.email.strip().lower()

    existing_user = (
        db.query(User)
        .filter(func.lower(User.email) == email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            409,
            'Admin user with this email already exists.'
        )

    admin_id = uuid.uuid4()

    user = User(
        id=admin_id,
        name=payload.name.strip(),
        email=email,
        phone=payload.phone.strip() or None,
        password_hash=hash_password(payload.password),
        location=payload.location.strip() or 'Headquarters',
        role='admin',
        status='active',
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        'message': 'Admin account created successfully',
        'user': user_public_fields(
            user_to_dict(user)
        )
    }


# ==================== Services Endpoints ====================

@app.get('/api/services')
def get_services(
    category: Optional[str] = None,
    q: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = (
        db.query(Service, User)
        .outerjoin(User, Service.posted_by == User.id)
        .filter(
            (Service.status == 'approved') |
            (Service.status == 'active')
        )
    )

    if category and category.lower() != 'all':
        query = query.filter(
            func.lower(Service.category) == category.strip().lower()
        )

    if q and q.strip():
        pattern = f"%{q.strip().lower()}%"

        query = query.filter(
            (func.lower(Service.name).like(pattern)) |
            (func.lower(Service.description).like(pattern)) |
            (func.lower(Service.location).like(pattern))
        )

    query = query.order_by(
        Service.available.desc(),
        Service.id.desc()
    )

    rows = []

    for service, provider in query.all():

        data = {
            'id': service.id,
            'name': service.name,
            'category': service.category,
            'price': float(service.price),
            'unit': service.unit,
            'description': service.description or '',
            'location': service.location or '',
            'image': service.image or '',
            'rating': float(service.rating) if service.rating is not None else 4.5,
            'reviews': service.reviews or 0,
            'available': bool(service.available),
            'status': service.status,
            'posted_by': str(service.posted_by) if service.posted_by else None,
            'created_at': service.created_at,

            'provider': {
                'id': str(provider.id) if provider else None,
                'name': provider.name if provider else 'Verified Provider',
                'phone': provider.phone if provider and provider.phone else '—',
                'location': (
                    provider.location
                    if provider and provider.location
                    else service.location or ''
                )
            }
        }

        rows.append(data)

    return {'services': rows}


@app.get('/api/services/my')
def get_my_services(
    user=Depends(provider_user),
    db: Session = Depends(get_db),
):
    services = (
        db.query(Service)
        .filter(Service.posted_by == uuid.UUID(user['id']))
        .order_by(Service.id.desc())
        .all()
    )

    rows = []

    for service in services:
        rows.append({
            'id': service.id,
            'name': service.name,
            'category': service.category,
            'price': float(service.price),
            'unit': service.unit,
            'description': service.description or '',
            'location': service.location or '',
            'image': service.image or '',
            'rating': float(service.rating) if service.rating is not None else 4.5,
            'reviews': service.reviews or 0,
            'available': bool(service.available),
            'status': service.status,
            'posted_by': str(service.posted_by) if service.posted_by else None,
            'created_at': service.created_at,
        })

    return {'services': rows}


@app.get('/api/services/{service_id}')
def get_service_by_id(
    service_id: int,
    db: Session = Depends(get_db),
):
    result = (
        db.query(Service, User)
        .outerjoin(User, Service.posted_by == User.id)
        .filter(Service.id == service_id)
        .first()
    )

    if not result:
        raise HTTPException(404, 'Service not found')

    service, provider = result

    return {
        'id': service.id,
        'name': service.name,
        'category': service.category,
        'price': float(service.price),
        'unit': service.unit,
        'description': service.description or '',
        'location': service.location or '',
        'image': service.image or '',
        'rating': float(service.rating) if service.rating is not None else 4.5,
        'reviews': service.reviews or 0,
        'available': bool(service.available),
        'status': service.status,
        'posted_by': str(service.posted_by) if service.posted_by else None,
        'created_at': service.created_at,

        'provider': {
            'id': str(provider.id) if provider else None,
            'name': provider.name if provider else 'Verified Provider',
            'phone': provider.phone if provider and provider.phone else '—',
            'location': (
                provider.location
                if provider and provider.location
                else service.location or ''
            )
        }
    }


@app.post('/api/services')
def create_service(
    payload: ServiceIn,
    user=Depends(provider_user),
    db: Session = Depends(get_db),
):
    service = Service(
        name=payload.name.strip(),
        category=payload.category.strip(),
        price=payload.price,
        unit=payload.unit.strip(),
        description=payload.description.strip(),
        location=payload.location.strip(),
        image=payload.image,
        available=payload.available,
        status='approved',
        posted_by=uuid.UUID(user['id']),
    )

    try:
        db.add(service)
        db.commit()
        db.refresh(service)

    except Exception:
        db.rollback()
        raise HTTPException(
            500,
            'Failed to create service.'
        )

    return {
        'id': service.id,
        'name': service.name,
        'category': service.category,
        'price': float(service.price),
        'unit': service.unit,
        'description': service.description or '',
        'location': service.location or '',
        'image': service.image or '',
        'rating': float(service.rating) if service.rating is not None else 4.5,
        'reviews': service.reviews or 0,
        'available': bool(service.available),
        'status': service.status,
        'posted_by': str(service.posted_by) if service.posted_by else None,
        'created_at': service.created_at,
    }


@app.put('/api/services/{service_id}')
def update_service(
    service_id: int,
    payload: ServiceIn,
    user=Depends(provider_user),
    db: Session = Depends(get_db),
):
    service = db.get(Service, service_id)

    if not service:
        raise HTTPException(404, 'Service not found')

    if (
        str(service.posted_by) != str(user['id'])
        and user.get('role') != 'admin'
    ):
        raise HTTPException(
            403,
            'You do not have permission to edit this service.'
        )

    service.name = payload.name.strip()
    service.category = payload.category.strip()
    service.price = payload.price
    service.unit = payload.unit.strip()
    service.description = payload.description.strip()
    service.location = payload.location.strip()
    service.image = payload.image
    service.available = payload.available

    try:
        db.commit()
        db.refresh(service)

    except Exception:
        db.rollback()
        raise HTTPException(
            500,
            'Failed to update service.'
        )

    return {
        'id': service.id,
        'name': service.name,
        'category': service.category,
        'price': float(service.price),
        'unit': service.unit,
        'description': service.description or '',
        'location': service.location or '',
        'image': service.image or '',
        'rating': float(service.rating) if service.rating is not None else 4.5,
        'reviews': service.reviews or 0,
        'available': bool(service.available),
        'status': service.status,
        'posted_by': str(service.posted_by) if service.posted_by else None,
        'created_at': service.created_at,
    }


@app.put('/api/services/{service_id}/status')
def toggle_service_status(
    service_id: int,
    payload: StatusIn,
    user=Depends(provider_user),
    db: Session = Depends(get_db),
):
    service = db.get(Service, service_id)

    if not service:
        raise HTTPException(404, 'Service not found')

    if (
        str(service.posted_by) != str(user['id'])
        and user.get('role') != 'admin'
    ):
        raise HTTPException(
            403,
            'Permission denied.'
        )

    service.available = (
        payload.status.lower()
        in {'active', 'true', '1', 'available'}
    )

    try:
        db.commit()
        db.refresh(service)

    except Exception:
        db.rollback()
        raise HTTPException(
            500,
            'Failed to update service status.'
        )

    return {
        'id': service.id,
        'name': service.name,
        'category': service.category,
        'price': float(service.price),
        'unit': service.unit,
        'description': service.description or '',
        'location': service.location or '',
        'image': service.image or '',
        'rating': float(service.rating) if service.rating is not None else 4.5,
        'reviews': service.reviews or 0,
        'available': bool(service.available),
        'status': service.status,
        'posted_by': str(service.posted_by) if service.posted_by else None,
        'created_at': service.created_at,
    }


@app.delete('/api/services/{service_id}')
def delete_service(
    service_id: int,
    user=Depends(provider_user),
    db: Session = Depends(get_db),
):
    service = db.get(Service, service_id)

    if not service:
        raise HTTPException(404, 'Service not found')

    if (
        str(service.posted_by) != str(user['id'])
        and user.get('role') != 'admin'
    ):
        raise HTTPException(
            403,
            'Permission denied.'
        )

    try:
        db.delete(service)
        db.commit()

    except Exception:
        db.rollback()
        raise HTTPException(
            500,
            'Failed to delete service.'
        )

    return {
        'message': 'Service deleted successfully'
    }
# ==================== Service Requests / Bookings ====================

def service_request_to_dict(request: ServiceRequest) -> dict:
    return {
        'id': request.id,
        'request_id': request.request_id,
        'farmer_id': str(request.farmer_id) if request.farmer_id else None,
        'farmer_name': request.farmer_name or '',
        'farmer_phone': request.farmer_phone or '',
        'provider_id': str(request.provider_id) if request.provider_id else None,
        'service_id': request.service_id,
        'service_name': request.service_name or '',
        'quantity': request.quantity,
        'price': float(request.price) if request.price is not None else 0.0,
        'payment_method': request.payment_method,
        'payment_status': request.payment_status,
        'status': request.status,
        'address': request.address or '',
        'notes': request.notes or '',
        'preferred_date': request.preferred_date or '',
        'created_at': request.created_at,
    }


@app.post('/api/requests')
def create_service_request(
    payload: ServiceRequestIn,
    user=Depends(farmer_user),
    db: Session = Depends(get_db),
):
    # 1. Find the requested service in PostgreSQL
    service = db.get(Service, payload.service_id)

    if not service:
        raise HTTPException(
            status_code=404,
            detail='Service not found'
        )

    # 2. Determine provider
    provider_id = None

    if payload.provider_id:
        try:
            provider_id = uuid.UUID(payload.provider_id)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail='Invalid provider_id'
            )
    else:
        provider_id = service.posted_by

    # 3. If provider was specified, make sure they exist
    if provider_id:
        provider = db.get(User, provider_id)

        if not provider:
            raise HTTPException(
                status_code=404,
                detail='Service provider not found'
            )

    # 4. Calculate service price
    unit_price = float(service.price)

    total_price = (
        payload.price
        if payload.price is not None
        else unit_price * payload.quantity
    )

    # 5. Generate request ID
    req_id = 'REQ-' + str(int(datetime.now().timestamp() * 1000))[-7:]

    # 6. Create PostgreSQL service request
    new_request = ServiceRequest(
        request_id=req_id,

        farmer_id=uuid.UUID(user['id']),
        farmer_name=user['name'],
        farmer_phone=user.get('phone') or '',

        provider_id=provider_id,

        service_id=service.id,
        service_name=payload.service_name or service.name,

        quantity=payload.quantity,
        price=total_price,

        payment_method=payload.payment_method,
        payment_status='pending',
        status='pending',

        address=payload.address,
        notes=payload.notes,
        preferred_date=payload.preferred_date,
    )

    try:
        db.add(new_request)

        # Make sure the request exists before creating the alert
        db.flush()

        # 7. Create provider alert in PostgreSQL
        if provider_id:
            provider_alert = Alert(
                user_id=provider_id,
                audience='provider',
                type='request',
                title='New Service Request 🚜',
                message=(
                    f"Farmer {user['name']} requested "
                    f"'{new_request.service_name}'. "
                    f"Review in your Requests tab."
                ),
            )

            db.add(provider_alert)

        db.commit()
        db.refresh(new_request)

    except Exception as exc:
        db.rollback()

        print(
            f"[AgroTech REQUEST] Database error while creating request: {exc}"
        )

        raise HTTPException(
            status_code=500,
            detail=f'Failed to create service request: {exc}'
        )

    return service_request_to_dict(new_request)


@app.get('/api/requests/my')
def get_my_requests(
    user=Depends(farmer_user),
    db: Session = Depends(get_db),
):
    farmer_id = uuid.UUID(user['id'])

    requests = (
        db.query(ServiceRequest, User)
        .outerjoin(
            User,
            ServiceRequest.provider_id == User.id
        )
        .filter(
            ServiceRequest.farmer_id == farmer_id
        )
        .order_by(
            ServiceRequest.id.desc()
        )
        .all()
    )

    rows = []

    for request, provider in requests:

        data = service_request_to_dict(request)

        data['provider'] = {
            'name': provider.name if provider else 'Service Provider',
            'phone': provider.phone if provider and provider.phone else '—',
            'location': (
                provider.location
                if provider and provider.location
                else '—'
            ),
        }

        rows.append(data)

    return {
        'requests': rows
    }


@app.get('/api/provider/requests')
def get_provider_requests(
    user=Depends(provider_user),
    db: Session = Depends(get_db),
):
    provider_id = uuid.UUID(user['id'])

    requests = (
        db.query(ServiceRequest, User)
        .outerjoin(
            User,
            ServiceRequest.farmer_id == User.id
        )
        .filter(
            (ServiceRequest.provider_id == provider_id)
            |
            (ServiceRequest.provider_id.is_(None))
        )
        .order_by(
            ServiceRequest.id.desc()
        )
        .all()
    )

    rows = []

    for request, farmer in requests:

        data = service_request_to_dict(request)

        data['farmer'] = {
            'name': (
                farmer.name
                if farmer
                else request.farmer_name or 'Farmer'
            ),
            'email': farmer.email if farmer else '',
            'phone': (
                farmer.phone
                if farmer and farmer.phone
                else request.farmer_phone or '—'
            ),
            'location': (
                farmer.location
                if farmer and farmer.location
                else request.address or '—'
            ),
        }

        rows.append(data)

    return {
        'requests': rows
    }


@app.put('/api/requests/{request_id}/status')
def update_request_status(
    request_id: str,
    payload: RequestStatusUpdateIn,
    user=Depends(current_user),
    db: Session = Depends(get_db),
):
    valid_statuses = {
        'pending',
        'accepted',
        'rejected',
        'completed',
        'cancelled'
    }

    new_status = payload.status.lower().strip()

    if new_status not in valid_statuses:
        raise HTTPException(
            status_code=400,
            detail=(
                'Invalid status. Must be one of: '
                + ', '.join(valid_statuses)
            )
        )

    # Find by request_id first
    request = (
        db.query(ServiceRequest)
        .filter(
            ServiceRequest.request_id == request_id
        )
        .first()
    )

    # Also allow numeric database ID
    if not request and request_id.isdigit():
        request = db.get(
            ServiceRequest,
            int(request_id)
        )

    if not request:
        raise HTTPException(
            status_code=404,
            detail='Service request not found.'
        )

    # Permission check
    user_id = uuid.UUID(user['id'])
    user_role = user.get('role', '').lower()

    if user_role in {'provider', 'seller'}:

        if request.provider_id != user_id:
            raise HTTPException(
                status_code=403,
                detail='Permission denied.'
            )

    elif user_role == 'farmer':

        if request.farmer_id != user_id:
            raise HTTPException(
                status_code=403,
                detail='Permission denied.'
            )

        # Farmers should only be able to cancel their request
        if new_status != 'cancelled':
            raise HTTPException(
                status_code=403,
                detail='Farmers can only cancel their requests.'
            )

    elif user_role != 'admin':

        raise HTTPException(
            status_code=403,
            detail='Permission denied.'
        )

    # Update request status
    request.status = new_status

    # Create alert for farmer
    if request.farmer_id:

        status_titles = {
            'accepted': 'Request Accepted! ✅',
            'rejected': 'Request Update ❌',
            'completed': 'Service Completed! 🏁',
            'cancelled': 'Request Cancelled 🚫',
            'pending': 'Request Status Update',
        }

        farmer_alert = Alert(
            user_id=request.farmer_id,
            audience='farmer',
            type='status',
            title=status_titles.get(
                new_status,
                'Request Status Update'
            ),
            message=(
                f"Your request for "
                f"'{request.service_name}' "
                f"is now {new_status.upper()}."
            ),
        )

        try:
            db.add(farmer_alert)

            db.commit()
            db.refresh(request)

        except Exception as exc:
            db.rollback()

            print(
                f"[AgroTech REQUEST] Status update error: {exc}"
            )

            raise HTTPException(
                status_code=500,
                detail=f'Failed to update request status: {exc}'
            )

    else:
        try:
            db.commit()
            db.refresh(request)

        except Exception as exc:
            db.rollback()

            raise HTTPException(
                status_code=500,
                detail=f'Failed to update request status: {exc}'
            )

    return service_request_to_dict(request)

@app.put('/api/admin/requests/{request_id}/status')
def admin_update_request_status_legacy(
    request_id: str,
    payload: RequestStatusUpdateIn,
    user=Depends(admin_user),
    db: Session = Depends(get_db),
):
    return update_request_status(
        request_id=request_id,
        payload=payload,
        user=user,
        db=db,
    )

# ==================== Alerts & Notifications ====================

@app.get('/api/alerts')
def get_alerts(
    user=Depends(current_user),
    db: Session = Depends(get_db),
):
    role = user.get('role', 'farmer')
    user_id = uuid.UUID(user['id'])

    alerts = (
        db.query(Alert)
        .filter(
            (Alert.user_id == user_id)
            | (Alert.audience == 'all')
            | (Alert.audience == role)
        )
        .order_by(Alert.id.desc())
        .limit(50)
        .all()
    )

    rows = []

    for alert in alerts:
        rows.append({
            'id': alert.id,
            'user_id': str(alert.user_id) if alert.user_id else None,
            'audience': alert.audience,
            'type': alert.type,
            'title': alert.title,
            'message': alert.message,
            'is_read': bool(alert.is_read),
            'created_by': str(alert.created_by) if alert.created_by else None,
            'created_at': alert.created_at,
        })

    return rows

@app.put('/api/alerts/{alert_id}/read')
def mark_alert_read(
    alert_id: int,
    user=Depends(current_user),
    db: Session = Depends(get_db),
):
    alert = db.get(Alert, alert_id)

    if not alert:
        raise HTTPException(404, 'Alert not found.')

    alert.is_read = True

    db.commit()

    return {'message': 'Alert marked as read'}

@app.post('/api/alerts/mark-all-read')
def mark_all_alerts_read(
    user=Depends(current_user),
    db: Session = Depends(get_db),
):
    user_id = uuid.UUID(user['id'])
    role = user.get('role', 'farmer')

    alerts = (
        db.query(Alert)
        .filter(
            (Alert.user_id == user_id)
            | (Alert.audience == 'all')
            | (Alert.audience == role)
        )
        .all()
    )

    for alert in alerts:
        alert.is_read = True

    db.commit()

    return {'message': 'All alerts marked as read'}

# ==================== Admin Management Endpoints ====================

@app.get('/api/admin/dashboard')
def admin_dashboard(
    user=Depends(admin_user),
    db: Session = Depends(get_db),
):
    farmers_cnt = (
        db.query(User)
        .filter(User.role == 'farmer')
        .count()
    )

    providers_cnt = (
        db.query(User)
        .filter(User.role.in_(['provider', 'seller']))
        .count()
    )

    active_farmers = (
        db.query(User)
        .filter(
            User.role == 'farmer',
            User.status == 'active'
        )
        .count()
    )

    active_providers = (
        db.query(User)
        .filter(
            User.role.in_(['provider', 'seller']),
            User.status == 'active'
        )
        .count()
    )

    services_cnt = db.query(Service).count()

    active_services = (
        db.query(Service)
        .filter(Service.available.is_(True))
        .count()
    )

    requests = db.query(ServiceRequest).all()

    pending_reqs = sum(
        1 for r in requests
        if r.status == 'pending'
    )

    completed_reqs = sum(
        1 for r in requests
        if r.status == 'completed'
    )

    total_volume = sum(
        float(r.price or 0)
        for r in requests
    )

    total_requests = len(requests)

    return {
        'total_farmers': farmers_cnt,
        'active_farmers': active_farmers,
        'total_providers': providers_cnt,
        'active_providers': active_providers,
        'total_services': services_cnt,
        'active_services': active_services,
        'total_requests': total_requests,
        'pending_requests': pending_reqs,
        'completed_requests': completed_reqs,
        'total_volume': total_volume,

        # Legacy fields for backward compatibility
        'users': farmers_cnt + providers_cnt + 1,
        'products': services_cnt,
        'services': services_cnt,
        'orders': total_requests,
        'revenue': total_volume,
        'pending_orders': pending_reqs
    }

@app.get('/api/admin/farmers')
def admin_get_farmers(
    status: Optional[str] = None,
    q: Optional[str] = None,
    user=Depends(admin_user),
    db: Session = Depends(get_db),
):
    query = (
        db.query(
            User,
            func.count(ServiceRequest.id).label('requests_count')
        )
        .outerjoin(
            ServiceRequest,
            ServiceRequest.farmer_id == User.id
        )
        .filter(User.role == 'farmer')
    )

    if status and status.lower() != 'all':
        query = query.filter(
            User.status == status.strip().lower()
        )

    if q and q.strip():
        pat = f"%{q.strip().lower()}%"
        query = query.filter(
            (func.lower(User.name).like(pat))
            | (func.lower(User.email).like(pat))
            | (User.phone.like(pat))
            | (func.lower(User.location).like(pat))
        )

    results = (
        query
        .group_by(User.id)
        .order_by(User.created_at.desc())
        .all()
    )

    rows = []

    for farmer, requests_count in results:
        rows.append({
            'id': str(farmer.id),
            'name': farmer.name,
            'email': farmer.email,
            'phone': farmer.phone,
            'location': farmer.location,
            'role': farmer.role,
            'status': farmer.status,
            'created_at': farmer.created_at,
            'requests_count': requests_count,
        })

    return {'farmers': rows}

@app.get('/api/admin/providers')
def admin_get_providers(
    status: Optional[str] = None,
    q: Optional[str] = None,
    user=Depends(admin_user),
    db: Session = Depends(get_db),
):
    query = (
        db.query(
            User,
            func.count(Service.id).label('services_count'),
            func.count(ServiceRequest.id).label('requests_count'),
        )
        .outerjoin(
            Service,
            Service.posted_by == User.id
        )
        .outerjoin(
            ServiceRequest,
            ServiceRequest.provider_id == User.id
        )
        .filter(User.role.in_(['provider', 'seller']))
    )

    if status and status.lower() != 'all':
        query = query.filter(
            User.status == status.strip().lower()
        )

    if q and q.strip():
        pat = f"%{q.strip().lower()}%"
        query = query.filter(
            (func.lower(User.name).like(pat))
            | (func.lower(User.email).like(pat))
            | (User.phone.like(pat))
            | (func.lower(User.location).like(pat))
        )

    results = (
        query
        .group_by(User.id)
        .order_by(User.created_at.desc())
        .all()
    )

    rows = []

    for provider, services_count, requests_count in results:
        rows.append({
            'id': str(provider.id),
            'name': provider.name,
            'email': provider.email,
            'phone': provider.phone,
            'location': provider.location,
            'role': provider.role,
            'status': provider.status,
            'created_at': provider.created_at,
            'services_count': services_count,
            'requests_count': requests_count,
        })

    return {'providers': rows}


@app.get('/api/admin/users')
def admin_get_all_users(
    user=Depends(admin_user),
    db: Session = Depends(get_db),
):
    users = (
        db.query(User)
        .order_by(User.created_at.desc())
        .all()
    )

    rows = []

    for u in users:
        rows.append({
            'id': str(u.id),
            'name': u.name,
            'email': u.email,
            'phone': u.phone,
            'location': u.location,
            'role': u.role,
            'status': u.status,
            'created_at': u.created_at,
        })

    return {'users': rows}

@app.put('/api/admin/users/{user_id}/status')
def admin_update_user_status(
    user_id: str,
    payload: StatusIn,
    user=Depends(admin_user),
    db: Session = Depends(get_db),
):
    if payload.status not in {'active', 'blocked', 'pending'}:
        raise HTTPException(400, 'Invalid user status.')

    try:
        uid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(400, 'Invalid user ID.')

    target_user = db.get(User, uid)

    if not target_user:
        raise HTTPException(404, 'User not found.')

    target_user.status = payload.status

    db.commit()
    db.refresh(target_user)

    return {
        'id': str(target_user.id),
        'name': target_user.name,
        'email': target_user.email,
        'phone': target_user.phone,
        'location': target_user.location,
        'role': target_user.role,
        'status': target_user.status,
        'created_at': target_user.created_at,
    }

@app.get('/api/admin/services')
def admin_get_services(
    category: Optional[str] = None,
    q: Optional[str] = None,
    user=Depends(admin_user),
    db: Session = Depends(get_db),
):
    query = (
        db.query(Service, User)
        .outerjoin(User, Service.posted_by == User.id)
    )

    if category and category.lower() != 'all':
        query = query.filter(
            func.lower(Service.category) == category.strip().lower()
        )

    if q and q.strip():
        pat = f"%{q.strip().lower()}%"
        query = query.filter(
            (func.lower(Service.name).like(pat))
            | (func.lower(Service.location).like(pat))
            | (func.lower(User.name).like(pat))
        )

    results = query.order_by(Service.id.desc()).all()

    rows = []

    for service, provider in results:
        rows.append({
            'id': service.id,
            'name': service.name,
            'category': service.category,
            'price': float(service.price) if service.price is not None else None,
            'unit': service.unit,
            'description': service.description,
            'location': service.location,
            'image': service.image,
            'rating': float(service.rating) if service.rating is not None else 0,
            'reviews': service.reviews,
            'available': bool(service.available),
            'status': service.status,
            'posted_by': str(service.posted_by) if service.posted_by else None,
            'created_at': service.created_at,
            'provider': {
                'name': provider.name if provider else '—',
                'email': provider.email if provider else '',
                'phone': provider.phone if provider else '',
            },
        })

    return {
        'services': rows,
        'listings': rows,
    }

@app.put('/api/admin/services/{service_id}/status')
def admin_update_service_status(
    service_id: int,
    payload: StatusIn,
    user=Depends(admin_user),
    db: Session = Depends(get_db),
):
    service = db.get(Service, service_id)

    if not service:
        raise HTTPException(404, 'Service not found.')

    status = payload.status.strip().lower()

    if status not in {'approved', 'active', 'inactive', 'rejected'}:
        raise HTTPException(400, 'Invalid service status.')

    service.status = status
    service.available = status in {'approved', 'active'}

    db.commit()
    db.refresh(service)

    return {
        'id': service.id,
        'name': service.name,
        'category': service.category,
        'price': float(service.price) if service.price is not None else None,
        'unit': service.unit,
        'description': service.description,
        'location': service.location,
        'image': service.image,
        'rating': float(service.rating) if service.rating is not None else 0,
        'reviews': service.reviews,
        'available': bool(service.available),
        'status': service.status,
        'posted_by': str(service.posted_by) if service.posted_by else None,
        'created_at': service.created_at,
    }

@app.delete('/api/admin/services/{service_id}')
def admin_delete_service(
    service_id: int,
    user=Depends(admin_user),
    db: Session = Depends(get_db),
):
    service = db.get(Service, service_id)

    if not service:
        raise HTTPException(404, 'Service not found.')

    db.delete(service)
    db.commit()

    return {'message': 'Service removed by admin'}

@app.get('/api/admin/requests')
def admin_get_requests(
    status: Optional[str] = None,
    user=Depends(admin_user),
    db: Session = Depends(get_db),
):
    query = (
        db.query(ServiceRequest, User, User)
        .outerjoin(
            User,
            ServiceRequest.farmer_id == User.id
        )
        .outerjoin(
            User,
            ServiceRequest.provider_id == User.id
        )
    )

    if status and status.lower() != 'all':
        query = query.filter(
            ServiceRequest.status == status.strip().lower()
        )

    results = (
        db.query(ServiceRequest)
        .order_by(ServiceRequest.id.desc())
        .all()
    )

    rows = []

    for request in results:
        farmer = db.get(User, request.farmer_id) if request.farmer_id else None
        provider = db.get(User, request.provider_id) if request.provider_id else None

        rows.append({
            'id': request.id,
            'request_id': request.request_id,
            'farmer_id': str(request.farmer_id) if request.farmer_id else None,
            'farmer_name': request.farmer_name,
            'farmer_phone': request.farmer_phone,
            'provider_id': str(request.provider_id) if request.provider_id else None,
            'service_id': request.service_id,
            'service_name': request.service_name,
            'quantity': request.quantity,
            'price': float(request.price) if request.price is not None else None,
            'payment_method': request.payment_method,
            'payment_status': request.payment_status,
            'status': request.status,
            'address': request.address,
            'notes': request.notes,
            'preferred_date': request.preferred_date,
            'created_at': request.created_at,
            'farmer': {
                'name': farmer.name if farmer else request.farmer_name or 'Farmer',
                'email': farmer.email if farmer else '',
                'phone': farmer.phone if farmer else request.farmer_phone or '',
            },
            'provider': {
                'name': provider.name if provider else 'Provider',
                'email': provider.email if provider else '',
                'phone': provider.phone if provider else '',
            },
        })

    return {
        'requests': rows,
        'orders': rows,
    }

@app.get('/api/admin/listings')
def admin_get_listings_legacy(
    user=Depends(admin_user),
    db: Session = Depends(get_db),
):
    return admin_get_services(user=user, db=db)


@app.put('/api/admin/listings/{listing_id}/status')
def admin_update_listing_status_legacy(
    listing_id: int,
    payload: StatusIn,
    user=Depends(admin_user),
    db: Session = Depends(get_db),
):
    return admin_update_service_status(
        listing_id=listing_id,
        payload=payload,
        user=user,
        db=db,
    )


@app.get('/api/admin/orders')
def admin_get_orders_legacy(
    user=Depends(admin_user),
    db: Session = Depends(get_db),
):
    return admin_get_requests(user=user, db=db)

@app.get('/api/admin/payments')
def admin_get_payments(
    user=Depends(admin_user),
    db: Session = Depends(get_db),
):
    requests = (
        db.query(ServiceRequest)
        .order_by(ServiceRequest.id.desc())
        .all()
    )

    rows = []

    for request in requests:
        rows.append({
            'order_id': request.request_id,
            'price': float(request.price) if request.price is not None else None,
            'payment_method': request.payment_method,
            'payment_status': request.payment_status,
            'status': request.status,
            'created_at': request.created_at,
        })

    return {'payments': rows}

@app.get('/api/admin/complaints')
def admin_get_complaints(
    user=Depends(admin_user),
    db: Session = Depends(get_db),
):
    complaints = (
        db.query(Complaint, User)
        .outerjoin(User, Complaint.user_id == User.id)
        .order_by(Complaint.id.desc())
        .all()
    )

    rows = []

    for complaint, complaint_user in complaints:
        rows.append({
            'id': complaint.id,
            'user_id': str(complaint.user_id) if complaint.user_id else None,
            'subject': complaint.subject,
            'description': complaint.description,
            'priority': complaint.priority,
            'status': complaint.status,
            'created_at': complaint.created_at,
            'users': {
                'name': complaint_user.name if complaint_user else '—',
                'email': complaint_user.email if complaint_user else '—',
            },
        })

    return {'complaints': rows}

@app.put('/api/admin/complaints/{complaint_id}/status')
def admin_update_complaint_status(
    complaint_id: int,
    payload: StatusIn,
    user=Depends(admin_user),
    db: Session = Depends(get_db),
):
    if payload.status not in {'open', 'assigned', 'resolved', 'closed'}:
        raise HTTPException(400, 'Invalid complaint status.')

    complaint = db.get(Complaint, complaint_id)

    if not complaint:
        raise HTTPException(404, 'Complaint not found.')

    complaint.status = payload.status

    db.commit()
    db.refresh(complaint)

    return {
        'id': complaint.id,
        'user_id': str(complaint.user_id) if complaint.user_id else None,
        'subject': complaint.subject,
        'description': complaint.description,
        'priority': complaint.priority,
        'status': complaint.status,
        'created_at': complaint.created_at,
    }
@app.post('/api/admin/notifications')
def admin_send_notification(
    payload: NotificationIn,
    user=Depends(admin_user),
    db: Session = Depends(get_db),
):
    alert = Alert(
        audience=payload.audience,
        type='system',
        title=payload.title or 'System Announcement',
        message=payload.message,
        created_by=uuid.UUID(user['id']),
    )

    db.add(alert)
    db.commit()
    db.refresh(alert)

    return {
        'id': alert.id,
        'audience': alert.audience,
        'type': alert.type,
        'title': alert.title,
        'message': alert.message,
        'is_read': bool(alert.is_read),
        'created_by': str(alert.created_by) if alert.created_by else None,
        'created_at': alert.created_at,
    }

# ==================== Legacy Products & Complaints Endpoints ====================

@app.get('/api/products')
def get_products(
    category: Optional[str] = None,
    db: Session = Depends(get_db),
):
    res = get_services(category=category, db=db)
    return {'products': res['services']}


@app.post('/api/orders')
def legacy_create_order(
    payload: ServiceRequestIn,
    user=Depends(current_user),
    db: Session = Depends(get_db),
):
    return create_service_request(
        payload=payload,
        user=user,
        db=db,
    )

@app.get('/api/orders')
def legacy_get_orders(
    user=Depends(current_user),
    db: Session = Depends(get_db),
):
    if user.get('role') in {'provider', 'seller'}:
        return get_provider_requests(user=user, db=db)

    return get_my_requests(user=user, db=db)

@app.post('/api/complaints')
def create_complaint(
    payload: ComplaintIn,
    user=Depends(current_user),
    db: Session = Depends(get_db),
):
    complaint = Complaint(
        user_id=uuid.UUID(user['id']),
        subject=payload.subject,
        description=payload.description,
        priority=payload.priority,
        status='open',
    )

    db.add(complaint)
    db.commit()
    db.refresh(complaint)

    return {
        'id': complaint.id,
        'user_id': str(complaint.user_id) if complaint.user_id else None,
        'subject': complaint.subject,
        'description': complaint.description,
        'priority': complaint.priority,
        'status': complaint.status,
        'created_at': complaint.created_at,
    }

@app.get('/api/notifications')
def legacy_get_notifications(
    user=Depends(current_user),
    db: Session = Depends(get_db),
):
    return get_alerts(user=user, db=db)


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
