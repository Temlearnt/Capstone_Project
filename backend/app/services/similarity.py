# backend/app/services/similarity.py
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import logging

logger = logging.getLogger(__name__)

def compute_similarity_matrix(jd_vector: np.ndarray, cv_vectors: list) -> np.ndarray:
    """
    Hitung similarity matrix antara JD vector dan semua CV vectors.
    Output: array of scores (0-1)
    """
    # Validasi input
    if not cv_vectors:
        logger.warning("No CV vectors provided")
        return np.array([])
    
    if jd_vector is None or len(jd_vector) == 0:
        logger.warning("JD vector is empty")
        return np.zeros(len(cv_vectors))
    
    # Convert to 2D array
    try:
        cv_matrix = np.array(cv_vectors)
        jd_matrix = jd_vector.reshape(1, -1)
        
        # Cek dimensi
        if cv_matrix.shape[1] != jd_matrix.shape[1]:
            logger.error(f"Dimension mismatch: cv {cv_matrix.shape}, jd {jd_matrix.shape}")
            return np.zeros(len(cv_vectors))
        
        # Cosine similarity
        similarities = cosine_similarity(jd_matrix, cv_matrix)[0]
        
        # Normalisasi ke range 0-1 (cosine similarity sudah di range -1 to 1)
        similarities = np.clip(similarities, 0, 1)
        
        return similarities
    
    except Exception as e:
        logger.error(f"Similarity computation failed: {e}")
        return np.zeros(len(cv_vectors))


def compute_pairwise_similarity(vectors: np.ndarray) -> np.ndarray:
    """Hitung pairwise similarity matrix antar CV (untuk clustering)"""
    if vectors is None or len(vectors) == 0:
        return np.array([])
    
    try:
        similarity = cosine_similarity(vectors)
        return np.clip(similarity, 0, 1)
    except Exception as e:
        logger.error(f"Pairwise similarity failed: {e}")
        return np.array([])
        
def compute_similarity_batch(jd_vectors: np.ndarray, cv_vectors: np.ndarray) -> np.ndarray:
    """
    Hitung similarity matrix untuk multiple JD dan multiple CV.
    Output: matrix (n_jd, n_cv)
    """
    try:
        similarities = cosine_similarity(jd_vectors, cv_vectors)
        return np.clip(similarities, 0, 1)
    except Exception as e:
        logger.error(f"Batch similarity failed: {e}")
        return np.zeros((len(jd_vectors), len(cv_vectors)))