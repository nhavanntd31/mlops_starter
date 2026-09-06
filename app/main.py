import time
import json
import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, HTTPException
from app.schemas import PredictRequest, PredictResponse, HealthResponse, ModelInfoResponse
from app.model_loader import model_holder
from app.predictors.tabular import predict_tabular
from app.metrics import PrometheusMiddleware, metrics_endpoint, PREDICTION_COUNT, PREDICTION_LATENCY

log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

logger = logging.getLogger("model-api")
logger.setLevel(logging.INFO)
handler = logging.FileHandler(log_dir / "app.log")
handler.setFormatter(logging.Formatter(json.dumps({
    "time": "%(asctime)s",
    "level": "%(levelname)s",
    "message": "%(message)s",
})))
logger.addHandler(handler)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        model_holder.load()
        logger.info("Model loaded successfully")
    except Exception as e:
        logger.warning(f"Model not loaded: {e}")
    yield


app = FastAPI(title="House Price Prediction API", lifespan=lifespan)
app.add_middleware(PrometheusMiddleware)
app.add_route("/metrics", metrics_endpoint)


@app.get("/health", response_model=HealthResponse)
def health():
    return HealthResponse(
        status="ok",
        model_loaded=model_holder.model is not None,
    )


@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    if model_holder.model is None:
        raise HTTPException(503, "Model not loaded")

    start = time.perf_counter()
    prediction = predict_tabular(req.features)
    latency = (time.perf_counter() - start) * 1000

    PREDICTION_COUNT.labels(model_version=model_holder.model_version).inc()
    PREDICTION_LATENCY.labels(model_version=model_holder.model_version).observe(latency / 1000)

    logger.info(json.dumps({
        "event": "prediction",
        "model_version": model_holder.model_version,
        "latency_ms": round(latency, 2),
        "prediction": prediction,
    }))

    return PredictResponse(
        prediction=prediction,
        latency_ms=round(latency, 2),
        model_version=model_holder.model_version,
    )


@app.get("/model-info", response_model=ModelInfoResponse)
def model_info():
    return ModelInfoResponse(
        model_name=model_holder.model_name,
        model_version=model_holder.model_version,
        features=model_holder.features,
    )
