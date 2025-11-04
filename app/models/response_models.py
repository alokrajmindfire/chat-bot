"""Pydantic models for API responses"""

from pydantic import BaseModel
from typing import List, Dict, Any

class SourceDocument(BaseModel):
    content: str
    metadata: Dict[str, Any]
    score: float

class QueryResponse(BaseModel):
    question: str
    answer: str
    sources: List[SourceDocument]
    model_used: str

class UploadResponse(BaseModel):
    message: str
    filename: str
    chunks_created: int
    collection_name: str

class HealthResponse(BaseModel):
    status: str
    app_name: str
    version: str
    vector_store_status: str