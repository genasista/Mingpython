from fastapi import APIRouter, HTTPException, Form
from typing import Dict, Any, List
from datetime import datetime
import logging
import json
from collections import Counter

router = APIRouter()
logger = logging.getLogger("Genassista-EDU-pythonAPI.student")

@router.post("/{student_id}/progress")
async def generate_progress_tracking(
    student_id: str,
    submissions_json: str = Form(...)  # JSON array of submissions with analyses
) -> Dict[str, Any]:
    """
    Generera progress tracking data för elev
    """
    try:
        # Parse submissions
        try:
            submissions = json.loads(submissions_json)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON format for submissions")
        
        if not isinstance(submissions, list):
            raise HTTPException(status_code=400, detail="Submissions must be a list")
        
        # Analysera submissions över tid
        progress_data = {
            "student_id": student_id,
            "total_submissions": len(submissions),
            "grade_history": [],
            "strengths": [],
            "improvement_areas": [],
            "trends": {}
        }
        
        # Process submissions
        all_strengths = []
        all_improvements = []
        grade_history = []
        
        for sub in submissions:
            analysis = sub.get('analysis', {})
            overall = analysis.get('overall_assessment', {})
            grade_suggestion = overall.get('grade_suggestion', 'C/D')
            
            grade_history.append({
                "assignment_id": sub.get('assignment_id'),
                "grade_suggestion": grade_suggestion,
                "date": sub.get('submitted_at', sub.get('date', datetime.now().isoformat())),
                "strengths": analysis.get('strengths', []),
                "improvements": analysis.get('improvements', [])
            })
            
            all_strengths.extend(analysis.get('strengths', []))
            all_improvements.extend(analysis.get('improvements', []))
        
        progress_data['grade_history'] = grade_history
        
        # Räkna vanligaste styrkor och förbättringsområden
        strength_counts = Counter(all_strengths)
        improvement_counts = Counter(all_improvements)
        
        progress_data['strengths'] = [{"area": s, "count": c} for s, c in strength_counts.most_common(5)]
        progress_data['improvement_areas'] = [{"area": i, "count": c} for i, c in improvement_counts.most_common(5)]
        
        # Identifiera trender
        if len(grade_history) > 1:
            # Konvertera betygsförslag till nummer för trendanalys
            def grade_to_number(grade_str):
                if 'A' in grade_str:
                    return 3
                elif 'B' in grade_str or 'C' in grade_str:
                    return 2
                else:
                    return 1
            
            grades = [grade_to_number(h['grade_suggestion']) for h in grade_history]
            
            # Beräkna trend
            if len(grades) >= 3:
                recent_avg = sum(grades[-3:]) / 3
                earlier_avg = sum(grades[:3]) / 3 if len(grades) >= 6 else sum(grades[:-3]) / len(grades[:-3]) if len(grades) > 3 else recent_avg
                improving = recent_avg > earlier_avg
                stable = abs(recent_avg - earlier_avg) < 0.2
            else:
                improving = False
                stable = True
            
            progress_data['trends'] = {
                'improving': improving,
                'stable': stable,
                'needs_attention': not improving and not stable
            }
        else:
            progress_data['trends'] = {
                'improving': False,
                'stable': True,
                'needs_attention': False
            }
        
        # Visualization data
        visualization_data = {
            "grade_timeline": [
                {
                    "date": h['date'],
                    "grade": h['grade_suggestion'],
                    "assignment_id": h['assignment_id']
                }
                for h in grade_history
            ],
            "strength_distribution": progress_data['strengths'],
            "improvement_distribution": progress_data['improvement_areas']
        }
        
        return {
            "success": True,
            "data": progress_data,
            "visualization": visualization_data,
            "generated_at": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Progress tracking failed: {e}")
        raise HTTPException(status_code=500, detail=f"Progress tracking failed: {str(e)}")

@router.get("/health")
async def student_health():
    """Hälsokontroll för student endpoints"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

