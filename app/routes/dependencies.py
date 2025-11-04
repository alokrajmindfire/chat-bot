"""Shared API dependencies"""

from app.controllers.document_controller import DocumentController
from app.controllers.query_controller import QueryController

def get_document_controller() -> DocumentController:
    return DocumentController()

def get_query_controller() -> QueryController:
    return QueryController()
