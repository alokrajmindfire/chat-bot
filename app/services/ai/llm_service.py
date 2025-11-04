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
            prompt = f"""Based on the following context, answer the question. If the answer is not in the context, say so clearly.

Context:
{context}

Question: {question}

Answer:"""
            
            response = self.client.generate_content(prompt)
            return response.text
        
        except Exception as e:
            raise LLMError(f"Error generating answer: {str(e)}")

