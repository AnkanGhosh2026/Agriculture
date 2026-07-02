"""Business logic for weather insights."""
from app.ml.weather_model import weather_model
from app.schemas.weather import WeatherInsightResponse, DailyForecast


class WeatherService:
    def __init__(self):
        self.model = weather_model

    async def get_insights(self, latitude: float, longitude: float) -> WeatherInsightResponse:
        raw = await self.model.get_forecast(latitude, longitude)

        # Normalize either real API response or mock response into our schema.
        # NOTE: adjust this mapping once a real weather API is wired in.
        location = raw.get("location", f"{latitude},{longitude}")
        current = raw.get("current", {"temp_c": 0, "condition": "Unknown"})
        forecast_raw = raw.get("forecast", [])

        forecast = [
            DailyForecast(
                date=day["date"],
                temp_min_c=day["temp_min_c"],
                temp_max_c=day["temp_max_c"],
                humidity_pct=day["humidity_pct"],
                precipitation_mm=day["precipitation_mm"],
                condition=day["condition"],
            )
            for day in forecast_raw
        ]

        advisory = self.model.generate_advisory(raw)

        return WeatherInsightResponse(
            location=location,
            current_temp_c=current["temp_c"],
            current_condition=current["condition"],
            forecast=forecast,
            farming_advisory=advisory,
        )


weather_service = WeatherService()
