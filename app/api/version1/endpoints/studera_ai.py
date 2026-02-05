from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List
from datetime import datetime
import logging

router = APIRouter()
logger = logging.getLogger("Genassista-EDU-pythonAPI.studera_ai")

@router.get("/images")
async def get_studera_ai_images(
    topic: str = Query("shakespeare", description="Topic to search for images"),
    limit: int = Query(10, description="Number of images to return", ge=1, le=50)
) -> Dict[str, Any]:
    """
    Hämta bilder från studera.ai (mock för MVP)
    """
    # Mock data för MVP
    mock_images = [
        {
            "id": f"image_{i}",
            "url": f"https://studera.ai/images/{topic}/{i}.jpg",
            "title": f"Bild {i} om {topic}",
            "description": f"Bild som visar {topic}",
            "category": topic,
            "tags": [topic, "education", "image"],
            "width": 800,
            "height": 600,
            "format": "jpg"
        }
        for i in range(1, limit + 1)
    ]
    
    return {
        "success": True,
        "images": mock_images,
        "total": len(mock_images),
        "topic": topic,
        "retrieved_at": datetime.now().isoformat()
    }

@router.get("/images/{image_id}")
async def get_studera_ai_image(image_id: str) -> Dict[str, Any]:
    """
    Hämta specifik bild från studera.ai
    """
    # Mock data för MVP
    return {
        "success": True,
        "image": {
            "id": image_id,
            "url": f"https://studera.ai/images/{image_id}.jpg",
            "title": f"Bild {image_id}",
            "description": "Bildbeskrivning",
            "metadata": {
                "width": 800,
                "height": 600,
                "format": "jpg",
                "size_kb": 150
            },
            "retrieved_at": datetime.now().isoformat()
        }
    }

@router.get("/health")
async def studera_ai_health():
    """Hälsokontroll för Studera.ai integration"""
    return {
        "status": "healthy",
        "service": "studera_ai_mock",
        "timestamp": datetime.now().isoformat()
    }

