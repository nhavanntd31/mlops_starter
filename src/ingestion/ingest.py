import pandas as pd
import yaml
import os

def load_config(path="configs/params.yaml"):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def ingest(config=None):
    if config is None:
        config = load_config()
    raw_path = config["data"]["raw_path"]
    print(f"[Ingestion] Reading data from {raw_path}")
    df = pd.read_csv(raw_path)
    print(f"[Ingestion] Loaded {len(df)} rows, {len(df.columns)} columns")
    return df

if __name__ == "__main__":
    df = ingest()
    print(df.head())
