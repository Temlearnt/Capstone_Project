from fastapi import APIRouter
from ..storage import screening_sessions

router = APIRouter()

@router.get("/")
async def get_history():
    sessions = list(screening_sessions.values())
    sessions.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    
    return {
        "total": len(sessions),
        "screenings": sessions
    }