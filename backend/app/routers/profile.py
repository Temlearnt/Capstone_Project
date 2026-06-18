# backend/app/routers/profile.py
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
import uuid
import os
import shutil

from ..db.supabase_client import get_supabase
from ..utils.auth import get_current_user
from passlib.context import CryptContext

router = APIRouter(prefix="/profile", tags=["Profile"])

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ============================================
# PYDANTIC MODELS
# ============================================

class ProfileResponse(BaseModel):
    user_id: str
    email: str
    full_name: str
    avatar_url: Optional[str] = None
    phone: Optional[str] = None
    role: str
    is_active: bool
    company_id: str
    company_name: str
    created_at: str
    last_login: Optional[str] = None


class ProfileUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str
    confirm_password: str


class MessageResponse(BaseModel):
    message: str
    success: bool


# ============================================
# HELPER FUNCTIONS
# ============================================

def hash_password(password: str) -> str:
    """Hash password menggunakan bcrypt"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifikasi password dengan bcrypt"""
    return pwd_context.verify(plain_password, hashed_password)


# ============================================
# ENDPOINTS
# ============================================

@router.get("/", response_model=ProfileResponse)
async def get_profile(current_user: dict = Depends(get_current_user)):
    """
    Get current user profile.
    """
    supabase = get_supabase()
    user_id = current_user["user_id"]
    
    try:
        # Ambil data user
        user_response = supabase.table("users")\
            .select("id, email, full_name, avatar_url, phone, role, is_active, company_id, created_at, last_login")\
            .eq("id", user_id)\
            .execute()
        
        if not user_response.data:
            raise HTTPException(status_code=404, detail="User not found")
        
        user = user_response.data[0]
        
        # Ambil data company
        company_response = supabase.table("companies")\
            .select("name")\
            .eq("id", user["company_id"])\
            .execute()
        
        company_name = company_response.data[0]["name"] if company_response.data else ""
        
        return ProfileResponse(
            user_id=user["id"],
            email=user["email"],
            full_name=user["full_name"],
            avatar_url=user.get("avatar_url"),
            phone=user.get("phone"),
            role=user["role"],
            is_active=user["is_active"],
            company_id=user["company_id"],
            company_name=company_name,
            created_at=user["created_at"],
            last_login=user.get("last_login")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get profile: {str(e)}")


@router.put("/", response_model=MessageResponse)
async def update_profile(
    profile_data: ProfileUpdateRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Update user profile (full_name and phone only).
    """
    supabase = get_supabase()
    user_id = current_user["user_id"]
    
    update_data = {}
    if profile_data.full_name is not None:
        update_data["full_name"] = profile_data.full_name
    if profile_data.phone is not None:
        update_data["phone"] = profile_data.phone
    update_data["updated_at"] = datetime.now().isoformat()
    
    if not update_data:
        return MessageResponse(message="No data to update", success=True)
    
    try:
        response = supabase.table("users")\
            .update(update_data)\
            .eq("id", user_id)\
            .execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="User not found")
        
        return MessageResponse(message="Profile updated successfully", success=True)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update profile: {str(e)}")


@router.post("/avatar", response_model=MessageResponse)
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Upload avatar image for current user.
    Supported formats: jpg, jpeg, png, gif, webp
    """
    supabase = get_supabase()
    user_id = current_user["user_id"]
    
    # Validasi file type
    allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="File type not supported. Use JPG, PNG, GIF, or WEBP")
    
    # Validasi ukuran (max 2MB)
    content = await file.read()
    if len(content) > 2 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large. Max 2MB")
    
    # Generate unique filename
    file_extension = file.filename.split(".")[-1].lower()
    filename = f"avatar_{user_id}_{uuid.uuid4().hex[:8]}.{file_extension}"
    
    try:
        # Upload ke Supabase Storage
        storage = supabase.storage()
        bucket = "avatars"
        
        # Cek apakah bucket ada, jika tidak buat
        try:
            storage.get_bucket(bucket)
        except:
            storage.create_bucket(bucket, {"public": True})
        
        # Upload file
        storage.from_(bucket).upload(filename, content)
        
        # Get public URL
        avatar_url = storage.from_(bucket).get_public_url(filename)
        
        # Update user avatar_url
        supabase.table("users")\
            .update({"avatar_url": avatar_url, "updated_at": datetime.now().isoformat()})\
            .eq("id", user_id)\
            .execute()
        
        return MessageResponse(message="Avatar uploaded successfully", success=True)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload avatar: {str(e)}")


@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    request: ChangePasswordRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Change user password.
    """
    supabase = get_supabase()
    user_id = current_user["user_id"]
    
    # Validasi password baru
    if len(request.new_password) < 6:
        raise HTTPException(status_code=400, detail="New password must be at least 6 characters")
    
    if request.new_password != request.confirm_password:
        raise HTTPException(status_code=400, detail="New password and confirmation do not match")
    
    if request.old_password == request.new_password:
        raise HTTPException(status_code=400, detail="New password must be different from old password")
    
    try:
        # Ambil user saat ini
        user_response = supabase.table("users")\
            .select("password_hash")\
            .eq("id", user_id)\
            .execute()
        
        if not user_response.data:
            raise HTTPException(status_code=404, detail="User not found")
        
        user = user_response.data[0]
        
        # Verifikasi old password
        if not verify_password(request.old_password, user["password_hash"]):
            raise HTTPException(status_code=401, detail="Old password is incorrect")
        
        # Hash new password
        new_hash = hash_password(request.new_password)
        
        # Update password
        supabase.table("users")\
            .update({"password_hash": new_hash, "updated_at": datetime.now().isoformat()})\
            .eq("id", user_id)\
            .execute()
        
        return MessageResponse(message="Password changed successfully", success=True)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to change password: {str(e)}")