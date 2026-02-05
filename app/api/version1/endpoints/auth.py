from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import logging

router = APIRouter()
logger = logging.getLogger("Genassista-EDU-pythonAPI.auth")

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    role: str

@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """Logga in användare"""
    try:
        # Enkel mock-autentisering
        if request.username == "teacher" and request.password == "password":
            return LoginResponse(
                access_token="mock_token_123",
                user_id="teacher_001",
                role="teacher"
            )
        elif request.username == "student" and request.password == "password":
            return LoginResponse(
                access_token="mock_token_456",
                user_id="student_001",
                role="student"
            )
        else:
            raise HTTPException(status_code=401, detail="Invalid credentials")
            
    except Exception as e:
        logger.error(f"Login failed: {e}")
        raise HTTPException(status_code=500, detail="Login failed")

@router.post("/logout")
async def logout():
    """Logga ut användare"""
    return {"message": "Successfully logged out"}

@router.get("/me")
async def get_current_user():
    """Hämta aktuell användare"""
    return {
        "user_id": "current_user",
        "role": "teacher",
        "username": "current_user"
    }