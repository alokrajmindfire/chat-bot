import http.client
import json
from app.core.config import get_settings

class NewsTool:
    """Fetch latest business news headlines using RapidAPI's Google News API."""

    def __init__(self):
        settings = get_settings()
        self.api_key = settings.RAPIDAPI_KEY
        self.host = "google-news13.p.rapidapi.com"

    def get_news(self, category: str = "business", language: str = "en-US") -> str:
        """Fetch latest news headlines for a given category."""
        try:
            conn = http.client.HTTPSConnection(self.host)
            headers = {
                "x-rapidapi-key": self.api_key,
                "x-rapidapi-host": self.host,
            }

            endpoint = f"/{category}?lr={language}"
            conn.request("GET", endpoint, headers=headers)
            res = conn.getresponse()
            data = res.read()
            conn.close()

            result = json.loads(data.decode("utf-8"))
            print("news",result)
            articles = result.get("items", [])[:5]
            if not articles:
                return "No news found."

            news_text = "\n".join(
                [f"- {a.get('title', 'No title')} ({a.get('link', '')})" for a in articles]
            )

            return f"📰 Top {category.capitalize()} News:\n{news_text}"

        except Exception as e:
            return f"Error fetching {category} news: {str(e)}"
