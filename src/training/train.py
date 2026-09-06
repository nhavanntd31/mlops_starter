import pandas as pd
import numpy as np
import yaml
import json
import mlflow
import mlflow.sklearn
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from pathlib import Path


def load_config(config_path: str = "configs/params.yaml") -> dict:
    with open(config_path) as f:
        return yaml.safe_load(f)


def load_data(processed_dir: str) -> tuple:
    train = pd.read_csv(f"{processed_dir}/train.csv")
    val = pd.read_csv(f"{processed_dir}/val.csv")
    test = pd.read_csv(f"{processed_dir}/test.csv")

    target = "price"
    features = [c for c in train.columns if c != target]

    return (
        train[features], train[target],
        val[features], val[target],
        test[features], test[target],
        features,
    )


def evaluate(model, X, y, prefix: str = "") -> dict:
    preds = model.predict(X)
    rmse = float(np.sqrt(mean_squared_error(y, preds)))
    mae = float(mean_absolute_error(y, preds))
    r2 = float(r2_score(y, preds))
    mape = float(np.mean(np.abs((y - preds) / np.where(y == 0, 1, y))) * 100)
    metrics = {
        f"{prefix}rmse": rmse,
        f"{prefix}mae": mae,
        f"{prefix}r2": r2,
        f"{prefix}mape": mape,
    }
    return metrics


def train(config: dict = None):
    if config is None:
        config = load_config()

    processed_dir = config["data"]["processed_dir"]
    seed = config["project"]["random_seed"]

    training_cfg = config.get("training", {})
    n_estimators = training_cfg.get("n_estimators", 200)
    max_depth = training_cfg.get("max_depth", 5)
    learning_rate = training_cfg.get("learning_rate", 0.1)
    subsample = training_cfg.get("subsample", 0.8)

    X_train, y_train, X_val, y_val, X_test, y_test, features = load_data(processed_dir)

    mlflow.set_experiment("house-price-prediction")

    with mlflow.start_run() as run:
        mlflow.log_param("model_type", "GradientBoostingRegressor")
        mlflow.log_param("n_estimators", n_estimators)
        mlflow.log_param("max_depth", max_depth)
        mlflow.log_param("learning_rate", learning_rate)
        mlflow.log_param("subsample", subsample)
        mlflow.log_param("random_seed", seed)
        mlflow.log_param("n_features", len(features))
        mlflow.log_param("n_train_samples", len(X_train))
        mlflow.set_tag("dataset_version", config["project"]["version"])

        model = GradientBoostingRegressor(
            n_estimators=n_estimators,
            max_depth=max_depth,
            learning_rate=learning_rate,
            subsample=subsample,
            random_state=seed,
        )
        model.fit(X_train, y_train)

        train_metrics = evaluate(model, X_train, y_train, "train_")
        val_metrics = evaluate(model, X_val, y_val, "val_")
        test_metrics = evaluate(model, X_test, y_test, "test_")

        all_metrics = {**train_metrics, **val_metrics, **test_metrics}
        mlflow.log_metrics(all_metrics)

        input_example = X_train.iloc[:1]
        mlflow.sklearn.log_model(
            model,
            artifact_path="model",
            input_example=input_example,
        )

        Path("reports").mkdir(exist_ok=True)
        report = {
            "run_id": run.info.run_id,
            "metrics": all_metrics,
            "params": {
                "n_estimators": n_estimators,
                "max_depth": max_depth,
                "learning_rate": learning_rate,
                "subsample": subsample,
            },
            "features": features,
        }
        with open("reports/evaluation.json", "w") as f:
            json.dump(report, f, indent=2)

        print(f"Run ID: {run.info.run_id}")
        print(f"Val RMSE: {val_metrics['val_rmse']:.2f}")
        print(f"Val R2:   {val_metrics['val_r2']:.4f}")
        print(f"Test RMSE: {test_metrics['test_rmse']:.2f}")
        print(f"Test R2:   {test_metrics['test_r2']:.4f}")

    return run.info.run_id


if __name__ == "__main__":
    train()
