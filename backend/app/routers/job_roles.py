# backend/app/routers/job_roles.py
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from ..db.supabase_client import get_supabase
from ..utils.auth import get_current_user

router = APIRouter(prefix="/job-roles", tags=["Job Roles"])


# ============================================
# PYDANTIC MODELS
# ============================================

class JobRoleResponse(BaseModel):
    id: str
    name: str
    category: str
    default_skills: List[str]
    suggested_jd: Optional[str] = None
    description: Optional[str] = None
    created_at: str


class JobRoleDetailResponse(JobRoleResponse):
    pass


class JobRoleCreate(BaseModel):
    name: str
    category: str
    default_skills: List[str]
    suggested_jd: Optional[str] = None
    description: Optional[str] = None


# ============================================
# ENDPOINTS
# ============================================

@router.get("/", response_model=List[JobRoleResponse])
async def get_all_job_roles():
    """
    Get all job roles for dropdown selection.
    Frontend akan panggil endpoint ini untuk mengisi dropdown role.
    """
    supabase = get_supabase()
    
    try:
        response = supabase.table("job_roles")\
            .select("*")\
            .order("name")\
            .execute()
        
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch job roles: {str(e)}")


@router.get("/{role_id}", response_model=JobRoleDetailResponse)
async def get_job_role_by_id(role_id: str):
    """
    Get job role details by ID.
    Setelah HR pilih role dari dropdown, panggil endpoint ini
    untuk mendapatkan suggested_jd yang akan ditampilkan di textarea.
    """
    supabase = get_supabase()
    
    try:
        response = supabase.table("job_roles")\
            .select("*")\
            .eq("id", role_id)\
            .execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail=f"Job role with id {role_id} not found")
        
        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch job role: {str(e)}")


@router.get("/by-name/{name}")
async def get_job_role_by_name(name: str):
    """
    Get job role by name (alternative to ID-based lookup)
    """
    supabase = get_supabase()
    
    try:
        response = supabase.table("job_roles")\
            .select("*")\
            .ilike("name", name)\
            .execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail=f"Job role '{name}' not found")
        
        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch job role: {str(e)}")


@router.get("/categories")
async def get_categories():
    """
    Get all unique job role categories.
    """
    supabase = get_supabase()
    
    try:
        response = supabase.table("job_roles")\
            .select("category")\
            .execute()
        
        categories = list(set([item["category"] for item in response.data if item.get("category")]))
        categories.sort()
        
        return {"categories": categories}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch categories: {str(e)}")


@router.get("/{role_id}/skills")
async def get_role_skills(role_id: str):
    """
    Get default skills for a specific job role.
    """
    supabase = get_supabase()
    
    try:
        response = supabase.table("job_roles")\
            .select("name, default_skills")\
            .eq("id", role_id)\
            .execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail=f"Job role not found")
        
        role = response.data[0]
        return {
            "role_id": role_id,
            "role_name": role.get("name"),
            "skills": role.get("default_skills", []),
            "skill_count": len(role.get("default_skills", []))
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch skills: {str(e)}")


@router.post("/", response_model=JobRoleResponse)
async def create_job_role(
    role: JobRoleCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new job role (admin only).
    """
    # Hanya admin yang boleh membuat role baru
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Only admin can create job roles")
    
    supabase = get_supabase()
    
    try:
        response = supabase.table("job_roles").insert({
            "name": role.name,
            "category": role.category,
            "default_skills": role.default_skills,
            "suggested_jd": role.suggested_jd,
            "description": role.description,
            "created_at": datetime.now().isoformat()
        }).execute()
        
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create job role: {str(e)}")


@router.delete("/{role_id}")
async def delete_job_role(
    role_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a job role (admin only).
    """
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Only admin can delete job roles")
    
    supabase = get_supabase()
    
    try:
        response = supabase.table("job_roles").delete().eq("id", role_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail=f"Job role not found")
        
        return {"message": "Job role deleted successfully", "success": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete job role: {str(e)}")