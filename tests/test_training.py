import os
import sys
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_model_can_fit_and_predict():
    X = np.random.rand(100, 6)
    y = np.random.rand(100) * 500000
    model = GradientBoostingRegressor(n_estimators=10, max_depth=3, random_state=42)
    model.fit(X, y)
    preds = model.predict(X[:5])
    assert len(preds) == 5
    assert all(p > 0 for p in preds)

def test_extract_disabled_keeps_columns():
    import pandas as pd
    from src.training.features import extract_features
    df = pd.DataFrame({
        "area": [1.0, 2.0],
        "bedrooms": [1.0, 3.0],
        "bathrooms": [1.0, 2.0],
        "age": [0.5, 1.0],
        "floors": [1.0, 2.0],
        "location": [0, 1],
    })
    out, extracted = extract_features(df, {"feature_engineering": {"enabled": False, "extract": ["total_rooms"]}})
    assert extracted == []
    assert list(out.columns) == list(df.columns)

def test_extract_adds_configured_features():
    import pandas as pd
    from src.training.features import extract_features
    df = pd.DataFrame({
        "area": [4.0, 6.0],
        "bedrooms": [1.0, 2.0],
        "bathrooms": [1.0, 1.0],
        "age": [2.0, 3.0],
        "floors": [1.0, 2.0],
        "location": [0, 1],
    })
    config = {
        "feature_engineering": {
            "enabled": True,
            "eps": 1e-6,
            "extract": ["total_rooms", "age_squared", "area_per_floor"],
        }
    }
    out, extracted = extract_features(df, config)
    assert extracted == ["total_rooms", "age_squared", "area_per_floor"]
    assert "total_rooms" in out.columns
    assert out["total_rooms"].iloc[0] == 2.0
    assert out["age_squared"].iloc[0] == 4.0
    assert len(out.columns) == len(df.columns) + 3

def test_model_metrics_are_valid():
    from sklearn.metrics import mean_squared_error, r2_score
    y_true = np.array([100, 200, 300, 400, 500])
    y_pred = np.array([110, 190, 310, 390, 510])
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    r2 = r2_score(y_true, y_pred)
    assert rmse < 20
    assert r2 > 0.9
