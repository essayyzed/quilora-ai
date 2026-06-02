from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any

class QueryRequest(BaseModel):
    query: str = Field(..., description="The user's question or query")
    top_k: Optional[int] = Field(default=None, description="Number of documents to retrieve (uses settings default if not provided)")
    filters: Optional[Dict[str, Any]] = Field(default=None, description="Metadata filters for document retrieval")
    stream: bool = Field(default=False, description="Enable streaming response via Server-Sent Events")
    provider: Optional[str] = Field(default=None, description="Override LLM provider selection (openai|anthropic|groq)")
    
    @field_validator('provider', mode='after')
    @classmethod
    def check_provider(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in ["openai", "anthropic", "groq"]:
            raise ValueError("provider must be one of: openai, anthropic, groq")
        return v
    provider: Optional[str] = Field(default=None, description="Manual LLM provider selection (openai|anthropic|groq)")
    
    @field_validator('provider')
    @classmethod
    def validate_provider(cls, v: Optional[str]) -> Optional[str]:
        """Validate provider is one of the supported options."""
        if v is not None and v not in ["openai", "anthropic", "groq"]:
            raise ValueError("Provider must be one of: openai, anthropic, groq")
        return v

class DocumentResult(BaseModel):
    content: str = Field(..., description="Document content")
    score: float = Field(..., description="Relevance score")

class QueryResponse(BaseModel):
    answer: str = Field(..., description="AI-generated answer based on retrieved documents")
    documents: List[DocumentResult] = Field(..., description="Retrieved document chunks with scores")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata including provider_used and timing")