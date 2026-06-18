# backend/app/services/scorer.py
import numpy as np
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


def weighted_score(
    similarity_scores: np.ndarray, 
    weights: Dict[str, float] = None,
    feature_names: list = None
) -> np.ndarray:
    """
    Hitung weighted score dari similarity scores.
    
    Args:
        similarity_scores: Array 1D atau 2D dari similarity scores
        weights: Dictionary bobot {"skills": 0.5, "experience": 0.3, "education": 0.2}
        feature_names: List nama fitur (jika similarity_scores 2D)
    
    Returns:
        Array 1D dari weighted scores (range 0-1)
    """
    # Default weights
    if weights is None:
        weights = {
            "skills": 0.50,
            "experience": 0.25,
            "education": 0.15,
            "projects": 0.10
        }
    
    # Jika input kosong
    if similarity_scores is None or len(similarity_scores) == 0:
        logger.warning("Empty similarity scores")
        return np.array([])
    
    # Jika 1D, langsung return (asumsikan sudah weighted)
    if similarity_scores.ndim == 1:
        return np.clip(similarity_scores, 0, 1)
    
    # Jika 2D, hitung weighted average
    total_weight = sum(weights.values())
    if total_weight == 0:
        total_weight = 1
    
    # Pastikan jumlah kolom sesuai dengan jumlah weight
    n_features = similarity_scores.shape[1]
    weight_values = list(weights.values())
    
    if len(weight_values) != n_features:
        logger.warning(f"Weight count ({len(weight_values)}) != features ({n_features}), using first {min(len(weight_values), n_features)}")
        weight_values = weight_values[:n_features]
    
    # Normalisasi weights
    normalized_weights = [w / total_weight for w in weight_values]
    
    # Hitung weighted score
    scores = np.zeros(similarity_scores.shape[0])
    for i, w in enumerate(normalized_weights):
        if i < similarity_scores.shape[1]:
            scores += w * similarity_scores[:, i]
    
    # Clip to range 0-1
    return np.clip(scores, 0, 1)


def compute_final_score(
    skill_score: float,
    experience_score: float,
    education_score: float,
    projects_score: float = 0.0,
    weights: Dict[str, float] = None
) -> float:
    """
    Hitung final score dari berbagai komponen.
    
    Args:
        skill_score: Skor skills (0-1)
        experience_score: Skor pengalaman (0-1)
        education_score: Skor pendidikan (0-1)
        projects_score: Skor proyek (0-1)
        weights: Bobot masing-masing komponen
    
    Returns:
        Final score (0-1)
    """
    if weights is None:
        weights = {
            "skills": 0.50,
            "experience": 0.25,
            "education": 0.15,
            "projects": 0.10
        }
    
    total_weight = sum(weights.values())
    if total_weight == 0:
        total_weight = 1
    
    final_score = (
        (weights.get("skills", 0) / total_weight) * skill_score +
        (weights.get("experience", 0) / total_weight) * experience_score +
        (weights.get("education", 0) / total_weight) * education_score +
        (weights.get("projects", 0) / total_weight) * projects_score
    )
    
    return min(1.0, max(0.0, final_score))


def normalize_scores(scores: np.ndarray) -> np.ndarray:
    """Normalisasi scores ke range 0-1 (min-max normalization)"""
    if len(scores) == 0:
        return scores
    
    min_score = np.min(scores)
    max_score = np.max(scores)
    
    if max_score == min_score:
        return np.ones_like(scores) * 0.5
    
    return (scores - min_score) / (max_score - min_score)