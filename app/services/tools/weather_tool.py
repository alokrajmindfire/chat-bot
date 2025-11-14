from datetime import datetime
import requests
from app.config.config import get_settings
from app.config.logger import logger


class WeatherTool:
    def __init__(self):
        settings = get_settings()
        self.api_key = settings.OPENWEATHER_API_KEY
        logger.info("Initialized WeatherTool with OpenWeather API key: %s...", self.api_key[:5] + "***")
    def get_weather(self, city: str) -> str:
        """Fetch real-time weather data for a given city."""
        try:
            url = (
                f"http://api.openweathermap.org/data/2.5/weather?"
                f"q={city}&appid={self.api_key}&units=metric"
            )
            logger.debug("Sending request to OpenWeather API: %s", url)
            resp = requests.get(url, timeout=10)
            data = resp.json()

            if resp.status_code != 200:
                logger.warning(
                    "Failed to fetch weather for %s — Status: %d, Message: %s",
                    city,
                    resp.status_code,
                    data.get("message", "Unknown error"),
                )
                return f"❌ Could not fetch weather for **{city}**. ({data.get('message', 'Unknown error')})"

            temp = data["main"]["temp"]
            feels = data["main"]["feels_like"]
            desc = data["weather"][0]["description"].capitalize()
            humidity = data["main"]["humidity"]
            wind = data["wind"]["speed"]
            city_name = data["name"]
            logger.info(
                "Weather data fetched successfully for %s: %s, %.1f°C",
                city_name,
                desc,
                temp,
            )
            return (
                f"🌤️ **Weather in {city_name}:** {desc}\n\n"
                f"🌡️ Temperature: {temp}°C (feels like {feels}°C)\n"
                f"💧 Humidity: {humidity}%\n"
                f"💨 Wind Speed: {wind} m/s\n"
                f"🕒 Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )

        except requests.exceptions.RequestException as e:
            logger.error("Network error while fetching weather for %s: %s", city, e)
            return f"⚠️ Network error while fetching weather for **{city}**: {e}"

        except Exception as e:
            logger.exception("Unexpected error fetching weather for %s: %s", city, e)
            return f"⚠️ Error fetching weather for **{city}**: {e}"
