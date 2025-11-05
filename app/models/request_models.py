"""Pydantic models for API requests"""

from pydantic import BaseModel, Field
from typing import Optional

class QuestionRequest(BaseModel):
    question: str = Field(..., min_length=1, description="Question to ask")
    top_k: Optional[int] = Field(3, ge=1, le=10, description="Number of documents to retrieve")
    collection_name: Optional[str] = Field(None, description="Collection to query from")
    conversation_id: Optional[str] = None
    use_memory: Optional[bool] = True  
    class Config:
        json_schema_extra = {
            "example": {
                "question": "What is the main topic of the document?",
                "top_k": 3
            }
        }

class ChunkingConfig(BaseModel):
    chunk_size: Optional[int] = Field(1000, ge=100, le=5000)
    chunk_overlap: Optional[int] = Field(200, ge=0, le=1000)
