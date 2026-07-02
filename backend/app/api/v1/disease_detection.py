"""Routes for crop disease detection."""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from app.schemas.disease import DiseaseDetectionResponse
from app.services.disease_service import disease_service

router = APIRouter(prefix="/disease-detection", tags=["Disease Detection"])

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/jpg"}


@router.post("/predict", response_model=DiseaseDetectionResponse)
async def predict_disease(
    file: UploadFile = File(..., description="Image of the crop leaf/plant"),
    crop_type: str | None = Form(None, description="Optional crop type hint, e.g. 'tomato'"),
):
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file.content_type}. Use JPEG or PNG.",
        )

    image_bytes = await file.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    result = await disease_service.detect(image_bytes, crop_type)
    return result
