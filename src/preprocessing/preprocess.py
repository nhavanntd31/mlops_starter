import pandas as pd
from sklearn.preprocessing import LabelEncoder, StandardScaler
import joblib
from pathlib import Path


def preprocess(df: pd.DataFrame, output_dir: str = "data/interim") -> pd.DataFrame:
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    df = df.copy()
    df = df.drop_duplicates()
    df = df.dropna()

    le = LabelEncoder()
    df["location_encoded"] = le.fit_transform(df["location"].astype(str))
    joblib.dump(le, Path(output_dir) / "label_encoder.pkl")

    feature_cols = ["area", "bedrooms", "bathrooms", "age", "floors", "location_encoded"]
    scaler = StandardScaler()
    df[feature_cols] = scaler.fit_transform(df[feature_cols])
    joblib.dump(scaler, Path(output_dir) / "scaler.pkl")

    df = df.drop(columns=["location"])
    print(f"Preprocessed: {len(df)} rows, saved encoders to {output_dir}")
    return df


if __name__ == "__main__":
    from src.ingestion.ingest import ingest
    df = ingest()
    df = preprocess(df)
    print(df.head())
