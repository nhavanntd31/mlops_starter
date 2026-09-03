import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_schemas_import():
    from app.schemas import PredictRequest, PredictResponse, HealthResponse, ModelInfoResponse
    req = PredictRequest(area=120, bedrooms=3, bathrooms=2, age=5, garage=1, location="District_1")
    assert req.area == 120
    assert req.location == "District_1"

def test_predict_request_validation():
    from app.schemas import PredictRequest
    from pydantic import ValidationError
    try:
        PredictRequest(area=-10, bedrooms=3, bathrooms=2, age=5, garage=1, location="District_1")
        assert False, "Should have raised ValidationError"
    except ValidationError:
        pass

def test_health_response():
    from app.schemas import HealthResponse
    resp = HealthResponse(status="healthy", model_loaded=True, timestamp="2024-01-01T00:00:00")
    assert resp.status == "healthy"
