"""
Health Check Endpoint

Provides health status for the API and its dependencies.
"""

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from datetime import datetime
import logging
import time

from src.api.schemas.documents import HealthResponse
from src.config.settings import settings

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Health"])

# Track application startup time for uptime calculation
_start_time = time.time()


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health Check",
    description="Check the health status of the API and its dependencies (Qdrant).",
    responses={
        200: {"description": "All services healthy"},
        503: {"description": "One or more services unhealthy"},
    },
)
async def health_check() -> JSONResponse:
    """
    Check health of API and dependencies.
    
    Returns:
        - 200: All services healthy
        - 503: One or more services unavailable
    """
    timestamp = datetime.utcnow().isoformat() + "Z"
    uptime_seconds = int(time.time() - _start_time)
    
    # Check Qdrant connectivity
    try:
        from src.document_stores.store import get_document_store
        
        store = get_document_store()
        doc_count = store.count_documents()
        
        response_data = {
            "status": "healthy",
            "qdrant": "connected",
            "qdrant_collection": store.collection_name,
            "document_count": doc_count,
            "timestamp": timestamp,
            "uptime": uptime_seconds,
            "api_version": "0.3.0"
        }
        return JSONResponse(content=response_data, status_code=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        response_data = {
            "status": "unhealthy",
            "qdrant": "disconnected",
            "timestamp": timestamp,
            "uptime": uptime_seconds,
            "api_version": "0.3.0",
            "error": str(e)
        }
        return JSONResponse(
            content=response_data, 
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE
        )
