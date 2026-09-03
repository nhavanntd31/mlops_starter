import pandas as pd
import numpy as np
import json
import os
from datetime import datetime

def calculate_psi(expected, actual, bins=10):
    breakpoints = np.linspace(min(expected.min(), actual.min()),
                              max(expected.max(), actual.max()), bins + 1)
    expected_counts = np.histogram(expected, bins=breakpoints)[0] + 1
    actual_counts = np.histogram(actual, bins=breakpoints)[0] + 1

    expected_pct = expected_counts / expected_counts.sum()
    actual_pct = actual_counts / actual_counts.sum()

    psi = np.sum((actual_pct - expected_pct) * np.log(actual_pct / expected_pct))
    return float(psi)

def generate_report(reference_path="data/processed/train.csv",
                    current_path="data/processed/test.csv",
                    output_dir="reports"):
    ref_df = pd.read_csv(reference_path)
    cur_df = pd.read_csv(current_path)

    numeric_cols = ["area", "bedrooms", "bathrooms", "age", "garage"]
    report = {
        "generated_at": datetime.now().isoformat(),
        "reference_samples": len(ref_df),
        "current_samples": len(cur_df),
        "features": {},
    }

    for col in numeric_cols:
        if col in ref_df.columns and col in cur_df.columns:
            psi = calculate_psi(ref_df[col], cur_df[col])
            drift_status = "no_drift" if psi < 0.1 else "moderate_drift" if psi < 0.2 else "significant_drift"
            report["features"][col] = {
                "psi": round(psi, 6),
                "status": drift_status,
                "ref_mean": round(float(ref_df[col].mean()), 4),
                "cur_mean": round(float(cur_df[col].mean()), 4),
            }

    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "drift_report.json")
    with open(output_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"[Drift] Report saved to {output_path}")
    return report

if __name__ == "__main__":
    report = generate_report()
    for feat, info in report["features"].items():
        print(f"  {feat}: PSI={info['psi']:.4f} ({info['status']})")
