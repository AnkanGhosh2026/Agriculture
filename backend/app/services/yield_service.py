# """Business logic for crop yield prediction."""
# from app.ml.yield_model import yield_model
# from app.schemas.yield_prediction import YieldPredictionRequest, YieldPredictionResponse


# class YieldService:
#     def __init__(self):
#         self.model = yield_model

#     async def predict(self, request: YieldPredictionRequest) -> YieldPredictionResponse:
#         result = self.model.predict(
#             crop_type=request.crop_type,
#             area_hectares=request.area_hectares,
#             soil_ph=request.soil_ph,
#             avg_rainfall_mm=request.avg_rainfall_mm,
#             avg_temperature_c=request.avg_temperature_c,
#             fertilizer_kg_per_hectare=request.fertilizer_kg_per_hectare,
#         )

#         return YieldPredictionResponse(
#             crop_type=request.crop_type,
#             predicted_yield_tonnes=result["predicted_yield_tonnes"],
#             predicted_yield_per_hectare=result["predicted_yield_per_hectare"],
#             confidence=result["confidence"],
#             factors=result["factors"],
#         )


# yield_service = YieldService()

"""Business logic for crop yield prediction."""
from app.ml.yield_model import yield_model
from app.schemas.yield_prediction import YieldPredictionRequest, YieldPredictionResponse


class YieldService:
    def __init__(self):
        self.model = yield_model

    async def predict(self, request: YieldPredictionRequest) -> YieldPredictionResponse:
        result = self.model.predict(
            crop_type=request.crop_type,
            soil_ph=request.soil_ph,
            rainfall_mm=request.rainfall_mm,
            fertilizer_kg=request.fertilizer_kg,
            area_hectares=request.area_hectares,
        )

        per_hectare = result["predicted_yield_per_hectare"]
        total_tonnes = round(per_hectare * request.area_hectares, 3)

        return YieldPredictionResponse(
            crop_type=request.crop_type,
            predicted_yield_per_hectare=per_hectare,
            predicted_yield_tonnes=total_tonnes,
            prediction_source=result["model_used"],
        )


yield_service = YieldService()