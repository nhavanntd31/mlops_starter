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

def test_model_metrics_are_valid():
    from sklearn.metrics import mean_squared_error, r2_score
    y_true = np.array([100, 200, 300, 400, 500])
    y_pred = np.array([110, 190, 310, 390, 510])
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    r2 = r2_score(y_true, y_pred)
    assert rmse < 20
    assert r2 > 0.9
