# app/services/ai/llm_service.py
import google.generativeai as genai
from app.core.config import get_settings
from app.core.exceptions import LLMError
from typing import List, Dict, Optional
from app.services.tools.weather_tool import WeatherTool
import re

class LLMService:
    def __init__(self):
        settings = get_settings()
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model_name = settings.GEMINI_MODEL
        self.client = genai.GenerativeModel(self.model_name)
        self.weather_tool = WeatherTool()
    
    def _detect_weather_intent(self, question: str) -> Optional[str]:
        """Check if user is asking about weather."""
        q = question.lower()
        if re.search(r"\b(weather|temperature|forecast|climate)\b", q):
            match = re.search(r"in\s+([A-Za-z\s]+)", q)
            if match:
                return match.group(1).strip()
        return None
    
    def _build_prompt(self, context: str, question: str, conversation_history: Optional[List[Dict]] = None) -> str:
        history_text = ""
        if conversation_history:
            history_parts = []
            for m in conversation_history[-10:]:
                role = m.get("role", "user")
                text = m.get("text", "")
                history_parts.append(f"{role.upper()}: {text}")
            history_text = "\n\n".join(history_parts)

        # prompt = (
        # "You are a knowledgeable and articulate assistant. "
        # "Answer the question clearly, naturally, and comprehensively — as if you are explaining directly to the user. "
        # "Do not mention that the answer is based on any provided text or context. "
        # "Use the information in the context below as your primary source of truth. "
        # "Only if the context is missing or clearly incomplete, you may use your own understanding to give a helpful and accurate answer. "
        # "Avoid speculation and keep your response factual and well-structured.\n\n"
        # )
        prompt = (
            "You are a highly knowledgeable and articulate assistant with expertise in reasoning, explanation, and synthesis. "
            "Provide a detailed, well-structured, and comprehensive answer that deeply explores the question. "
            "Use the information in the provided context as your primary source of truth. "
            "Integrate relevant background knowledge only if the context is incomplete or unclear, ensuring accuracy and consistency. "
            "Your response should be clear, natural, and written as if you are directly explaining to the user. "
            "Go beyond surface-level information — include explanations, underlying principles, examples, and implications where appropriate. "
            "Avoid speculation or unrelated content. "
            "If the question involves a process or concept, break it down step-by-step. "
            "Keep the tone confident, informative, and easy to follow.\n\n"
        )
        if history_text:
            prompt += f"Conversation history:\n{history_text}\n\n"

        prompt += f"Context:\n{context}\n\nQuestion: {question}"
        return prompt

    def generate_answer(
        self,
        context: str,
        question: str,
        conversation_history: Optional[List[Dict]] = None
    ) -> str:
        """Generate answer using Gemini"""
        try:
            city = self._detect_weather_intent(question)
            if city:
                return self.weather_tool.get_weather(city)
            prompt = self._build_prompt(context, question, conversation_history)
            # Use the correct method for your genai client. This is a general example.
            response = self.client.generate_content(prompt)
            # response.text or response.candidates[0].content depending on lib
            return getattr(response, "text", None) or str(response)
        except Exception as e:
            raise LLMError(f"Error generating answer: {str(e)}")
