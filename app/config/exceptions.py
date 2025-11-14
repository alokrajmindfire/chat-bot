"""Custom exceptions for the application"""

class RAGException(Exception):
    """Base exception for RAG pipeline"""
    pass

class DocumentProcessingError(RAGException):
    """Error during document processing"""
    pass

class VectorStoreError(RAGException):
    """Error with vector store operations"""
    pass

class LLMError(RAGException):
    """Error with LLM operations"""
    pass

class InvalidFileTypeError(RAGException):
    """Invalid file type uploaded"""
    pass