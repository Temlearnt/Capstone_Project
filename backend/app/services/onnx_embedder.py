# backend/app/services/matching.py
import math
import numpy as np
from .entity_extractor import extract_all_entities
from .encoder import encode_to_vector, encode_batch, compute_similarity
import logging

logger = logging.getLogger(__name__)


def compute_match_score(cv_text: str, jd_text: str) -> float:
    """
    Compute match score between CV and Job Description menggunakan SBERT.
    Returns score between 0 and 1
    """
    if not cv_text or not jd_text:
        return 0.0
    
    try:
        # Gunakan SBERT similarity dari encoder.py
        score = compute_similarity(cv_text, jd_text)
        return min(1.0, max(0.0, score))
    except Exception as e:
        logger.error(f"SBERT similarity failed: {e}, falling back to keyword matching")
        return compute_keyword_match(cv_text, jd_text)


def compute_keyword_match(cv_text: str, jd_text: str) -> float:
    """
    Fallback: keyword matching sederhana (jika SBERT gagal)
    """
    jd_words = set(jd_text.lower().split())
    cv_words = set(cv_text.lower().split())
    
    if not jd_words:
        return 0.0
    
    match_count = len(jd_words.intersection(cv_words))
    return min(1.0, match_count / len(jd_words))


def compute_batch_scores(cv_texts: list, jd_text: str) -> list:
    """
    Compute scores for multiple CVs menggunakan SBERT batch processing
    """
    if not cv_texts:
        return []
    
    try:
        # Encode JD sekali
        jd_embedding = encode_to_vector(jd_text)
        
        # Encode semua CV
        cv_text_list = [cv["text"] for cv in cv_texts]
        cv_embeddings = encode_batch(cv_text_list)
        
        # Hitung similarity
        results = []
        for i, cv in enumerate(cv_texts):
            # Cosine similarity
            similarity = np.dot(jd_embedding, cv_embeddings[i]) / (
                np.linalg.norm(jd_embedding) * np.linalg.norm(cv_embeddings[i])
            )
            score = float(similarity)
            
            # Extract entities
            entities = extract_all_entities(cv["text"])
            
            results.append({
                "filename": cv["filename"],
                "name": entities.get("name", "Unknown"),
                "email": entities.get("email", ""),
                "phone": entities.get("phone", ""),
                "skills": entities.get("skills", []),
                "experience": entities.get("experience", {}).get("full_text", "") if isinstance(entities.get("experience"), dict) else entities.get("experience", ""),
                "education": entities.get("education", {}).get("full_text", "") if isinstance(entities.get("education"), dict) else entities.get("education", ""),
                "certifications": entities.get("certifications", []),
                "organizations": entities.get("organizations", []),
                "awards": entities.get("awards", []),
                "projects": entities.get("projects", []),
                "match_score": score,
                "skill_score": score,  # Bisa di-sesuaikan
            })
        
        return results
    
    except Exception as e:
        logger.error(f"Batch scoring failed: {e}, falling back to individual processing")
        # Fallback: proses satu per satu
        results = []
        for cv in cv_texts:
            score = compute_match_score(cv["text"], jd_text)
            entities = extract_all_entities(cv["text"])
            results.append({
                "filename": cv["filename"],
                "name": entities.get("name", "Unknown"),
                "email": entities.get("email", ""),
                "phone": entities.get("phone", ""),
                "skills": entities.get("skills", []),
                "experience": entities.get("experience", {}).get("full_text", "") if isinstance(entities.get("experience"), dict) else entities.get("experience", ""),
                "education": entities.get("education", {}).get("full_text", "") if isinstance(entities.get("education"), dict) else entities.get("education", ""),
                "match_score": score,
                "skill_score": score,
            })
        return results


def compute_advanced_match(
    cv_text: str, 
    jd_text: str, 
    cv_entities: dict = None,
    jd_skills: list = None,
    weights: dict = None
) -> dict:
    """
    Advanced matching dengan breakdown skor per komponen.
    """
    if weights is None:
        weights = {
            "semantic": 0.50,
            "skills": 0.30,
            "experience": 0.10,
            "education": 0.10
        }
    
    # 1. Semantic similarity (SBERT)
    semantic_score = compute_match_score(cv_text, jd_text)
    
    # 2. Skill match (jika ada data)
    skill_score = 0.0
    if cv_entities and jd_skills:
        cv_skills = set([s.lower() for s in cv_entities.get("skills", [])])
        jd_skills_set = set([s.lower() for s in jd_skills])
        if jd_skills_set:
            skill_score = len(cv_skills & jd_skills_set) / len(jd_skills_set)
    
    # 3. Experience score (dari entities)
    exp_score = 0.0
    if cv_entities:
        exp_data = cv_entities.get("experience", {})
        if isinstance(exp_data, dict):
            exp_years = exp_data.get("years", 0)
            exp_score = min(1.0, exp_years / 5)  # 5 tahun = perfect
    
    # 4. Education score
    edu_score = 0.0
    if cv_entities:
        edu_data = cv_entities.get("education", {})
        if isinstance(edu_data, dict):
            edu_level = edu_data.get("level", "").lower()
            edu_scores = {
                's3': 1.0, 'doktor': 1.0,
                's2': 0.8, 'magister': 0.8,
                's1': 0.6, 'sarjana': 0.6,
                'd4': 0.5, 'd3': 0.4,
                'sma': 0.2, 'smk': 0.2
            }
            edu_score = edu_scores.get(edu_level, 0.0)
    
    # 5. Final weighted score
    total_weight = sum(weights.values())
    final_score = (
        (weights.get("semantic", 0.5) / total_weight) * semantic_score +
        (weights.get("skills", 0.3) / total_weight) * skill_score +
        (weights.get("experience", 0.1) / total_weight) * exp_score +
        (weights.get("education", 0.1) / total_weight) * edu_score
    )
    
    return {
        "final_score": round(final_score, 3),
        "breakdown": {
            "semantic": round(semantic_score, 3),
            "skills": round(skill_score, 3),
            "experience": round(exp_score, 3),
            "education": round(edu_score, 3)
        }
    }