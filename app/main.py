import logging
import json
import sys
from datetime import datetime
from fastapi import FastAPI, HTTPException
from app.schemas import PredictRequest, PredictResponse, HealthResponse, ModelInfoResponse
from app.model_loader import model_holder
from app.predictors.tabular import predict_price
from app.metrics import PrometheusMiddleware, metrics_endpoint

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
        }
        return json.dumps(log_data)

handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(JSONFormatter())
logger = logging.getLogger("house-price-api")
logger.addHandler(handler)
logger.setLevel(logging.INFO)

app = FastAPI(title="House Price Prediction API", version="0.1.0")
app.add_middleware(PrometheusMiddleware)
app.add_route("/metrics", metrics_endpoint, methods=["GET"])

@app.on_event("startup")
def startup_event():
    try:
        model_holder.load()
        logger.info("Model loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load model: {e}")

@app.get("/health", response_model=HealthResponse)
def health():
    return HealthResponse(
        status="healthy" if model_holder.is_loaded else "unhealthy",
        model_loaded=model_holder.is_loaded,
        timestamp=datetime.now().isoformat(),
    )

@app.get("/model-info", response_model=ModelInfoResponse)
def model_info():
    if not model_holder.is_loaded:
        raise HTTPException(status_code=503, detail="Model not loaded")
    return ModelInfoResponse(
        model_type="GradientBoostingRegressor",
        model_version=model_holder.version,
        features=["area", "bedrooms", "bathrooms", "age", "garage", "location"],
        loaded_at=model_holder.loaded_at,
    )

@app.post("/predict", response_model=PredictResponse)
def predict(request: PredictRequest):
    if not model_holder.is_loaded:
        raise HTTPException(status_code=503, detail="Model not loaded")
    try:
        price = predict_price(
            area=request.area,
            bedrooms=request.bedrooms,
            bathrooms=request.bathrooms,
            age=request.age,
            garage=request.garage,
            location=request.location,
        )
        logger.info(f"Prediction: {price:.2f} for {request.dict()}")
        return PredictResponse(
            predicted_price=round(price, 2),
            model_version=model_holder.version,
            timestamp=datetime.now().isoformat(),
        )
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
