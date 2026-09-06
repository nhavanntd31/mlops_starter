import os
import mlflow.pyfunc


class ModelHolder:
    def __init__(self):
        self.model = None
        self.model_name = os.getenv("MODEL_NAME", "house-price-model")
        self.model_version = os.getenv("MODEL_VERSION", "1")
        self.features = []

    def load(self):
        tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
        mlflow.set_tracking_uri(tracking_uri)
        model_uri = f"models:/{self.model_name}/{self.model_version}"
        self.model = mlflow.pyfunc.load_model(model_uri)
        if hasattr(self.model, "metadata") and self.model.metadata.signature:
            sig = self.model.metadata.signature
            if sig.inputs:
                self.features = [inp.name for inp in sig.inputs.inputs]
        print(f"Loaded {model_uri}")

    def predict(self, features: dict) -> float:
        import pandas as pd
        df = pd.DataFrame([features])
        prediction = self.model.predict(df)
        return float(prediction[0])


model_holder = ModelHolder()
