"""Service for PDF processing using LangChain"""

import tempfile
import os
from typing import List
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from app.core.exceptions import DocumentProcessingError
from app.config.logger import logger

class PDFService:
    """PDFService"""
    @staticmethod
    async def load_pdf(file_content: bytes, filename: str) -> List[Document]:
        """Load PDF using LangChain PyPDFLoader"""
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                tmp_file.write(file_content)
                tmp_file_path = tmp_file.name
            logger.debug(f"Temporary file created at: {tmp_file_path} ({len(file_content)} bytes)")
            loader = PyPDFLoader(tmp_file_path)
            documents = loader.load()
            logger.info(f"Loaded {len(documents)} pages from {filename}")
            for doc in documents:
                doc.metadata['filename'] = filename
            
            os.unlink(tmp_file_path)
            logger.debug(f"Temporary file deleted: {tmp_file_path}")
            logger.info(f"Successfully processed PDF: {filename}")
            return documents
        
        except Exception as e:
            logger.exception(f"Error processing PDF '{filename}': {e}")
            raise DocumentProcessingError(f"Error loading PDF: {str(e)}")
