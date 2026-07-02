"""Routes for crop yield prediction."""
from fastapi import APIRouter

from app.schemas.yield_prediction import YieldPredictionRequest, YieldPredictionResponse
from app.services.yield_service import yield_service

router = APIRouter(prefix="/yield-prediction", tags=["Yield Prediction"])


@router.post("/predict", response_model=YieldPredictionResponse)
async def predict_yield(request: YieldPredictionRequest):
    result = await yield_service.predict(request)
    return result
