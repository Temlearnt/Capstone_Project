"""In-memory storage untuk testing tanpa database"""

from typing import Dict, List, Any
from datetime import datetime

# Storage dictionaries
screening_sessions: Dict[str, Dict[str, Any]] = {}
candidates: Dict[str, List[Dict[str, Any]]] = {}

def create_screening_session(screening_id: str, job_description: str, employment_type: str = "fulltime"):
    """Create a new screening session in memory"""
    screening_sessions[screening_id] = {
        "id": screening_id,
        "job_description": job_description,
        "employment_type": employment_type,
        "status": "pending",
        "total_cvs": 0,
        "created_at": datetime.now().isoformat(),
        "completed_at": None
    }
    return screening_sessions[screening_id]

def update_screening_status(screening_id: str, status: str, total_cvs: int = None):
    """Update screening session status"""
    if screening_id in screening_sessions:
        screening_sessions[screening_id]["status"] = status
        if total_cvs:
            screening_sessions[screening_id]["total_cvs"] = total_cvs
        if status == "completed":
            screening_sessions[screening_id]["completed_at"] = datetime.now().isoformat()

def get_screening_session(screening_id: str):
    """Get screening session by ID"""
    return screening_sessions.get(screening_id)

def save_candidates(screening_id: str, candidates_list: List[Dict]):
    """Save candidates results"""
    candidates[screening_id] = candidates_list
    update_screening_status(screening_id, "completed", len(candidates_list))

def get_candidates(screening_id: str):
    """Get candidates by screening ID"""
    return candidates.get(screening_id, [])