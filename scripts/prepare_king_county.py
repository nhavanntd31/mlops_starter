from pathlib import Path
import csv
import pandas as pd

RAW_DIR = Path("data/raw")
SOURCE = RAW_DIR / "kc_house_data.csv"
TARGET = RAW_DIR / "houses.csv"


def prepare(source: Path = SOURCE, target: Path = TARGET) -> pd.DataFrame:
    df = pd.read_csv(source)
    out = pd.DataFrame(
        {
            "area": df["sqft_living"],
            "bedrooms": df["bedrooms"],
            "bathrooms": df["bathrooms"],
            "age": 2015 - df["yr_built"],
            "floors": df["floors"].astype(float),
            "location": df["zipcode"].astype(str),
            "price": df["price"],
        }
    )
    out = out[(out["bedrooms"] >= 1) & (out["bedrooms"] <= 10)]
    out = out[(out["bathrooms"] >= 0.5) & (out["bathrooms"] <= 8)]
    out = out[(out["area"] >= 300) & (out["area"] <= 10000)]
    out = out[(out["price"] >= 50_000) & (out["price"] <= 3_000_000)]
    out = out[(out["age"] >= 0) & (out["age"] <= 120)]
    out = out.drop_duplicates().reset_index(drop=True)
    target.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(target, index=False, quoting=csv.QUOTE_NONNUMERIC)
    print(f"Wrote {len(out)} rows to {target}")
    return out


if __name__ == "__main__":
    prepare()
