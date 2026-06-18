# backend/app/routers/onnx_screen.py
from fastapi import APIRouter, UploadFile, File, Form, BackgroundTasks, HTTPException
from typing import List
import uuid
from datetime import datetime
import numpy as np
import logging

from ..services.pdf_extractor import extract_text_from_pdf
from ..services.onnx_embedder import get_embedder
from ..services.onnx_ner import get_ner_extractor
from ..services.batch_processor import BatchProcessor
from ..storage import screening_sessions, candidates as storage_candidates

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/onnx", tags=["ONNX Screening"])


@router.post("/screen")
async def onnx_screening(
    background_tasks: BackgroundTasks,
    job_description: str = Form(...),
    batch_size: int = Form(10),
    files: List[UploadFile] = File(...)
):
    """
    Screening menggunakan SBERT ONNX untuk embedding.
    Lebih cepat dan efisien daripada TF-IDF.
    """
    if not files:
        raise HTTPException(400, "Tidak ada file yang diupload")
    
    screening_id = str(uuid.uuid4())
    
    # Ekstrak teks dari semua PDF
    cv_texts = []
    for file in files:
        try:
            content = await file.read()
            text = extract_text_from_pdf(content)
            if text.strip():
                cv_texts.append({
                    "filename": file.filename,
                    "text": text
                })
            else:
                logger.warning(f"Empty text extracted from {file.filename}")
        except Exception as e:
            logger.error(f"Failed to extract text from {file.filename}: {e}")
    
    if not cv_texts:
        raise HTTPException(400, "Tidak ada file PDF yang valid")
    
    # Simpan sesi
    screening_sessions[screening_id] = {
        "id": screening_id,
        "job_description": job_description,
        "status": "processing",
        "total_cvs": len(cv_texts),
        "batch_size": batch_size,
        "created_at": datetime.now().isoformat(),
        "progress": 0
    }
    
    # Proses di background dengan ONNX
    background_tasks.add_task(
        process_with_onnx,
        screening_id,
        job_description,
        cv_texts,
        batch_size
    )
    
    return {
        "screening_id": screening_id,
        "status": "processing",
        "total_cvs": len(cv_texts),
        "batch_size": batch_size,
        "model": "SBERT ONNX (quantized)"
    }


@router.post("/screen/async")
async def onnx_screening_async(
    job_description: str = Form(...),
    batch_size: int = Form(10),
    files: List[UploadFile] = File(...)
):
    """
    Screening async - langsung return screening_id tanpa background task.
    Client harus polling ke /status/{id} dan /result/{id}
    """
    if not files:
        raise HTTPException(400, "Tidak ada file yang diupload")
    
    screening_id = str(uuid.uuid4())
    
    # Ekstrak teks dari semua PDF
    cv_texts = []
    for file in files:
        content = await file.read()
        text = extract_text_from_pdf(content)
        if text.strip():
            cv_texts.append({
                "filename": file.filename,
                "text": text
            })
    
    # Simpan sesi
    screening_sessions[screening_id] = {
        "id": screening_id,
        "job_description": job_description,
        "status": "pending",
        "total_cvs": len(cv_texts),
        "batch_size": batch_size,
        "created_at": datetime.now().isoformat()
    }
    
    return {
        "screening_id": screening_id,
        "status": "pending",
        "total_cvs": len(cv_texts),
        "message": "Silakan cek status menggunakan /onnx/status/{screening_id}"
    }


async def process_with_onnx(screening_id: str, jd_text: str, cv_texts: list, batch_size: int):
    """Proses screening dengan ONNX models"""
    try:
        embedder = get_embedder()
        ner_extractor = get_ner_extractor()
        
        # Update status
        screening_sessions[screening_id]["status"] = "processing"
        
        # 1. Encode JD sekali
        jd_embedding = embedder.encode_single(jd_text)
        
        # 2. Proses CV dalam batch
        processor = BatchProcessor(batch_size=batch_size)
        batches = processor.split_into_batches(cv_texts)
        
        all_results = []
        
        for batch_idx, batch in enumerate(batches):
            batch_texts = [cv["text"] for cv in batch]
            
            # Encode semua teks dalam batch
            cv_embeddings = embedder.encode(batch_texts)
            
            # Hitung similarity
            for i, cv in enumerate(batch):
                # Cosine similarity
                norm_jd = np.linalg.norm(jd_embedding)
                norm_cv = np.linalg.norm(cv_embeddings[i])
                
                if norm_jd > 0 and norm_cv > 0:
                    similarity = np.dot(jd_embedding, cv_embeddings[i]) / (norm_jd * norm_cv)
                else:
                    similarity = 0.0
                
                # Ekstrak entities dengan NER ONNX
                try:
                    entities = ner_extractor.extract_entities(cv["text"])
                except Exception as e:
                    logger.error(f"NER extraction failed for {cv['filename']}: {e}")
                    entities = {}
                
                all_results.append({
                    "filename": cv["filename"],
                    "name": entities.get("name", "Unknown"),
                    "email": entities.get("email", ""),
                    "skills": entities.get("skills", []),
                    "certifications": entities.get("certifications", []),
                    "organizations": entities.get("organizations", []),
                    "match_score": float(similarity),
                    "rank": 0
                })
            
            # Update progress
            progress = int(((batch_idx + 1) / len(batches)) * 100)
            screening_sessions[screening_id]["progress"] = progress
            logger.info(f"Screening {screening_id} progress: {progress}%")
        
        # Sorting dan ranking
        all_results.sort(key=lambda x: x["match_score"], reverse=True)
        for i, result in enumerate(all_results, 1):
            result["rank"] = i
        
        # Simpan hasil
        screening_sessions[screening_id]["status"] = "completed"
        screening_sessions[screening_id]["completed_at"] = datetime.now().isoformat()
        storage_candidates[screening_id] = all_results
        
        logger.info(f"Screening {screening_id} completed, {len(all_results)} candidates processed")
        
    except Exception as e:
        logger.error(f"Screening {screening_id} failed: {e}")
        screening_sessions[screening_id]["status"] = "failed"
        screening_sessions[screening_id]["error"] = str(e)


@router.get("/status/{screening_id}")
async def get_onnx_status(screening_id: str):
    """Cek status screening ONNX"""
    session = screening_sessions.get(screening_id)
    if not session:
        raise HTTPException(404, "Screening tidak ditemukan")
    
    return {
        "screening_id": screening_id,
        "status": session.get("status"),
        "total_cvs": session.get("total_cvs", 0),
        "progress": session.get("progress", 0),
        "created_at": session.get("created_at"),
        "completed_at": session.get("completed_at"),
        "error": session.get("error")
    }


@router.get("/result/{screening_id}")
async def get_onnx_result(screening_id: str):
    """Ambil hasil screening ONNX"""
    session = screening_sessions.get(screening_id)
    if not session:
        raise HTTPException(404, "Screening tidak ditemukan")
    
    candidates = storage_candidates.get(screening_id, [])
    
    return {
        "screening_id": screening_id,
        "job_description": session.get("job_description"),
        "status": session.get("status"),
        "total_cvs": session.get("total_cvs", 0),
        "candidates": candidates
    }


@router.post("/ner/extract")
async def extract_entities_from_text(
    text: str = Form(...)
):
    """Test endpoint untuk ekstraksi entities dengan NER ONNX"""
    ner = get_ner_extractor()
    entities = ner.extract_entities(text)
    return entities


@router.post("/similarity")
async def compute_similarity(
    text1: str = Form(...),
    text2: str = Form(...)
):
    """Hitung similarity antara dua teks menggunakan SBERT ONNX"""
    try:
        embedder = get_embedder()
        similarity = embedder.compute_similarity(text1, text2)
        return {
            "similarity": similarity,
            "percentage": round(similarity * 100, 2),
            "text1": text1[:100],
            "text2": text2[:100]
        }
    except Exception as e:
        logger.error(f"Similarity computation failed: {e}")
        raise HTTPException(500, f"Similarity computation failed: {e}")