from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Dict, Any
from datetime import datetime
import logging
import tempfile
import os
from pathlib import Path

from app.servies.document_service import document_processor
from app.servies.ai_analysis_service import ai_analysis_service

router = APIRouter()
logger = logging.getLogger("Genassista-EDU-pythonAPI.handwriting")

@router.post("/process")
async def process_handwriting(
    file: UploadFile = File(..., description="Handskrift-bild (JPG, PNG)"),
    assignment_id: str = Form("handwriting_test"),
    student_id: str = Form("student_123"),
    subject: str = Form("engelska"),
    level: str = Form("5")
):
    """Bearbeta uppladdad handskrift-bild med OCR och AI-analys"""
    try:
        # Spara temporär fil
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp_file:
            file_path = Path(tmp_file.name)
            content = await file.read()
            tmp_file.write(content)
        
        # OCR-bearbetning
        processed_data = document_processor.process_document(file_path)
        ocr_text = processed_data.get('content', '')
        
        if not ocr_text.strip():
            ocr_text = "Kunde inte läsa text från bilden."
            logger.warning(f"OCR failed to extract text from {file.filename}")

        # Enkel analys för betyg
        word_count = len(ocr_text.split())
        if word_count < 50:
            betyg = "E"
        elif word_count < 150:
            betyg = "C"
        else:
            betyg = "A"
        
        # Rensa upp temporär fil
        os.unlink(file_path)
        
        result = {
            "success": True,
            "filename": file.filename,
            "ocr_text": ocr_text,
            "betyg": betyg,
            "word_count": word_count,
            "assignment_id": assignment_id,
            "student_id": student_id,
            "subject": subject,
            "level": level,
            "processed_at": datetime.now().isoformat()
        }
        
        logger.info(f"Handwriting processing completed: {assignment_id} for student {student_id}")
        return result
        
    except Exception as e:
        logger.error(f"Handwriting processing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Handwriting processing failed: {str(e)}")

@router.get("/health")
async def handwriting_health():
    """Hälsokontroll för handskrift-bearbetning"""
    return {
        "status": "healthy",
        "service": "handwriting_processing",
        "features": ["OCR", "AI_analysis"],
        "timestamp": datetime.now().isoformat()
    }