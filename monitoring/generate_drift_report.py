import pandas as pd
import numpy as np
import json
from pathlib import Path
from datetime import datetime


def compute_stats(df: pd.DataFrame, numeric_cols: list) -> dict:
    stats = {}
    for col in numeric_cols:
        stats[col] = {
            "mean": float(df[col].mean()),
            "std": float(df[col].std()),
            "min": float(df[col].min()),
            "max": float(df[col].max()),
            "median": float(df[col].median()),
        }
    return stats


def detect_drift(reference_stats: dict, current_stats: dict, threshold: float = 2.0) -> dict:
    drift = {}
    for col in reference_stats:
        if col not in current_stats:
            continue
        ref_mean = reference_stats[col]["mean"]
        ref_std = reference_stats[col]["std"]
        cur_mean = current_stats[col]["mean"]

        if ref_std > 0:
            z_score = abs(cur_mean - ref_mean) / ref_std
        else:
            z_score = 0.0

        drift[col] = {
            "z_score": round(z_score, 4),
            "drifted": z_score > threshold,
            "ref_mean": ref_mean,
            "cur_mean": cur_mean,
        }
    return drift


def generate_report(
    reference_path: str = "data/processed/train.csv",
    current_path: str = None,
    output_dir: str = "monitoring/reports",
):
    ref_df = pd.read_csv(reference_path)
    numeric_cols = ref_df.select_dtypes(include=[np.number]).columns.tolist()
    if "price" in numeric_cols:
        numeric_cols.remove("price")

    ref_stats = compute_stats(ref_df, numeric_cols)

    if current_path:
        cur_df = pd.read_csv(current_path)
    else:
        cur_df = ref_df.copy()
        for col in numeric_cols:
            cur_df[col] = cur_df[col] + np.random.normal(0, 0.1, len(cur_df))

    cur_stats = compute_stats(cur_df, numeric_cols)
    drift = detect_drift(ref_stats, cur_stats)

    report = {
        "generated_at": datetime.now().isoformat(),
        "reference_path": reference_path,
        "current_path": current_path or "simulated",
        "n_features": len(numeric_cols),
        "features_drifted": sum(1 for v in drift.values() if v["drifted"]),
        "details": drift,
    }

    Path(output_dir).mkdir(parents=True, exist_ok=True)
    out_path = Path(output_dir) / "drift_report.json"
    with open(out_path, "w") as f:
        json.dump(report, f, indent=2)

    print(f"Drift report saved to {out_path}")
    print(f"Features drifted: {report['features_drifted']}/{report['n_features']}")
    return report


if __name__ == "__main__":
    generate_report()
