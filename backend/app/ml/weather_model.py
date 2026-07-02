# """
# Weather insights helper.

# This doesn't "predict" weather itself — it calls an external weather API
# (e.g. OpenWeatherMap) and derives simple farming advisories from the data.
# """
# import httpx
# from app.core.config import settings


# class WeatherModel:
#     def __init__(self, api_key: str | None = None, base_url: str | None = None):
#         self.api_key = api_key or settings.WEATHER_API_KEY
#         self.base_url = base_url or settings.WEATHER_API_BASE_URL

#     async def get_forecast(self, latitude: float, longitude: float) -> dict:
#         """
#         Fetches current weather + forecast for a location.
#         Falls back to mock data if no API key is configured.
#         """
#         if not self.api_key:
#             return self._mock_forecast()

#         async with httpx.AsyncClient(timeout=10) as client:
#             resp = await client.get(
#                 f"{self.base_url}/forecast",
#                 params={
#                     "lat": latitude,
#                     "lon": longitude,
#                     "appid": self.api_key,
#                     "units": "metric",
#                 },
#             )
#             resp.raise_for_status()
#             return resp.json()

#     def _mock_forecast(self) -> dict:
#         """Placeholder data used when WEATHER_API_KEY is not set."""
#         return {
#             "location": "Unknown (mock data — set WEATHER_API_KEY)",
#             "current": {"temp_c": 28.5, "condition": "Partly Cloudy"},
#             "forecast": [
#                 {
#                     "date": "Day 1",
#                     "temp_min_c": 22.0,
#                     "temp_max_c": 31.0,
#                     "humidity_pct": 65,
#                     "precipitation_mm": 2.5,
#                     "condition": "Partly Cloudy",
#                 },
#                 {
#                     "date": "Day 2",
#                     "temp_min_c": 21.5,
#                     "temp_max_c": 29.0,
#                     "humidity_pct": 72,
#                     "precipitation_mm": 8.0,
#                     "condition": "Light Rain",
#                 },
#                 {
#                     "date": "Day 3",
#                     "temp_min_c": 23.0,
#                     "temp_max_c": 32.0,
#                     "humidity_pct": 55,
#                     "precipitation_mm": 0.0,
#                     "condition": "Sunny",
#                 },
#             ],
#         }

#     def generate_advisory(self, forecast_data: dict) -> list[str]:
#         """Derives simple farming tips from forecast data."""
#         advisories = []
#         for day in forecast_data.get("forecast", []):
#             if day["precipitation_mm"] > 5:
#                 advisories.append(
#                     f"{day['date']}: Heavy rain expected — delay irrigation and pesticide spraying."
#                 )
#             if day["temp_max_c"] > 35:
#                 advisories.append(
#                     f"{day['date']}: High temperature — ensure adequate crop irrigation."
#                 )
#             if day["humidity_pct"] > 80:
#                 advisories.append(
#                     f"{day['date']}: High humidity — monitor for fungal disease risk."
#                 )
#         if not advisories:
#             advisories.append("Conditions look favorable — no immediate action needed.")
#         return advisories


# weather_model = WeatherModel()

"""
Weather insights helper.

Calls the OpenWeatherMap free "5 day / 3 hour forecast" API
(https://openweathermap.org/forecast5) and normalizes the response into
the shape weather_service.py expects: {location, current, forecast: [...]}.

Falls back to mock data if WEATHER_API_KEY is not set, so the API keeps
working during development without a key.
"""
from collections import defaultdict
from datetime import datetime

import httpx
from app.core.config import settings


class WeatherModel:
    def __init__(self, api_key: str | None = None, base_url: str | None = None):
        self.api_key = api_key or settings.WEATHER_API_KEY
        self.base_url = base_url or settings.WEATHER_API_BASE_URL

    async def get_forecast(self, latitude: float, longitude: float) -> dict:
        """
        Fetches current weather + forecast for a location and normalizes
        it into our internal schema. Falls back to mock data if no API
        key is configured, or if the API call fails for any reason.
        """
        if not self.api_key:
            return self._mock_forecast()

        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(
                    f"{self.base_url}/forecast",
                    params={
                        "lat": latitude,
                        "lon": longitude,
                        "appid": self.api_key,
                        "units": "metric",
                    },
                )
                resp.raise_for_status()
                raw = resp.json()
            return self._normalize(raw, latitude, longitude)
        except httpx.HTTPStatusError as e:
            # Common case: brand-new API keys take up to ~2 hours to activate,
            # so a 401 right after signup is expected, not a bug.
            print(f"⚠️  Weather API call failed ({e.response.status_code}): "
                  f"{e.response.text[:200]}. Falling back to mock data.")
            return self._mock_forecast()
        except Exception as e:
            print(f"⚠️  Weather API call failed: {e}. Falling back to mock data.")
            return self._mock_forecast()

    def _normalize(self, raw: dict, latitude: float, longitude: float) -> dict:
        """
        OpenWeatherMap's free forecast endpoint returns 3-hour steps for
        the next 5 days. We group these into daily min/max/avg buckets to
        match our DailyForecast schema (one entry per day).
        """
        city_info = raw.get("city", {})
        location = city_info.get("name") or f"{latitude},{longitude}"
        if city_info.get("country"):
            location = f"{location}, {city_info['country']}"

        entries = raw.get("list", [])
        if not entries:
            return self._mock_forecast()

        # Current conditions = the very first 3-hour entry
        first = entries[0]
        current = {
            "temp_c": round(first["main"]["temp"], 1),
            "condition": first["weather"][0]["main"] if first.get("weather") else "Unknown",
        }

        # Group 3-hourly entries by calendar date
        by_date = defaultdict(list)
        for entry in entries:
            date_str = entry["dt_txt"].split(" ")[0]  # "2026-07-02 15:00:00" -> "2026-07-02"
            by_date[date_str].append(entry)

        forecast = []
        for date_str, day_entries in list(by_date.items())[:5]:  # cap at 5 days
            temps = [e["main"]["temp"] for e in day_entries]
            humidity = [e["main"]["humidity"] for e in day_entries]
            precipitation = sum(
                e.get("rain", {}).get("3h", 0) + e.get("snow", {}).get("3h", 0)
                for e in day_entries
            )
            # Use the most common weather condition that day as the label
            conditions = [e["weather"][0]["main"] for e in day_entries if e.get("weather")]
            condition = max(set(conditions), key=conditions.count) if conditions else "Unknown"

            try:
                formatted_date = datetime.strptime(date_str, "%Y-%m-%d").strftime("%b %d")
            except ValueError:
                formatted_date = date_str

            forecast.append({
                "date": formatted_date,
                "temp_min_c": round(min(temps), 1),
                "temp_max_c": round(max(temps), 1),
                "humidity_pct": round(sum(humidity) / len(humidity), 1),
                "precipitation_mm": round(precipitation, 1),
                "condition": condition,
            })

        return {"location": location, "current": current, "forecast": forecast}

    def _mock_forecast(self) -> dict:
        """Placeholder data used when WEATHER_API_KEY is not set or the API call fails."""
        return {
            "location": "Unknown (mock data — set WEATHER_API_KEY)",
            "current": {"temp_c": 28.5, "condition": "Partly Cloudy"},
            "forecast": [
                {
                    "date": "Day 1",
                    "temp_min_c": 22.0,
                    "temp_max_c": 31.0,
                    "humidity_pct": 65,
                    "precipitation_mm": 2.5,
                    "condition": "Partly Cloudy",
                },
                {
                    "date": "Day 2",
                    "temp_min_c": 21.5,
                    "temp_max_c": 29.0,
                    "humidity_pct": 72,
                    "precipitation_mm": 8.0,
                    "condition": "Light Rain",
                },
                {
                    "date": "Day 3",
                    "temp_min_c": 23.0,
                    "temp_max_c": 32.0,
                    "humidity_pct": 55,
                    "precipitation_mm": 0.0,
                    "condition": "Sunny",
                },
            ],
        }

    def generate_advisory(self, forecast_data: dict) -> list[str]:
        """Derives simple farming tips from forecast data."""
        advisories = []
        for day in forecast_data.get("forecast", []):
            if day["precipitation_mm"] > 5:
                advisories.append(
                    f"{day['date']}: Heavy rain expected — delay irrigation and pesticide spraying."
                )
            if day["temp_max_c"] > 35:
                advisories.append(
                    f"{day['date']}: High temperature — ensure adequate crop irrigation."
                )
            if day["humidity_pct"] > 80:
                advisories.append(
                    f"{day['date']}: High humidity — monitor for fungal disease risk."
                )
        if not advisories:
            advisories.append("Conditions look favorable — no immediate action needed.")
        return advisories


weather_model = WeatherModel()