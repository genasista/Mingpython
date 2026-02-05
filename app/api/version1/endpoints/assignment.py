from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Dict, Any, List
from datetime import datetime
from pydantic import BaseModel
import logging
import tempfile
import os
from pathlib import Path
import asyncio
import json

from app.servies.document_service import document_processor
from app.servies.ai_analysis_service import ai_analysis_service
from app.servies.storage_service import storage_service, generate_storage_path
from app.servies.llm_service import llm_service

router = APIRouter()
logger = logging.getLogger("Genassista-EDU-pythonAPI.assignment")

class AssignmentAnalysisRequest(BaseModel):
    assignment_id: str
    student_id: str
    content: str
    assignment_type: str = "essay"
    subject: str = "engelska"
    level: str = "5"

@router.post("/submit")
async def submit_assignment(
    file: UploadFile = File(..., description="Uppgiftsfil (Word .docx, PDF, eller bild för handskrift)"),
    assignment_id: str = Form(...),
    student_id: str = Form(...),
    school_id: str = Form("school_001"),  # Default för lokalt
    course_id: str = Form("course_eng5"),  # Default för lokalt
    subject: str = Form("engelska"),
    level: str = Form("5")
):
    """Lämna in uppgift från Word, PDF eller bild"""
    try:
        # Kontrollera filtyp
        file_ext = Path(file.filename).suffix.lower()
        supported_types = ['.docx', '.doc', '.pdf', '.jpg', '.jpeg', '.png']
        
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
            assignment_id=assignment_id,
            student_id=student_id,
            filename=f"submission_{timestamp}{file_ext}"
        )
        
        # Upload till storage (lokalt eller Azure)
        stored_path = await storage_service().upload_file(
            file_content=content,
            path=storage_path,
            metadata={
                "content_type": file.content_type or "application/octet-stream",
                "filename": file.filename,
                "assignment_id": assignment_id,
                "student_id": student_id,
                "subject": subject,
                "level": level,
                "uploaded_at": datetime.now().isoformat()
            }
        )
        
        # Ladda fil från storage för processing
        file_content = await storage_service().download_file(stored_path)
        
        # Skapa temporär fil för processing (document_processor behöver file path)
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
            tmp_file.write(file_content)
            tmp_file_path = Path(tmp_file.name)
        
        # Bearbeta dokument (Word, PDF eller bild)
        processed_data = document_processor.process_document(tmp_file_path)
        extracted_text = processed_data.get('content', '')
        
        if not extracted_text.strip():
            extracted_text = "Kunde inte extrahera text från filen."
            logger.warning(f"Text extraction failed from {file.filename}")
        
        # AI-analys av innehållet
        analysis = await ai_analysis_service.analyze_student_submission(
            content=extracted_text,
            submission_type="essay",
            student_id=student_id,
            assignment_id=assignment_id,
            subject=subject,
            level=level
        )
        
        # Rensa upp temporär fil
        os.unlink(tmp_file_path)
        
        result = {
            "success": True,
            "filename": file.filename,
            "file_type": file_ext,
            "storage_path": stored_path,  # Path till filen i storage
            "extracted_text": extracted_text,
            "word_count": len(extracted_text.split()),
            "betyg": analysis.get('overall_assessment', {}).get('assessed_level', 'C'),
            "analysis": analysis,
            "assignment_id": assignment_id,
            "student_id": student_id,
            "subject": subject,
            "level": level,
            "processed_at": datetime.now().isoformat()
        }
        
        logger.info(
            f"Assignment submitted: {assignment_id} for student {student_id}, "
            f"file: {file.filename}, storage_path: {stored_path}"
        )
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Assignment submission failed: {e}")
        raise HTTPException(status_code=500, detail=f"Assignment submission failed: {str(e)}")

@router.post("/analyze")
async def analyze_assignment_submission(request: AssignmentAnalysisRequest):
    """Analysera elevuppgift med AI"""
    try:
        # Validera input
        if not request.content or len(request.content.strip()) < 10:
            raise HTTPException(status_code=400, detail="Content too short (minimum 10 characters)")
        
        if not request.assignment_id or not request.student_id:
            raise HTTPException(status_code=400, detail="assignment_id and student_id are required")
        
        # Timeout hantering (max 30 sekunder)
        try:
            analysis = await asyncio.wait_for(
                ai_analysis_service.analyze_student_submission(
                    content=request.content,
                    submission_type=request.assignment_type,
                    student_id=request.student_id,
                    assignment_id=request.assignment_id,
                    subject=request.subject,
                    level=request.level
                ),
                timeout=30.0
            )
        except asyncio.TimeoutError:
            logger.error(f"AI analysis timeout for {request.assignment_id}")
            raise HTTPException(status_code=504, detail="AI analysis timeout (max 30 seconds)")
        
        overall = analysis.get('overall_assessment', {})
        recommendations = analysis.get('recommendations', [])
        next_steps = analysis.get('next_steps', [])

        def format_score_value(value: float, default: float = 0.0) -> float:
            try:
                return round(float(value), 2)
            except (TypeError, ValueError):
                return default

        def status_from_score(value: float) -> str:
            if value is None:
                return "unknown"
            if value >= 0.8:
                return "exceeds"
            if value >= 0.6:
                return "meets"
            return "developing"

        grading_criteria = [
            {
                "name": "Content Quality",
                "score": format_score_value(analysis.get('content_quality', {}).get('coherence_score', 0.6), 0.6),
                "status": status_from_score(analysis.get('content_quality', {}).get('coherence_score', 0.6)),
                "details": analysis.get('content_quality', {}).get('structure_quality', 'N/A')
            },
            {
                "name": "Language Skills",
                "score": format_score_value(analysis.get('language_skills', {}).get('language_level', 0.6), 0.6),
                "status": status_from_score(analysis.get('language_skills', {}).get('language_level', 0.6)),
                "details": f"Vocabulary richness: {format_score_value(analysis.get('language_skills', {}).get('vocabulary_richness', 0.0))}"
            },
            {
                "name": "Critical Thinking",
                "score": format_score_value(analysis.get('critical_thinking', {}).get('critical_thinking_score', 0.6), 0.6),
                "status": status_from_score(analysis.get('critical_thinking', {}).get('critical_thinking_score', 0.6)),
                "details": analysis.get('critical_thinking', {}).get('analysis_depth', 'N/A')
            },
            {
                "name": "Creativity",
                "score": format_score_value(analysis.get('creativity', {}).get('creativity_score', 0.6), 0.6),
                "status": status_from_score(analysis.get('creativity', {}).get('creativity_score', 0.6)),
                "details": analysis.get('creativity', {}).get('originality_level', 'N/A')
            },
            {
                "name": "Gy25 Alignment",
                "score": format_score_value(analysis.get('gy25_compliance', {}).get('curriculum_alignment', 0.6), 0.6),
                "status": status_from_score(analysis.get('gy25_compliance', {}).get('curriculum_alignment', 0.6)),
                "details": analysis.get('gy25_compliance', {}).get('assessment_criteria_met', 'N/A')
            }
        ]

        suggestions = [
            {
                "category": rec.get("category", "general"),
                "priority": rec.get("priority", "medium"),
                "recommendation": rec.get("recommendation", ""),
                "actions": rec.get("specific_actions", [])
            }
            for rec in recommendations
        ]

        suggestions.extend(
            {
                "category": "next_step",
                "priority": step.get("timeline", "short_term"),
                "recommendation": step.get("action", ""),
                "actions": step.get("resources", [])
            }
            for step in next_steps
        )

        if not suggestions:
            suggestions = [
                {
                    "category": "improvement",
                    "priority": "medium",
                    "recommendation": improvement,
                    "actions": []
                }
                for improvement in overall.get('areas_for_improvement', [])
            ]

        result = {
            "success": True,
            "assignment_id": request.assignment_id,
            "student_id": request.student_id,
            "score": {
                "level": overall.get('assessed_level', 'C'),
                "gradeSuggestion": overall.get('grade_suggestion', 'C/D'),
                "value": format_score_value(overall.get('overall_score', 0.65), 0.65),
                "confidence": format_score_value(overall.get('confidence', 0.75), 0.75)
            },
            "feedback": {
                "teacher": analysis.get('feedback', {}).get('teacher', ''),
                "student": analysis.get('feedback', {}).get('student', ''),
                "parent": analysis.get('feedback', {}).get('parent', '')
            },
            "suggestions": suggestions,
            "gradingCriteria": grading_criteria,
            "processed_at": datetime.now().isoformat(),
            "raw_analysis": analysis  # För kompatibilitet/debugging
        }
        
        logger.info(f"Assignment analysis completed: {request.assignment_id} for student {request.student_id}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Assignment analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.post("/process/generate-exercise")
async def generate_individual_exercise(
    student_id: str = Form(...),
    student_level: str = Form(...),  # "E", "C", "A"
    improvement_areas: str = Form(...),  # JSON array
    subject: str = Form("engelska"),
    level: str = Form("5")
) -> Dict[str, Any]:
    """Generera individuell övning för elev"""
    try:
        # Parse improvement areas
        try:
            areas = json.loads(improvement_areas)
        except json.JSONDecodeError:
            areas = improvement_areas.split(",") if isinstance(improvement_areas, str) else []
        
        # Generera övning med LLM
        exercise_prompt = f"""
        Generate an individual exercise for a student with:
        - Level: {student_level}
        - Improvement areas: {', '.join(areas) if areas else 'general'}
        - Subject: {subject}
        - Course level: {level}
        
        Include:
        1. Title and clear instructions
        2. 3-5 questions/exercises tailored to the student's level
        3. Examples if needed
        4. Estimated time to complete
        
        Format as JSON with structure: {{"title": "...", "instructions": "...", "questions": [...], "examples": [...], "estimated_time": 30}}
        """
        
        exercise_content = await llm_service.generate_text(
            prompt=exercise_prompt,
            max_tokens=1500,
            temperature=0.7
        )
        
        try:
            exercise_data = json.loads(exercise_content)
        except json.JSONDecodeError:
            # Fallback om LLM inte returnerar JSON
            exercise_data = {
                "title": f"Individuell övning - Nivå {student_level}",
                "instructions": exercise_content[:500],
                "questions": [],
                "examples": [],
                "estimated_time": 30
            }
        
        return {
            "success": True,
            "student_id": student_id,
            "exercise": {
                "title": exercise_data.get('title', ''),
                "instructions": exercise_data.get('instructions', ''),
                "questions": exercise_data.get('questions', []),
                "examples": exercise_data.get('examples', []),
                "difficulty": student_level,
                "estimated_time": exercise_data.get('estimated_time', 30)
            },
            "generated_at": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Exercise generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Exercise generation failed: {str(e)}")

@router.post("/process/batch-analyze")
async def batch_analyze_assignments(
    submissions_json: str = Form(...)  # JSON array of submissions
) -> Dict[str, Any]:
    """Batch analysera flera uppgifter"""
    try:
        # Parse submissions
        try:
            submissions = json.loads(submissions_json)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON format for submissions")
        
        if not isinstance(submissions, list):
            raise HTTPException(status_code=400, detail="Submissions must be a list")
        
        # Process parallellt
        tasks = []
        for sub in submissions:
            task = ai_analysis_service.analyze_student_submission(
                content=sub.get('content', ''),
                student_id=sub.get('student_id', ''),
                assignment_id=sub.get('assignment_id', ''),
                subject=sub.get('subject', 'engelska'),
                level=sub.get('level', '5'),
                submission_type=sub.get('submission_type', 'essay')
            )
            tasks.append((sub.get('submission_id', ''), task))
        
        # Wait for all with timeout
        results = []
        for submission_id, task in tasks:
            try:
                analysis = await asyncio.wait_for(task, timeout=30.0)
                results.append({
                    "submission_id": submission_id,
                    "success": True,
                    "analysis": analysis
                })
            except asyncio.TimeoutError:
                results.append({
                    "submission_id": submission_id,
                    "success": False,
                    "error": "Analysis timeout"
                })
            except Exception as e:
                results.append({
                    "submission_id": submission_id,
                    "success": False,
                    "error": str(e)
                })
        
        return {
            "success": True,
            "results": results,
            "total": len(submissions),
            "successful": sum(1 for r in results if r['success']),
            "failed": sum(1 for r in results if not r['success'])
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Batch analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Batch analysis failed: {str(e)}")

@router.post("/process/generate-quiz")
async def generate_quiz(
    student_id: str = Form(...),
    student_level: str = Form(...),  # "E", "C", "A"
    subject: str = Form("engelska"),
    level: str = Form("5"),
    topic: str = Form(""),
    num_questions: int = Form(10)
) -> Dict[str, Any]:
    """Generera quiz för elev"""
    try:
        quiz_prompt = f"""
        Generate a quiz for a student with:
        - Level: {student_level}
        - Subject: {subject}
        - Course level: {level}
        - Topic: {topic if topic else 'general'}
        - Number of questions: {num_questions}
        
        Include:
        1. Quiz title
        2. {num_questions} questions with multiple choice answers (4 options each)
        3. Correct answers
        4. Explanations for each answer
        
        Format as JSON: {{"title": "...", "questions": [{{"question": "...", "options": ["...", "..."], "correct": 0, "explanation": "..."}}]}}
        """
        
        quiz_content = await llm_service.generate_text(
            prompt=quiz_prompt,
            max_tokens=2000,
            temperature=0.7
        )
        
        try:
            quiz_data = json.loads(quiz_content)
        except json.JSONDecodeError:
            quiz_data = {
                "title": f"Quiz - Nivå {student_level}",
                "questions": []
            }
        
        return {
            "success": True,
            "student_id": student_id,
            "quiz": {
                "title": quiz_data.get('title', ''),
                "questions": quiz_data.get('questions', []),
                "difficulty": student_level,
                "num_questions": len(quiz_data.get('questions', []))
            },
            "generated_at": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Quiz generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Quiz generation failed: {str(e)}")

@router.post("/process/generate-flashcards")
async def generate_flashcards(
    student_id: str = Form(...),
    student_level: str = Form(...),
    subject: str = Form("engelska"),
    level: str = Form("5"),
    topic: str = Form(""),
    num_flashcards: int = Form(20)
) -> Dict[str, Any]:
    """Generera flashcards för elev"""
    try:
        flashcard_prompt = f"""
        Generate flashcards for a student with:
        - Level: {student_level}
        - Subject: {subject}
        - Course level: {level}
        - Topic: {topic if topic else 'general'}
        - Number of flashcards: {num_flashcards}
        
        Each flashcard should have:
        - Front: Question or term
        - Back: Answer or definition
        
        Format as JSON: {{"flashcards": [{{"front": "...", "back": "..."}}]}}
        """
        
        flashcard_content = await llm_service.generate_text(
            prompt=flashcard_prompt,
            max_tokens=2000,
            temperature=0.7
        )
        
        try:
            flashcard_data = json.loads(flashcard_content)
        except json.JSONDecodeError:
            flashcard_data = {"flashcards": []}
        
        return {
            "success": True,
            "student_id": student_id,
            "flashcards": {
                "cards": flashcard_data.get('flashcards', []),
                "difficulty": student_level,
                "num_flashcards": len(flashcard_data.get('flashcards', []))
            },
            "generated_at": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Flashcard generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Flashcard generation failed: {str(e)}")

@router.post("/process/generate-template")
async def generate_assignment_template(
    assignment_type: str = Form(...),  # "essay", "presentation", "project", etc.
    subject: str = Form("engelska"),
    level: str = Form("5"),
    topic: str = Form(""),
    duration_minutes: int = Form(60)
) -> Dict[str, Any]:
    """Generera uppgiftsmall med AI"""
    try:
        template_prompt = f"""
        Generate an assignment template for:
        - Type: {assignment_type}
        - Subject: {subject}
        - Level: {level}
        - Topic: {topic if topic else 'general'}
        - Duration: {duration_minutes} minutes
        
        Include:
        1. Title
        2. Description
        3. Instructions
        4. Assessment criteria (aligned with Gy25)
        5. Requirements
        6. Grading rubric
        
        Format as JSON with clear structure.
        """
        
        template_content = await llm_service.generate_text(
            prompt=template_prompt,
            max_tokens=2000,
            temperature=0.7
        )
        
        try:
            template_data = json.loads(template_content)
        except json.JSONDecodeError:
            template_data = {
                "title": f"{assignment_type.title()} - {topic if topic else 'General'}",
                "description": template_content[:500],
                "instructions": "",
                "assessment_criteria": [],
                "requirements": [],
                "grading_rubric": {}
            }
        
        return {
            "success": True,
            "template": {
                "type": assignment_type,
                "title": template_data.get('title', ''),
                "description": template_data.get('description', ''),
                "instructions": template_data.get('instructions', ''),
                "assessment_criteria": template_data.get('assessment_criteria', []),
                "requirements": template_data.get('requirements', []),
                "grading_rubric": template_data.get('grading_rubric', {}),
                "duration_minutes": duration_minutes
            },
            "generated_at": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Template generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Template generation failed: {str(e)}")

@router.post("/process/generate-learning-path")
async def generate_learning_path(
    student_id: str = Form(...),
    student_level: str = Form(...),
    improvement_areas: str = Form(...),  # JSON array
    subject: str = Form("engelska"),
    level: str = Form("5")
) -> Dict[str, Any]:
    """Generera anpassad lärandeväg för elev"""
    try:
        try:
            areas = json.loads(improvement_areas)
        except json.JSONDecodeError:
            areas = improvement_areas.split(",") if isinstance(improvement_areas, str) else []
        
        path_prompt = f"""
        Generate an adaptive learning path for a student with:
        - Level: {student_level}
        - Improvement areas: {', '.join(areas) if areas else 'general'}
        - Subject: {subject}
        - Course level: {level}
        
        Include:
        1. Learning path title
        2. 5-7 steps with:
           - Step title
           - Description
           - Exercises/activities
           - Expected outcomes
        3. Overall goal
        
        Format as JSON: {{"title": "...", "goal": "...", "steps": [{{"title": "...", "description": "...", "activities": [...], "outcomes": "..."}}]}}
        """
        
        path_content = await llm_service.generate_text(
            prompt=path_prompt,
            max_tokens=2000,
            temperature=0.7
        )
        
        try:
            path_data = json.loads(path_content)
        except json.JSONDecodeError:
            path_data = {
                "title": f"Lärandeväg - Nivå {student_level}",
                "goal": "Förbättra kunskaper",
                "steps": []
            }
        
        return {
            "success": True,
            "student_id": student_id,
            "learning_path": {
                "title": path_data.get('title', ''),
                "goal": path_data.get('goal', ''),
                "steps": path_data.get('steps', []),
                "difficulty": student_level
            },
            "generated_at": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Learning path generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Learning path generation failed: {str(e)}")

@router.post("/process/generate-study-recommendations")
async def generate_study_recommendations(
    student_id: str = Form(...),
    performance_data: str = Form(...),  # JSON with past performance
    improvement_areas: str = Form(...),  # JSON array
    subject: str = Form("engelska"),
    level: str = Form("5")
) -> Dict[str, Any]:
    """Generera studietips baserat på elevens prestationer"""
    try:
        try:
            areas = json.loads(improvement_areas)
        except json.JSONDecodeError:
            areas = improvement_areas.split(",") if isinstance(improvement_areas, str) else []
        
        try:
            performance = json.loads(performance_data)
        except json.JSONDecodeError:
            performance = {}
        
        recommendations_prompt = f"""
        Generate study recommendations for a student with:
        - Performance: {json.dumps(performance, ensure_ascii=False)[:500]}
        - Improvement areas: {', '.join(areas) if areas else 'general'}
        - Subject: {subject}
        - Level: {level}
        
        Provide:
        1. 5-7 concrete study tips
        2. Specific strategies for improvement
        3. Suggested resources
        4. Time management suggestions
        
        Format as JSON: {{"recommendations": [{{"tip": "...", "strategy": "...", "resource": "..."}}], "summary": "..."}}
        """
        
        recommendations_content = await llm_service.generate_text(
            prompt=recommendations_prompt,
            max_tokens=1500,
            temperature=0.7
        )
        
        try:
            recommendations_data = json.loads(recommendations_content)
        except json.JSONDecodeError:
            recommendations_data = {
                "recommendations": [],
                "summary": "Fokusera på regelbunden träning och repetition"
            }
        
        return {
            "success": True,
            "student_id": student_id,
            "recommendations": {
                "tips": recommendations_data.get('recommendations', []),
                "summary": recommendations_data.get('summary', ''),
                "improvement_areas": areas
            },
            "generated_at": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Study recommendations generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Study recommendations generation failed: {str(e)}")

@router.get("/health")
async def assignment_health():
    """Hälsokontroll för uppgiftsbearbetning"""
    return {
        "status": "healthy",
        "ai_analysis_service": "operational",
        "document_processor": "operational",
        "supported_file_types": [".docx", ".doc", ".pdf", ".jpg", ".jpeg", ".png"],
        "timestamp": datetime.now().isoformat()
    }