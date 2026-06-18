from fastapi import APIRouter, UploadFile, File, Form, BackgroundTasks, HTTPException
import uuid
import os
from ..services.pdf_extractor import extract_text_from_pdf
from ..storage import create_screening_session, update_screening_status, save_candidates
from ..services.matching import compute_batch_scores
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/")
async def upload_cvs(
    background_tasks: BackgroundTasks,
    job_description: str = Form(...),
    employment_type: str = Form("fulltime"),
    files: list[UploadFile] = File(...)
):
    # Validasi file
    if not files:
        raise HTTPException(400, "No files uploaded")
    
    # Filter hanya file PDF
    pdf_files = [f for f in files if f.filename.lower().endswith('.pdf')]
    if not pdf_files:
        raise HTTPException(400, "No PDF files found")
    
    # Buat screening session
    screening_id = str(uuid.uuid4())
    create_screening_session(screening_id, job_description, employment_type)
    
    # Ekstrak teks dari PDF
    cv_texts = []
    for file in pdf_files:
        try:
            content = await file.read()
            text = extract_text_from_pdf(content)
            cv_texts.append({
                "filename": file.filename,
                "text": text
            })
        except Exception as e:
            logger.error(f"Error processing {file.filename}: {e}")
    
    update_screening_status(screening_id, "processing", len(cv_texts))
    
    # Proses screening di background
    background_tasks.add_task(
        process_screening,
        screening_id,
        job_description,
        employment_type,
        cv_texts
    )
    
    return {
        "screening_id": screening_id,
        "status": "processing",
        "total_cvs": len(cv_texts),
        "message": f"Processing {len(cv_texts)} CVs"
    }

async def process_screening(screening_id: str, jd_text: str, emp_type: str, cv_texts: list):
    """Background task untuk screening CV"""
    logger.info(f"Processing screening {screening_id} with {len(cv_texts)} CVs")
    
    # Hitung skor untuk semua CV
    results = compute_batch_scores(cv_texts, jd_text, emp_type)
    
    # Urutkan berdasarkan skor
    results.sort(key=lambda x: x["match_score"], reverse=True)
    
    # Tambahkan peringkat
    for i, candidate in enumerate(results, 1):
        candidate["rank"] = i
    
    # Simpan hasil
    save_candidates(screening_id, results)
    
    logger.info(f"Screening {screening_id} completed")