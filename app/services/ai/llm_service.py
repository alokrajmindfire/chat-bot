from typing import List, Dict, Optional

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.tools import tool
from langchain import hub

from app.services.tools.weather_tool import WeatherTool
from app.core.exceptions import LLMError
from app.core.config import get_settings


class LLMService:
    def __init__(self):
        settings = get_settings()

        self.llm = ChatGoogleGenerativeAI(
            model=settings.GEMINI_MODEL,
            google_api_key=settings.GEMINI_API_KEY,
            temperature=0.7,
        )

        self.tools = self._create_tools()
        
        self.llm_with_tools = self.llm.bind_tools(self.tools)

    def _create_tools(self) -> List:
        """Create and return list of tools for the agent."""
        weather_tool_service = WeatherTool()

        @tool("get_weather")
        def get_weather(city: str) -> str:
            """Get real-time weather information for a given city.
            
            Args:
                city: Name of the city to get weather for
            
            Returns:
                Weather information as a string
            """
            print("city",city)
            try:
                return weather_tool_service.get_weather(city)
            except Exception as e:
                return f"Error fetching weather for {city}: {str(e)}"

        return [get_weather]

    def _build_prompt(
        self,
        context: str,
        question: str,
        conversation_history: Optional[List[Dict]] = None
    ) -> str:
        """Combine context and history into a single natural-language prompt."""
        history_text = ""
        if conversation_history:
            parts = []
            for msg in conversation_history[-10:]:
                role = msg.get("role", "user")
                text = msg.get("text", "")
                parts.append(f"{role.upper()}: {text}")
            history_text = "\n\n".join(parts)

        prompt = (
            "You are a highly knowledgeable and articulate assistant with expertise in reasoning, explanation, and synthesis. "
            "Provide a detailed, well-structured, and comprehensive answer that deeply explores the question. "
            "Use the information in the provided context as your primary source of truth. "
            "Integrate relevant background knowledge only if the context is incomplete or unclear, ensuring accuracy and consistency. "
            "Your response should be clear, natural, and written as if you are directly explaining to the user. "
            "Go beyond surface-level information — include explanations, underlying principles, examples, and implications where appropriate. "
            "Avoid speculation or unrelated content. "
            "If a question involves real-time information like current weather, call the appropriate tool. "
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
        """Generate an answer using Gemini with tool support."""
        try:
            prompt = self._build_prompt(context, question, conversation_history)
            response = self.llm_with_tools.invoke(prompt)
            print("response",response)
            if hasattr(response, 'tool_calls') and response.tool_calls:
                tool_results = []
                for tool_call in response.tool_calls:
                    tool_name = tool_call['name']
                    tool_args = tool_call['args']
                    
                    for tool in self.tools:
                        if tool.name == tool_name:
                            result = tool.invoke(tool_args)
                            tool_results.append(result)
                            break
                
                return tool_results[0] if tool_results else response.content
            
            return response.content
        except Exception as e:
            raise LLMError(f"Error generating answer: {str(e)}")