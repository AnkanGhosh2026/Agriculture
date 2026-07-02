# """
# Crop yield prediction model wrapper.

# Replace the internals of `predict()` with a real trained regression
# model (e.g. scikit-learn / XGBoost loaded from YIELD_MODEL_PATH).
# For now this uses a simple heuristic formula so the API works end-to-end.
# """

# # Rough baseline yield (tonnes/hectare) per crop — placeholder values
# BASE_YIELD_PER_HECTARE = {
#     "wheat": 3.2,
#     "rice": 4.5,
#     "maize": 5.5,
#     "soybean": 2.8,
#     "cotton": 2.0,
#     "sugarcane": 70.0,
# }


# class YieldModel:
#     def __init__(self, model_path: str | None = None):
#         self.model_path = model_path
#         self._model = None  # load real model here, e.g. joblib.load(model_path)

#     def load(self):
#         # TODO: load actual trained model
#         # self._model = joblib.load(self.model_path)
#         pass

#     def predict(
#         self,
#         crop_type: str,
#         area_hectares: float,
#         soil_ph: float,
#         avg_rainfall_mm: float,
#         avg_temperature_c: float,
#         fertilizer_kg_per_hectare: float,
#     ) -> dict:
#         """
#         Returns predicted yield. Currently a heuristic — swap with real model.
#         """
#         # TODO: replace with self._model.predict([[features...]])
#         base = BASE_YIELD_PER_HECTARE.get(crop_type.lower(), 3.0)

#         # Simple adjustment factors (placeholder logic)
#         ph_factor = 1.0 - abs(6.5 - soil_ph) * 0.05
#         rainfall_factor = min(avg_rainfall_mm / 800, 1.2)
#         temp_factor = 1.0 - abs(25 - avg_temperature_c) * 0.01
#         fertilizer_factor = 1.0 + min(fertilizer_kg_per_hectare / 500, 0.3)

#         adjusted_per_hectare = max(
#             base * ph_factor * rainfall_factor * temp_factor * fertilizer_factor, 0
#         )
#         total_yield = round(adjusted_per_hectare * area_hectares, 2)

#         confidence = round(min(0.6 + (fertilizer_kg_per_hectare / 1000), 0.95), 2)

#         return {
#             "predicted_yield_tonnes": total_yield,
#             "predicted_yield_per_hectare": round(adjusted_per_hectare, 2),
#             "confidence": confidence,
#             "factors": {
#                 "soil_ph_impact": "favorable" if ph_factor > 0.9 else "suboptimal",
#                 "rainfall_impact": "favorable" if rainfall_factor > 0.8 else "low",
#                 "temperature_impact": "favorable" if temp_factor > 0.9 else "suboptimal",
#             },
#         }


# yield_model = YieldModel()


"""
Crop yield prediction model wrapper.

Accepts the simplified inputs the frontend collects (crop type, area,
soil pH, rainfall, fertilizer kg). If a trained model (from
ml/yield_prediction/train.py, trained on the Kaggle "Agriculture Crop
Yield" dataset) is present, its inputs are richer than what the frontend
collects (region, soil_type category, weather_condition, irrigation,
days_to_harvest) — so those extra fields are filled with reasonable
defaults. If no trained model is found, falls back to a simple heuristic
formula so the API always returns a result.

To activate real predictions:
    1. Train the model in Colab: see ml/yield_prediction/README.md
    2. Download yield_model.pkl + feature_columns.json from Colab
    3. Copy both into backend/app/ml/artifacts/
    4. Restart the API — this file auto-detects the files and loads them
"""
import json
import os

import joblib
import pandas as pd

from app.core.config import settings

# Baseline yield (tons/hectare) per crop — used in heuristic fallback mode
BASE_YIELD_PER_HECTARE = {
    "wheat": 3.2,
    "rice": 4.5,
    "maize": 5.5,
    "barley": 2.9,
    "soybean": 2.8,
    "cotton": 2.0,
    "sugarcane": 70.0,
}

# Defaults used to fill fields the frontend doesn't collect, when calling
# a trained model that expects the full Kaggle dataset schema.
DEFAULT_REGION = "North"
DEFAULT_WEATHER_CONDITION = "Sunny"
DEFAULT_DAYS_TO_HARVEST = 100
DEFAULT_IRRIGATION_USED = True


def _soil_ph_to_soil_type(soil_ph: float) -> str:
    """Rough mapping from pH to a soil type category, since the trained
    model (if present) expects a categorical soil type, not a pH value."""
    if soil_ph < 5.5:
        return "Sandy"
    if soil_ph < 6.5:
        return "Clay"
    if soil_ph < 7.5:
        return "Loam"
    return "Chalky"


class YieldModel:
    def __init__(self, model_path: str | None = None):
        self.model_path = model_path or settings.YIELD_MODEL_PATH
        self.feature_meta_path = os.path.join(
            os.path.dirname(self.model_path), "feature_columns.json"
        )
        self._pipeline = None
        self._feature_cols: list[str] = []
        self._loaded = False

        self.load()

    def load(self):
        """Loads the trained pipeline + feature metadata if present."""
        if not os.path.exists(self.model_path) or not os.path.exists(self.feature_meta_path):
            self._loaded = False
            return

        self._pipeline = joblib.load(self.model_path)
        with open(self.feature_meta_path) as f:
            meta = json.load(f)
        self._feature_cols = meta["feature_cols"]
        self._loaded = True

    @property
    def is_using_real_model(self) -> bool:
        return self._loaded

    def predict(
        self,
        crop_type: str,
        soil_ph: float,
        rainfall_mm: float,
        fertilizer_kg: float,
        area_hectares: float,
    ) -> dict:
        if self._loaded:
            return self._predict_real(crop_type, soil_ph, rainfall_mm, fertilizer_kg, area_hectares)
        return self._predict_heuristic(crop_type, rainfall_mm, fertilizer_kg)

    def _predict_real(
        self, crop_type: str, soil_ph: float, rainfall_mm: float,
        fertilizer_kg: float, area_hectares: float,
    ) -> dict:
        # Approximate fertilizer_kg (total for the farm) as a per-hectare
        # amount, then convert to the boolean the trained model expects.
        fertilizer_kg_per_hectare = fertilizer_kg / area_hectares if area_hectares else 0
        fertilizer_used = fertilizer_kg_per_hectare > 20  # rough threshold

        row = pd.DataFrame([{
            "Region": DEFAULT_REGION,
            "Soil_Type": _soil_ph_to_soil_type(soil_ph),
            "Crop": crop_type,
            "Rainfall_mm": rainfall_mm,
            "Temperature_Celsius": 25,  # not collected by frontend; use a neutral default
            "Fertilizer_Used": int(fertilizer_used),
            "Irrigation_Used": int(DEFAULT_IRRIGATION_USED),
            "Weather_Condition": DEFAULT_WEATHER_CONDITION,
            "Days_to_Harvest": DEFAULT_DAYS_TO_HARVEST,
        }])[self._feature_cols]

        prediction = float(self._pipeline.predict(row)[0])
        return {
            "predicted_yield_per_hectare": round(max(prediction, 0), 3),
            "model_used": "trained_model",
        }

    def _predict_heuristic(
        self, crop_type: str, rainfall_mm: float, fertilizer_kg: float,
    ) -> dict:
        base = BASE_YIELD_PER_HECTARE.get(crop_type.lower(), 3.0)
        rainfall_factor = min(rainfall_mm / 800, 1.2)
        fertilizer_factor = 1.0 + min(fertilizer_kg / 500, 0.3)

        adjusted = max(base * rainfall_factor * fertilizer_factor, 0)
        return {
            "predicted_yield_per_hectare": round(adjusted, 3),
            "model_used": "heuristic_fallback",
        }


yield_model = YieldModel()