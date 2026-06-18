# backend/app/routers/screen.py
from fastapi import APIRouter, UploadFile, File, Form, BackgroundTasks, HTTPException, Depends
from typing import List, Optional
import uuid
import os
import tempfile
import shutil
import logging
import json
from datetime import datetime

from ..services.pdf_extractor import extract_text_from_pdf
from ..services.matching import compute_match_score
from ..services.entity_extractor import extract_all_entities
from ..storage import screening_sessions, candidates as storage_candidates
from ..db.operations import save_candidates, create_screening_session, update_screening_status
from ..db.supabase_client import get_supabase
from ..utils.auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()


# ============================================
# HELPER FUNCTIONS
# ============================================

def process_zip_file(zip_bytes: bytes) -> List[dict]:
    """Ekstrak ZIP dan ambil semua PDF di dalamnya"""
    import zipfile
    pdf_files = []
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tmp:
        tmp.write(zip_bytes)
        tmp_path = tmp.name
    
    extract_dir = tempfile.mkdtemp()
    try:
        with zipfile.ZipFile(tmp_path, 'r') as zf:
            zf.extractall(extract_dir)
        
        for root, dirs, files in os.walk(extract_dir):
            for file in files:
                if file.lower().endswith('.pdf'):
                    full_path = os.path.join(root, file)
                    with open(full_path, 'rb') as f:
                        pdf_content = f.read()
                    pdf_files.append({
                        "filename": file,
                        "content": pdf_content
                    })
        return pdf_files
    except Exception as e:
        logger.error(f"Error extracting ZIP: {e}")
        return []
    finally:
        try:
            os.unlink(tmp_path)
            shutil.rmtree(extract_dir, ignore_errors=True)
        except Exception as e:
            logger.warning(f"Error cleaning up temp files: {e}")


async def process_screening_background(screening_id: str, jd_text: str, cv_texts: list):
    """Background task untuk memproses screening (bobot default)"""
    try:
        logger.info(f"Starting background processing for screening {screening_id}, {len(cv_texts)} CVs")
        results = []
        total = len(cv_texts)
        
        for idx, cv in enumerate(cv_texts):
            logger.debug(f"Processing CV {idx+1}/{total}: {cv['filename']}")
            
            # Hitung skor
            score = compute_match_score(cv["text"], jd_text)
            
            # Ekstrak entities
            entities = extract_all_entities(cv["text"])
            
            # Update progress (hanya di memory, karena di background)
            if screening_id in screening_sessions:
                progress = int(((idx + 1) / total) * 100)
                screening_sessions[screening_id]["progress"] = progress
            
            results.append({
                "filename": cv["filename"],
                "name": entities.get("name", "Unknown"),
                "email": entities.get("email", ""),
                "skills": entities.get("skills", []),
                "experience": entities.get("experience", ""),
                "education": entities.get("education", ""),
                "match_score": score,
                "rank": 0,
                "score_breakdown": {
                    "skills": score,
                    "experience": score,
                    "education": score
                }
            })
        
        # Urutkan berdasarkan skor
        results.sort(key=lambda x: x["match_score"], reverse=True)
        
        # Tambahkan rank
        for i, candidate in enumerate(results, 1):
            candidate["rank"] = i
        
        # ============ SAVE TO SUPABASE ============
        update_screening_status(screening_id, "completed", len(results), 100)
        saved = save_candidates(screening_id, results)
        
        if saved:
            logger.info(f"✅ Saved {len(saved)} candidates to Supabase")
        else:
            logger.warning(f"⚠️ Failed to save candidates to Supabase")
        
        # Simpan ke storage (in-memory backup)
        if screening_id in screening_sessions:
            screening_sessions[screening_id]["status"] = "completed"
            screening_sessions[screening_id]["completed_at"] = datetime.now().isoformat()
            screening_sessions[screening_id]["progress"] = 100
            storage_candidates[screening_id] = results
        
        logger.info(f"Screening {screening_id} completed, {len(results)} candidates processed")
        
    except Exception as e:
        logger.error(f"Screening {screening_id} failed: {e}")
        if screening_id in screening_sessions:
            screening_sessions[screening_id]["status"] = "failed"
            screening_sessions[screening_id]["error"] = str(e)
        update_screening_status(screening_id, "failed")


async def process_weighted_screening_background(
    screening_id: str, 
    jd_text: str, 
    cv_texts: list,
    weights: dict
):
    """Background task untuk weighted screening"""
    try:
        logger.info(f"Starting weighted screening {screening_id}, weights: {weights}")
        results = []
        total = len(cv_texts)
        
        for idx, cv in enumerate(cv_texts):
            logger.debug(f"Processing CV {idx+1}/{total}: {cv['filename']}")
            
            # Hitung skor dasar
            base_score = compute_match_score(cv["text"], jd_text)
            
            # Ekstrak entities
            entities = extract_all_entities(cv["text"])
            
            # Simulasi breakdown (nanti bisa diganti dengan model terpisah)
            # Idealnya: skill_score, experience_score, education_score dari model berbeda
            skill_score = base_score
            experience_score = base_score
            education_score = base_score
            
            # Weighted final score
            final_score = (
                weights.get("skills", 0.4) * skill_score +
                weights.get("experience", 0.3) * experience_score +
                weights.get("education", 0.3) * education_score
            )
            
            # Update progress
            if screening_id in screening_sessions:
                progress = int(((idx + 1) / total) * 100)
                screening_sessions[screening_id]["progress"] = progress
            
            results.append({
                "filename": cv["filename"],
                "name": entities.get("name", "Unknown"),
                "email": entities.get("email", ""),
                "skills": entities.get("skills", []),
                "experience": entities.get("experience", ""),
                "education": entities.get("education", ""),
                "match_score": final_score,
                "rank": 0,
                "score_breakdown": {
                    "skills": skill_score,
                    "experience": experience_score,
                    "education": education_score
                }
            })
        
        # Urutkan berdasarkan skor
        results.sort(key=lambda x: x["match_score"], reverse=True)
        
        # Tambahkan rank
        for i, candidate in enumerate(results, 1):
            candidate["rank"] = i
        
        # Simpan ke database
        update_screening_status(screening_id, "completed", len(results), 100)
        saved = save_candidates(screening_id, results)
        
        if saved:
            logger.info(f"✅ Saved {len(saved)} weighted candidates to Supabase")
        else:
            logger.warning(f"⚠️ Failed to save weighted candidates to Supabase")
        
        # Simpan ke memory
        if screening_id in screening_sessions:
            screening_sessions[screening_id]["status"] = "completed"
            screening_sessions[screening_id]["completed_at"] = datetime.now().isoformat()
            screening_sessions[screening_id]["progress"] = 100
            storage_candidates[screening_id] = results
        
        logger.info(f"Weighted screening {screening_id} completed, {len(results)} candidates")
        
    except Exception as e:
        logger.error(f"Weighted screening {screening_id} failed: {e}")
        if screening_id in screening_sessions:
            screening_sessions[screening_id]["status"] = "failed"
            screening_sessions[screening_id]["error"] = str(e)
        update_screening_status(screening_id, "failed")


# ============================================
# ENDPOINTS
# ============================================

@router.post("/")
async def create_screening(
    background_tasks: BackgroundTasks,
    job_description: str = Form(...),
    files: List[UploadFile] = File(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Mulai screening CV baru (bobot default: skills 40%, experience 30%, education 30%)
    Upload file PDF atau ZIP, masukkan job description.
    """
    if not files:
        raise HTTPException(400, "Tidak ada file yang diupload")
    
    user_id = current_user["user_id"]
    company_id = current_user["company_id"]
    logger.info(f"User {current_user['email']} from company {company_id}")
    
    # Buat screening session di Supabase
    session = create_screening_session(
        company_id=company_id,
        user_id=user_id,
        job_description=job_description,
        job_role_id=None,
        custom_skills=None
    )
    
    if not session:
        logger.error("Failed to create screening session in Supabase")
        raise HTTPException(500, "Gagal membuat sesi screening")
    
    screening_id = session.get("id")
    logger.info(f"✅ Screening session created: {screening_id}")
    
    # Proses file
    cv_texts = []
    for file in files:
        try:
            content = await file.read()
            filename = file.filename.lower()
            
            if filename.endswith('.pdf'):
                text = extract_text_from_pdf(content)
                if text.strip():
                    cv_texts.append({
                        "filename": file.filename,
                        "text": text
                    })
            elif filename.endswith('.zip'):
                extracted = process_zip_file(content)
                for pdf in extracted:
                    text = extract_text_from_pdf(pdf["content"])
                    if text.strip():
                        cv_texts.append({
                            "filename": pdf["filename"],
                            "text": text
                        })
        except Exception as e:
            logger.error(f"Error processing file {file.filename}: {e}")
    
    if not cv_texts:
        raise HTTPException(400, "Tidak ada file PDF yang valid ditemukan")
    
    # Update total_cvs
    update_screening_status(screening_id, "processing", len(cv_texts), 0)
    
    # Simpan ke memory
    screening_sessions[screening_id] = {
        "id": screening_id,
        "job_description": job_description,
        "status": "processing",
        "total_cvs": len(cv_texts),
        "progress": 0,
        "created_at": datetime.now().isoformat(),
        "completed_at": None
    }
    
    # Jalankan background task
    background_tasks.add_task(
        process_screening_background,
        screening_id,
        job_description,
        cv_texts
    )
    
    return {
        "screening_id": screening_id,
        "status": "processing",
        "total_cvs": len(cv_texts),
        "message": f"Memproses {len(cv_texts)} CV"
    }


@router.post("/weighted")
async def create_weighted_screening(
    background_tasks: BackgroundTasks,
    job_description: str = Form(...),
    files: List[UploadFile] = File(...),
    weights: str = Form('{"skills": 40, "experience": 30, "education": 30}'),
    job_role_id: Optional[str] = Form(None),
    current_user: dict = Depends(get_current_user)
):
    """
    Screening CV dengan bobot kustom yang bisa diatur HR.
    
    Bobot bisa diatur bebas (0-100) tanpa harus total 100%.
    Contoh weights: {"skills": 50, "experience": 25, "education": 25}
    """
    if not files:
        raise HTTPException(400, "Tidak ada file yang diupload")
    
    # Parse weights
    try:
        weights_dict = json.loads(weights)
        # Validasi keys
        if "skills" not in weights_dict:
            weights_dict["skills"] = 40
        if "experience" not in weights_dict:
            weights_dict["experience"] = 30
        if "education" not in weights_dict:
            weights_dict["education"] = 30
        
        # Normalisasi ke 0-1
        total = sum(weights_dict.values())
        if total > 0:
            weights_dict = {k: v / total for k, v in weights_dict.items()}
    except:
        weights_dict = {"skills": 0.4, "experience": 0.3, "education": 0.3}
    
    user_id = current_user["user_id"]
    company_id = current_user["company_id"]
    logger.info(f"Weighted screening by {current_user['email']}, weights: {weights_dict}")
    
    # Buat screening session
    session = create_screening_session(
        company_id=company_id,
        user_id=user_id,
        job_description=job_description,
        job_role_id=job_role_id,
        custom_skills=None
    )
    
    if not session:
        raise HTTPException(500, "Gagal membuat sesi screening")
    
    screening_id = session.get("id")
    
    # Update weights di database
    supabase = get_supabase()
    supabase.table("screening_sessions")\
        .update({"weights": weights_dict})\
        .eq("id", screening_id)\
        .execute()
    
    # Proses file
    cv_texts = []
    for file in files:
        try:
            content = await file.read()
            filename = file.filename.lower()
            
            if filename.endswith('.pdf'):
                text = extract_text_from_pdf(content)
                if text.strip():
                    cv_texts.append({
                        "filename": file.filename,
                        "text": text
                    })
            elif filename.endswith('.zip'):
                extracted = process_zip_file(content)
                for pdf in extracted:
                    text = extract_text_from_pdf(pdf["content"])
                    if text.strip():
                        cv_texts.append({
                            "filename": pdf["filename"],
                            "text": text
                        })
        except Exception as e:
            logger.error(f"Error processing file {file.filename}: {e}")
    
    if not cv_texts:
        raise HTTPException(400, "Tidak ada file PDF yang valid ditemukan")
    
    update_screening_status(screening_id, "processing", len(cv_texts), 0)
    
    # Simpan ke memory
    screening_sessions[screening_id] = {
        "id": screening_id,
        "job_description": job_description,
        "status": "processing",
        "total_cvs": len(cv_texts),
        "progress": 0,
        "weights": weights_dict,
        "created_at": datetime.now().isoformat(),
        "completed_at": None
    }
    
    # Jalankan background task dengan weights
    background_tasks.add_task(
        process_weighted_screening_background,
        screening_id,
        job_description,
        cv_texts,
        weights_dict
    )
    
    return {
        "screening_id": screening_id,
        "status": "processing",
        "total_cvs": len(cv_texts),
        "weights": {k: round(v * 100, 1) for k, v in weights_dict.items()},
        "message": f"Memproses {len(cv_texts)} CV dengan bobot kustom"
    }


@router.get("/{screening_id}/status")
async def get_screening_status(screening_id: str):
    """Cek status screening"""
    session = screening_sessions.get(screening_id)
    if not session:
        from ..db.operations import get_screening_session
        session = get_screening_session(screening_id)
        if not session:
            raise HTTPException(404, "Screening tidak ditemukan")
    
    return {
        "screening_id": screening_id,
        "status": session.get("status"),
        "total_cvs": session.get("total_cvs", 0),
        "progress": session.get("progress", 0),
        "created_at": session.get("created_at"),
        "completed_at": session.get("completed_at"),
        "error": session.get("error"),
        "weights": session.get("weights")
    }


@router.get("/{screening_id}/result")
async def get_screening_result(screening_id: str):
    """Ambil hasil ranking kandidat"""
    candidates = storage_candidates.get(screening_id, [])
    
    if not candidates:
        from ..db.operations import get_candidates_by_screening
        db_candidates = get_candidates_by_screening(screening_id)
        if db_candidates:
            candidates = db_candidates
    
    session = screening_sessions.get(screening_id)
    if not session:
        from ..db.operations import get_screening_session
        session = get_screening_session(screening_id)
        if not session:
            raise HTTPException(404, "Screening tidak ditemukan")
    
    return {
        "screening_id": screening_id,
        "job_description": session.get("job_description"),
        "status": session.get("status"),
        "total_cvs": len(candidates),
        "weights": session.get("weights"),
        "candidates": [
            {
                "rank": c.get("rank", i+1),
                "name": c.get("name", "Unknown"),
                "email": c.get("email", ""),
                "skills": c.get("skills", [])[:10],
                "experience": c.get("experience", "")[:300],
                "education": c.get("education", "")[:200],
                "match_score": round(c.get("match_score", 0) * 100, 1),
                "score_breakdown": c.get("score_breakdown", {}),
                "filename": c.get("filename") or c.get("original_filename", "")
            }
            for i, c in enumerate(candidates)
        ]
    }


@router.get("/history")
async def get_screening_history(
    limit: int = 20,
    current_user: dict = Depends(get_current_user)
):
    """Riwayat screening untuk user yang login"""
    from ..db.operations import get_user_screening_sessions
    
    sessions = get_user_screening_sessions(current_user["user_id"], limit)
    
    return {
        "total": len(sessions),
        "screenings": [
            {
                "id": s.get("id"),
                "job_description": (s.get("job_description", "")[:100] + "...") if len(s.get("job_description", "")) > 100 else s.get("job_description", ""),
                "status": s.get("status"),
                "total_cvs": s.get("total_cvs", 0),
                "weights": s.get("weights"),
                "created_at": s.get("created_at"),
                "completed_at": s.get("completed_at")
            }
            for s in sessions
        ]
    }


@router.delete("/{screening_id}")
async def delete_screening(
    screening_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Hapus screening session"""
    if screening_id not in screening_sessions:
        raise HTTPException(404, "Screening tidak ditemukan")
    
    del screening_sessions[screening_id]
    if screening_id in storage_candidates:
        del storage_candidates[screening_id]
    
    return {"message": f"Screening {screening_id} berhasil dihapus", "success": True}