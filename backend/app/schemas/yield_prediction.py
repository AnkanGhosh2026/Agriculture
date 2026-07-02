# """Schemas for yield prediction."""
# from pydantic import BaseModel, Field


# class YieldPredictionRequest(BaseModel):
#     crop_type: str
#     area_hectares: float = Field(..., gt=0)
#     soil_ph: float = Field(..., ge=0, le=14)
#     avg_rainfall_mm: float = Field(..., ge=0)
#     avg_temperature_c: float
#     fertilizer_kg_per_hectare: float = Field(default=0, ge=0)


# class YieldPredictionResponse(BaseModel):
#     crop_type: str
#     predicted_yield_tonnes: float
#     predicted_yield_per_hectare: float
#     confidence: float = Field(..., ge=0, le=1)
#     factors: dict[str, str] = {}
"""Schemas for yield prediction. Fields match the CropSense frontend form:
Crop Type, Area (Hectares), Soil pH, Expected Rainfall (mm), Fertilizer (kg)."""
from pydantic import BaseModel, Field


class YieldPredictionRequest(BaseModel):
    crop_type: str
    area_hectares: float = Field(..., gt=0)
    soil_ph: float = Field(..., ge=0, le=14)
    rainfall_mm: float = Field(..., ge=0)
    fertilizer_kg: float = Field(default=0, ge=0)


class YieldPredictionResponse(BaseModel):
    crop_type: str
    predicted_yield_per_hectare: float
    predicted_yield_tonnes: float
    prediction_source: str  # "trained_model" or "heuristic_fallback"
