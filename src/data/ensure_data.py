import os
import sys
import shutil
import subprocess
from pathlib import Path

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def load_config(path="configs/params.yaml"):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def required_columns(config):
    return (
        list(config["features"]["numeric"])
        + list(config["features"]["categorical"])
        + [config["features"]["target"]]
    )


def split_paths(config):
    processed_dir = config["data"]["processed_dir"]
    return {
        "train": os.path.join(processed_dir, "train.csv"),
        "val": os.path.join(processed_dir, "val.csv"),
        "test": os.path.join(processed_dir, "test.csv"),
    }


def check_csv(path, cols, min_rows=1):
    if not os.path.isfile(path):
        return False, f"missing file: {path}"
    try:
        df = pd.read_csv(path)
    except Exception as e:
        return False, f"cannot read {path}: {e}"
    if len(df) < min_rows:
        return False, f"{path} has {len(df)} rows (need >= {min_rows})"
    missing = [c for c in cols if c not in df.columns]
    if missing:
        return False, f"{path} missing columns: {missing}"
    return True, f"ok {path} rows={len(df)}"


def data_ready(config=None):
    if config is None:
        config = load_config()
    cols = required_columns(config)
    paths = split_paths(config)
    issues = []
    details = []
    for name, path in paths.items():
        ok, msg = check_csv(path, cols)
        details.append(msg)
        if not ok:
            issues.append(msg)
    raw = config["data"]["raw_path"]
    if not os.path.isfile(raw):
        issues.append(f"missing raw: {raw}")
    else:
        details.append(f"ok raw={raw}")
    return len(issues) == 0, issues, details


def _run(cmd):
    print(f"[ensure_data] $ {' '.join(cmd)}")
    subprocess.run(cmd, check=True, cwd=str(ROOT))


def try_dvc_pull():
    lock = ROOT / "dvc.lock"
    config = ROOT / ".dvc" / "config"
    if not lock.is_file() or not config.is_file():
        print("[ensure_data] skip dvc pull (no dvc.lock or .dvc/config)")
        return False
    dvc = shutil.which("dvc")
    if not dvc:
        print("[ensure_data] skip dvc pull (dvc not installed)")
        return False
    try:
        _run([dvc, "pull"])
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ensure_data] dvc pull failed: {e}")
        return False


def rebuild_pipeline():
    print("[ensure_data] rebuilding data pipeline...")
    _run([sys.executable, "src/ingestion/ingest.py"])
    _run([sys.executable, "src/validation/validate.py"])
    _run([sys.executable, "src/preprocessing/preprocess.py"])
    _run([sys.executable, "src/split/split.py"])


def ensure_data(config=None):
    if config is None:
        config = load_config()

    ready, issues, details = data_ready(config)
    print("[ensure_data] check:")
    for line in details:
        print(f"  {line}")
    if ready:
        print("[ensure_data] data ready")
        return True

    print("[ensure_data] not ready:")
    for issue in issues:
        print(f"  - {issue}")

    try_dvc_pull()
    ready, issues, _ = data_ready(config)
    if ready:
        print("[ensure_data] data ready after dvc pull")
        return True

    raw = config["data"]["raw_path"]
    if not os.path.isfile(raw):
        raise FileNotFoundError(
            f"Missing {raw}. Place kc_house_data.csv under data/raw/ then retry."
        )

    rebuild_pipeline()
    ready, issues, details = data_ready(config)
    print("[ensure_data] recheck:")
    for line in details:
        print(f"  {line}")
    if not ready:
        raise RuntimeError("Data still incomplete after rebuild:\n- " + "\n- ".join(issues))
    print("[ensure_data] data ready after rebuild")
    return True


if __name__ == "__main__":
    ensure_data()
