from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Dict, Any
from datetime import datetime
import logging
import tempfile
import os
from pathlib import Path

from app.servies.document_service import document_processor
from app.servies.storage_service import storage_service, generate_storage_path

router = APIRouter()
logger = logging.getLogger("Genassista-EDU-pythonAPI.materials")

@router.post("/process")
async def process_material(
    file: UploadFile = File(..., description="Material file (Word .docx, PDF)"),
    material_id: str = Form(...),
    school_id: str = Form("school_001"),
    course_id: str = Form("course_eng5"),
    subject: str = Form("engelska"),
    level: str = Form("5")
) -> Dict[str, Any]:
    """Bearbeta uppladdat undervisningsmaterial (Word, PDF)"""
    try:
        # Kontrollera filtyp
        file_ext = Path(file.filename).suffix.lower()
        supported_types = ['.docx', '.doc', '.pdf']
        
        if file_ext not in supported_types:
            raise HTTPException(
                status_code=400,
                detail=f"Filtyp {file_ext} stöds inte. Stödda typer: {', '.join(supported_types)}"
            )
        
        # Läs fil content
        content = await file.read()
        
        # Generera storage path
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        storage_path = generate_storage_path(
            school_id=school_id,
            course_id=course_id,
            assignment_id=material_id,
            student_id="teacher",
            filename=f"material_{timestamp}{file_ext}"
        )
        
        # Upload till storage
        stored_path = await storage_service().upload_file(
            file_content=content,
            path=storage_path,
            metadata={
                "content_type": file.content_type or "application/octet-stream",
                "filename": file.filename,
                "material_id": material_id,
                "subject": subject,
                "level": level,
                "uploaded_at": datetime.now().isoformat()
            }
        )
        
        # Ladda fil från storage för processing
        file_content = await storage_service().download_file(stored_path)
        
        # Skapa temporär fil för processing
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
            tmp_file.write(file_content)
            tmp_file_path = Path(tmp_file.name)
        
        # Bearbeta dokument
        processed_data = document_processor.process_document(tmp_file_path)
        extracted_text = processed_data.get('content', '')
        
        # Extrahera metadata
        metadata = {
            "word_count": len(extracted_text.split()),
            "character_count": len(extracted_text),
            "file_type": file_ext,
            "file_size": len(content),
            "pages": processed_data.get('pages', 1),
            "sections": processed_data.get('sections', [])
        }
        
        # Rensa upp temporär fil
        os.unlink(tmp_file_path)
        
        result = {
            "success": True,
            "material_id": material_id,
            "filename": file.filename,
            "file_type": file_ext,
            "storage_path": stored_path,
            "extracted_text": extracted_text[:500],  # Första 500 tecken som preview
            "full_text_length": len(extracted_text),
            "metadata": metadata,
            "subject": subject,
            "level": level,
            "processed_at": datetime.now().isoformat()
        }
        
        logger.info(f"Material processed: {material_id}, file: {file.filename}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Material processing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Material processing failed: {str(e)}")

@router.get("/{material_id}/preview")
async def get_material_preview(
    material_id: str,
    school_id: str = "school_001",
    course_id: str = "course_eng5"
) -> Dict[str, Any]:
    """Generera förhandsvisning av bearbetat material"""
    try:
        # Hitta material i storage (mock implementation)
        # I verklig implementation skulle man hämta från databas eller storage
        preview_data = {
            "material_id": material_id,
            "preview_text": "Förhandsvisning av material...",
            "image_url": None,  # Om material har bilder
            "metadata": {
                "word_count": 0,
                "pages": 0,
                "sections": []
            }
        }
        
        return {
            "success": True,
            "preview": preview_data,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Material preview failed: {e}")
        raise HTTPException(status_code=500, detail=f"Material preview failed: {str(e)}")

@router.get("/health")
async def materials_health():
    """Hälsokontroll för materialbearbetning"""
    return {
        "status": "healthy",
        "document_processor": "operational",
        "supported_file_types": [".docx", ".doc", ".pdf"],
        "timestamp": datetime.now().isoformat()
    }

