"""Routes for weather insights."""
from fastapi import APIRouter, Query

from app.schemas.weather import WeatherInsightResponse
from app.services.weather_service import weather_service

router = APIRouter(prefix="/weather", tags=["Weather Insights"])


@router.get("/insights", response_model=WeatherInsightResponse)
async def get_weather_insights(
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180),
):
    result = await weather_service.get_insights(latitude, longitude)
    return result
