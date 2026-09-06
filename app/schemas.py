from pydantic import BaseModel


class PredictRequest(BaseModel):
    features: dict


class PredictResponse(BaseModel):
    prediction: float
    latency_ms: float
    model_version: str


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool


class ModelInfoResponse(BaseModel):
    model_name: str
    model_version: str
    features: list
