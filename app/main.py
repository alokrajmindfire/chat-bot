"""FastAPI application entry point"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import document_routes, query_routes
from app.config.config import get_settings
from app.models.response_models import HealthResponse
from app.services.vector_store_service import VectorStoreService

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Professional RAG Pipeline with LangChain and ChromaDB"
)
origins = [
    "http://localhost:8501",
    "http://127.0.0.1:8501",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(document_routes.router)
app.include_router(query_routes.router)
print("DEBUG GEMINI KEY =", get_settings().LLM_API_KEY)

@app.get("/", tags=["root"])
async def root():
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "docs": "/docs"
    }

@app.get("/health", response_model=HealthResponse, tags=["health"])
async def health_check():
    """Health check endpoint"""
    vector_store = VectorStoreService()
    vector_store_status = "healthy" if vector_store.check_health() else "unhealthy"
    
    return HealthResponse(
        status="healthy",
        app_name=settings.APP_NAME,
        version=settings.APP_VERSION,
        vector_store_status=vector_store_status
    )

