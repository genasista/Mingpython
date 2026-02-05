from fastapi import APIRouter, HTTPException, Form
from typing import Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel
import logging

from app.servies.ai_analysis_service import ai_analysis_service
from app.servies.llm_service import llm_service

router = APIRouter()
logger = logging.getLogger("Genassista-EDU-pythonAPI.exam")

class ExamSubmissionRequest(BaseModel):
    exam_id: str
    student_id: str
    submission_content: str
    subject: str = "engelska"
    level: str = "5"

@router.post("/analyze")
async def analyze_exam_submission(request: ExamSubmissionRequest):
    """Analysera elevs provinlämning med AI"""
    try:
        analysis = await ai_analysis_service.analyze_student_submission(
            content=request.submission_content,
            submission_type="exam",
            student_id=request.student_id,
            assignment_id=request.exam_id,
            subject=request.subject,
            level=request.level
        )
        
        logger.info(f"Exam submission analysis completed: {request.exam_id} for student {request.student_id}")
        return {
            "success": True,
            "exam_id": request.exam_id,
            "student_id": request.student_id,
            "analysis": analysis,
            "processed_at": datetime.now().isoformat(), 
            "message": "Exam submission analysis completed successfully"
        }
        
    except Exception as e:
        logger.error(f"Exam submission analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

class ExamQuestionGenerationRequest(BaseModel):
    exam_id: Optional[str] = None
    exam_title: str
    topic: Optional[str] = None
    exam_description: Optional[str] = None
    difficulty: Optional[str] = "medium"  # "easy", "medium", "hard"
    question_count: int = 5
    subject: str = "engelska"
    level: str = "5"

@router.post("/generate-questions")
async def generate_exam_questions(request: ExamQuestionGenerationRequest):
    """Generera provfrågor med AI - Accepterar JSON"""
    try:
        import json
        
        # Använd topic om det finns, annars exam_title
        topic = request.topic or request.exam_title
        description = request.exam_description or f"Exam about {topic}"
        num_questions = request.question_count
        
        question_prompt = f"""
        Generate {num_questions} multiple choice questions for an exam titled '{request.exam_title}' 
        with description '{description}'.
        Topic: {topic}
        Difficulty: {request.difficulty}
        Subject: {request.subject}, Level: {request.level}.
        
        Return ONLY valid JSON in this exact format:
        {{
          "questions": [
            {{
              "question": "Question text here?",
              "options": ["Option A", "Option B", "Option C", "Option D"],
              "correct": 0,
              "explanation": "Why this answer is correct"
            }}
          ]
        }}
        
        Each question must have exactly 4 options. The "correct" field is the index (0-3) of the correct answer.
        """
        
        questions_content = await llm_service.generate_text(
            prompt=question_prompt,
            max_tokens=2000,
            temperature=0.7
        )
        
        # Parse JSON response
        try:
            parsed_data = json.loads(questions_content)
            # Normalize to ensure questions is always an array
            if isinstance(parsed_data, dict) and "questions" in parsed_data:
                questions_list = parsed_data["questions"]
            elif isinstance(parsed_data, list):
                questions_list = parsed_data
            else:
                questions_list = []
            
            # Validate and normalize each question structure
            normalized_questions = []
            for q in questions_list:
                if isinstance(q, dict):
                    normalized_questions.append({
                        "question": q.get("question", ""),
                        "options": q.get("options", [])[:4],  # Ensure max 4 options
                        "correct": q.get("correct", 0),
                        "explanation": q.get("explanation", "")
                    })
            
            # Ensure we have the requested number of questions
            while len(normalized_questions) < num_questions:
                normalized_questions.append({
                    "question": f"Question {len(normalized_questions) + 1}",
                    "options": ["Option A", "Option B", "Option C", "Option D"],
                    "correct": 0,
                    "explanation": ""
                })
            
            questions_list = normalized_questions[:num_questions]
            
        except json.JSONDecodeError:
            logger.warning(f"Failed to parse JSON from LLM response, using fallback")
            # Fallback: create empty structure
            questions_list = [
                {
                    "question": f"Question {i+1}",
                    "options": ["Option A", "Option B", "Option C", "Option D"],
                    "correct": 0,
                    "explanation": ""
                }
                for i in range(num_questions)
            ]
        
        logger.info(f"Exam questions generated for: {request.exam_title} ({len(questions_list)} questions)")
        return {
            "success": True,
            "exam_id": request.exam_id,
            "exam_title": request.exam_title,
            "topic": topic,
            "exam_description": description,
            "subject": request.subject,
            "level": request.level,
            "difficulty": request.difficulty,
            "questions": questions_list,
            "question_count": len(questions_list),
            "generated_at": datetime.now().isoformat(),
            "message": "Exam questions generated successfully"
        }
        
    except Exception as e:
        logger.error(f"Exam question generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Question generation failed: {str(e)}")

@router.get("/health")
async def exam_health():
    """Hälsokontroll för provbearbetning"""
    return {
        "status": "healthy",
        "ai_analysis_service": "operational",
        "llm_service": "operational",
        "timestamp": datetime.now().isoformat()
    }