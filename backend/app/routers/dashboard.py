# backend/app/routers/dashboard.py
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List
from datetime import datetime
import numpy as np

from ..db.supabase_client import get_supabase
from ..utils.auth import get_current_user

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


# ============================================
# HELPER FUNCTIONS
# ============================================

def get_score_category(score: float) -> str:
    """Kategorikan skor (dalam persentase)"""
    if score >= 85:
        return "Sangat Cocok"
    elif score >= 65:
        return "Cukup Cocok"
    else:
        return "Perlu Review"


# ============================================
# MAIN DASHBOARD ENDPOINTS
# ============================================

@router.get("/stats")
async def get_dashboard_stats(current_user: dict = Depends(get_current_user)):
    """
    Get dashboard statistics (6 KPI):
    - Total kandidat
    - Rata-rata skor
    - Sangat cocok (≥85%)
    - Cukup cocok (65-84%)
    - Perlu review (<65%)
    - Total screening sessions
    """
    supabase = get_supabase()
    company_id = current_user["company_id"]
    
    # Gunakan view dashboard_stats yang sudah dibuat di database
    try:
        response = supabase.table("dashboard_stats").select("*").execute()
        stats = response.data[0] if response.data else {}
        
        return {
            "total_candidates": stats.get("total_candidates", 0),
            "avg_score": stats.get("avg_score", 0),
            "very_good_count": stats.get("very_good_count", 0),
            "good_count": stats.get("good_count", 0),
            "need_review_count": stats.get("need_review_count", 0),
            "total_screenings": stats.get("total_screenings", 0)
        }
    except Exception as e:
        # Fallback: query manual jika view belum ada
        return await get_dashboard_stats_manual(company_id)


async def get_dashboard_stats_manual(company_id: str):
    """Fallback query manual jika view dashboard_stats belum ada"""
    supabase = get_supabase()
    
    # Ambil semua screening sessions perusahaan ini
    screenings = supabase.table("screening_sessions")\
        .select("id")\
        .eq("company_id", company_id)\
        .execute()
    
    screening_ids = [s["id"] for s in screenings.data]
    
    if not screening_ids:
        return {
            "total_candidates": 0,
            "avg_score": 0,
            "very_good_count": 0,
            "good_count": 0,
            "need_review_count": 0,
            "total_screenings": len(screening_ids)
        }
    
    # Ambil semua candidates dari screening tersebut
    candidates = supabase.table("candidates")\
        .select("match_score")\
        .in_("screening_id", screening_ids)\
        .execute()
    
    scores = [c.get("match_score", 0) for c in candidates.data]
    
    if not scores:
        return {
            "total_candidates": 0,
            "avg_score": 0,
            "very_good_count": 0,
            "good_count": 0,
            "need_review_count": 0,
            "total_screenings": len(screening_ids)
        }
    
    avg_score = np.mean(scores) * 100
    very_good = sum(1 for s in scores if s >= 0.85)
    good = sum(1 for s in scores if 0.65 <= s < 0.85)
    need_review = sum(1 for s in scores if s < 0.65)
    
    return {
        "total_candidates": len(scores),
        "avg_score": round(avg_score, 1),
        "very_good_count": very_good,
        "good_count": good,
        "need_review_count": need_review,
        "total_screenings": len(screening_ids)
    }


@router.get("/top-candidates")
async def get_top_candidates(
    limit: int = 5,
    current_user: dict = Depends(get_current_user)
):
    """Get top N candidates by score for this company"""
    supabase = get_supabase()
    company_id = current_user["company_id"]
    
    # Ambil screening sessions perusahaan ini
    screenings = supabase.table("screening_sessions")\
        .select("id")\
        .eq("company_id", company_id)\
        .execute()
    
    screening_ids = [s["id"] for s in screenings.data]
    
    if not screening_ids:
        return {"total_candidates": 0, "candidates": []}
    
    # Ambil candidates terbaik
    candidates = supabase.table("candidates")\
        .select("name, email, skills, match_score, screening_id")\
        .in_("screening_id", screening_ids)\
        .order("match_score", desc=True)\
        .limit(limit)\
        .execute()
    
    result = []
    for i, cand in enumerate(candidates.data, 1):
        score = cand.get("match_score", 0) * 100
        result.append({
            "rank": i,
            "name": cand.get("name", "Unknown"),
            "score": round(score, 1),
            "score_category": get_score_category(score),
            "skills": cand.get("skills", [])[:5],
            "email": cand.get("email", ""),
            "screening_id": cand.get("screening_id")
        })
    
    return {
        "total_candidates": len(candidates.data),
        "candidates": result
    }


@router.get("/recent-screenings")
async def get_recent_screenings(
    limit: int = 5,
    current_user: dict = Depends(get_current_user)
):
    """Get recent screening sessions for this company"""
    supabase = get_supabase()
    company_id = current_user["company_id"]
    
    screenings = supabase.table("screening_sessions")\
        .select("id, job_description, total_cvs, status, created_at, completed_at")\
        .eq("company_id", company_id)\
        .order("created_at", desc=True)\
        .limit(limit)\
        .execute()
    
    result = []
    for s in screenings.data:
        result.append({
            "screening_id": s["id"],
            "job_description": s.get("job_description", "")[:100] + ("..." if len(s.get("job_description", "")) > 100 else ""),
            "total_cvs": s.get("total_cvs", 0),
            "status": s.get("status", "unknown"),
            "created_at": s.get("created_at"),
            "completed_at": s.get("completed_at")
        })
    
    return {"screenings": result}


@router.get("/skill-distribution")
async def get_skill_distribution(
    limit: int = 10,
    current_user: dict = Depends(get_current_user)
):
    """Get skill distribution across all candidates for this company"""
    supabase = get_supabase()
    company_id = current_user["company_id"]
    
    # Ambil screening sessions
    screenings = supabase.table("screening_sessions")\
        .select("id")\
        .eq("company_id", company_id)\
        .execute()
    
    screening_ids = [s["id"] for s in screenings.data]
    
    if not screening_ids:
        return {"skills": []}
    
    # Ambil semua skills dari candidates
    candidates = supabase.table("candidates")\
        .select("skills")\
        .in_("screening_id", screening_ids)\
        .execute()
    
    skill_count = {}
    total_candidates = len(candidates.data)
    
    for cand in candidates.data:
        skills = cand.get("skills", [])
        for skill in skills:
            skill_lower = skill.lower()
            skill_count[skill_lower] = skill_count.get(skill_lower, 0) + 1
    
    sorted_skills = sorted(skill_count.items(), key=lambda x: x[1], reverse=True)
    top_skills = sorted_skills[:limit]
    
    return {
        "skills": [
            {
                "name": skill,
                "count": count,
                "percentage": round(count / total_candidates * 100, 1) if total_candidates > 0 else 0
            }
            for skill, count in top_skills
        ]
    }


@router.get("/screening/{screening_id}")
async def get_screening_detail(
    screening_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get detailed information for a specific screening"""
    supabase = get_supabase()
    company_id = current_user["company_id"]
    
    # Verifikasi screening milik perusahaan ini
    session = supabase.table("screening_sessions")\
        .select("*")\
        .eq("id", screening_id)\
        .eq("company_id", company_id)\
        .execute()
    
    if not session.data:
        raise HTTPException(404, "Screening not found")
    
    session_data = session.data[0]
    
    # Ambil candidates
    candidates = supabase.table("candidates")\
        .select("name, email, skills, match_score, rank")\
        .eq("screening_id", screening_id)\
        .order("rank")\
        .execute()
    
    scores = [c.get("match_score", 0) for c in candidates.data]
    avg_score = np.mean(scores) * 100 if scores else 0
    
    return {
        "screening_id": screening_id,
        "job_description": session_data.get("job_description"),
        "status": session_data.get("status"),
        "total_cvs": session_data.get("total_cvs", 0),
        "avg_score": round(avg_score, 1),
        "created_at": session_data.get("created_at"),
        "completed_at": session_data.get("completed_at"),
        "candidates": [
            {
                "rank": c.get("rank", i+1),
                "name": c.get("name", "Unknown"),
                "score": round(c.get("match_score", 0) * 100, 1),
                "score_category": get_score_category(c.get("match_score", 0) * 100),
                "skills": c.get("skills", [])[:5],
                "email": c.get("email", "")
            }
            for i, c in enumerate(candidates.data)
        ]
    }