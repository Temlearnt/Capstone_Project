# backend/app/services/formatter.py
def format_response(results: list, screening_id: str = None) -> dict:
    """
    Format hasil screening ke JSON response yang rapi.
    """
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
            "skills": r.get("skills", [])[:10],  # Top 10 skills
            "final_score": round(r.get("final_score", 0) * 100, 1),  # Percentage
            "breakdown": r.get("breakdown", {}),
            "gap_analysis": r.get("gap_analysis", {})
        })
    
    response = {
        "screening_id": screening_id,
        "total_candidates": len(candidates),
        "candidates": candidates
    }
    
    return response