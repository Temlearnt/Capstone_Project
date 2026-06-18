# backend/app/services/onnx_ner.py
import onnxruntime as ort
import numpy as np
import re
from pathlib import Path
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class NERExtractor:
    """Named Entity Recognition menggunakan ONNX model"""
    
    # Mapping label ke entity type (sesuaikan dengan model Anda)
    LABEL_MAPPING = {
        'B-NAME': 'name', 'I-NAME': 'name',
        'B-EMAIL': 'email', 'I-EMAIL': 'email',
        'B-PHONE': 'phone', 'I-PHONE': 'phone',
        'B-SKILL': 'skill', 'I-SKILL': 'skill',
        'B-EXPERIENCE': 'experience', 'I-EXPERIENCE': 'experience',
        'B-EDUCATION': 'education', 'I-EDUCATION': 'education',
        'B-CERTIFICATION': 'certification', 'I-CERTIFICATION': 'certification',
        'B-ORG': 'organization', 'I-ORG': 'organization',
        'B-AWARD': 'award', 'I-AWARD': 'award',
        'B-PROJECT': 'project', 'I-PROJECT': 'project',
    }
    
    def __init__(self, model_path: str = "models/ner_model_quantized.onnx"):
        self.model_path = Path(model_path)
        self.session = None
        self._load_model()
    
    def _load_model(self):
        """Load ONNX model"""
        if not self.model_path.exists():
            logger.warning(f"NER model not found at {self.model_path}, using regex fallback")
            self.session = None
            return
        
        try:
            sess_options = ort.SessionOptions()
            sess_options.enable_cpu_mem_arena = True
            sess_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
            
            self.session = ort.InferenceSession(
                str(self.model_path),
                sess_options,
                providers=['CPUExecutionProvider']
            )
            logger.info(f"NER ONNX model loaded from {self.model_path}")
        except Exception as e:
            logger.error(f"Failed to load NER model: {e}")
            self.session = None
    
    def _tokenize(self, text: str, max_length: int = 512) -> Dict[str, np.ndarray]:
        """
        Tokenisasi teks untuk input model ONNX.
        Sesuaikan dengan tokenizer yang digunakan model Anda.
        """
        # Ini contoh sederhana - sesuaikan dengan model Anda
        # Model mungkin membutuhkan input_ids, attention_mask, token_type_ids
        
        # Split into characters or words (sesuai model)
        tokens = list(text[:max_length])
        token_ids = [ord(c) for c in tokens]  # Simple: convert char to int
        
        # Pad to max_length
        if len(token_ids) < max_length:
            token_ids += [0] * (max_length - len(token_ids))
        else:
            token_ids = token_ids[:max_length]
        
        return {
            "input_ids": np.array([token_ids], dtype=np.int64),
            "attention_mask": np.array([[1] * max_length], dtype=np.int64)
        }
    
    def _parse_outputs(self, outputs, tokens: List[str]) -> Dict[str, Any]:
        """
        Parse output model menjadi entities dictionary.
        Sesuaikan dengan format output model Anda.
        """
        entities = {
            "name": "",
            "email": "",
            "phone": "",
            "skills": [],
            "experience": "",
            "education": "",
            "certifications": [],
            "organizations": [],
            "awards": [],
            "projects": []
        }
        
        # Asumsi output: predictions (labels per token)
        # Sesuaikan index output dengan model Anda
        try:
            predictions = outputs[0][0]  # shape: (seq_len,)
            
            current_entity = None
            current_text = []
            
            for i, label_id in enumerate(predictions):
                label = self._get_label_from_id(int(label_id))
                entity_type = self.LABEL_MAPPING.get(label)
                
                if entity_type:
                    if label.startswith('B-'):  # Beginning of entity
                        # Save previous entity
                        if current_entity and current_text:
                            self._add_to_entities(entities, current_entity, ' '.join(current_text))
                        current_entity = entity_type
                        current_text = [tokens[i] if i < len(tokens) else '']
                    elif label.startswith('I-') and current_entity == entity_type:
                        # Inside entity
                        if i < len(tokens):
                            current_text.append(tokens[i])
                else:
                    # End of entity
                    if current_entity and current_text:
                        self._add_to_entities(entities, current_entity, ' '.join(current_text))
                    current_entity = None
                    current_text = []
            
            # Save last entity
            if current_entity and current_text:
                self._add_to_entities(entities, current_entity, ' '.join(current_text))
                
        except Exception as e:
            logger.warning(f"Failed to parse NER outputs: {e}")
        
        return entities
    
    def _get_label_from_id(self, label_id: int) -> str:
        """Mapping dari label ID ke string label"""
        # Sesuaikan dengan model Anda
        labels = [
            'O', 'B-NAME', 'I-NAME', 'B-EMAIL', 'I-EMAIL',
            'B-PHONE', 'I-PHONE', 'B-SKILL', 'I-SKILL',
            'B-EXPERIENCE', 'I-EXPERIENCE', 'B-EDUCATION', 'I-EDUCATION'
        ]
        return labels[label_id] if label_id < len(labels) else 'O'
    
    def _add_to_entities(self, entities: dict, entity_type: str, text: str):
        """Tambahkan entity ke dictionary sesuai tipenya"""
        text = text.strip()
        if not text:
            return
        
        if entity_type == 'name':
            entities['name'] = text
        elif entity_type == 'email':
            entities['email'] = text
        elif entity_type == 'phone':
            entities['phone'] = text
        elif entity_type == 'skill':
            entities['skills'].append(text)
        elif entity_type == 'experience':
            entities['experience'] += text + "\n"
        elif entity_type == 'education':
            entities['education'] += text + "\n"
        elif entity_type == 'certification':
            entities['certifications'].append(text)
        elif entity_type == 'organization':
            entities['organizations'].append(text)
        elif entity_type == 'award':
            entities['awards'].append(text)
        elif entity_type == 'project':
            entities['projects'].append(text)
    
    def extract_entities(self, text: str) -> dict:
        """
        Ekstrak entities dari teks menggunakan ONNX model.
        Output: dictionary lengkap entities.
        """
        # Jika model tidak tersedia, langsung fallback
        if self.session is None:
            return self._fallback_extract(text)
        
        try:
            # Tokenize input
            tokens = list(text[:512])  # Simple tokenization
            inputs = self._tokenize(text)
            
            # Run inference
            outputs = self.session.run(None, inputs)
            
            # Parse outputs
            entities = self._parse_outputs(outputs, tokens)
            
            # Validasi hasil
            if not entities.get('name') and not entities.get('skills'):
                logger.info("NER produced no entities, falling back to regex")
                return self._fallback_extract(text)
            
            return entities
            
        except Exception as e:
            logger.warning(f"ONNX NER failed: {e}, falling back to regex")
            return self._fallback_extract(text)
    
    def _fallback_extract(self, text: str) -> dict:
        """Fallback extraction menggunakan regex"""
        from .entity_extractor import extract_all_entities
        return extract_all_entities(text)
    
    def extract_batch(self, texts: List[str]) -> List[dict]:
        """Ekstrak entities untuk banyak teks"""
        return [self.extract_entities(t) for t in texts]


# Singleton instance
_ner_extractor = None


def get_ner_extractor() -> NERExtractor:
    """Get singleton NERExtractor instance"""
    global _ner_extractor
    if _ner_extractor is None:
        _ner_extractor = NERExtractor()
    return _ner_extractor


# Convenience functions
def extract_entities(text: str) -> dict:
    """Ekstrak entities dari teks (convenience function)"""
    return get_ner_extractor().extract_entities(text)