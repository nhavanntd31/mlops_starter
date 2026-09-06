import pandas as pd
import pytest
from src.ingestion.ingest import ingest
from src.validation.validate import validate, REQUIRED_COLUMNS


def test_ingest_returns_dataframe():
    df = ingest()
    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0


def test_ingest_has_required_columns():
    df = ingest()
    for col in REQUIRED_COLUMNS:
        assert col in df.columns, f"Missing column: {col}"


def test_validate_clean_data():
    df = ingest()
    report = validate(df)
    assert report["valid"] is True
    assert len(report["errors"]) == 0


def test_validate_detects_missing_column():
    df = pd.DataFrame({"area": [100], "bedrooms": [2]})
    report = validate(df)
    assert report["valid"] is False


def test_validate_detects_out_of_range():
    df = ingest()
    df.loc[0, "price"] = -100
    report = validate(df)
    assert any("price" in e for e in report["errors"])
