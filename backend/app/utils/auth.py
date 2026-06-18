# backend/app/utils/auth.py
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from datetime import datetime, timedelta
import os

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "recruitly-super-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 1 hari

security = HTTPBearer()

def create_access_token(data: dict) -> str:
    """Buat JWT token baru"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> dict:
    """Verifikasi JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token sudah kadaluarsa")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token tidak valid")

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Dependency untuk mendapatkan user dari token"""
    token = credentials.credentials
    payload = verify_token(token)
    
    return {
        "user_id": payload.get("sub"),
        "email": payload.get("email"),
        "company_id": payload.get("company_id"),
        "role": payload.get("role")
    }