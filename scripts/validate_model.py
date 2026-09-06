import json
import yaml
import sys


def load_thresholds(path: str = "configs/thresholds.yaml") -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def validate_model(report_path: str = "reports/evaluation.json") -> bool:
    with open(report_path) as f:
        report = json.load(f)

    thresholds = load_thresholds()["tabular"]
    metrics = report["metrics"]

    checks = []

    test_rmse = metrics.get("test_rmse", float("inf"))
    passed = test_rmse <= thresholds["rmse_max"]
    checks.append(("RMSE", test_rmse, thresholds["rmse_max"], "<=", passed))

    test_mae = metrics.get("test_mae", float("inf"))
    passed = test_mae <= thresholds["mae_max"]
    checks.append(("MAE", test_mae, thresholds["mae_max"], "<=", passed))

    test_r2 = metrics.get("test_r2", -1)
    passed = test_r2 >= thresholds["r2_min"]
    checks.append(("R2", test_r2, thresholds["r2_min"], ">=", passed))

    test_mape = metrics.get("test_mape", float("inf"))
    passed = test_mape <= thresholds["mape_max"]
    checks.append(("MAPE", test_mape, thresholds["mape_max"], "<=", passed))

    all_passed = True
    for name, value, threshold, op, passed in checks:
        status = "PASS" if passed else "FAIL"
        print(f"  [{status}] {name}: {value:.4f} {op} {threshold}")
        if not passed:
            all_passed = False

    return all_passed


if __name__ == "__main__":
    ok = validate_model()
    print(f"\nOverall: {'PASSED' if ok else 'FAILED'}")
    sys.exit(0 if ok else 1)
