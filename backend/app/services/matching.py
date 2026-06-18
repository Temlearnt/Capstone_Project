import math
from .entity_extractor import extract_all_entities
import logging

logger = logging.getLogger(__name__)

def compute_match_score(cv_text: str, jd_text: str, employment_type: str = "fulltime") -> float:
    """
    Compute match score between CV and Job Description
    Returns score between 0 and 1
    """
    if not cv_text or not jd_text:
        return 0.0
    
    # Dummy: hitung berdasarkan keyword matching
    jd_words = set(jd_text.lower().split())
    cv_words = set(cv_text.lower().split())
    
    if not jd_words:
        return 0.0
    
    match_count = len(jd_words.intersection(cv_words))
    score = match_count / len(jd_words)
    
    # Batasi ke range 0-1
    return min(1.0, score)

def compute_batch_scores(cv_texts: list, jd_text: str, employment_type: str = "fulltime") -> list:
    """Compute scores for multiple CVs"""
    results = []
    
    for cv in cv_texts:
        score = compute_match_score(cv["text"], jd_text, employment_type)
        
        # Extract entities
        entities = extract_all_entities(cv["text"])
        
        results.append({
            "filename": cv["filename"],
            "name": entities.get("name", "Unknown"),
            "email": entities.get("email", ""),
            "phone": entities.get("phone", ""),
            "skills": entities.get("skills", []),
            "experience": entities.get("experience", ""),
            "education": entities.get("education", ""),
            "employment_preferences": entities.get("employment_preferences", []),
            "match_score": score,
            "skill_score": score * 0.8,  # dummy
            "employment_score": 0.5  # dummy
        })
    
    return results