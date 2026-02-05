from fastapi import APIRouter, HTTPException, Depends
from app.servies.ai_analysis_service import ai_analysis_service
from pydantic import BaseModel
import logging

logger = logging.getLogger("Genassista-EDU-pythonAPI.feedback")
router = APIRouter()

class FeedbackRequest(BaseModel):
    question_text: str
    student_answer: str

@router.post("/generate")
async def generate_feedback(request: FeedbackRequest):
    """Generate AI feedback for a student's answer"""
    try:
        # Use ai_analysis_service instead of AIService
        analysis = await ai_analysis_service.analyze_student_submission(
            content=request.student_answer,
            submission_type="essay",
            student_id="feedback_user",
            assignment_id="feedback_assignment",
            subject="engelska",
            level="5"
        )
        
        # Simple feedback based on analysis
        level = analysis.get('overall_assessment', {}).get('assessed_level', 'C')
        word_count = len(request.student_answer.split())
        
        feedback = f"Texten är {word_count} ord lång och når {level}-nivå. "
        if level == "E":
            feedback += "Förbättra genom att utveckla argumenten mer och använd längre meningar."
        elif level == "C":
            feedback += "Bra jobbat! Utveckla mer sofistikerade analyser för A-nivå."
        else:
            feedback += "Utmärkt! Fortsätt att utveckla dina analytiska färdigheter."
        
        return {
            "question_text": request.question_text,
            "student_answer": request.student_answer,
            "feedback": feedback,
            "level": level,
            "word_count": word_count
        }
        
    except Exception as e:
        logger.error(f"Error generating feedback: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Feedback generation failed: {str(e)}"
        )