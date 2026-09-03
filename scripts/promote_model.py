import shutil
import os
import json
from datetime import datetime

def promote_model(source="models/model.pkl", target_dir="models/production"):
    os.makedirs(target_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    target_path = os.path.join(target_dir, f"model_{timestamp}.pkl")

    shutil.copy2(source, target_path)
    print(f"[Promote] Model copied to {target_path}")

    latest_path = os.path.join(target_dir, "model_latest.pkl")
    shutil.copy2(source, latest_path)
    print(f"[Promote] Latest model updated at {latest_path}")

    if os.path.exists("reports/evaluation.json"):
        shutil.copy2("reports/evaluation.json", os.path.join(target_dir, "evaluation.json"))

    manifest = {
        "promoted_at": timestamp,
        "source": source,
        "target": target_path,
    }
    with open(os.path.join(target_dir, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)
    print("[Promote] Manifest saved")

if __name__ == "__main__":
    promote_model()
