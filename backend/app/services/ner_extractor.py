# backend/app/services/ner_extractor.py
import onnxruntime as ort
import numpy as np
import re
from pathlib import Path
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)


class NERExtractor:
    """
    Named Entity Recognition menggunakan ONNX model.
    Mengekstrak: nama, email, nomor telepon, skill, pengalaman, pendidikan
    """
    
    def __init__(self, model_path: str = "models/ner_model_quantized.onnx"):
        self.model_path = Path(model_path)
        self.session = None
        self._load_model()
    
    def _load_model(self):
        """Load ONNX NER model"""
        if not self.model_path.exists():
            logger.warning(f"NER model not found at {self.model_path}, using regex fallback")
            self.session = None
            return
        
        # Load model with optimizations
        sess_options = ort.SessionOptions()
        sess_options.enable_cpu_mem_arena = True
        sess_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        
        self.session = ort.InferenceSession(
            str(self.model_path),
            sess_options,
            providers=['CPUExecutionProvider']
        )
        logger.info(f"NER ONNX model loaded from {self.model_path}")
    
    def extract_entities(self, text: str) -> Dict[str, Any]:
        """
        Ekstrak entities dari teks CV.
        Output: {
            "name": "...",
            "email": "...",
            "phone": "...",
            "skills": [...],
            "experience": "...",
            "education": "..."
        }
        """
        # Jika model ONNX tersedia, coba pakai
        if self.session is not None:
            try:
                return self._extract_with_onnx(text)
            except Exception as e:
                logger.warning(f"ONNX extraction failed: {e}, falling back to regex")
        
        # Fallback ke regex
        return self._extract_with_regex(text)
    
    def _extract_with_onnx(self, text: str) -> Dict[str, Any]:
        """Ekstraksi menggunakan ONNX model"""
        # Sesuaikan dengan format input model Anda
        # Asumsi model menerima tokenized input
        input_name = self.session.get_inputs()[0].name
        input_shape = self.session.get_inputs()[0].shape
        
        # Preprocessing (sesuai kebutuhan model)
        # Ini contoh sederhana, sesuaikan dengan model Anda
        tokens = text.split()[:512]  # Limit token
        # ... preprocessing sesuai model
        
        # Run inference
        # inputs = {input_name: ...}
        # outputs = self.session.run(None, inputs)
        
        # Parse output (sesuaikan dengan output model Anda)
        # entities = self._parse_outputs(outputs, tokens)
        
        # Sementara fallback ke regex
        logger.info("ONNX model loaded but output parsing not implemented, using regex")
        return self._extract_with_regex(text)
    
    def _extract_with_regex(self, text: str) -> dict:
    """Fallback extraction menggunakan regex"""
    from .entity_extractor import (
        extract_name, extract_email, extract_phone, extract_location,
        extract_skills, extract_experience, extract_education,
        extract_certifications, extract_organizations, extract_awards,
        extract_projects
    )
    
    return {
        "name": extract_name(text),
        "email": extract_email(text),
        "phone": extract_phone(text),
        "location": extract_location(text),
        "skills": extract_skills(text),
        "experience": extract_experience(text),
        "education": extract_education(text),
        "certifications": extract_certifications(text),
        "organizations": extract_organizations(text),
        "awards": extract_awards(text),
        "projects": extract_projects(text),
    } 
    
    def extract_batch(self, texts: List[str]) -> List[Dict[str, Any]]:
        """Ekstrak entities untuk banyak teks"""
        return [self.extract_entities(t) for t in texts]


# ============================================
# Singleton instance
# ============================================

_ner_extractor = None

def get_ner_extractor() -> NERExtractor:
    """Get singleton NERExtractor instance"""
    global _ner_extractor
    if _ner_extractor is None:
        _ner_extractor = NERExtractor()
    return _ner_extractor

# ============================================
# CONVENIENCE FUNCTIONS (untuk kompatibilitas)
# ============================================

def extract_name(text: str) -> str:
    """Ekstrak nama dari CV"""
    return get_ner_extractor().extract_entities(text).get("name", "Unknown")

def extract_email(text: str) -> str:
    """Ekstrak email dari CV"""
    return get_ner_extractor().extract_entities(text).get("email", "")

def extract_phone(text: str) -> str:
    """Ekstrak nomor telepon dari CV"""
    return get_ner_extractor().extract_entities(text).get("phone", "")

def extract_skills(text: str) -> list:
    """Ekstrak skills dari CV"""
    return get_ner_extractor().extract_entities(text).get("skills", [])

def extract_experience(text: str) -> str:
    """Ekstrak pengalaman dari CV"""
    return get_ner_extractor().extract_entities(text).get("experience", "")

def extract_education(text: str) -> str:
    """Ekstrak pendidikan dari CV"""
    return get_ner_extractor().extract_entities(text).get("education", "")

def extract_certifications(text: str) -> list:
    """Ekstrak sertifikasi dari CV"""
    return get_ner_extractor().extract_entities(text).get("certifications", [])

def extract_organizations(text: str) -> list:
    """Ekstrak organisasi dari CV"""
    return get_ner_extractor().extract_entities(text).get("organizations", [])

def extract_awards(text: str) -> list:
    """Ekstrak penghargaan dari CV"""
    return get_ner_extractor().extract_entities(text).get("awards", [])

def extract_projects(text: str) -> list:
    """Ekstrak proyek dari CV"""
    return get_ner_extractor().extract_entities(text).get("projects", [])

def extract_all_entities(text: str) -> dict:
    """Ekstrak semua entities dari CV"""
    return get_ner_extractor().extract_entities(text)