import json
import os
import shutil
from datetime import datetime

def register_best_model(metrics_path="reports/evaluation.json",
                        model_path="models/model.pkl",
                        registry_dir="models/registry"):
    with open(metrics_path, "r") as f:
        metrics = json.load(f)

    os.makedirs(registry_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    version_dir = os.path.join(registry_dir, f"v_{timestamp}")
    os.makedirs(version_dir, exist_ok=True)

    shutil.copy2(model_path, os.path.join(version_dir, "model.pkl"))

    for artifact in ["scaler.pkl", "label_encoder.pkl"]:
        src = os.path.join("models", artifact)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(version_dir, artifact))

    with open(os.path.join(version_dir, "metrics.json"), "w") as f:
        json.dump(metrics, f, indent=2)

    manifest = {
        "version": timestamp,
        "registered_at": datetime.now().isoformat(),
        "metrics": metrics,
        "artifacts": os.listdir(version_dir),
    }
    with open(os.path.join(version_dir, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)

    latest_link = os.path.join(registry_dir, "latest.json")
    with open(latest_link, "w") as f:
        json.dump({"version": timestamp, "path": version_dir}, f, indent=2)

    print(f"[Registry] Model registered as v_{timestamp}")
    return version_dir

if __name__ == "__main__":
    register_best_model()
