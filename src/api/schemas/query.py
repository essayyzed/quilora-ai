from pydantic import BaseModel
from typing import List, Optional

class QueryRequest(BaseModel):
    query: str
    filters: Optional[dict] = None

class QueryResponse(BaseModel):
    results: List[dict]
    total: int
    query: str