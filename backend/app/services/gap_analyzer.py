# backend/app/services/gap_analyzer.py
def format_response(results: list, screening_id: str = None) -> dict:
    """
    Format hasil screening ke JSON response yang rapi.
    """
    # Validasi input
    if not results:
        return {
            "screening_id": screening_id,
            "total_candidates": 0,
            "candidates": []
        }
    
    # Sort by score
    sorted_results = sorted(results, key=lambda x: x.get("final_score", 0), reverse=True)
    
    # Add rank
    for i, result in enumerate(sorted_results, 1):
        result["rank"] = i
    
    candidates = []
    for r in sorted_results:
        candidates.append({
            "rank": r.get("rank"),
            "name": r.get("name", "Unknown"),
            "email": r.get("email", ""),
            "skills": r.get("skills", [])[:10],
            "final_score": round(r.get("final_score", 0) * 100, 1),
            "breakdown": r.get("breakdown", {}),
            "gap_analysis": r.get("gap_analysis", {})
        })
    
    return {
        "screening_id": screening_id,
        "total_candidates": len(candidates),
        "candidates": candidates
    }
    
def analyze_gaps(cv_sections: dict, jd_sections: dict) -> dict:
    """
    Analisis gap antara CV dan JD.
    Output: missing_skills, extra_skills, recommendations
    """
    cv_skills = set(cv_sections.get("skills", []))
    jd_skills = set(jd_sections.get("skills", []))
    
    missing_skills = list(jd_skills - cv_skills)
    matched_skills = list(cv_skills & jd_skills)
    extra_skills = list(cv_skills - jd_skills)
    
    # Generate recommendations
    recommendations = []
    if len(matched_skills) == 0:
        recommendations.append("Tidak ada skill yang cocok dengan job description")
    elif len(missing_skills) <= 2:
        recommendations.append(f"Hanya kurang {len(missing_skills)} skill: {', '.join(missing_skills)}")
    else:
        recommendations.append(f"Kurang {len(missing_skills)} skill yang dibutuhkan")
    
    # Experience check
    if len(cv_sections.get("experience", "")) < 50:
        recommendations.append("Pengalaman kerja kurang terdokumentasi dengan baik")
    
    return {
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "extra_skills": extra_skills,
        "match_percentage": len(matched_skills) / max(len(jd_skills), 1) * 100,
        "recommendations": recommendations
    }


def analyze_gaps_batch(cv_sections_list: list, jd_sections: dict) -> list:
    """Analisis gap untuk banyak CV"""
    return [analyze_gaps(cv, jd_sections) for cv in cv_sections_list]