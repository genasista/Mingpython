from fastapi import APIRouter
from app.api.version1.endpoints import health, assignment, exam, teaching, feedback, handwriting, auth, grading, questions, rag, privacy, data_endpoint, materials, studera_ai, student

# all v1 under this prefix
api_router = APIRouter(prefix="/api/version1")

# health check
api_router.include_router(health.router, prefix="/health", tags=["health"])

# assignment AI endpoints
api_router.include_router(assignment.router, prefix="/assignments", tags=["assignment-ai"])

# exam AI endpoints
api_router.include_router(exam.router, prefix="/exams", tags=["exam-ai"])

# teaching AI endpoints
api_router.include_router(teaching.router, prefix="/teaching", tags=["teaching-ai"])

# materials endpoints
api_router.include_router(materials.router, prefix="/materials", tags=["materials"])

# feedback endpoints
api_router.include_router(feedback.router, prefix="/feedback", tags=["feedback"])

# handwriting endpoints
api_router.include_router(handwriting.router, prefix="/handwriting", tags=["handwriting"])

# auth endpoints
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])

# grading endpoints
api_router.include_router(grading.router, prefix="/grading", tags=["grading"])

# questions endpoints
api_router.include_router(questions.router, prefix="/questions", tags=["questions"])

# RAG endpoints
api_router.include_router(rag.router, prefix="/rag", tags=["rag"])

# privacy endpoints
api_router.include_router(privacy.router, prefix="/privacy", tags=["privacy"])

# data proxy endpoints
api_router.include_router(data_endpoint.router, prefix="/data", tags=["data"])

# studera.ai endpoints
api_router.include_router(studera_ai.router, prefix="/studera-ai", tags=["studera-ai"])

# student endpoints
api_router.include_router(student.router, prefix="/students", tags=["student"])