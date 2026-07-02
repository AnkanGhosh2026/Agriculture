"""Business logic for crop disease detection."""
from app.ml.disease_model import disease_model
from app.schemas.disease import DiseaseDetectionResponse

# Keyword -> recommendations. Matched case-insensitively against the
# predicted disease name, so this works for both the mock class names
# and real PlantVillage class names (e.g. "Tomato - Late blight",
# "Apple - Apple scab", "Corn - Common rust").
RECOMMENDATIONS_BY_KEYWORD = {
    "healthy": ["No action needed — crop appears healthy."],
    "blight": [
        "Remove and destroy infected leaves.",
        "Apply a copper-based fungicide.",
        "Avoid overhead irrigation to reduce leaf wetness.",
    ],
    "powdery mildew": [
        "Improve air circulation between plants.",
        "Apply sulfur-based fungicide.",
        "Avoid excess nitrogen fertilizer.",
    ],
    "bacterial spot": [
        "Use disease-free certified seeds.",
        "Apply copper-based bactericide.",
        "Rotate crops to reduce pathogen buildup.",
    ],
    "rust": [
        "Apply appropriate fungicide at first sign of infection.",
        "Remove volunteer plants and weeds that host rust.",
    ],
    "mosaic virus": [
        "Remove and destroy infected plants.",
        "Control aphid populations (common vector).",
        "Use virus-resistant crop varieties.",
    ],
    "scab": [
        "Prune to improve airflow and reduce humidity around leaves.",
        "Apply a fungicide labeled for scab, starting at bud break.",
        "Rake and destroy fallen leaves in autumn to reduce spores.",
    ],
    "black rot": [
        "Prune out and destroy infected wood/fruit.",
        "Apply fungicide during the growing season.",
        "Improve air circulation via pruning.",
    ],
    "leaf spot": [
        "Remove and destroy affected leaves.",
        "Avoid overhead watering; water at the base instead.",
        "Apply an appropriate fungicide if severe.",
    ],
    "yellow leaf curl": [
        "Control whitefly populations (main vector).",
        "Remove and destroy infected plants promptly.",
        "Use resistant varieties where available.",
    ],
    "haunglongbing": [
        "Remove and destroy infected trees — this disease has no cure.",
        "Control psyllid insect populations aggressively.",
        "Use certified disease-free planting material.",
    ],
    "early blight": [
        "Remove lower infected leaves promptly.",
        "Apply fungicide preventively in humid conditions.",
        "Rotate crops and avoid planting in the same spot yearly.",
    ],
}

DEFAULT_RECOMMENDATIONS = [
    "Isolate or monitor the affected plant closely.",
    "Consult a local agricultural extension office for confirmation.",
    "Consider a broad-spectrum fungicide/bactericide if symptoms spread.",
]


def _get_recommendations(disease_name: str) -> list[str]:
    name_lower = disease_name.lower()
    for keyword, recs in RECOMMENDATIONS_BY_KEYWORD.items():
        if keyword in name_lower:
            return recs
    return DEFAULT_RECOMMENDATIONS


class DiseaseService:
    def __init__(self):
        self.model = disease_model

    async def detect(self, image_bytes: bytes, crop_type: str | None = None) -> DiseaseDetectionResponse:
        predictions = self.model.predict(image_bytes)
        top = predictions[0]
        recommendations = _get_recommendations(top.disease_name)

        return DiseaseDetectionResponse(
            crop_type=crop_type,
            predictions=predictions,
            top_prediction=top,
            recommendations=recommendations,
        )


disease_service = DiseaseService()
