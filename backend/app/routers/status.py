from fastapi import APIRouter, HTTPException
from ..storage import get_screening_session

router = APIRouter()

@router.get("/{screening_id}")
async def get_status(screening_id: str):
    session = get_screening_session(screening_id)
    
    if not session:
        raise HTTPException(404, "Screening session not found")
    
    return {
        "screening_id": screening_id,
        "status": session.get("status", "unknown"),
        "total_cvs": session.get("total_cvs", 0),
        "created_at": session.get("created_at"),
        "completed_at": session.get("completed_at")
    }