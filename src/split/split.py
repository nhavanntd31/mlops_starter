import pandas as pd
from sklearn.model_selection import train_test_split
from pathlib import Path
import yaml


def load_config(config_path: str = "configs/params.yaml") -> dict:
    with open(config_path) as f:
        return yaml.safe_load(f)


def split_data(df: pd.DataFrame, config: dict = None) -> dict:
    if config is None:
        config = load_config()

    test_size = config["data"]["test_size"]
    val_size = config["data"]["val_size"]
    seed = config["project"]["random_seed"]
    output_dir = Path(config["data"]["processed_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)

    train_val, test = train_test_split(df, test_size=test_size, random_state=seed)
    relative_val = val_size / (1 - test_size)
    train, val = train_test_split(train_val, test_size=relative_val, random_state=seed)

    train.to_csv(output_dir / "train.csv", index=False)
    val.to_csv(output_dir / "val.csv", index=False)
    test.to_csv(output_dir / "test.csv", index=False)

    result = {"train": len(train), "val": len(val), "test": len(test)}
    print(f"Split: train={result['train']}, val={result['val']}, test={result['test']}")
    return result


if __name__ == "__main__":
    from src.ingestion.ingest import ingest
    from src.preprocessing.preprocess import preprocess
    df = ingest()
    df = preprocess(df)
    split_data(df)
