from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from app.controllers.document_controller import DocumentController
from app.routes.dependencies import get_document_controller
from app.models.response_models import UploadResponse
from app.core.exceptions import RAGException

router = APIRouter(prefix="/documents", tags=["documents"])

@router.post("/upload", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    controller: DocumentController = Depends(get_document_controller)
):
    """Upload and index a PDF document"""
    try:
        content = await file.read()
        result = await controller.process_and_index_pdf(content, file.filename)
        return result
    
    except RAGException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")