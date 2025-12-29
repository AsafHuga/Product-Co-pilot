"""Data profiling and KPI detection."""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Tuple, Literal, Optional
from metrics_copilot.schemas import DataProfile, KPIDetection, Anomaly
from metrics_copilot.ingest import infer_column_type


def profile_data(df: pd.DataFrame, date_col: Optional[str], metadata: dict) -> DataProfile:
    """Generate comprehensive data profile.

    Args:
        df: Input dataframe
        date_col: Name of date column (if any)
        metadata: Ingestion metadata

    Returns:
        DataProfile object
    """
    # Basic stats
    row_count = len(df)
    column_count = len(df.columns)
    duplicate_count = df.duplicated().sum()

    # Time range
    time_range = None
    if date_col and date_col in df.columns:
        date_series = df[date_col].dropna()
        if len(date_series) > 0:
            time_range = {
                "start": str(date_series.min()),
                "end": str(date_series.max()),
                "days": (date_series.max() - date_series.min()).days,
            }

    # Column profiles
    columns = {}
    for col in df.columns:
        col_profile = {
            "dtype": str(df[col].dtype),
            "semantic_type": infer_column_type(df[col]),
            "null_count": int(df[col].isna().sum()),
            "null_pct": float(df[col].isna().sum() / len(df) * 100),
            "unique_count": int(df[col].nunique()),
            "cardinality": float(df[col].nunique() / len(df)),
        }

        # Add stats for numeric columns
        if pd.api.types.is_numeric_dtype(df[col]):
            col_profile.update({
                "mean": float(df[col].mean()) if not df[col].isna().all() else None,
                "median": float(df[col].median()) if not df[col].isna().all() else None,
                "std": float(df[col].std()) if not df[col].isna().all() else None,
                "min": float(df[col].min()) if not df[col].isna().all() else None,
                "max": float(df[col].max()) if not df[col].isna().all() else None,
            })

        # Add top values for categorical
        if col_profile["semantic_type"] == "categorical":
            top_values = df[col].value_counts().head(5).to_dict()
            col_profile["top_values"] = {str(k): int(v) for k, v in top_values.items()}

        columns[col] = col_profile

    # Detect quality issues
    quality_issues = []

    # High missingness
    for col, profile in columns.items():
        if profile["null_pct"] > 50:
            quality_issues.append({
                "type": "high_missingness",
                "column": col,
                "severity": "high" if profile["null_pct"] > 80 else "medium",
                "description": f"Column '{col}' has {profile['null_pct']:.1f}% missing values",
            })

    # Add validation issues from metadata
    for issue in metadata.get("validation_issues", []):
        quality_issues.append({
            "type": "validation",
            "severity": "medium",
            "description": issue,
        })

    # Detect data mode
    data_mode = detect_data_mode(df, date_col, columns)

    return DataProfile(
        row_count=row_count,
        column_count=column_count,
        duplicate_count=duplicate_count,
        date_column=date_col,
        time_range=time_range,
        columns=columns,
        quality_issues=quality_issues,
        data_mode=data_mode,
    )


def detect_data_mode(
    df: pd.DataFrame, date_col: Optional[str], column_profiles: Dict[str, Dict[str, Any]]
) -> Literal["timeseries", "experiment", "both", "static"]:
    """Detect the mode of the data.

    Args:
        df: Input dataframe
        date_col: Name of date column
        column_profiles: Column profile metadata

    Returns:
        Data mode
    """
    has_timeseries = date_col is not None
    has_experiment = False

    # Check for experiment columns
    experiment_keywords = ['variant', 'group', 'experiment', 'treatment', 'control', 'test', 'arm']
    for col in df.columns:
        if any(keyword in col for keyword in experiment_keywords):
            # Check if it's binary or low cardinality
            if df[col].nunique() <= 10:
                has_experiment = True
                break

    if has_timeseries and has_experiment:
        return "both"
    elif has_timeseries:
        return "timeseries"
    elif has_experiment:
        return "experiment"
    else:
        return "static"


def detect_kpis(df: pd.DataFrame, column_profiles: Dict[str, Dict[str, Any]]) -> List[KPIDetection]:
    """Detect KPI columns and their types.

    Args:
        df: Input dataframe
        column_profiles: Column profile metadata

    Returns:
        List of detected KPIs
    """
    kpis = []

    # Keywords for different KPI types
    rate_keywords = ['rate', 'conversion', 'retention', 'pct', 'percent', 'ratio', 'ctr', 'cvr']
    count_keywords = ['count', 'users', 'dau', 'mau', 'wau', 'sessions', 'visits', 'impressions', 'clicks', 'events']
    money_keywords = ['revenue', 'arr', 'mrr', 'ltv', 'arpu', 'arpdau', 'arppu', 'price', 'cost', 'spend']
    duration_keywords = ['duration', 'time', 'latency', 'ttfb', 'load_time', 'session_length']

    for col, profile in column_profiles.items():
        # Skip non-numeric columns
        if profile["semantic_type"] != "numeric":
            continue

        # Skip ID-like columns
        if col.endswith('_id') or col == 'id':
            continue

        col_lower = col.lower()

        # Detect KPI type
        kpi_type = None
        unit = None

        if any(keyword in col_lower for keyword in rate_keywords):
            kpi_type = "rate"
            unit = "fraction"
        elif any(keyword in col_lower for keyword in money_keywords):
            kpi_type = "money"
            unit = "currency"
        elif any(keyword in col_lower for keyword in duration_keywords):
            kpi_type = "duration"
            unit = "seconds"
        elif any(keyword in col_lower for keyword in count_keywords):
            kpi_type = "count"
            unit = "count"
        else:
            # Default to ratio if values are between 0 and 1
            if profile.get("min", 0) >= 0 and profile.get("max", 2) <= 1:
                kpi_type = "ratio"
                unit = "fraction"
            else:
                kpi_type = "count"
                unit = "count"

        # Try to detect numerator/denominator pairs
        numerator = None
        denominator = None

        if kpi_type == "rate":
            # Look for matching count columns
            for possible_num in df.columns:
                if possible_num == col:
                    continue
                # e.g., conversion_rate might match with conversions and visits
                if 'conversion' in col_lower and 'conversion' in possible_num.lower():
                    numerator = possible_num
                # Look for denominators
                for possible_denom in df.columns:
                    if possible_denom in [col, numerator]:
                        continue
                    if any(kw in possible_denom.lower() for kw in ['total', 'visit', 'session', 'user']):
                        denominator = possible_denom
                        break

        # Determine if primary KPI (heuristic)
        is_primary = any(
            keyword in col_lower
            for keyword in ['revenue', 'conversion', 'retention', 'dau', 'engagement', 'gmv']
        )

        kpis.append(
            KPIDetection(
                column_name=col,
                kpi_type=kpi_type,
                numerator=numerator,
                denominator=denominator,
                unit=unit,
                is_primary=is_primary,
            )
        )

    # Sort by primary first
    kpis.sort(key=lambda k: (not k.is_primary, k.column_name))

    return kpis


def detect_segment_columns(df: pd.DataFrame, column_profiles: Dict[str, Dict[str, Any]]) -> List[str]:
    """Detect columns that represent segments.

    Args:
        df: Input dataframe
        column_profiles: Column profile metadata

    Returns:
        List of segment column names
    """
    segments = []

    for col, profile in column_profiles.items():
        # Categorical columns with reasonable cardinality
        if profile["semantic_type"] == "categorical":
            if 2 <= profile["unique_count"] <= 50:
                segments.append(col)

    return segments


def detect_experiment_column(df: pd.DataFrame) -> Optional[str]:
    """Detect the experiment/variant column.

    Args:
        df: Input dataframe

    Returns:
        Name of experiment column or None
    """
    experiment_keywords = ['variant', 'group', 'experiment', 'treatment', 'arm']

    for col in df.columns:
        col_lower = col.lower()
        if any(keyword in col_lower for keyword in experiment_keywords):
            # Check if binary or low cardinality
            if df[col].nunique() <= 10:
                return col

    # Check for columns with 'control' and 'test' values
    for col in df.columns:
        if df[col].dtype == 'object' or pd.api.types.is_categorical_dtype(df[col]):
            unique_vals = df[col].dropna().unique()
            unique_vals_lower = [str(v).lower() for v in unique_vals]
            if any('control' in v for v in unique_vals_lower) and any(
                'test' in v or 'treatment' in v for v in unique_vals_lower
            ):
                return col

    return None
