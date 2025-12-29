"""Tests for profiling module."""

import pytest
import pandas as pd
from metrics_copilot.profiling import detect_kpis, detect_data_mode, detect_experiment_column


def test_detect_kpis():
    """Test KPI detection."""
    df = pd.DataFrame(
        {
            "date": pd.date_range("2024-01-01", periods=10),
            "revenue": [100.0, 150.0, 200.0] * 3 + [100],
            "dau": [1000, 1100, 1200] * 3 + [1000],
            "conversion_rate": [0.05, 0.06, 0.07] * 3 + [0.05],
            "user_id": range(10),
        }
    )

    column_profiles = {
        col: {"semantic_type": "numeric" if df[col].dtype in ["float64", "int64"] else "other"}
        for col in df.columns
        if col != "date"
    }

    kpis = detect_kpis(df, column_profiles)

    # Should detect revenue, dau, conversion_rate as KPIs
    kpi_names = [k.column_name for k in kpis]
    assert "revenue" in kpi_names
    assert "dau" in kpi_names
    assert "conversion_rate" in kpi_names
    assert "user_id" not in kpi_names  # Should skip IDs

    # Check KPI types
    revenue_kpi = next(k for k in kpis if k.column_name == "revenue")
    assert revenue_kpi.kpi_type == "money"

    conversion_kpi = next(k for k in kpis if k.column_name == "conversion_rate")
    assert conversion_kpi.kpi_type == "rate"


def test_detect_data_mode():
    """Test data mode detection."""
    # Time series only
    df = pd.DataFrame({"date": pd.date_range("2024-01-01", periods=10), "value": range(10)})
    column_profiles = {"value": {"semantic_type": "numeric"}}
    mode = detect_data_mode(df, "date", column_profiles)
    assert mode == "timeseries"

    # Experiment only
    df = pd.DataFrame({"variant": ["control", "test"] * 5, "value": range(10)})
    column_profiles = {"value": {"semantic_type": "numeric"}}
    mode = detect_data_mode(df, None, column_profiles)
    assert mode == "experiment"

    # Both
    df = pd.DataFrame(
        {"date": pd.date_range("2024-01-01", periods=10), "variant": ["control", "test"] * 5, "value": range(10)}
    )
    column_profiles = {"value": {"semantic_type": "numeric"}}
    mode = detect_data_mode(df, "date", column_profiles)
    assert mode == "both"


def test_detect_experiment_column():
    """Test experiment column detection."""
    # Explicit variant column
    df = pd.DataFrame({"variant": ["control", "test"] * 5, "value": range(10)})
    exp_col = detect_experiment_column(df)
    assert exp_col == "variant"

    # Group column
    df = pd.DataFrame({"experiment_group": ["A", "B"] * 5, "value": range(10)})
    exp_col = detect_experiment_column(df)
    assert exp_col == "experiment_group"

    # No experiment column
    df = pd.DataFrame({"user_id": range(10), "value": range(10)})
    exp_col = detect_experiment_column(df)
    assert exp_col is None
