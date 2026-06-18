from fastapi import APIRouter, HTTPException
from ..storage import get_screening_session, get_candidates

router = APIRouter()

@router.get("/{screening_id}")
async def get_result(screening_id: str):
    session = get_screening_session(screening_id)
    
    if not session:
        raise HTTPException(404, "Screening session not found")
    
    candidates = get_candidates(screening_id)
    
    return {
        "screening_id": screening_id,
        "job_description": session.get("job_description"),
        "employment_type": session.get("employment_type"),
        "status": session.get("status"),
        "total_cvs": len(candidates),
        "candidates": candidates
    }