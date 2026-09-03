from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class PredictRequest(BaseModel):
    area: float = Field(..., gt=0, description="Area in sqm")
    bedrooms: int = Field(..., ge=0)
    bathrooms: int = Field(..., ge=0)
    age: int = Field(..., ge=0)
    garage: int = Field(..., ge=0)
    location: str = Field(..., description="District name")

class PredictResponse(BaseModel):
    predicted_price: float
    model_version: str
    timestamp: str

class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    timestamp: str

class ModelInfoResponse(BaseModel):
    model_type: str
    model_version: str
    features: list
    loaded_at: str
