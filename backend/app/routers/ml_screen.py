# backend/app/routers/ml_screen.py
from fastapi import APIRouter, UploadFile, File, Form, BackgroundTasks, HTTPException
from typing import List, Optional
import uuid
from datetime import datetime
import logging

from ..services.pdf_extractor import extract_text_from_pdf
from ..services.text_cleaner import clean_text
from ..services.section_extractor import extract_sections
from ..services.encoder import encode_to_vector
from ..services.similarity import compute_similarity_matrix
from ..services.scorer import weighted_score, compute_final_score
from ..services.gap_analyzer import analyze_gaps
from ..services.formatter import format_response
from ..services.batch_processor import BatchProcessor
from ..storage import screening_sessions, candidates as storage_candidates

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ml", tags=["ML Screening"])


async def process_single_cv(cv_data: dict, jd_text: str, jd_sections: dict) -> dict:
    """Proses satu CV (untuk batch)"""
    try:
        # Extract text from PDF
        raw_text = extract_text_from_pdf(cv_data["content"])
        
        # Clean text
        clean = clean_text(raw_text)
        
        # Extract sections
        cv_sections = extract_sections(clean)
        
        # Extract entities (nama, email)
        from ..services.entity_extractor import extract_all_entities
        entities = extract_all_entities(raw_text)
        
        # Encode to vector
        cv_vector = encode_to_vector(clean)
        
        return {
            "filename": cv_data["filename"],
            "name": entities.get("name", "Unknown"),
            "email": entities.get("email", ""),
            "raw_text": raw_text,
            "clean_text": clean,
            "sections": cv_sections,
            "vector": cv_vector,
            "entities": entities
        }
    except Exception as e:
        logger.error(f"Error processing CV {cv_data.get('filename', 'unknown')}: {e}")
        return {
            "filename": cv_data.get("filename", "unknown"),
            "name": "Error",
            "email": "",
            "error": str(e)
        }


async def process_batch_job(
    jd_text: str, 
    cv_list: List[dict], 
    weights: dict, 
    batch_size: int = 10
) -> List[dict]:
    """Proses batch screening (untuk background task)"""
    
    processor = BatchProcessor(batch_size=batch_size, max_concurrent=2)
    
    # Encode JD once
    clean_jd = clean_text(jd_text)
    jd_sections = extract_sections(clean_jd)
    jd_vector = encode_to_vector(clean_jd)
    
    async def process_batch(batch: List[dict]) -> List[dict]:
        """Proses satu batch CV"""
        batch_results = []
        for cv in batch:
            result = await process_single_cv(cv, jd_text, jd_sections)
            if "error" not in result:
                batch_results.append(result)
        
        if not batch_results:
            return []
        
        # Encode vectors for batch
        vectors = [r["vector"] for r in batch_results]
        
        # Compute similarities
        similarities = compute_similarity_matrix(jd_vector, vectors)
        
        # Update scores dengan weighted scoring
        for i, result in enumerate(batch_results):
            result["similarity_score"] = float(similarities[i])
            
            # Hitung final score dengan bobot dari parameter
            skill_score = result.get("similarity_score", 0)
            exp_score = result.get("similarity_score", 0)  # TODO: dari experience extractor
            edu_score = result.get("similarity_score", 0)  # TODO: dari education extractor
            
            final_score = compute_final_score(
                skill_score=skill_score,
                experience_score=exp_score,
                education_score=edu_score,
                projects_score=0.0,
                weights=weights
            )
            result["final_score"] = final_score
        
        return batch_results
    
    # Process all CVs in batches
    all_results = await processor.process_in_batches(
        items=cv_list,
        process_func=process_batch,
        on_progress=lambda batch, total, progress: logger.info(f"Progress: {progress:.1f}%")
    )
    
    # Apply gap analysis
    for result in all_results:
        if "error" not in result:
            try:
                gaps = analyze_gaps(result.get("sections", {}), jd_sections)
                result["gap_analysis"] = gaps
            except Exception as e:
                logger.error(f"Gap analysis failed: {e}")
                result["gap_analysis"] = {}
    
    return all_results


@router.post("/screen")
async def ml_screening(
    background_tasks: BackgroundTasks,
    job_description: str = Form(...),
    batch_size: int = Form(10),
    skill_weight: float = Form(0.5),
    experience_weight: float = Form(0.3),
    education_weight: float = Form(0.2),
    files: List[UploadFile] = File(...)
):
    """
    ML Pipeline Screening dengan Batch Processing.
    HR bisa mengatur bobot penilaian (skill, experience, education).
    """
    if not files:
        raise HTTPException(400, "Tidak ada file yang diupload")
    
    screening_id = str(uuid.uuid4())
    
    # Prepare CV list
    cv_list = []
    for file in files:
        content = await file.read()
        cv_list.append({
            "filename": file.filename,
            "content": content
        })
    
    weights = {
        "skills": skill_weight,
        "experience": experience_weight,
        "education": education_weight,
        "projects": 0.0
    }
    
    # Save session
    screening_sessions[screening_id] = {
        "id": screening_id,
        "job_description": job_description,
        "status": "processing",
        "total_cvs": len(cv_list),
        "batch_size": batch_size,
        "weights": weights,
        "created_at": datetime.now().isoformat()
    }
    
    # Start background processing
    background_tasks.add_task(
        process_and_save_results,
        screening_id,
        job_description,
        cv_list,
        weights,
        batch_size
    )
    
    return {
        "screening_id": screening_id,
        "status": "processing",
        "total_cvs": len(cv_list),
        "batch_size": batch_size,
        "weights": weights,
        "message": f"ML Pipeline started with batch size {batch_size}"
    }


async def process_and_save_results(
    screening_id: str, 
    jd_text: str, 
    cv_list: List[dict], 
    weights: dict, 
    batch_size: int
):
    """Background task: proses batch dan simpan hasil"""
    try:
        results = await process_batch_job(jd_text, cv_list, weights, batch_size)
        
        # Filter hasil yang error
        valid_results = [r for r in results if "error" not in r]
        
        # Sort by final score
        valid_results.sort(key=lambda x: x.get("final_score", 0), reverse=True)
        
        # Format response
        formatted = format_response(valid_results, screening_id)
        
        # Save to storage
        screening_sessions[screening_id]["status"] = "completed"
        screening_sessions[screening_id]["completed_at"] = datetime.now().isoformat()
        storage_candidates[screening_id] = formatted.get("candidates", [])
        
        logger.info(f"Screening {screening_id} completed, {len(valid_results)} candidates processed")
        
    except Exception as e:
        logger.error(f"Screening {screening_id} failed: {e}")
        screening_sessions[screening_id]["status"] = "failed"
        screening_sessions[screening_id]["error"] = str(e)


@router.get("/batch-info")
async def get_batch_info(total_cvs: int = 100, batch_size: int = 10):
    """Informasi tentang batch processing (untuk preview sebelum upload)"""
    processor = BatchProcessor(batch_size=batch_size)
    return processor.get_batch_info(total_cvs)


@router.get("/status/{screening_id}")
async def get_ml_screening_status(screening_id: str):
    """Cek status ML screening"""
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
async def get_ml_screening_result(screening_id: str):
    """Ambil hasil ML screening"""
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