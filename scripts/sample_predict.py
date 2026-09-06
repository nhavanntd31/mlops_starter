import httpx
import sys


def main():
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"

    health = httpx.get(f"{base_url}/health")
    print(f"Health: {health.json()}")

    payload = {
        "features": {
            "area": 2000,
            "bedrooms": 3,
            "bathrooms": 2.25,
            "age": 30,
            "floors": 1.0,
            "location_encoded": 20,
        }
    }
    resp = httpx.post(f"{base_url}/predict", json=payload)
    print(f"Predict: {resp.json()}")

    info = httpx.get(f"{base_url}/model-info")
    print(f"Model Info: {info.json()}")


if __name__ == "__main__":
    main()
