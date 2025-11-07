from langchain_classic.agents import AgentExecutor, create_react_agent
from langsmith import Client
from typing import List, Dict, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools import Tool
from langchain.tools import tool
from app.core.config import get_settings
from app.services.tools.weather_tool import WeatherTool
from app.core.exceptions import LLMError
from app.services.tools.news_tool import NewsTool

class LLMService:
    def __init__(self):
        settings = get_settings()
        client = Client(api_key=settings.LANGSMITH_API_KEY)
        self.llm = ChatGoogleGenerativeAI(
            model=settings.GEMINI_MODEL,
            google_api_key=settings.GEMINI_API_KEY,
            temperature=0.7,
        )

        self.tools = self._create_tools()
        self.prompt_template = client.pull_prompt("hwchase17/react:d15fe3c4", include_model=True)
        self.agent = create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.prompt_template,
        )

        self.agent_executor = AgentExecutor(agent=self.agent, tools=self.tools, verbose=True)

    def _create_tools(self) -> List[Tool]:
        """Create and return a list of tools for the agent."""
        weather_service = WeatherTool()
        news_service = NewsTool()

        @tool("get_weather", return_direct=False)
        def get_weather(city: str) -> str:
            """Get real-time weather information for a given city."""
            try:
                return weather_service.get_weather(city)
            except Exception as e:
                return f"Error fetching weather for {city}: {str(e)}"
    
        @tool("get_news", return_direct=False)
        def get_news(category: str = "business") -> str:
                """Fetch the latest news for a given category (e.g. business, sports, technology)."""
                try:
                    return news_service.get_news(category)
                except Exception as e:
                    return f"Error fetching news for {category}: {str(e)}"

        return [get_weather, get_news]
    
    def generate_answer(
        self,
        context: str,
        question: str,
        conversation_history: Optional[List[Dict]] = None,
    ) -> str:
        """Generate an answer using the agent."""
        try:
            history = []
            if conversation_history:
                for msg in conversation_history[-5:]:
                    role = msg.get("role", "user")
                    text = msg.get("text", "")
                    history.append(f"{role.capitalize()}: {text}")

            system_prompt = (
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

            user_prompt = (
                f"{system_prompt}"
                f"Conversation history:\n{chr(10).join(history)}\n\n"
                f"Context:\n{context}\n\n"
                f"Question:\n{question}\n"
            )

            result = self.agent_executor.invoke({"input": user_prompt})
            print("asad",result)
            return result.get("output", "").strip() or "No response."

        except Exception as e:
            raise LLMError(f"Error generating answer: {str(e)}")