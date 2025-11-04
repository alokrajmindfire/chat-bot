"""Service for PDF processing using LangChain"""

from langchain_community.document_loaders import PyPDFLoader
from typing import List
from langchain_core.documents import Document
import tempfile
import os
from app.core.exceptions import DocumentProcessingError

class PDFService:
    @staticmethod
    async def load_pdf(file_content: bytes, filename: str) -> List[Document]:
        """Load PDF using LangChain PyPDFLoader"""
        try:
            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                tmp_file.write(file_content)
                tmp_file_path = tmp_file.name
            
            # Load using LangChain
            loader = PyPDFLoader(tmp_file_path)
            documents = loader.load()
            
            # Add filename to metadata
            for doc in documents:
                doc.metadata['filename'] = filename
            
            # Cleanup
            os.unlink(tmp_file_path)
            
            return documents
        
        except Exception as e:
            raise DocumentProcessingError(f"Error loading PDF: {str(e)}")
