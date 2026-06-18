# backend/app/routers/candidates.py
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime
import math

from ..db.supabase_client import get_supabase
from ..utils.auth import get_current_user

router = APIRouter(prefix="/candidates", tags=["Candidates"])


# ============================================
# PYDANTIC MODELS
# ============================================

class CandidateResponse(BaseModel):
    id: str
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    skills: List[str]
    match_score: float
    rank: int
    status: str
    screening_id: str
    created_at: str


class CandidateDetailResponse(BaseModel):
    id: str
    screening_id: str
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    skills: List[str]
    experience: Optional[str] = None
    education: Optional[str] = None
    summary: Optional[str] = None
    match_score: float
    rank: int
    score_breakdown: Dict[str, Any]
    matched_skills: List[str]
    missing_skills: List[str]
    certifications: List[Any]
    organizations: List[Any]
    awards: List[Any]
    projects: List[Any]
    experience_years: float
    original_filename: Optional[str] = None
    original_cv_url: Optional[str] = None
    viewed: bool
    created_at: str


class CandidateUpdateRequest(BaseModel):
    viewed: Optional[bool] = None
    notes: Optional[str] = None  # akan disimpan di tabel terpisah


class NoteResponse(BaseModel):
    id: str
    note: str
    user_id: str
    user_name: Optional[str] = None
    created_at: str


class NoteCreateRequest(BaseModel):
    note: str


class MessageResponse(BaseModel):
    message: str
    success: bool


# ============================================
# HELPER FUNCTIONS
# ============================================

def get_score_category(score: float) -> str:
    """Kategorikan skor (dalam desimal 0-1)"""
    if score >= 0.85:
        return "Sangat Cocok"
    elif score >= 0.65:
        return "Cukup Cocok"
    else:
        return "Perlu Review"


# ============================================
# ENDPOINTS
# ============================================

@router.get("/", response_model=Dict[str, Any])
async def get_candidates(
    search: Optional[str] = Query(None, description="Cari nama atau email"),
    sort_by: Optional[str] = Query("created_at", description="Sort by: name, score, rank, created_at"),
    order: Optional[str] = Query("desc", description="asc or desc"),
    status: Optional[str] = Query(None, description="Filter by status: very_good, good, review"),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_user)
):
    """
    Get list of candidates with filtering, sorting, and pagination.
    """
    supabase = get_supabase()
    company_id = current_user["company_id"]
    
    # Ambil screening sessions perusahaan ini
    screenings = supabase.table("screening_sessions")\
        .select("id")\
        .eq("company_id", company_id)\
        .execute()
    
    screening_ids = [s["id"] for s in screenings.data]
    
    if not screening_ids:
        return {
            "total": 0,
            "page": offset // limit + 1,
            "limit": limit,
            "candidates": []
        }
    
    # Build query
    query = supabase.table("candidates")\
        .select("*")\
        .in_("screening_id", screening_ids)
    
    # Search filter
    if search:
        query = query.or_(f"name.ilike.%{search}%,email.ilike.%{search}%")
    
    # Status filter
    if status:
        if status == "very_good":
            query = query.gte("match_score", 0.85)
        elif status == "good":
            query = query.gte("match_score", 0.65).lt("match_score", 0.85)
        elif status == "review":
            query = query.lt("match_score", 0.65)
    
    # Sorting
    sort_column = {
        "name": "name",
        "score": "match_score",
        "rank": "rank",
        "created_at": "created_at"
    }.get(sort_by, "created_at")
    
    query = query.order(sort_column, desc=(order == "desc"))
    
    # Pagination
    query = query.range(offset, offset + limit - 1)
    
    # Execute
    response = query.execute()
    
    # Format response
    candidates = []
    for c in response.data:
        score = c.get("match_score", 0)
        candidates.append({
            "id": c["id"],
            "name": c.get("name", "Unknown"),
            "email": c.get("email", ""),
            "phone": c.get("phone", ""),
            "skills": c.get("skills", [])[:5],
            "match_score": round(score * 100, 1),
            "rank": c.get("rank", 0),
            "status": get_score_category(score),
            "screening_id": c.get("screening_id"),
            "created_at": c.get("created_at")
        })
    
    # Get total count
    count_query = supabase.table("candidates")\
        .select("id", count="exact")\
        .in_("screening_id", screening_ids)
    
    if search:
        count_query = count_query.or_(f"name.ilike.%{search}%,email.ilike.%{search}%")
    if status:
        if status == "very_good":
            count_query = count_query.gte("match_score", 0.85)
        elif status == "good":
            count_query = count_query.gte("match_score", 0.65).lt("match_score", 0.85)
        elif status == "review":
            count_query = count_query.lt("match_score", 0.65)
    
    count_response = count_query.execute()
    total = count_response.count
    
    return {
        "total": total,
        "page": offset // limit + 1,
        "limit": limit,
        "candidates": candidates
    }


@router.get("/{candidate_id}", response_model=CandidateDetailResponse)
async def get_candidate_detail(
    candidate_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get detailed information for a specific candidate.
    """
    supabase = get_supabase()
    company_id = current_user["company_id"]
    
    # Ambil candidate
    candidate = supabase.table("candidates")\
        .select("*")\
        .eq("id", candidate_id)\
        .execute()
    
    if not candidate.data:
        raise HTTPException(404, "Candidate not found")
    
    candidate_data = candidate.data[0]
    
    # Verifikasi candidate milik perusahaan ini
    screening = supabase.table("screening_sessions")\
        .select("company_id")\
        .eq("id", candidate_data["screening_id"])\
        .execute()
    
    if not screening.data or screening.data[0]["company_id"] != company_id:
        raise HTTPException(403, "Access denied")
    
    # Mark as viewed
    if not candidate_data.get("viewed"):
        supabase.table("candidates")\
            .update({"viewed": True})\
            .eq("id", candidate_id)\
            .execute()
    
    score = candidate_data.get("match_score", 0)
    score_breakdown = candidate_data.get("score_breakdown", {})
    
    return CandidateDetailResponse(
        id=candidate_data["id"],
        screening_id=candidate_data["screening_id"],
        name=candidate_data.get("name", "Unknown"),
        email=candidate_data.get("email"),
        phone=candidate_data.get("phone"),
        skills=candidate_data.get("skills", []),
        experience=candidate_data.get("experience"),
        education=candidate_data.get("education"),
        summary=candidate_data.get("summary"),
        match_score=round(score * 100, 1),
        rank=candidate_data.get("rank", 0),
        score_breakdown=score_breakdown,
        matched_skills=candidate_data.get("matched_skills", []),
        missing_skills=candidate_data.get("missing_skills", []),
        certifications=candidate_data.get("certifications", []),
        organizations=candidate_data.get("organizations", []),
        awards=candidate_data.get("awards", []),
        projects=candidate_data.get("projects", []),
        experience_years=candidate_data.get("experience_years", 0),
        original_filename=candidate_data.get("original_filename"),
        original_cv_url=candidate_data.get("original_cv_url"),
        viewed=True,
        created_at=candidate_data["created_at"]
    )


@router.get("/{candidate_id}/download")
async def download_cv(
    candidate_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Download original CV file for a candidate.
    """
    supabase = get_supabase()
    company_id = current_user["company_id"]
    
    # Ambil candidate
    candidate = supabase.table("candidates")\
        .select("original_cv_url, original_filename, screening_id")\
        .eq("id", candidate_id)\
        .execute()
    
    if not candidate.data:
        raise HTTPException(404, "Candidate not found")
    
    candidate_data = candidate.data[0]
    
    # Verifikasi akses
    screening = supabase.table("screening_sessions")\
        .select("company_id")\
        .eq("id", candidate_data["screening_id"])\
        .execute()
    
    if not screening.data or screening.data[0]["company_id"] != company_id:
        raise HTTPException(403, "Access denied")
    
    if not candidate_data.get("original_cv_url"):
        raise HTTPException(404, "CV file not found")
    
    # Redirect ke URL file atau download langsung
    return {
        "download_url": candidate_data["original_cv_url"],
        "filename": candidate_data.get("original_filename", "cv.pdf")
    }


@router.patch("/{candidate_id}", response_model=MessageResponse)
async def update_candidate(
    candidate_id: str,
    update_data: CandidateUpdateRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Update candidate (mark as viewed, etc.)
    """
    supabase = get_supabase()
    company_id = current_user["company_id"]
    
    # Verifikasi candidate milik perusahaan ini
    candidate = supabase.table("candidates")\
        .select("screening_id")\
        .eq("id", candidate_id)\
        .execute()
    
    if not candidate.data:
        raise HTTPException(404, "Candidate not found")
    
    screening = supabase.table("screening_sessions")\
        .select("company_id")\
        .eq("id", candidate.data[0]["screening_id"])\
        .execute()
    
    if not screening.data or screening.data[0]["company_id"] != company_id:
        raise HTTPException(403, "Access denied")
    
    # Update data
    update_dict = {}
    if update_data.viewed is not None:
        update_dict["viewed"] = update_data.viewed
    
    if update_dict:
        supabase.table("candidates")\
            .update(update_dict)\
            .eq("id", candidate_id)\
            .execute()
    
    return MessageResponse(message="Candidate updated successfully", success=True)


@router.delete("/{candidate_id}", response_model=MessageResponse)
async def delete_candidate(
    candidate_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a candidate (admin only or HR for their own data).
    """
    supabase = get_supabase()
    company_id = current_user["company_id"]
    
    # Verifikasi candidate milik perusahaan ini
    candidate = supabase.table("candidates")\
        .select("screening_id")\
        .eq("id", candidate_id)\
        .execute()
    
    if not candidate.data:
        raise HTTPException(404, "Candidate not found")
    
    screening = supabase.table("screening_sessions")\
        .select("company_id")\
        .eq("id", candidate.data[0]["screening_id"])\
        .execute()
    
    if not screening.data or screening.data[0]["company_id"] != company_id:
        raise HTTPException(403, "Access denied")
    
    # Delete candidate
    supabase.table("candidates")\
        .delete()\
        .eq("id", candidate_id)\
        .execute()
    
    return MessageResponse(message="Candidate deleted successfully", success=True)


# ============================================
# CANDIDATE NOTES
# ============================================

@router.get("/{candidate_id}/notes", response_model=List[NoteResponse])
async def get_candidate_notes(
    candidate_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get all notes for a candidate.
    """
    supabase = get_supabase()
    company_id = current_user["company_id"]
    
    # Verifikasi akses
    candidate = supabase.table("candidates")\
        .select("screening_id")\
        .eq("id", candidate_id)\
        .execute()
    
    if not candidate.data:
        raise HTTPException(404, "Candidate not found")
    
    screening = supabase.table("screening_sessions")\
        .select("company_id")\
        .eq("id", candidate.data[0]["screening_id"])\
        .execute()
    
    if not screening.data or screening.data[0]["company_id"] != company_id:
        raise HTTPException(403, "Access denied")
    
    # Ambil notes
    notes = supabase.table("candidate_notes")\
        .select("*, users(full_name)")\
        .eq("candidate_id", candidate_id)\
        .order("created_at", desc=True)\
        .execute()
    
    result = []
    for note in notes.data:
        result.append({
            "id": note["id"],
            "note": note["note"],
            "user_id": note["user_id"],
            "user_name": note.get("users", {}).get("full_name") if note.get("users") else None,
            "created_at": note["created_at"]
        })
    
    return result


@router.post("/{candidate_id}/notes", response_model=NoteResponse)
async def create_candidate_note(
    candidate_id: str,
    request: NoteCreateRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Add a note to a candidate.
    """
    supabase = get_supabase()
    company_id = current_user["company_id"]
    user_id = current_user["user_id"]
    
    # Verifikasi akses
    candidate = supabase.table("candidates")\
        .select("screening_id")\
        .eq("id", candidate_id)\
        .execute()
    
    if not candidate.data:
        raise HTTPException(404, "Candidate not found")
    
    screening = supabase.table("screening_sessions")\
        .select("company_id")\
        .eq("id", candidate.data[0]["screening_id"])\
        .execute()
    
    if not screening.data or screening.data[0]["company_id"] != company_id:
        raise HTTPException(403, "Access denied")
    
    # Create note
    new_note = supabase.table("candidate_notes")\
        .insert({
            "candidate_id": candidate_id,
            "user_id": user_id,
            "note": request.note,
            "created_at": datetime.now().isoformat()
        })\
        .execute()
    
    if not new_note.data:
        raise HTTPException(500, "Failed to create note")
    
    note_data = new_note.data[0]
    
    return NoteResponse(
        id=note_data["id"],
        note=note_data["note"],
        user_id=note_data["user_id"],
        user_name=current_user.get("full_name"),
        created_at=note_data["created_at"]
    )


@router.delete("/{candidate_id}/notes/{note_id}", response_model=MessageResponse)
async def delete_candidate_note(
    candidate_id: str,
    note_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a note from a candidate.
    """
    supabase = get_supabase()
    company_id = current_user["company_id"]
    
    # Verifikasi akses candidate
    candidate = supabase.table("candidates")\
        .select("screening_id")\
        .eq("id", candidate_id)\
        .execute()
    
    if not candidate.data:
        raise HTTPException(404, "Candidate not found")
    
    screening = supabase.table("screening_sessions")\
        .select("company_id")\
        .eq("id", candidate.data[0]["screening_id"])\
        .execute()
    
    if not screening.data or screening.data[0]["company_id"] != company_id:
        raise HTTPException(403, "Access denied")
    
    # Verifikasi note milik user ini atau admin
    note = supabase.table("candidate_notes")\
        .select("user_id")\
        .eq("id", note_id)\
        .eq("candidate_id", candidate_id)\
        .execute()
    
    if not note.data:
        raise HTTPException(404, "Note not found")
    
    if note.data[0]["user_id"] != current_user["user_id"] and current_user.get("role") != "admin":
        raise HTTPException(403, "You can only delete your own notes")
    
    # Delete note
    supabase.table("candidate_notes")\
        .delete()\
        .eq("id", note_id)\
        .execute()
    
    return MessageResponse(message="Note deleted successfully", success=True)