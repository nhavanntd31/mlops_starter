import json
import mlflow
import os
import sys


def register_best(
    report_path: str = "reports/evaluation.json",
    model_name: str = None,
):
    model_name = model_name or os.getenv("MODEL_NAME", "house-price-model")

    with open(report_path) as f:
        report = json.load(f)

    run_id = report["run_id"]
    model_uri = f"runs:/{run_id}/model"

    result = mlflow.register_model(model_uri=model_uri, name=model_name)
    print(f"Registered {model_name} version {result.version} from run {run_id}")
    return result


if __name__ == "__main__":
    name = sys.argv[1] if len(sys.argv) > 1 else None
    register_best(model_name=name)
