from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from datetime import datetime
from pydantic import BaseModel
import logging

router = APIRouter()
logger = logging.getLogger("Genassista-EDU-pythonAPI.questions")

class QuestionRequest(BaseModel):
    question_text: str
    question_type: str = "multiple_choice"  # multiple_choice, essay, short_answer
    correct_answer: str
    assignment_id: str
    points: int = 1

class QuestionResponse(BaseModel):
    question_id: str
    question_text: str
    question_type: str
    correct_answer: str
    assignment_id: str
    points: int
    created_at: datetime

@router.post("/questions", response_model=QuestionResponse)
async def create_question(request: QuestionRequest):
    """Skapa ny fråga"""
    try:
        question_id = f"q_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        question = QuestionResponse(
            question_id=question_id,
            question_text=request.question_text,
            question_type=request.question_type,
            correct_answer=request.correct_answer,
            assignment_id=request.assignment_id,
            points=request.points,
            created_at=datetime.now()
        )
        
        logger.info(f"Question created: {question_id}")
        return question
        
    except Exception as e:
        logger.error(f"Question creation failed: {e}")
        raise HTTPException(status_code=500, detail="Question creation failed")

@router.get("/questions/{question_id}")
async def get_question(question_id: str):
    """Hämta fråga"""
    try:
        # Mock data
        return {
            "question_id": question_id,
            "question_text": "Vad är huvudsyftet med klimatförändringar?",
            "question_type": "essay",
            "correct_answer": "Klimatförändringar påverkar vår planet...",
            "assignment_id": "assignment_001",
            "points": 5,
            "created_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Get question failed: {e}")
        raise HTTPException(status_code=500, detail="Get question failed")

@router.get("/assignments/{assignment_id}/questions")
async def get_assignment_questions(assignment_id: str):
    """Hämta alla frågor för en uppgift"""
    try:
        # Mock data
        return {
            "assignment_id": assignment_id,
            "questions": [
                {
                    "question_id": "q_001",
                    "question_text": "Beskriv klimatförändringar",
                    "question_type": "essay",
                    "points": 5
                }
            ]
        }
        
    except Exception as e:
        logger.error(f"Get assignment questions failed: {e}")
        raise HTTPException(status_code=500, detail="Get assignment questions failed")