import pandas as pd
import numpy as np
import yaml
import pickle
import os
import json
import sys
from pathlib import Path
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from src.training.features import extract_features

try:
    import mlflow
    import mlflow.sklearn
    HAS_MLFLOW = True
except ImportError:
    HAS_MLFLOW = False

def load_config(path="configs/params.yaml"):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def train(config=None):
    if config is None:
        config = load_config()

    processed_dir = config["data"]["processed_dir"]
    target = config["features"]["target"]
    model_params = config["training"]["params"]
    fe = config.get("feature_engineering") or {}
    fe_enabled = bool(fe.get("enabled", False))
    run_name = fe.get("run_name") or ("with-extracted-features" if fe_enabled else "baseline")

    train_df = pd.read_csv(os.path.join(processed_dir, "train.csv"))
    val_df = pd.read_csv(os.path.join(processed_dir, "val.csv"))
    test_df = pd.read_csv(os.path.join(processed_dir, "test.csv"))

    X_train = train_df.drop(columns=[target])
    y_train = train_df[target]
    X_val = val_df.drop(columns=[target])
    y_val = val_df[target]
    X_test = test_df.drop(columns=[target])
    y_test = test_df[target]

    X_train, extracted = extract_features(X_train, config)
    X_val, _ = extract_features(X_val, config)
    X_test, _ = extract_features(X_test, config)
    feature_names = list(X_train.columns)

    print(f"[Training] run_name={run_name} fe_enabled={fe_enabled}")
    print(f"[Training] n_features={len(feature_names)}")
    print(f"[Training] features={feature_names}")
    if extracted:
        print(f"[Training] extracted={extracted}")

    if HAS_MLFLOW:
        tracking_uri = config.get("mlflow", {}).get("tracking_uri", "http://localhost:5000")
        experiment_name = config["training"]["experiment_name"]
        try:
            mlflow.set_tracking_uri(tracking_uri)
        except Exception:
            pass
        try:
            mlflow.set_experiment(experiment_name)
        except Exception:
            pass

    model = GradientBoostingRegressor(**model_params)
    model.fit(X_train, y_train)

    y_pred_val = model.predict(X_val)
    y_pred_test = model.predict(X_test)

    metrics = {
        "val_rmse": float(np.sqrt(mean_squared_error(y_val, y_pred_val))),
        "val_mae": float(mean_absolute_error(y_val, y_pred_val)),
        "val_r2": float(r2_score(y_val, y_pred_val)),
        "test_rmse": float(np.sqrt(mean_squared_error(y_test, y_pred_test))),
        "test_mae": float(mean_absolute_error(y_test, y_pred_test)),
        "test_r2": float(r2_score(y_test, y_pred_test)),
        "n_features": float(len(feature_names)),
    }

    print("[Training] Metrics:")
    for k, v in metrics.items():
        print(f"  {k}: {v:.4f}")

    importances = {}
    if hasattr(model, "feature_importances_"):
        importances = {
            name: float(val)
            for name, val in zip(feature_names, model.feature_importances_)
        }

    feature_report = {
        "run_name": run_name,
        "fe_enabled": fe_enabled,
        "feature_names": feature_names,
        "extracted": extracted,
        "n_features": len(feature_names),
        "importances": importances,
    }

    if HAS_MLFLOW:
        try:
            with mlflow.start_run(run_name=str(run_name)):
                mlflow.set_tag("run_type", "feature_engineering" if fe_enabled else "baseline")
                mlflow.log_params(model_params)
                mlflow.log_param("fe_enabled", fe_enabled)
                mlflow.log_param("n_features", len(feature_names))
                mlflow.log_param("extracted_features", ",".join(extracted) if extracted else "none")
                mlflow.log_param("feature_names", ",".join(feature_names))
                mlflow.log_metrics(metrics)
                mlflow.log_dict(feature_report, "features.json")
                mlflow.sklearn.log_model(model, "model")
        except Exception as e:
            print(f"[Training] MLflow logging failed: {e}")

    os.makedirs("models", exist_ok=True)
    model_path = os.path.join("models", "model.pkl")
    with open(model_path, "wb") as f:
        pickle.dump(model, f)
    print(f"[Training] Model saved to {model_path}")

    os.makedirs("reports", exist_ok=True)
    with open("reports/evaluation.json", "w") as f:
        json.dump({**metrics, "features": feature_report}, f, indent=2)
    with open("reports/features.json", "w") as f:
        json.dump(feature_report, f, indent=2)
    print("[Training] Evaluation saved to reports/evaluation.json")
    print("[Training] Features saved to reports/features.json")

    return model, metrics

if __name__ == "__main__":
    train()
