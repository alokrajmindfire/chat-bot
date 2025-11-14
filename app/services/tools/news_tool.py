import http.client
import json
from app.config.config import get_settings
from app.config.logger import logger

class NewsTool:
    """Fetch latest business news headlines using RapidAPI's Google News API."""

    def __init__(self):
        settings = get_settings()
        self.api_key = settings.RAPIDAPI_KEY
        self.host = "google-news13.p.rapidapi.com"
        logger.info("Initialized NewsTool with host: %s", self.host)

    def get_news(self, category: str = "business", language: str = "en-US") -> str:
        """Fetch latest news headlines for a given category."""
        logger.info("Fetching news for category: %s (language: %s)", category, language)
        try:
            conn = http.client.HTTPSConnection(self.host)
            headers = {
                "x-rapidapi-key": self.api_key,
                "x-rapidapi-host": self.host,
            }

            endpoint = f"/{category}?lr={language}"
            logger.debug("Sending GET request to endpoint: %s", endpoint)
            conn.request("GET", endpoint, headers=headers)
            res = conn.getresponse()
            data = res.read()
            conn.close()
            if res.status != 200:
                logger.warning("Non-200 response: %d %s", res.status, res.reason)
                return f"Failed to fetch {category} news. API responded with status {res.status}."

            result = json.loads(data.decode("utf-8"))
            logger.debug("API response received successfully for category: %s", category)
            # print("news",result)
            articles = result.get("items", [])[:5]
            if not articles:
                logger.info("No news articles found for category: %s", category)
                return "No news found."

            news_text = "\n".join(
                [f"- {a.get('title', 'No title')} ({a.get('link', '')})" for a in articles]
            )
            logger.info("Fetched %d news articles for category: %s", len(articles), category)
            return f"📰 Top {category.capitalize()} News:\n{news_text}"

        except Exception as e:
            logger.exception("Error fetching %s news: %s", category, e)
            return f"Error fetching {category} news: {str(e)}"
