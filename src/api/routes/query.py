from fastapi import APIRouter, HTTPException
from src.api.schemas.query import QueryRequest, QueryResponse
from src.pipelines.retrieval import retrieve_documents

router = APIRouter()

@router.post("/query", response_model=QueryResponse)
async def query_documents(query_request: QueryRequest):
    """
    Query documents and get AI-generated answers.
    
    This endpoint:
    1. Embeds the query
    2. Retrieves relevant document chunks from Qdrant
    3. Generates an answer using LLM with retrieved context
    """
    # Validate query before processing
    if not query_request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    try:
        results = retrieve_documents(
            query=query_request.query,
            top_k=query_request.top_k if hasattr(query_request, 'top_k') else None
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
        # Convert other exceptions to 500 errors
        raise HTTPException(status_code=500, detail=str(e))