"""Schemas for weather insights."""
from pydantic import BaseModel


class WeatherRequest(BaseModel):
    latitude: float
    longitude: float


class DailyForecast(BaseModel):
    date: str
    temp_min_c: float
    temp_max_c: float
    humidity_pct: float
    precipitation_mm: float
    condition: str


class WeatherInsightResponse(BaseModel):
    location: str
    current_temp_c: float
    current_condition: str
    forecast: list[DailyForecast]
    farming_advisory: list[str] = []
