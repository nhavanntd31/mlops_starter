import json
import yaml
import sys

def load_thresholds(path="configs/thresholds.yaml"):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def load_metrics(path="reports/evaluation.json"):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def validate_model():
    thresholds = load_thresholds()
    metrics = load_metrics()
    t = thresholds["model_validation"]

    checks = []

    r2 = metrics.get("test_r2", 0)
    checks.append(("R2 >= {:.2f}".format(t["min_r2"]), r2 >= t["min_r2"], f"R2={r2:.4f}"))

    rmse = metrics.get("test_rmse", float("inf"))
    checks.append(("RMSE <= {}".format(t["max_rmse"]), rmse <= t["max_rmse"], f"RMSE={rmse:.2f}"))

    mae = metrics.get("test_mae", float("inf"))
    checks.append(("MAE <= {}".format(t["max_mae"]), mae <= t["max_mae"], f"MAE={mae:.2f}"))

    print("=" * 50)
    print("MODEL VALIDATION REPORT")
    print("=" * 50)

    all_passed = True
    for name, passed, detail in checks:
        status = "PASS" if passed else "FAIL"
        print(f"  [{status}] {name} -> {detail}")
        if not passed:
            all_passed = False

    print("=" * 50)
    if all_passed:
        print("Result: ALL CHECKS PASSED")
    else:
        print("Result: VALIDATION FAILED")
        sys.exit(1)

if __name__ == "__main__":
    validate_model()
