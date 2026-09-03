import yaml
import sys
import os

REQUIRED_KEYS = {
    "configs/params.yaml": ["project", "data", "features", "training"],
    "configs/thresholds.yaml": ["model_validation"],
}

def validate_yaml(path, required_keys):
    if not os.path.exists(path):
        print(f"[WARN] {path} not found, skipping")
        return True

    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if data is None:
        print(f"[FAIL] {path} is empty")
        return False

    missing = [k for k in required_keys if k not in data]
    if missing:
        print(f"[FAIL] {path} missing keys: {missing}")
        return False

    print(f"[PASS] {path} is valid")
    return True

def main():
    all_passed = True
    for path, keys in REQUIRED_KEYS.items():
        if not validate_yaml(path, keys):
            all_passed = False

    if not all_passed:
        print("Config validation FAILED")
        sys.exit(1)
    else:
        print("All configs valid")

if __name__ == "__main__":
    main()
