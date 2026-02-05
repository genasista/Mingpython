from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
import logging
import httpx
import os

router = APIRouter()
logger = logging.getLogger("Genassista-EDU-pythonAPI.data")

# Backend URL från miljövariabel
BACKEND_URL = os.getenv("CORE_BASE_URL", "http://localhost:3001")

@router.get("/courses")
async def get_courses():
    """Hämta kurser från backend"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BACKEND_URL}/courses")
            response.raise_for_status()
            return response.json()
            
    except httpx.RequestError as e:
        logger.error(f"Backend request failed: {e}")
        raise HTTPException(status_code=503, detail="Backend service unavailable")
    except Exception as e:
        logger.error(f"Get courses failed: {e}")
        raise HTTPException(status_code=500, detail="Get courses failed")

@router.get("/students")
async def get_students():
    """Hämta elever från backend"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BACKEND_URL}/students")
            response.raise_for_status()
            return response.json()
            
    except httpx.RequestError as e:
        logger.error(f"Backend request failed: {e}")
        raise HTTPException(status_code=503, detail="Backend service unavailable")
    except Exception as e:
        logger.error(f"Get students failed: {e}")
        raise HTTPException(status_code=500, detail="Get students failed")

@router.get("/schools")
async def get_schools():
    """Hämta skolor från backend"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BACKEND_URL}/schools")
            response.raise_for_status()
            return response.json()
            
    except httpx.RequestError as e:
        logger.error(f"Backend request failed: {e}")
        raise HTTPException(status_code=503, detail="Backend service unavailable")
    except Exception as e:
        logger.error(f"Get schools failed: {e}")
        raise HTTPException(status_code=500, detail="Get schools failed")

@router.get("/health")
async def data_health():
    """Hälsokontroll för data-proxy"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BACKEND_URL}/health", timeout=5.0)
            backend_status = "healthy" if response.status_code == 200 else "unhealthy"
    except:
        backend_status = "unhealthy"
    
    return {
        "status": "healthy",
        "backend_status": backend_status,
        "backend_url": BACKEND_URL
    }