"""
Train a crop yield prediction model on the "Agriculture Crop Yield" dataset.

Designed to run in Google Colab as a series of cells (copy each ## CELL ##
block into its own Colab cell), or as a single script if run locally.

Dataset: https://www.kaggle.com/datasets/samuelotiattakorah/agriculture-crop-yield
Columns: Region, Soil_Type, Crop, Rainfall_mm, Temperature_Celsius,
         Fertilizer_Used, Irrigation_Used, Weather_Condition, Days_to_Harvest,
         Yield_tons_per_hectare (target)

Output:
    yield_model.pkl          - trained model + preprocessing pipeline
    feature_columns.json     - exact feature order/encoding needed at inference
    training_metrics.json    - R2 / MAE / RMSE on held-out test set
"""

## CELL 1: Install & import ##
# !pip install -q scikit-learn pandas joblib kaggle

import json
import os

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


## CELL 2: Download dataset from Kaggle ##
"""
In Colab, run this first to authenticate with Kaggle:

    from google.colab import files
    files.upload()  # upload your kaggle.json (from kaggle.com/settings -> API -> Create New Token)

    !mkdir -p ~/.kaggle
    !mv kaggle.json ~/.kaggle/
    !chmod 600 ~/.kaggle/kaggle.json

    !kaggle datasets download -d samuelotiattakorah/agriculture-crop-yield
    !unzip -o agriculture-crop-yield.zip -d ./data

Then the CSV will be at ./data/crop_yield.csv (check the exact filename
after unzipping — Kaggle dataset filenames can vary slightly).
"""

DATA_PATH = "./data/crop_yield.csv"  # update if the actual filename differs
OUTPUT_DIR = "./saved_models"


## CELL 3: Load & inspect data ##
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    print(f"Loaded {len(df)} rows, {len(df.columns)} columns")
    print(df.columns.tolist())
    print(df.head())
    print(df.isnull().sum())
    return df


## CELL 4: Preprocessing + train/test split ##
CATEGORICAL_FEATURES = ["Region", "Soil_Type", "Crop", "Weather_Condition"]
BOOLEAN_FEATURES = ["Fertilizer_Used", "Irrigation_Used"]
NUMERIC_FEATURES = ["Rainfall_mm", "Temperature_Celsius", "Days_to_Harvest"]
TARGET = "Yield_tons_per_hectare"


def prepare_data(df: pd.DataFrame):
    # Drop rows with missing target
    df = df.dropna(subset=[TARGET])

    # Coerce boolean-like columns to 0/1 in case they're read as strings
    for col in BOOLEAN_FEATURES:
        if col in df.columns and df[col].dtype == object:
            df[col] = df[col].map({"True": 1, "False": 0, True: 1, False: 0}).fillna(df[col])

    feature_cols = [c for c in CATEGORICAL_FEATURES + BOOLEAN_FEATURES + NUMERIC_FEATURES if c in df.columns]
    X = df[feature_cols]
    y = df[TARGET]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    return X_train, X_test, y_train, y_test, feature_cols


## CELL 5: Build pipeline (preprocessing + model) ##
def build_pipeline(feature_cols: list[str]) -> Pipeline:
    categorical_present = [c for c in CATEGORICAL_FEATURES if c in feature_cols]
    numeric_present = [c for c in NUMERIC_FEATURES + BOOLEAN_FEATURES if c in feature_cols]

    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_present),
            ("num", StandardScaler(), numeric_present),
        ]
    )

    model = RandomForestRegressor(
        n_estimators=200,
        max_depth=15,
        min_samples_leaf=3,
        n_jobs=-1,
        random_state=42,
    )

    pipeline = Pipeline(steps=[
        ("preprocessor", preprocessor),
        ("regressor", model),
    ])
    return pipeline


## CELL 6: Train & evaluate ##
def train_and_evaluate():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    df = load_data(DATA_PATH)
    X_train, X_test, y_train, y_test, feature_cols = prepare_data(df)

    pipeline = build_pipeline(feature_cols)
    print("\nTraining RandomForestRegressor...")
    pipeline.fit(X_train, y_train)

    y_pred = pipeline.predict(X_test)
    r2 = r2_score(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))

    print(f"\nTest R²:   {r2:.4f}")
    print(f"Test MAE:  {mae:.4f} tons/hectare")
    print(f"Test RMSE: {rmse:.4f} tons/hectare")

    # Feature importance (helps sanity-check the model learned something sensible)
    try:
        cat_encoder = pipeline.named_steps["preprocessor"].named_transformers_["cat"]
        cat_names = cat_encoder.get_feature_names_out(
            [c for c in CATEGORICAL_FEATURES if c in feature_cols]
        ).tolist()
        num_names = [c for c in NUMERIC_FEATURES + BOOLEAN_FEATURES if c in feature_cols]
        all_feature_names = cat_names + num_names
        importances = pipeline.named_steps["regressor"].feature_importances_
        top_features = sorted(zip(all_feature_names, importances), key=lambda x: x[1], reverse=True)[:10]
        print("\nTop 10 most important features:")
        for name, imp in top_features:
            print(f"  {name:35s} {imp:.4f}")
    except Exception as e:
        print(f"(Skipping feature importance display: {e})")

    # Save model
    model_path = os.path.join(OUTPUT_DIR, "yield_model.pkl")
    joblib.dump(pipeline, model_path)
    print(f"\nSaved model to: {model_path}")

    # Save feature column order/metadata needed at inference time
    feature_meta_path = os.path.join(OUTPUT_DIR, "feature_columns.json")
    with open(feature_meta_path, "w") as f:
        json.dump({
            "feature_cols": feature_cols,
            "categorical": [c for c in CATEGORICAL_FEATURES if c in feature_cols],
            "numeric": [c for c in NUMERIC_FEATURES + BOOLEAN_FEATURES if c in feature_cols],
            "target": TARGET,
        }, f, indent=2)
    print(f"Saved feature metadata to: {feature_meta_path}")

    # Save metrics
    metrics_path = os.path.join(OUTPUT_DIR, "training_metrics.json")
    with open(metrics_path, "w") as f:
        json.dump({"r2": r2, "mae": mae, "rmse": rmse, "n_train": len(X_train), "n_test": len(X_test)}, f, indent=2)
    print(f"Saved metrics to: {metrics_path}")

    print("\nNext step: download yield_model.pkl and feature_columns.json from Colab,")
    print("then copy them into backend/app/ml/artifacts/ in your project.")
    print("See ml/yield_prediction/README.md for exact instructions.")

    return pipeline


## CELL 7: Run everything ##
if __name__ == "__main__":
    train_and_evaluate()