import yaml
import sys
from pathlib import Path


REQUIRED_SECTIONS = {
    "configs/params.yaml": ["project", "data", "training"],
    "configs/thresholds.yaml": ["tabular", "serving"],
}


def validate_config():
    errors = []

    for config_path, sections in REQUIRED_SECTIONS.items():
        path = Path(config_path)
        if not path.exists():
            errors.append(f"Missing config file: {config_path}")
            continue

        with open(path) as f:
            data = yaml.safe_load(f)

        if data is None:
            errors.append(f"Empty config file: {config_path}")
            continue

        for section in sections:
            if section not in data:
                errors.append(f"{config_path}: missing section '{section}'")

    params_path = Path("configs/params.yaml")
    if params_path.exists():
        with open(params_path) as f:
            params = yaml.safe_load(f)

        data_cfg = params.get("data", {})
        raw = data_cfg.get("raw_path")
        if raw and not Path(raw).exists():
            errors.append(f"Raw data path does not exist: {raw}")

        training = params.get("training", {})
        if training.get("n_estimators", 0) < 1:
            errors.append("training.n_estimators must be >= 1")
        if not (0 < training.get("learning_rate", 0) <= 1):
            errors.append("training.learning_rate must be in (0, 1]")

    if errors:
        print("Config validation FAILED:")
        for e in errors:
            print(f"  - {e}")
        return False

    print("Config validation PASSED")
    return True


if __name__ == "__main__":
    ok = validate_config()
    sys.exit(0 if ok else 1)
