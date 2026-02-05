from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel
import logging
import tempfile
import os
from pathlib import Path

from app.servies.llm_service import llm_service
from app.servies.document_service import document_processor

router = APIRouter()
logger = logging.getLogger("Genassista-EDU-pythonAPI.teaching")

class LessonGenerationRequest(BaseModel):
    topic: str
    subject: str = "engelska"
    level: str = "5"
    duration_minutes: int = 45
    material_id: Optional[int] = None  # Material är valfritt

class MaterialGenerationRequest(BaseModel):
    topic: str
    material_type: str = "worksheet"  # "worksheet", "presentation", "handout", "lesson_plan", "study_guide", "activity"
    target_audience: str = "High school"
    subject: str = "engelska"
    level: str = "5"
    duration_minutes: Optional[int] = 45

@router.post("/generate-lesson")
async def generate_lesson_plan(request: LessonGenerationRequest):
    """Generera läroplan (innehållplan) baserad på Skolverkets Gy25-kriterier"""
    try:
        # Hämta relevant Skolverket innehåll från RAG system (valfritt)
        skolverket_knowledge = []
        try:
            # Importera vector_db dynamiskt för att undvika import-fel
            from app.servies.vector_service import vector_db
            
            # Sök i Skolverket knowledge base för relevant innehåll
            search_query = f"{request.subject} {request.level} {request.topic} centralt innehåll"
            knowledge_results = vector_db.search_knowledge(
                query=search_query,
                subject=request.subject,
                level=request.level,
                n_results=5
            )
            if knowledge_results and len(knowledge_results) > 0:
                skolverket_knowledge = [item.get('content', '') for item in knowledge_results if item.get('content')]
                logger.info(f"Retrieved {len(skolverket_knowledge)} Skolverket knowledge items")
        except ImportError as e:
            logger.warning(f"Vector DB not available (will continue without RAG): {e}")
        except Exception as e:
            logger.warning(f"Could not retrieve Skolverket knowledge (will continue without it): {e}")
            # Fortsätt utan RAG - AI kommer fortfarande generera baserat på Gy25 i prompten
        
        # Bygg prompt med Skolverket innehåll
        skolverket_context = ""
        if skolverket_knowledge:
            skolverket_context = "\n\nRELEVANT SKOLVERKET INNEHÅLLSPLAN (Gy25):\n"
            for i, knowledge in enumerate(skolverket_knowledge[:3], 1):
                skolverket_context += f"{i}. {knowledge}\n"
        
        lesson_prompt = f"""
Du är en expert på svensk gymnasieutbildning och Skolverkets Gy25-kriterier.

Generera en detaljerad innehållplan (läroplan) för ämnet: {request.topic}
Ämne: {request.subject}
Nivå: {request.level}
Varaktighet: {request.duration_minutes} minuter

{skolverket_context}

Innehållsplanen ska inkludera:
1. **Lärandemål** - Exakt kopplade till Skolverkets Gy25-kriterier för {request.subject} nivå {request.level}
2. **Centralt innehåll** - Baserat på Skolverkets ämnesplan
3. **Aktiviteter** - Steg-för-steg aktiviteter som följer Gy25
4. **Bedömning** - Metoder för att bedöma elevernas kunskaper enligt Skolverkets kriterier
5. **Resurser** - Material och resurser som behövs
6. **Koppling till Gy25** - Tydlig koppling till Skolverkets läroplan

Format: Strukturerad text med tydliga rubriker. Använd svenska och referera till Skolverkets kriterier.
"""
        
        generated_content = await llm_service.generate_text(
            prompt=lesson_prompt,
            max_tokens=3000,
            temperature=0.7
        )
        
        logger.info(f"AI-generated lesson plan created for topic: {request.topic}")
        return {
            "success": True,
            "topic": request.topic,
            "subject": request.subject,
            "level": request.level,
            "duration_minutes": request.duration_minutes,
            "lesson_plan": generated_content,
            "generated_at": datetime.now().isoformat(),
            "message": "Lesson plan generated successfully"
        }
        
    except Exception as e:
        logger.error(f"Lesson generation failed: {e}", exc_info=True)
        error_detail = str(e)
        # Ge mer detaljerad felinformation
        if "LLM" in error_detail or "API" in error_detail or "key" in error_detail.lower():
            error_detail = f"LLM service error: {error_detail}. Kontrollera att Groq API key är konfigurerad."
        raise HTTPException(status_code=500, detail=f"Lesson generation failed: {error_detail}")

@router.post("/generate-materials")
async def generate_teaching_materials(request: MaterialGenerationRequest) -> Dict[str, Any]:
    """Generera undervisningsmaterial med AI - Accepterar JSON"""
    try:
        duration = request.duration_minutes or 45
        material_prompt = f"""
        Generate teaching materials for:
        - Subject: {request.subject}
        - Level: {request.level}
        - Topic: {request.topic}
        - Type: {request.material_type}
        - Target Audience: {request.target_audience}
        - Duration: {duration} minutes
        
        Include:
        1. Title and description
        2. Content sections
        3. Activities/exercises
        4. Assessment suggestions
        5. Resources needed
        
        Format as JSON with clear structure aligned with Gy25.
        """
        
        material_content = await llm_service.generate_text(
            prompt=material_prompt,
            max_tokens=2000,
            temperature=0.7
        )
        
        import json
        try:
            material_data = json.loads(material_content)
        except json.JSONDecodeError:
            material_data = {
                "title": f"{request.material_type.title()} - {request.topic}",
                "description": material_content[:500],
                "content": [],
                "activities": [],
                "assessment": [],
                "resources": []
            }
        
        return {
            "success": True,
            "material": {
                "type": request.material_type,
                "title": material_data.get('title', f"{request.material_type.title()} - {request.topic}"),
                "description": material_data.get('description', ''),
                "content": material_data.get('content', []),
                "sections": material_data.get('sections', material_data.get('content', [])),
                "activities": material_data.get('activities', []),
                "assessment": material_data.get('assessment', []),
                "resources": material_data.get('resources', []),
                "target_audience": request.target_audience,
                "duration_minutes": duration
            },
            "topic": request.topic,
            "subject": request.subject,
            "level": request.level,
            "generated_at": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Material generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Material generation failed: {str(e)}")

@router.post("/process-document")
async def process_teaching_document(
    file: UploadFile = File(..., description="Document file for processing")
):
    """Bearbeta uppladdat dokument för undervisningsmaterial"""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp_file:
            file_path = Path(tmp_file.name)
            content = await file.read()
            tmp_file.write(content)
        
        processed_data = document_processor.process_document(file_path)
        
        os.unlink(file_path)  # Clean up temp file
        
        logger.info(f"Teaching document processed: {file.filename}")
        return {
            "success": True,
            "filename": file.filename,
            "processed_data": processed_data,
            "message": "Teaching document processed successfully"
        }
        
    except Exception as e:
        logger.error(f"Teaching document processing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Document processing failed: {str(e)}")

@router.get("/health")
async def teaching_health():
    """Hälsokontroll för undervisningsbearbetning"""
    return {
        "status": "healthy",
        "llm_service": "operational",
        "document_processor": "operational",
        "timestamp": datetime.now().isoformat()
    }