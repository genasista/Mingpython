
from time import perf_counter
from uuid import uuid4
import os
import logging
from fastapi import Request, Response, FastAPI, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.middleware.cors import CORSMiddleware

logger = logging.getLogger("Genassista-EDU-pythonAPI.middleware")
SERVICE_NAME = os.getenv("SERVICE_NAME", "Genassista-EDU-pythonAPI")
PYTHON_API_KEY = os.getenv("PYTHON_API_KEY", "CHANGE-ME-IN-PRODUCTION")

class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        req_id = request.headers.get("X-Request-ID") or str(uuid4())
        request.state.request_id = req_id
        data_mode = "sandbox" if os.getenv("SANDBOX_MODE", "true").lower() == "true" else "production"

        start = perf_counter()
        response = Response(status_code=500)  # default om något kraschar
        try:
            response = await call_next(request)
        finally:
            duration_ms = round((perf_counter() - start) * 1000, 2)
            logger.info(
                "service=%s correlationId=%s dataMode=%s method=%s path=%s status=%s duration_ms=%.2f",
                SERVICE_NAME, req_id, data_mode, request.method, request.url.path,
                response.status_code, duration_ms
            )
            response.headers["X-Request-ID"] = req_id

        return response

class APIKeyMiddleware(BaseHTTPMiddleware):
    """Validera att requests kommer från backend"""
    
    async def dispatch(self, request: Request, call_next):
        # Skip health checks och root
        skip_paths = ["/", "/health", "/api/version1/health", "/docs", "/openapi.json", "/redoc"]
        if request.url.path in skip_paths or request.url.path.startswith("/docs") or request.url.path.startswith("/openapi.json"):
            return await call_next(request)
        
        # Validera API key
        api_key = request.headers.get("X-API-KEY") or request.headers.get("X-Backend-Key")
        
        if not api_key or api_key != PYTHON_API_KEY:
            logger.warning(f"Invalid API key attempt from {request.client.host if request.client else 'unknown'}")
            raise HTTPException(status_code=403, detail="Invalid API key")
        
        return await call_next(request)

def add_builtin_middlewares(
    app: FastAPI,
    allow_origins: list[str] | None = None,
    allow_methods: list[str] | None = None,
    allow_headers: list[str] | None = None,
    enable_api_key: bool = True,
) -> None:
    app.add_middleware(RequestIdMiddleware)
    if enable_api_key:
        app.add_middleware(APIKeyMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origins or ["*"],
        allow_credentials=True,
        allow_methods=allow_methods or ["*"],
        allow_headers=allow_headers or ["*"],
        expose_headers=["X-Request-ID"],
    )
