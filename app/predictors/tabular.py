import pandas as pd
from app.model_loader import model_holder


def predict_tabular(features: dict) -> float:
    return model_holder.predict(features)
