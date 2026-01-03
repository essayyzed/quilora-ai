from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import logging
import json
from src.api.schemas.query import QueryRequest, QueryResponse
from src.pipelines.retrieval import retrieve_documents, retrieve_documents_streaming

logger = logging.getLogger(__name__)
router = APIRouter()


async def generate_sse_stream(query: str, top_k: int):
    """Generate Server-Sent Events stream for query results."""
    try:
        for chunk in retrieve_documents_streaming(query=query, top_k=top_k):
            if chunk["type"] == "documents":
                # Send document metadata first
                data = {
                    "type": "documents",
                    "count": len(chunk["documents"]),
                    "metadata": chunk["metadata"]
                }
                yield f"data: {json.dumps(data)}\n\n"
                
            elif chunk["type"] == "token":
                # Send each token as it arrives
                data = {
                    "type": "token",
                    "content": chunk["content"]
                }
                yield f"data: {json.dumps(data)}\n\n"
                
            elif chunk["type"] == "done":
                # Signal completion
                yield f"data: {json.dumps({'type': 'done'})}\n\n"
                
            elif chunk["type"] == "error":
                # Send error and stop
                data = {
                    "type": "error",
                    "error": chunk["error"]
                }
                yield f"data: {json.dumps(data)}\n\n"
                break
                
    except Exception as e:
        logger.exception("Error in SSE stream generation")
        error_data = {
            "type": "error",
            "error": "Internal server error"
        }
        yield f"data: {json.dumps(error_data)}\n\n"


@router.post("/query", response_model=QueryResponse)
async def query_documents(query_request: QueryRequest):
    """
    Query documents and get AI-generated answers.
    
    This endpoint supports both streaming and non-streaming modes:
    - stream=false (default): Returns complete JSON response
    - stream=true: Returns Server-Sent Events (SSE) stream
    
    The endpoint:
    1. Embeds the query
    2. Retrieves relevant document chunks from Qdrant
    3. Generates an answer using LLM with retrieved context
    """
    # Validate query before processing
    if not query_request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    # Handle streaming vs non-streaming
    if query_request.stream:
        return StreamingResponse(
            generate_sse_stream(query=query_request.query, top_k=query_request.top_k),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"  # Disable nginx buffering
            }
        )
    
    # Non-streaming response (existing behavior)
    try:
        results = retrieve_documents(
            query=query_request.query,
            top_k=query_request.top_k
        )
        
        return QueryResponse(
            answer=results["answer"],
            documents=[{"content": doc.content, "score": doc.score} for doc in results["documents"]],
            metadata=results["metadata"]
        )
    except HTTPException:
        # Re-raise HTTP exceptions (like 400 errors)
        raise
    except Exception as e:
        # Log the full exception with stack trace for debugging
        logger.exception("Error processing query request")
        # Return generic error to client (don't leak internals)
        raise HTTPException(status_code=500, detail="Internal server error")