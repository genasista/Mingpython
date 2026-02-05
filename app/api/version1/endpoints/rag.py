from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Dict, Any
from datetime import datetime
import logging
import tempfile
import os
from pathlib import Path

from app.servies.document_service import document_processor

router = APIRouter()
logger = logging.getLogger("Genassista-EDU-pythonAPI.rag")

@router.post("/documents/upload")
async def upload_document(
    file: UploadFile = File(..., description="Document file (PDF, Word, image)")
):
    """Ladda upp dokument för bearbetning"""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp_file:
            file_path = Path(tmp_file.name)
            content = await file.read()
            tmp_file.write(content)
        
        processed_data = document_processor.process_document(file_path)
        
        os.unlink(file_path)  # Clean up temp file
        
        logger.info(f"Document uploaded and processed: {file.filename}")
        return {
            "success": True,
            "filename": file.filename,
            "processed_data": processed_data,
            "message": "Document uploaded and processed successfully"
        }
        
    except Exception as e:
        logger.error(f"Document upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Document upload failed: {str(e)}")

@router.post("/documents/analyze")
async def analyze_document(
    content: str = Form(..., description="Document content to analyze"),
    document_type: str = Form("essay", description="Type of document")
):
    """Analysera dokumentinnehåll"""
    try:
        # Enkel analys
        word_count = len(content.split())
        sentences = content.split('.')
        avg_sentence_length = word_count / len(sentences) if sentences else 0
        
        # Enkel nivåbedömning
        if word_count < 200:
            level = "E"
        elif word_count < 400:
            level = "C"
        else:
            level = "A"
        
        analysis = {
            "word_count": word_count,
            "sentence_count": len(sentences),
            "avg_sentence_length": avg_sentence_length,
            "assessed_level": level,
            "document_type": document_type,
            "analyzed_at": datetime.now().isoformat()
        }
        
        logger.info(f"Document analyzed: {word_count} words, level {level}")
        return {
            "success": True,
            "analysis": analysis,
            "message": "Document analysis completed successfully"
        }
        
    except Exception as e:
        logger.error(f"Document analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Document analysis failed: {str(e)}")

@router.get("/documents/stats")
async def get_document_stats():
    """Hämta statistik över dokument"""
    try:
        return {
            "total_documents": 0,
            "documents_by_type": {
                "pdf": 0,
                "word": 0,
                "image": 0
            },
            "last_processed": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Get document stats failed: {e}")
        raise HTTPException(status_code=500, detail="Get document stats failed")