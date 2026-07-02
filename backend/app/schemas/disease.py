"""Schemas for crop disease detection."""
from pydantic import BaseModel, Field


class DiseasePrediction(BaseModel):
    disease_name: str
    confidence: float = Field(..., ge=0, le=1)
    is_healthy: bool


class DiseaseDetectionResponse(BaseModel):
    crop_type: str | None = None
    predictions: list[DiseasePrediction]
    top_prediction: DiseasePrediction
    recommendations: list[str] = []
