"""Controller for document operations"""

from app.services.pdf_service import PDFService
from app.services.ai.chunking_service import ChunkingService
from app.services.vector_store_service import VectorStoreService
from app.models.response_models import UploadResponse
from app.core.config import get_settings
from app.core.exceptions import InvalidFileTypeError

class DocumentController:
    def __init__(self):
        self.pdf_service = PDFService()
        self.chunking_service = ChunkingService()
        self.vector_store_service = VectorStoreService()
        self.settings = get_settings()
    
    async def process_and_index_pdf(
        self,
        file_content: bytes,
        filename: str,
        chunk_size: int = None,
        chunk_overlap: int = None
    ) -> UploadResponse:
        """Process PDF and index in vector store"""
        
        if not filename.lower().endswith('.pdf'):
            raise InvalidFileTypeError("Only PDF files are supported")
        
        documents = await self.pdf_service.load_pdf(file_content, filename)
        
        chunks = self.chunking_service.chunk_documents(
            documents,
            chunk_size=chunk_size or self.settings.CHUNK_SIZE,
            chunk_overlap=chunk_overlap or self.settings.CHUNK_OVERLAP
        )
        
        self.vector_store_service.add_documents(chunks)
        
        return UploadResponse(
            message="PDF processed and indexed successfully",
            filename=filename,
            chunks_created=len(chunks),
            collection_name=self.settings.CHROMA_COLLECTION_NAME
        )