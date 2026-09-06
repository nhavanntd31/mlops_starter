import mlflow
from mlflow.tracking import MlflowClient
import json
import sys
import os


def promote(
    model_name: str = None,
    version: int = None,
    alias: str = "champion",
    report_path: str = "reports/evaluation.json",
):
    model_name = model_name or os.getenv("MODEL_NAME", "house-price-model")
    client = MlflowClient()

    if version is None:
        with open(report_path) as f:
            report = json.load(f)
        run_id = report["run_id"]
        versions = client.search_model_versions(f"run_id='{run_id}'")
        if not versions:
            print(f"No registered version found for run {run_id}")
            print("Register first: mlflow.register_model('runs:/<run_id>/model', '<name>')")
            sys.exit(1)
        version = versions[0].version

    client.set_registered_model_alias(model_name, alias, version)
    print(f"Promoted {model_name} v{version} -> alias '{alias}'")


if __name__ == "__main__":
    alias = sys.argv[1] if len(sys.argv) > 1 else "champion"
    promote(alias=alias)
