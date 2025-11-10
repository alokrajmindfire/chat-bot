from typing import List, Dict, Optional
from langchain_community.tools import DuckDuckGoSearchResults
from langchain_classic.agents import AgentExecutor, create_react_agent
from langsmith import Client
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.tools import tool
from app.core.config import get_settings
from app.services.tools.weather_tool import WeatherTool
from app.core.exceptions import LLMError
from app.services.tools.news_tool import NewsTool
import ddgs
from langchain_community.tools import Tool
from app.config.logger import logger
class LLMService:
    """LLMService manages all interactions with the underlying Large Language Model (Gemini)
    and coordinates with LangChain tools and agent execution"""
    def __init__(self):
        settings = get_settings()
        logger.info("Initializing LLMService with model: %s", settings.GEMINI_MODEL)
        try:
            client = Client(api_key=settings.LANGSMITH_API_KEY)

            self.llm = ChatGoogleGenerativeAI(
                model=settings.GEMINI_MODEL,
                google_api_key=settings.GEMINI_API_KEY,
                temperature=0.7,
            )

            self.tools = self._create_tools()
            logger.info("Successfully initialized %d tools.", len(self.tools))

            self.prompt_template = client.pull_prompt("hwchase17/react:d15fe3c4", include_model=True)
            logger.debug("Pulled LangSmith prompt template successfully.")

            self.agent = create_react_agent(
                llm=self.llm,
                tools=self.tools,
                prompt=self.prompt_template,
            )

            self.agent_executor = AgentExecutor(agent=self.agent, tools=self.tools, verbose=True)
            logger.info("AgentExecutor successfully created.")

        except Exception as e:
            logger.exception("Error initializing LLMService: %s", e)
            raise LLMError(f"Failed to initialize LLMService: {str(e)}")

    def _create_tools(self) -> List[Tool]:
        """Create and return a list of tools for the agent."""
        weather_service = WeatherTool()
        news_service = NewsTool()

        @tool("get_weather", return_direct=False)
        def get_weather(city: str) -> str:
            """Get real-time weather information for a given city."""
            try:
                logger.info("Fetching weather for city: %s", city)
                return weather_service.get_weather(city)
            except Exception as e:
                logger.exception("Error fetching weather for city '%s': %s", city, e)
                return f"Error fetching weather for {city}: {str(e)}"
    
        @tool("get_news", return_direct=False)
        def get_news(category: str = "business") -> str:
                """Fetch the latest news for a given category (e.g. business, sports, technology)."""
                try:
                    logger.info("Fetching news for category: %s", category)
                    return news_service.get_news(category)
                except Exception as e:
                    logger.exception("Error fetching news for category '%s': %s", category, e)
                    return f"Error fetching news for {category}: {str(e)}"
        
        @tool("search_web", return_direct=False)
        def search_web(query: str) -> str:
            """Search the web for up-to-date information using DuckDuckGo."""
            try:
                logger.info("Performing web search for query: %.80s...", query)
                search = DuckDuckGoSearchResults()
                result = search.run(query)
                # print("result",result)
                logger.debug("DuckDuckGo returned result length: %d", len(result) if result else 0)
                return result
            except Exception as e:
                logger.exception("Error performing web search for query '%s': %s", query, e)
                return f"Error: {str(e)}"

        return [get_weather, get_news, search_web]
    
    def generate_answer(
        self,
        context: str,
        question: str,
        conversation_history: Optional[List[Dict]] = None,
    ) -> str:
        """Generate an answer using the agent."""
        try:
            logger.info("Generating answer for question: %.80s...", question)
            history = []
            if conversation_history:
                for msg in conversation_history[-5:]:
                    role = msg.get("role", "user")
                    text = msg.get("text", "")
                    history.append(f"{role.capitalize()}: {text}")
            logger.debug("Loaded %d previous messages from conversation history.", len(history))

            system_prompt = (
                "You are an intelligent, articulate, and reliable assistant. "
                "Your responses should be thoughtful, precise, and naturally written. "
                "Rely on the provided context first; if something is unclear, reason carefully or use a tool when available. "
                "Be confident but not verbose — aim for clarity and depth. "
                "When relevant, include brief insights or examples that make your answer more useful or intuitive. "
                "Avoid speculation, filler phrases, or unnecessary repetition. "
                "If the question involves real-time topics like weather or news, use the appropriate tool. "
                "Always respond in a natural, conversational tone while maintaining professional quality.\n\n"
            )

            user_prompt = (
                f"{system_prompt}"
                f"Conversation history:\n{chr(10).join(history)}\n\n"
                f"Context:\n{context}\n\n"
                f"Question:\n{question}\n"
            )

            result = self.agent_executor.invoke({"input": user_prompt})
            # print("response agent",result)
            logger.debug("Agent execution result keys: %s", list(result.keys()))
            output = result.get("output", "").strip() or "No response."
            used_tool = False
            if isinstance(result, dict) and "intermediate_steps" in result:
                used_tool = any("tool" in str(step).lower() for step in result["intermediate_steps"])
                logger.info("Tool usage detected during reasoning: %s", used_tool)

            logger.info("Successfully generated response for question.")
            return {"output": output, "used_tool": used_tool}

        except Exception as e:
            logger.exception("Error generating answer: %s", e)
            raise LLMError(f"Error generating answer: {str(e)}")