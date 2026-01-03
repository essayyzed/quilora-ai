"""
Document API Schemas

Pydantic models for document management endpoints.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class DocumentCreateRequest(BaseModel):
    """Request model for creating a document via JSON."""
    content: str = Field(..., min_length=1, description="The text content of the document")
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict, 
        description="Optional metadata for the document (e.g., source, author)"
    )
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "content": "This is the content of my document about AI.",
                    "metadata": {"source": "manual", "author": "user"}
                }
            ]
        }
    }


class DocumentResponse(BaseModel):
    """Response model for a single document."""
    id: str = Field(..., description="Unique document identifier")
    content_preview: str = Field(..., description="First 200 characters of content")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Document metadata")
    chunk_count: Optional[int] = Field(default=None, description="Number of chunks created (if indexed)")


class DocumentListResponse(BaseModel):
    """Response model for listing documents."""
    documents: List[DocumentResponse] = Field(..., description="List of documents")
    total_count: int = Field(..., description="Total number of documents in store")
    limit: int = Field(..., description="Maximum documents returned")
    offset: int = Field(..., description="Offset for pagination")


class DocumentDeleteResponse(BaseModel):
    """Response model for document deletion."""
    message: str = Field(..., description="Confirmation message")
    document_id: Optional[str] = Field(default=None, description="Deleted document ID (for single deletion)")
    deleted_count: Optional[int] = Field(default=None, description="Number of documents deleted (for bulk)")


class DocumentUploadResponse(BaseModel):
    """Response model for document upload."""
    document_id: str = Field(..., description="Generated document identifier")
    chunk_count: int = Field(..., description="Number of chunks created during indexing")
    message: str = Field(..., description="Success message")


class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str = Field(..., description="Overall health status: 'healthy' or 'unhealthy'")
    qdrant: str = Field(..., description="Qdrant connection status: 'connected' or 'disconnected'")
    qdrant_collection: Optional[str] = Field(default=None, description="Active collection name")
    document_count: Optional[int] = Field(default=None, description="Number of documents in store")
    timestamp: str = Field(..., description="Timestamp of health check in ISO format")
    error: Optional[str] = Field(default=None, description="Error details if unhealthy")
