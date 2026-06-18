# backend/app/services/encoder.py
import numpy as np
import onnxruntime as ort
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# Global session (load sekali)
_sbert_session = None

def load_sbert_model(model_path: str = "models/sbert_embedding_quantized.onnx"):
    """Load SBERT ONNX model"""
    global _sbert_session
    if _sbert_session is None:
        model_path = Path(model_path)
        if not model_path.exists():
            raise FileNotFoundError(f"SBERT model not found at {model_path}")
        
        sess_options = ort.SessionOptions()
        sess_options.enable_cpu_mem_arena = True
        sess_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        
        _sbert_session = ort.InferenceSession(
            str(model_path),
            sess_options,
            providers=['CPUExecutionProvider']
        )
        logger.info(f"SBERT ONNX model loaded from {model_path}")
    return _sbert_session

def encode_to_vector(text: str) -> np.ndarray:
    """Encode teks ke vektor menggunakan SBERT ONNX"""
    if not text or not text.strip():
        logger.warning("Empty text provided to encode_to_vector")
        return np.zeros(384)  # Return zero vector (sesuaikan dimensi)
    
    try:
        session = load_sbert_model()
        input_name = session.get_inputs()[0].name
        inputs = {input_name: [text]}
        output = session.run(None, inputs)
        return output[0][0]
    except Exception as e:
        logger.error(f"SBERT encoding failed: {e}")
        return np.zeros(384)  # Fallback zero vector

def encode_batch(texts: list) -> np.ndarray:
    """Encode banyak teks sekaligus"""
    session = load_sbert_model()
    input_name = session.get_inputs()[0].name
    
    embeddings = []
    for text in texts:
        inputs = {input_name: [text]}
        output = session.run(None, inputs)
        embeddings.append(output[0][0])
    
    return np.array(embeddings)

def compute_similarity(text1: str, text2: str) -> float:
    """Hitung cosine similarity antara dua teks"""
    emb1 = encode_to_vector(text1)
    emb2 = encode_to_vector(text2)
    
    similarity = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
    return float(similarity)