import pandas as pd
import os
import yaml
from sklearn.model_selection import train_test_split

def load_config(path="configs/params.yaml"):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def split_data(df, config=None):
    if config is None:
        config = load_config()

    test_size = config["data"]["test_size"]
    val_size = config["data"]["val_size"]
    seed = config["project"]["random_seed"]
    out_dir = config["data"]["processed_dir"]
    os.makedirs(out_dir, exist_ok=True)

    train_val, test = train_test_split(df, test_size=test_size, random_state=seed)
    val_ratio = val_size / (1 - test_size)
    train, val = train_test_split(train_val, test_size=val_ratio, random_state=seed)

    train.to_csv(os.path.join(out_dir, "train.csv"), index=False)
    val.to_csv(os.path.join(out_dir, "val.csv"), index=False)
    test.to_csv(os.path.join(out_dir, "test.csv"), index=False)

    print(f"[Split] Train: {len(train)}, Val: {len(val)}, Test: {len(test)}")
    return train, val, test

if __name__ == "__main__":
    df = pd.read_csv("data/processed/processed.csv")
    split_data(df)
