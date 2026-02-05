from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import logging
import os
from datetime import datetime

router = APIRouter()
logger = logging.getLogger("Genassista-EDU-pythonAPI.health")

@router.get("")
async def health() -> Dict[str, Any]:
    """
    Förbättrad health check med dependencies status
    """
    health_status = {
        "status": "healthy",
        "version": os.getenv("SERVICE_VERSION", "1.0.0"),
        "dependencies": {},
        "timestamp": datetime.now().isoformat()
    }
    
    # Check OpenAI API
    try:
        from app.servies.llm_service import llm_service
        # Simple check - if API key exists, consider it healthy
        # Check for either Groq or OpenAI API key
        if os.getenv("GROQ_API_KEY") or os.getenv("OPENAI_API_KEY"):
            health_status['dependencies']['openai'] = "healthy"
        else:
            health_status['dependencies']['openai'] = "degraded (no API key)"
            health_status['status'] = "degraded"
    except Exception as e:
        health_status['dependencies']['openai'] = f"unhealthy: {str(e)}"
        health_status['status'] = "degraded"
    
    # Check ChromaDB
    try:
        from app.servies.rag_service import rag_service
        # Simple check - if service exists, consider it healthy
        health_status['dependencies']['chromadb'] = "healthy"
    except Exception as e:
        health_status['dependencies']['chromadb'] = f"unhealthy: {str(e)}"
        health_status['status'] = "degraded"
    
    # Check Document Processing
    try:
        from app.servies.document_service import document_processor
        health_status['dependencies']['document_processing'] = "healthy"
    except Exception as e:
        health_status['dependencies']['document_processing'] = f"unhealthy: {str(e)}"
        health_status['status'] = "degraded"
    
    # Check Storage Service
    try:
        from app.servies.storage_service import storage_service
        health_status['dependencies']['storage'] = "healthy"
    except Exception as e:
        health_status['dependencies']['storage'] = f"unhealthy: {str(e)}"
        health_status['status'] = "degraded"
    
    return health_status
