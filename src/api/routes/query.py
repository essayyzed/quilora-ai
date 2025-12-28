from fastapi import APIRouter, HTTPException
from src.api.schemas.query import QueryRequest, QueryResponse
from src.pipelines.retrieval import retrieve_documents

router = APIRouter()

@router.post("/query", response_model=QueryResponse)
async def query_documents(query_request: QueryRequest):
    try:
        results = retrieve_documents(query_request.query)
        return QueryResponse(results=results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))