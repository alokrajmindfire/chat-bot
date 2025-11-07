"""Routes for query operations"""

from fastapi import APIRouter, HTTPException, Depends
from app.controllers.query_controller import QueryController
from app.routes.dependencies import get_query_controller
from app.models.request_models import QuestionRequest
from app.models.response_models import QueryResponse
from app.core.exceptions import RAGException

router = APIRouter(prefix="/query", tags=["query"])

@router.post("/", response_model=QueryResponse)
async def query_documents(
    request: QuestionRequest,
    controller: QueryController = Depends(get_query_controller)
):
    """Query indexed documents"""
    try:
        result = await controller.query_documents(
            question=request.question,
            top_k=request.top_k,
            collection_name=request.collection_name,
            conversation_id=request.conversation_id,
            use_memory=request.use_memory  
        )
        return result
    
    except RAGException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
