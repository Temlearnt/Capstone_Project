# backend/app/routers/test_db.py
from fastapi import APIRouter
from ..db.operations import test_connection, get_job_roles

router = APIRouter()

@router.get("/db")
async def test_database():
    """Test database connection and return data"""
    connected = test_connection()
    
    if not connected:
        return {
            "status": "error",
            "message": "Database connection failed. Check your SUPABASE_URL and SUPABASE_KEY"
        }
    
    job_roles = get_job_roles()
    
    return {
        "status": "ok",
        "message": "Database connected successfully!",
        "job_roles_count": len(job_roles),
        "job_roles": job_roles
    }