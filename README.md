# AI Agriculture Platform

An AI-powered platform offering:
- **Crop Disease Detection** — upload a leaf/plant image, get disease predictions + recommendations
- **Weather Insights** — location-based forecast + farming advisories
- **Yield Prediction** — estimate crop yield from soil, weather, and fertilizer inputs

## Tech Stack
- **Backend**: FastAPI (Python)
- **ML**: scikit-learn / custom models (currently stubbed with mock/heuristic logic — see `Next Steps`)

## Project Structure

```
backend/       FastAPI app (routes, services, ML wrappers, schemas)
ml/            Model training & experimentation (notebooks, training scripts)
data/          Datasets (raw / processed / external)
docs/          Architecture & API documentation
```

## Getting Started

### 1. Set up the backend

```bash
cd backend
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env          # then edit .env with your values
```

### 2. Run the API

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`
Interactive docs (Swagger UI): `http://localhost:8000/docs`

### 3. Try the endpoints

**Health check**
```bash
curl http://localhost:8000/health
```

**Disease detection** (multipart form upload)
```bash
curl -X POST http://localhost:8000/api/v1/disease-detection/predict \
  -F "file=@/path/to/leaf.jpg" \
  -F "crop_type=tomato"
```

**Weather insights**
```bash
curl "http://localhost:8000/api/v1/weather/insights?latitude=22.57&longitude=88.36"
```

**Yield prediction**
```bash
curl -X POST http://localhost:8000/api/v1/yield-prediction/predict \
  -H "Content-Type: application/json" \
  -d '{
    "crop_type": "wheat",
    "area_hectares": 10,
    "soil_ph": 6.5,
    "avg_rainfall_mm": 700,
    "avg_temperature_c": 24,
    "fertilizer_kg_per_hectare": 150
  }'
```

## Current State (Important)

| Feature | File | Current logic | Replace with |
|---|---|---|---|
| Disease Detection | `backend/app/ml/disease_model.py` | **Real PyTorch inference**, auto-falls back to mock scores if no trained model file is present | Train on your dataset — see `ml/disease_detection/README.md` |
| Weather Insights | `backend/app/ml/weather_model.py` | Mock data if no `WEATHER_API_KEY` set | Real weather API (OpenWeatherMap, etc.) — already wired, just add your key |
| Yield Prediction | `backend/app/ml/yield_model.py` | Simple heuristic formula | Trained regression model (scikit-learn/XGBoost) loaded from `YIELD_MODEL_PATH` |

## Training the Disease Detection Model

Full step-by-step guide: **`ml/disease_detection/README.md`**

Quick summary:
```bash
# 1. Download PlantVillage dataset from Kaggle, extract the 'color' folder to:
#    data/raw/plantvillage/color/

# 2. Install training deps and train
cd ml/disease_detection
pip install -r requirements.txt
python inspect_dataset.py   # verify dataset layout
python train.py             # trains + saves to saved_models/

# 3. Deploy into the backend (no code changes needed)
cp saved_models/disease_model.pt ../../backend/app/ml/artifacts/disease_model.pt

# 4. Restart the API — it auto-detects and loads the real model
```

## Next Steps

1. Train the disease detection model (see above)
2. Collect/source yield data and train `ml/yield_prediction/train.py` (regression model — not yet implemented, currently heuristic)
3. Sign up for a weather API (OpenWeatherMap is a good free option) and set `WEATHER_API_KEY` in `.env`
4. Add a database (models are stubbed in `backend/app/models/`) if you want to persist predictions/history
5. Add a frontend once the backend is stable
