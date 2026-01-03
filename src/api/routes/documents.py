"""
Document Management Endpoints

CRUD operations for documents in the RAG system.
"""

from fastapi import APIRouter, HTTPException, status, UploadFile, File, Query
from typing import Optional
import logging
import uuid

from haystack.dataclasses import Document

from src.api.schemas.documents import (
    DocumentCreateRequest,
    DocumentResponse,
    DocumentListResponse,
    DocumentDeleteResponse,
    DocumentUploadResponse,
)
from src.document_stores.store import get_document_store
from src.pipelines.indexing import index_documents

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/documents", tags=["Documents"])

# Supported file extensions
SUPPORTED_EXTENSIONS = {".txt", ".md"}


@router.post(
    "",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Document",
    description="Create and index a document from JSON content.",
)
async def create_document(request: DocumentCreateRequest) -> DocumentUploadResponse:
    """
    Create a document from text content and index it.
    
    The document will be chunked and embedded for retrieval.
    """
    if not request.content or not request.content.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Content cannot be empty",
        )
    
    try:
        # Generate document ID
        doc_id = str(uuid.uuid4())
        
        # Create Haystack Document
        doc = Document(
            id=doc_id,
            content=request.content,
            meta=request.metadata or {},
        )
        
        # Index the document - returns dict with pipeline results
        result = index_documents([doc])
        
        # Extract chunk count from writer result
        chunk_count = result.get("writer", {}).get("documents_written", 0)
        
        return DocumentUploadResponse(
            document_id=doc_id,
            chunk_count=chunk_count,
            message=f"Document indexed successfully with {chunk_count} chunks",
        )
        
    except Exception as e:
        logger.exception("Failed to create document")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.post(
    "/upload",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload Document File",
    description="Upload and index a document file (TXT, MD).",
)
async def upload_document(
    file: UploadFile = File(..., description="Document file to upload"),
) -> DocumentUploadResponse:
    """
    Upload a file and index its content.
    
    Supported formats: .txt, .md
    """
    # Validate file extension
    filename = file.filename or "unknown"
    extension = "." + filename.split(".")[-1].lower() if "." in filename else ""
    
    if extension not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type. Supported formats: {', '.join(SUPPORTED_EXTENSIONS)}",
        )
    
    try:
        # Read file content
        content = await file.read()
        text_content = content.decode("utf-8")
        
        if not text_content.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Content cannot be empty",
            )
        
        # Generate document ID
        doc_id = str(uuid.uuid4())
        
        # Create Haystack Document with file metadata
        doc = Document(
            id=doc_id,
            content=text_content,
            meta={
                "filename": filename,
                "source": "file_upload",
            },
        )
        
        # Index the document - returns dict with pipeline results
        result = index_documents([doc])
        
        # Extract chunk count from writer result
        chunk_count = result.get("writer", {}).get("documents_written", 0)
        
        return DocumentUploadResponse(
            document_id=doc_id,
            chunk_count=chunk_count,
            message=f"File '{filename}' indexed successfully with {chunk_count} chunks",
        )
        
    except HTTPException:
        raise
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be valid UTF-8 text",
        )
    except Exception as e:
        logger.exception("Failed to upload document")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get(
    "",
    response_model=DocumentListResponse,
    summary="List Documents",
    description="List all indexed documents with pagination.",
)
async def list_documents(
    limit: int = Query(default=20, ge=1, le=100, description="Maximum documents to return"),
    offset: int = Query(default=0, ge=0, description="Number of documents to skip"),
) -> DocumentListResponse:
    """
    List documents in the vector store.
    
    Note: Due to Qdrant's design, this retrieves point data which may be chunked.
    Returns unique documents based on metadata.
    """
    try:
        store = get_document_store()
        total_count = store.count_documents()
        
        if total_count == 0:
            return DocumentListResponse(
                documents=[],
                total_count=0,
                limit=limit,
                offset=offset,
            )
        
        # Scroll through points to get documents
        # Note: This retrieves chunks, not original documents
        points, _ = store.client.scroll(
            collection_name=store.collection_name,
            limit=limit,
            offset=offset,
            with_payload=True,
            with_vectors=False,
        )
        
        documents = []
        for point in points:
            payload = point.payload or {}
            content = payload.get("content", "")
            doc_id = payload.get("doc_id", str(point.id))
            
            # Filter out internal fields from metadata
            meta = {k: v for k, v in payload.items() if k not in ["content", "doc_id"]}
            
            documents.append(DocumentResponse(
                id=doc_id,
                content_preview=content[:200] + "..." if len(content) > 200 else content,
                metadata=meta,
            ))
        
        return DocumentListResponse(
            documents=documents,
            total_count=total_count,
            limit=limit,
            offset=offset,
        )
        
    except Exception as e:
        logger.exception("Failed to list documents")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.delete(
    "/{document_id}",
    response_model=DocumentDeleteResponse,
    summary="Delete Document",
    description="Delete a document by its ID.",
)
async def delete_document(document_id: str) -> DocumentDeleteResponse:
    """
    Delete a document by ID.
    
    Note: This deletes all chunks associated with the document.
    """
    try:
        store = get_document_store()
        
        # Delete the document
        result = store.delete_documents(document_ids=[document_id])
        
        # result is -1 for successful deletion (Qdrant doesn't return count)
        if result == -1:
            return DocumentDeleteResponse(
                message=f"Document '{document_id}' deletion requested",
                document_id=document_id,
            )
        else:
            # No deletion happened (empty request)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found",
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to delete document")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.delete(
    "",
    response_model=DocumentDeleteResponse,
    summary="Delete All Documents",
    description="Delete all documents from the store. Requires confirmation parameter.",
)
async def delete_all_documents(
    all: bool = Query(
        default=False,
        description="Must be true to confirm deletion of all documents",
    ),
) -> DocumentDeleteResponse:
    """
    Delete all documents from the vector store.
    
    Requires `all=true` query parameter for safety.
    """
    if not all:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must provide 'all=true' query parameter to confirm bulk deletion",
        )
    
    try:
        store = get_document_store()
        
        # Get count before deletion
        count_before = store.count_documents()
        
        if count_before == 0:
            return DocumentDeleteResponse(
                message="No documents to delete",
                deleted_count=0,
            )
        
        # Delete and recreate collection (most efficient for full wipe)
        store.delete_collection()
        store._ensure_collection()
        
        return DocumentDeleteResponse(
            message=f"Deleted all {count_before} documents",
            deleted_count=count_before,
        )
        
    except Exception as e:
        logger.exception("Failed to delete all documents")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )
