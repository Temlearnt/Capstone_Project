# backend/app/db/operations.py
from supabase import Client
from .supabase_client import get_supabase
import logging

logger = logging.getLogger(__name__)


def get_supabase_client() -> Client:
    """Get Supabase client instance"""
    return get_supabase()


# ============ TEST CONNECTION ============
def test_connection() -> bool:
    """Test database connection - check if users table exists"""
    try:
        supabase = get_supabase_client()
        if supabase is None:
            return False
        # Cek tabel users (bukan employment_types!)
        supabase.table("users").select("*").limit(1).execute()
        logger.info("Database connection successful!")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False


# ============ JOB ROLES ============
def get_job_roles():
    """Get all job roles"""
    supabase = get_supabase_client()
    if supabase is None:
        return []
    try:
        response = supabase.table("job_roles").select("*").order("name").execute()
        return response.data
    except Exception as e:
        logger.warning(f"Could not fetch job roles: {e}")
        return []


# ============ COMPANIES ============
def create_company(name: str, email: str, phone: str = None) -> dict:
    """Create a new company"""
    supabase = get_supabase_client()
    if supabase is None:
        return {"id": "mock-id", "name": name}
    
    response = supabase.table("companies").insert({
        "name": name,
        "email": email,
        "phone": phone
    }).execute()
    return response.data[0] if response.data else None


def get_company_by_id(company_id: str):
    """Get company by ID"""
    supabase = get_supabase_client()
    if supabase is None:
        return None
    
    response = supabase.table("companies").select("*").eq("id", company_id).execute()
    return response.data[0] if response.data else None


# ============ USERS ============
def create_user(company_id: str, email: str, full_name: str, password_hash: str, role: str = "hr"):
    """Create a new user"""
    supabase = get_supabase_client()
    if supabase is None:
        return {"id": "mock-id", "email": email}
    
    response = supabase.table("users").insert({
        "company_id": company_id,
        "email": email,
        "full_name": full_name,
        "password_hash": password_hash,
        "role": role
    }).execute()
    return response.data[0] if response.data else None


def get_user_by_email(email: str):
    """Get user by email"""
    supabase = get_supabase_client()
    if supabase is None:
        return None
    
    response = supabase.table("users").select("*").eq("email", email).execute()
    return response.data[0] if response.data else None


def get_user_by_id(user_id: str):
    """Get user by ID"""
    supabase = get_supabase_client()
    if supabase is None:
        return None
    
    response = supabase.table("users").select("*").eq("id", user_id).execute()
    return response.data[0] if response.data else None


def update_user_last_login(user_id: str):
    """Update user's last login timestamp"""
    supabase = get_supabase_client()
    if supabase is None:
        return None
    
    from datetime import datetime
    response = supabase.table("users").update({
        "last_login": datetime.now().isoformat()
    }).eq("id", user_id).execute()
    return response.data[0] if response.data else None


# ============ SCREENING SESSIONS ============
def create_screening_session(
    company_id: str,
    user_id: str,
    job_description: str,
    job_role_id: str = None,
    custom_skills: list = None
):
    """Create a new screening session"""
    supabase = get_supabase_client()
    if supabase is None:
        return {"id": "mock-id", "status": "pending"}
    
    try:
        response = supabase.table("screening_sessions").insert({
            "company_id": company_id,
            "user_id": user_id,
            "job_description": job_description,
            "job_role_id": job_role_id,
            "custom_skills": custom_skills or [],
            "status": "pending",
            "total_cvs": 0
        }).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        logger.error(f"Failed to create screening session: {e}")
        return None


def update_screening_status(screening_id: str, status: str, total_cvs: int = None, progress: int = None):
    """Update screening session status"""
    supabase = get_supabase_client()
    if supabase is None:
        return None
    
    update_data = {"status": status}
    if total_cvs is not None:
        update_data["total_cvs"] = total_cvs
    if progress is not None:
        update_data["progress"] = progress
    if status == "completed":
        from datetime import datetime
        update_data["completed_at"] = datetime.now().isoformat()
    
    try:
        response = supabase.table("screening_sessions").update(update_data).eq("id", screening_id).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        logger.error(f"Failed to update screening status: {e}")
        return None


def get_screening_session(screening_id: str):
    """Get screening session by ID"""
    supabase = get_supabase_client()
    if supabase is None:
        return None
    
    try:
        response = supabase.table("screening_sessions").select("*").eq("id", screening_id).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        logger.error(f"Failed to get screening session: {e}")
        return None


def get_user_screening_sessions(user_id: str, limit: int = 20):
    """Get all screening sessions for a user"""
    supabase = get_supabase_client()
    if supabase is None:
        return []
    
    try:
        response = supabase.table("screening_sessions")\
            .select("*")\
            .eq("user_id", user_id)\
            .order("created_at", desc=True)\
            .limit(limit)\
            .execute()
        return response.data
    except Exception as e:
        logger.error(f"Failed to get user screenings: {e}")
        return []


# ============ CANDIDATES ============
def save_candidates(screening_id: str, candidates_list: list):
    """Save multiple candidates from screening result"""
    supabase = get_supabase_client()
    if supabase is None:
        return []
    
    data = []
    for cand in candidates_list:
        data.append({
            "screening_id": screening_id,
            "name": cand.get("name", "Unknown"),
            "email": cand.get("email", ""),
            "phone": cand.get("phone", ""),
            "skills": cand.get("skills", []),
            "experience": cand.get("experience", ""),
            "education": cand.get("education", ""),
            "match_score": cand.get("match_score", 0),
            "rank": cand.get("rank", 0),
            "original_filename": cand.get("filename", "")
        })
    
    if data:
        try:
            response = supabase.table("candidates").insert(data).execute()
            logger.info(f"Saved {len(data)} candidates to database")
            return response.data
        except Exception as e:
            logger.error(f"Failed to save candidates: {e}")
            return []
    return []


def get_candidates_by_screening(screening_id: str):
    """Get all candidates for a screening session, ordered by rank"""
    supabase = get_supabase_client()
    if supabase is None:
        return []
    
    try:
        response = supabase.table("candidates")\
            .select("*")\
            .eq("screening_id", screening_id)\
            .order("rank")\
            .execute()
        return response.data
    except Exception as e:
        logger.error(f"Failed to get candidates: {e}")
        return []