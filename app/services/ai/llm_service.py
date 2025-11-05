"""Service for LLM interactions using Gemini"""

import google.generativeai as genai
from app.core.config import get_settings
from app.core.exceptions import LLMError

class LLMService:
    def __init__(self):
        settings = get_settings()
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model_name = settings.GEMINI_MODEL
        self.client = genai.GenerativeModel(self.model_name)
    
    def generate_answer(self, context: str, question: str) -> str:
        """Generate answer using Gemini"""
        try:
            prompt = (
                "You are a knowledgeable assistant. "
                "Use the provided context to answer the question clearly and concisely. "
                "If the answer is not found in the context, respond with "
                "'The answer is not available in the provided context.'\n\n"
                f"Context:\n{context}\n\n"
                f"Question: {question}"
            )
            
            response = self.client.generate_content(prompt)
            return response.text
        
        except Exception as e:
            raise LLMError(f"Error generating answer: {str(e)}")

