from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from src.api.routes import query
from src.api.routes import health
from src.api.routes import documents
from src.middleware.logging import LoggingMiddleware, configure_logging

# Configure logging on startup
configure_logging(
    log_level=os.getenv("LOG_LEVEL", "INFO"),
    json_logs=os.getenv("JSON_LOGS", "false").lower() == "true"
)

app = FastAPI(
    title="Quilora AI - RAG API",
    description="Retrieval-Augmented Generation API for document Q&A with streaming support",
    version="0.3.0",  # Phase 2: Production Readiness
)

# Add logging middleware (first, so it captures all requests)
app.add_middleware(LoggingMiddleware)

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(health.router)
app.include_router(query.router)
app.include_router(documents.router)


@app.get("/", tags=["Root"])
def read_root():
    return {
        "message": "Welcome to the Quilora AI RAG API!",
        "version": "0.3.0",
        "docs": "/docs",
        "features": ["RAG", "Streaming", "Document Management"]
    }