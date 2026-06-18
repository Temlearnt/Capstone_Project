from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
import jwt
from ..config import settings
from ..db.supabase_client import get_supabase
from passlib.context import CryptContext

router = APIRouter()

# ============================================
# PASSWORD HASHING
# ============================================
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hash password menggunakan bcrypt"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifikasi password dengan bcrypt"""
    return pwd_context.verify(plain_password, hashed_password)

# ============================================
# JWT FUNCTIONS (mengambil dari settings)
# ============================================

def create_access_token(data: dict) -> str:
    """
    Membuat JWT token.
    Secret key dan algoritma diambil dari environment variable.
    """
    expire = datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    data.update({"exp": expire})
    
    # Encode token dengan secret key dari .env
    encoded_jwt = jwt.encode(
        data, 
        settings.JWT_SECRET_KEY, 
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt

def decode_access_token(token: str) -> dict:
    """
    Mendecode JWT token untuk validasi.
    """
    try:
        decoded = jwt.decode(
            token, 
            settings.JWT_SECRET_KEY, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        return decoded
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token sudah kadaluarsa")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token tidak valid")

# ============================================
# REQUEST MODELS
# ============================================

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    company_name: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    email: str
    full_name: str
    company_id: str

class MessageResponse(BaseModel):
    message: str
    success: bool

# ============================================
# DEPENDENCY: Get Current User from Token
# ============================================

async def get_current_user(token: str):
    """
    Dependency untuk mendapatkan user dari JWT token.
    Nanti bisa dipakai di endpoint yang butuh autentikasi.
    """
    payload = decode_access_token(token)
    user_id = payload.get("sub")
    email = payload.get("email")
    
    if not user_id or not email:
        raise HTTPException(status_code=401, detail="Token tidak valid")
    
    return {
        "user_id": user_id,
        "email": email,
        "company_id": payload.get("company_id"),
        "role": payload.get("role")
    }

# ============================================
# ENDPOINTS
# ============================================

@router.post("/register", response_model=TokenResponse)
async def register(request: RegisterRequest):
    """Registrasi HR user baru"""
    supabase = get_supabase()
    
    # Cek email sudah terdaftar
    existing_user = supabase.table("users").select("*").eq("email", request.email).execute()
    if existing_user.data:
        raise HTTPException(status_code=400, detail="Email sudah terdaftar")
    
    # Buat company
    company_response = supabase.table("companies").insert({
        "name": request.company_name,
        "email": request.email,
        "created_at": datetime.utcnow().isoformat()
    }).execute()
    company_id = company_response.data[0]["id"]
    
    # Hash password
    hashed_password = hash_password(request.password)
    
    # Buat user
    user_response = supabase.table("users").insert({
        "email": request.email,
        "password_hash": hashed_password,
        "full_name": request.full_name,
        "company_id": company_id,
        "role": "hr",
        "is_active": True,
        "created_at": datetime.utcnow().isoformat()
    }).execute()
    
    if not user_response.data:
        raise HTTPException(status_code=500, detail="Gagal membuat user")
    
    user = user_response.data[0]
    
    # Buat JWT token
    token_data = {
        "sub": user["id"],
        "email": user["email"],
        "company_id": user["company_id"],
        "role": user["role"]
    }
    access_token = create_access_token(token_data)
    
    return TokenResponse(
        access_token=access_token,
        user_id=user["id"],
        email=user["email"],
        full_name=user["full_name"],
        company_id=user["company_id"]
    )

@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """Login HR user"""
    supabase = get_supabase()
    
    # Cari user
    response = supabase.table("users").select("*").eq("email", request.email).execute()
    if not response.data:
        raise HTTPException(status_code=401, detail="Email atau password salah")
    
    user = response.data[0]
    
    # Verifikasi password
    if not verify_password(request.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Email atau password salah")
    
    # Update last_login
    supabase.table("users").update({
        "last_login": datetime.utcnow().isoformat()
    }).eq("id", user["id"]).execute()
    
    # Buat JWT token
    token_data = {
        "sub": user["id"],
        "email": user["email"],
        "company_id": user["company_id"],
        "role": user["role"]
    }
    access_token = create_access_token(token_data)
    
    return TokenResponse(
        access_token=access_token,
        user_id=user["id"],
        email=user["email"],
        full_name=user["full_name"],
        company_id=user["company_id"]
    )

@router.get("/me")
async def get_current_user_info(email: str = None, token: str = None):
    """
    Mendapatkan data user saat ini.
    Bisa pakai query param email (untuk testing) atau token.
    """
    supabase = get_supabase()
    
    # Jika ada token, decode dulu
    if token:
        payload = decode_access_token(token)
        email = payload.get("email")
    
    if not email:
        raise HTTPException(status_code=400, detail="Email atau token diperlukan")
    
    response = supabase.table("users").select("*, companies(name)").eq("email", email).execute()
    
    if not response.data:
        raise HTTPException(status_code=404, detail="User not found")
    
    user = response.data[0]
    
    return {
        "user_id": user["id"],
        "email": user["email"],
        "full_name": user["full_name"],
        "role": user["role"],
        "company_id": user["company_id"],
        "company_name": user["companies"]["name"] if user.get("companies") else None,
        "is_active": user["is_active"],
        "last_login": user.get("last_login"),
        "created_at": user.get("created_at")
    }

@router.post("/logout", response_model=MessageResponse)
async def logout():
    """Logout user - cukup hapus token di frontend"""
    return MessageResponse(
        message="Logout berhasil",
        success=True
    )

@router.get("/verify-token")
async def verify_token(token: str):
    """Endpoint untuk memverifikasi apakah token masih valid"""
    try:
        payload = decode_access_token(token)
        return {
            "valid": True,
            "user_id": payload.get("sub"),
            "email": payload.get("email"),
            "exp": payload.get("exp")
        }
    except HTTPException:
        return {"valid": False, "message": "Token tidak valid"}