import requests
import json

BASE_URL = "http://localhost:8000"

def check_health():
    resp = requests.get(f"{BASE_URL}/health")
    print(f"Health: {resp.json()}")

def get_model_info():
    resp = requests.get(f"{BASE_URL}/model-info")
    print(f"Model Info: {json.dumps(resp.json(), indent=2)}")

def predict():
    payload = {
        "area": 150.0,
        "bedrooms": 3,
        "bathrooms": 2,
        "age": 10,
        "garage": 1,
        "location": "District_1"
    }
    resp = requests.post(f"{BASE_URL}/predict", json=payload)
    print(f"Prediction: {json.dumps(resp.json(), indent=2)}")

if __name__ == "__main__":
    check_health()
    get_model_info()
    predict()
