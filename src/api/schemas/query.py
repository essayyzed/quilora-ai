from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class QueryRequest(BaseModel):
    query: str = Field(..., description="The user's question or query")
    top_k: Optional[int] = Field(default=None, description="Number of documents to retrieve (uses settings default if not provided)")
    filters: Optional[Dict[str, Any]] = Field(default=None, description="Metadata filters for document retrieval")

class DocumentResult(BaseModel):
    content: str = Field(..., description="Document content")
    score: float = Field(..., description="Relevance score")

class QueryResponse(BaseModel):
    answer: str = Field(..., description="AI-generated answer based on retrieved documents")
    documents: List[DocumentResult] = Field(..., description="Retrieved document chunks with scores")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata about the query")