import pandas as pd
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ingestion.ingest import ingest
from src.validation.validate import REQUIRED_COLUMNS, NUMERIC_COLUMNS

def test_ingest_returns_dataframe():
    df = ingest()
    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0

def test_required_columns_exist():
    df = ingest()
    for col in REQUIRED_COLUMNS:
        assert col in df.columns, f"Missing column: {col}"

def test_no_excessive_nulls():
    df = ingest()
    null_ratio = df.isnull().mean()
    for col in df.columns:
        assert null_ratio[col] <= 0.05, f"{col} has {null_ratio[col]:.2%} nulls"

def test_numeric_columns_are_numeric():
    df = ingest()
    for col in NUMERIC_COLUMNS:
        assert pd.api.types.is_numeric_dtype(df[col]), f"{col} is not numeric"

def test_price_is_positive():
    df = ingest()
    assert (df["price"] > 0).all(), "Some prices are not positive"
