import pandas as pd


REQUIRED_COLUMNS = ["area", "bedrooms", "bathrooms", "age", "floors", "location", "price"]
NUMERIC_COLUMNS = ["area", "bedrooms", "bathrooms", "age", "floors", "price"]

RANGES = {
    "area": (300, 10000),
    "bedrooms": (1, 10),
    "bathrooms": (0.5, 8),
    "age": (0, 120),
    "floors": (1, 4),
    "price": (50_000, 3_000_000),
}


def validate(df: pd.DataFrame) -> dict:
    report = {"total_rows": len(df), "errors": []}

    missing = set(REQUIRED_COLUMNS) - set(df.columns)
    if missing:
        report["errors"].append(f"Missing columns: {missing}")
        return report

    for col in NUMERIC_COLUMNS:
        non_numeric = pd.to_numeric(df[col], errors="coerce").isna().sum() - df[col].isna().sum()
        if non_numeric > 0:
            report["errors"].append(f"{col}: {non_numeric} non-numeric values")

    null_counts = df[REQUIRED_COLUMNS].isnull().sum()
    for col, cnt in null_counts.items():
        if cnt > 0:
            report["errors"].append(f"{col}: {cnt} null values")

    dup_count = df.duplicated().sum()
    if dup_count > 0:
        report["errors"].append(f"{dup_count} duplicate rows")

    for col, (lo, hi) in RANGES.items():
        out = ((df[col] < lo) | (df[col] > hi)).sum()
        if out > 0:
            report["errors"].append(f"{col}: {out} values out of range [{lo}, {hi}]")

    empty_loc = df["location"].astype(str).str.strip().eq("") | df["location"].isna()
    if empty_loc.sum() > 0:
        report["errors"].append(f"location: {empty_loc.sum()} empty values")

    report["valid"] = len(report["errors"]) == 0
    report["valid_rows"] = len(df) - df.duplicated().sum()
    print(f"Validation: {len(report['errors'])} issues found")
    return report


if __name__ == "__main__":
    from src.ingestion.ingest import ingest
    df = ingest()
    result = validate(df)
    for k, v in result.items():
        print(f"  {k}: {v}")
