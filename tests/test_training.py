import numpy as np
import pytest
from sklearn.ensemble import GradientBoostingRegressor


def test_model_can_fit_and_predict():
    rng = np.random.RandomState(42)
    X = rng.rand(50, 3)
    y = X[:, 0] * 100 + X[:, 1] * 50 + rng.randn(50) * 5

    model = GradientBoostingRegressor(n_estimators=10, random_state=42)
    model.fit(X, y)
    preds = model.predict(X[:5])
    assert preds.shape == (5,)
    assert all(np.isfinite(preds))


def test_model_improves_over_mean():
    rng = np.random.RandomState(42)
    X = rng.rand(100, 4)
    y = X[:, 0] * 200 + X[:, 1] * 80 + rng.randn(100) * 10

    model = GradientBoostingRegressor(n_estimators=50, random_state=42)
    model.fit(X[:80], y[:80])
    preds = model.predict(X[80:])

    mse_model = np.mean((y[80:] - preds) ** 2)
    mse_mean = np.mean((y[80:] - np.mean(y[:80])) ** 2)
    assert mse_model < mse_mean
