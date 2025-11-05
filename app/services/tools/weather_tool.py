# app/services/ai/tools/weather_tool.py

import requests
from datetime import datetime
from app.core.config import get_settings


class WeatherTool:
    def __init__(self):
        settings = get_settings()
        self.api_key = settings.OPENWEATHER_API_KEY

    def get_weather(self, city: str) -> str:
        """Fetch real-time weather data for a given city."""
        try:
            url = (
                f"http://api.openweathermap.org/data/2.5/weather?"
                f"q={city}&appid={self.api_key}&units=metric"
            )
            resp = requests.get(url, timeout=10)
            data = resp.json()

            if resp.status_code != 200:
                return f"❌ Could not fetch weather for **{city}**. ({data.get('message', 'Unknown error')})"

            temp = data["main"]["temp"]
            feels = data["main"]["feels_like"]
            desc = data["weather"][0]["description"].capitalize()
            humidity = data["main"]["humidity"]
            wind = data["wind"]["speed"]
            city_name = data["name"]

            return (
                f"🌤️ **Weather in {city_name}:** {desc}\n\n"
                f"🌡️ Temperature: {temp}°C (feels like {feels}°C)\n"
                f"💧 Humidity: {humidity}%\n"
                f"💨 Wind Speed: {wind} m/s\n"
                f"🕒 Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )

        except Exception as e:
            return f"⚠️ Error fetching weather: {e}"
