"""Phase 5: FastAPI serving layer for the XGBoost risk model.
Provides a production-ready REST API with health checks and input validation.
"""
from __future__ import annotations

import time
from contextlib import asynccontextmanager
from pathlib import Path

import mlflow
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

ROOT = Path(__file__).resolve().parents[2]


class AssetFeatures(BaseModel):
    avg_vibration: float
    std_vibration: float
    avg_power: float
    outlier_count: int
    wo_count: int
    sla_breach_count: int


class PredictionRequest(BaseModel):
    assets: list[AssetFeatures]


class PredictionResponse(BaseModel):
    predictions: list[float]
    probabilities: list[float]


model = None
model_load_time = 0.0


@asynccontextmanager
async def lifespan(app: FastAPI):
    global model, model_load_time
    start = time.time()
    tracking_uri = f"sqlite:///{ROOT}/mlflow.db"
    mlflow.set_tracking_uri(tracking_uri)

    client = mlflow.tracking.MlflowClient(tracking_uri)
    experiment = client.get_experiment_by_name("opstwin_asset_risk_prediction")
    if not experiment:
        raise RuntimeError("Experiment not found. Run Phase 4 first.")

    # Fetch the latest ground-truth model run
    runs = client.search_runs(
        experiment.experiment_id,
        filter_string="params.target = 'target_label'",
        order_by=["attributes.start_time DESC"],
        max_results=1,
    )
    if not runs:
        raise RuntimeError("No ground-truth model runs found.")

    run_id = runs[0].info.run_id
    model_uri = f"runs:/{run_id}/xgb_risk_model"
    model = mlflow.xgboost.load_model(model_uri)
    model_load_time = time.time() - start
    print(f"[API] Loaded model from run {run_id} in {model_load_time:.2f}s")
    yield


app = FastAPI(
    title="OpsTwin Risk Prediction API",
    description="Serves the XGBoost asset risk model trained in Phase 4.",
    version="1.0.0",
    docs_url="/",
    lifespan=lifespan,
)


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "model_load_time_sec": round(model_load_time, 3),
    }


@app.post("/predict", response_model=PredictionResponse)
def predict_risk(request: PredictionRequest):
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    df = pd.DataFrame([asset.model_dump() for asset in request.assets])
    feature_cols = [
        "avg_vibration", "std_vibration", "avg_power",
        "outlier_count", "wo_count", "sla_breach_count",
    ]

    for col in feature_cols:
        if col not in df.columns:
            df[col] = 0

    X = df[feature_cols]
    probs = model.predict_proba(X)[:, 1].tolist()
    preds = model.predict(X).tolist()

    return PredictionResponse(predictions=preds, probabilities=probs)