"""Tests for data ingestion module."""

import pytest
import pandas as pd
from metrics_copilot.ingest import (
    standardize_column_name,
    parse_numeric_column,
    detect_date_column,
    infer_column_type,
)


def test_standardize_column_name():
    """Test column name standardization."""
    assert standardize_column_name("User Count") == "user_count"
    assert standardize_column_name("Daily-Active-Users") == "daily_active_users"
    assert standardize_column_name("Conversion %") == "conversion"
    assert standardize_column_name("Revenue ($)") == "revenue"
    assert standardize_column_name("  DAU  ") == "dau"


def test_parse_numeric_column():
    """Test parsing numeric columns with various formats."""
    # Test with commas
    series = pd.Series(["1,000", "2,500", "3,750"])
    result = parse_numeric_column(series)
    assert result.tolist() == [1000, 2500, 3750]

    # Test with percentages
    series = pd.Series(["5%", "10.5%", "15%"])
    result = parse_numeric_column(series)
    assert result.tolist() == [5, 10.5, 15]

    # Test with dollar signs
    series = pd.Series(["$100", "$250.50", "$1,000"])
    result = parse_numeric_column(series)
    assert result.tolist() == [100, 250.50, 1000]

    # Test already numeric
    series = pd.Series([100, 200, 300])
    result = parse_numeric_column(series)
    assert result.tolist() == [100, 200, 300]


def test_detect_date_column():
    """Test date column detection."""
    # Test with explicit date column
    df = pd.DataFrame({"date": ["2024-01-01", "2024-01-02"], "value": [1, 2]})
    date_col, df_parsed = detect_date_column(df)
    assert date_col == "date"
    assert pd.api.types.is_datetime64_any_dtype(df_parsed["date"])

    # Test with various date formats
    df = pd.DataFrame({"timestamp": ["01/01/2024", "01/02/2024"], "value": [1, 2]})
    date_col, df_parsed = detect_date_column(df)
    assert date_col == "timestamp"

    # Test with no date column
    df = pd.DataFrame({"user_id": [1, 2], "value": [100, 200]})
    date_col, df_parsed = detect_date_column(df)
    assert date_col is None


def test_infer_column_type():
    """Test column type inference."""
    # Numeric
    series = pd.Series([1.5, 2.5, 3.5])
    assert infer_column_type(series) == "numeric"

    # Categorical
    series = pd.Series(["A", "B", "A", "B", "C"] * 10)
    assert infer_column_type(series) == "categorical"

    # Datetime
    series = pd.Series(pd.date_range("2024-01-01", periods=10))
    assert infer_column_type(series) == "datetime"

    # High cardinality (ID-like)
    series = pd.Series([f"user_{i}" for i in range(100)])
    assert infer_column_type(series) in ["id", "text"]
