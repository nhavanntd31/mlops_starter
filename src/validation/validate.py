import pandas as pd
import sys

REQUIRED_COLUMNS = ["area", "bedrooms", "bathrooms", "age", "garage", "location", "price"]
NUMERIC_COLUMNS = ["area", "bedrooms", "bathrooms", "age", "garage", "price"]

RANGE_CHECKS = {
    "area": (10, 10000),
    "bedrooms": (0, 20),
    "bathrooms": (0, 10),
    "age": (0, 200),
    "garage": (0, 10),
    "price": (1000, 100000000),
}

VALID_LOCATIONS = [f"District_{i}" for i in range(1, 21)]

def validate_columns(df):
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    assert not missing, f"Missing columns: {missing}"
    print("[Validation] All required columns present")

def validate_numeric(df):
    for col in NUMERIC_COLUMNS:
        assert pd.api.types.is_numeric_dtype(df[col]), f"{col} is not numeric"
    print("[Validation] All numeric columns valid")

def validate_nulls(df, threshold=0.05):
    null_ratio = df.isnull().mean()
    bad = null_ratio[null_ratio > threshold]
    assert bad.empty, f"Columns exceed null threshold: {bad.to_dict()}"
    print("[Validation] Null check passed")

def validate_duplicates(df, threshold=0.01):
    dup_ratio = df.duplicated().mean()
    assert dup_ratio <= threshold, f"Duplicate ratio {dup_ratio:.2%} exceeds {threshold:.2%}"
    print("[Validation] Duplicate check passed")

def validate_ranges(df):
    for col, (lo, hi) in RANGE_CHECKS.items():
        out = df[(df[col] < lo) | (df[col] > hi)]
        assert out.empty, f"{col} has {len(out)} values out of range [{lo}, {hi}]"
    print("[Validation] Range check passed")

def validate_location(df):
    invalid = df[~df["location"].isin(VALID_LOCATIONS)]
    assert invalid.empty, f"{len(invalid)} rows with invalid location"
    print("[Validation] Location check passed")

def run_validation(df):
    validate_columns(df)
    validate_numeric(df)
    validate_nulls(df)
    validate_duplicates(df)
    validate_ranges(df)
    validate_location(df)
    print("[Validation] All checks passed!")
    return True

if __name__ == "__main__":
    df = pd.read_csv("data/raw/houses.csv")
    run_validation(df)
