from fastapi import APIRouter, HTTPException
from typing import Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel
import logging

router = APIRouter()
logger = logging.getLogger("Genassista-EDU-pythonAPI.grading")

class GradeRequest(BaseModel):
    student_id: str
    assignment_id: str
    grade: str  # E, C, A
    feedback: str
    graded_by: str

class GradeResponse(BaseModel):
    grade_id: str
    student_id: str
    assignment_id: str
    grade: str
    feedback: str
    graded_by: str
    graded_at: datetime

@router.post("/grades", response_model=GradeResponse)
async def create_grade(request: GradeRequest):
    """Skapa nytt betyg"""
    try:
        grade_id = f"grade_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        grade = GradeResponse(
            grade_id=grade_id,
            student_id=request.student_id,
            assignment_id=request.assignment_id,
            grade=request.grade,
            feedback=request.feedback,
            graded_by=request.graded_by,
            graded_at=datetime.now()
        )
        
        logger.info(f"Grade created: {grade_id} for student {request.student_id}")
        return grade
        
    except Exception as e:
        logger.error(f"Grade creation failed: {e}")
        raise HTTPException(status_code=500, detail="Grade creation failed")

@router.get("/grades/{grade_id}")
async def get_grade(grade_id: str):
    """Hämta betyg"""
    try:
        # Mock data
        return {
            "grade_id": grade_id,
            "student_id": "student_001",
            "assignment_id": "assignment_001",
            "grade": "C",
            "feedback": "Bra jobbat! Utveckla mer för A-nivå.",
            "graded_by": "teacher_001",
            "graded_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Get grade failed: {e}")
        raise HTTPException(status_code=500, detail="Get grade failed")

@router.get("/students/{student_id}/grades")
async def get_student_grades(student_id: str):
    """Hämta alla betyg för en elev"""
    try:
        # Mock data
        return {
            "student_id": student_id,
            "grades": [
                {
                    "grade_id": "grade_001",
                    "assignment_id": "assignment_001",
                    "grade": "C",
                    "feedback": "Bra jobbat!",
                    "graded_at": datetime.now().isoformat()
                }
            ]
        }
        
    except Exception as e:
        logger.error(f"Get student grades failed: {e}")
        raise HTTPException(status_code=500, detail="Get student grades failed")