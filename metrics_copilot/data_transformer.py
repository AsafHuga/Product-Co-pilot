"""Transform raw data into analysis-ready format.

This module provides intelligent data transformation to convert various raw data formats
into the standardized format expected by the metrics copilot.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import re
from metrics_copilot.ingest import (
    detect_encoding,
    detect_delimiter,
    standardize_column_name,
    detect_date_column,
    parse_numeric_column,
)


def detect_event_data_format(df: pd.DataFrame) -> bool:
    """Detect if data is in raw event format (one row per event).

    Args:
        df: Input dataframe

    Returns:
        True if data appears to be event-level data
    """
    # Event data typically has:
    # - High cardinality ID columns (user_id, event_id, session_id)
    # - Timestamp columns with high granularity
    # - Event name/type columns

    has_event_columns = any(
        col for col in df.columns
        if any(keyword in col for keyword in ['event', 'action', 'activity'])
    )

    has_user_id = any(
        col for col in df.columns
        if any(keyword in col for keyword in ['user', 'customer', 'visitor', 'uid'])
    )

    # Check if timestamp is very granular (suggests events)
    date_col = None
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            date_col = col
            break
        if any(keyword in col for keyword in ['date', 'time', 'timestamp']):
            try:
                df[col] = pd.to_datetime(df[col], errors='coerce')
                if df[col].notna().sum() > len(df) * 0.5:
                    date_col = col
                    break
            except:
                pass

    if date_col:
        unique_dates = df[date_col].nunique()
        # If we have timestamps for most rows, it's likely event data
        if unique_dates / len(df) > 0.8:
            return True

    return has_event_columns and has_user_id


def aggregate_event_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Convert event-level data to aggregated timeseries format.

    Args:
        df: Event-level dataframe

    Returns:
        Tuple of (aggregated dataframe, transformation metadata)
    """
    metadata = {
        "transformation_type": "event_aggregation",
        "original_rows": len(df),
        "transformations": []
    }

    # Detect date column
    date_col = None
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            date_col = col
            break
        if any(keyword in col for keyword in ['date', 'time', 'timestamp', 'ts', 'dt']):
            try:
                df[col] = pd.to_datetime(df[col], errors='coerce')
                if df[col].notna().sum() > len(df) * 0.5:
                    date_col = col
                    break
            except:
                pass

    if not date_col:
        raise ValueError("Could not detect date/timestamp column for aggregation")

    # Convert to date (remove time component)
    df['date'] = pd.to_datetime(df[date_col]).dt.date
    metadata["transformations"].append(f"Extracted date from {date_col}")

    # Detect dimension columns (categorical with reasonable cardinality)
    dimension_cols = []
    for col in df.columns:
        if col == date_col or col == 'date':
            continue
        cardinality = df[col].nunique()
        if cardinality < 50 and cardinality > 1:  # Reasonable dimension
            if not pd.api.types.is_numeric_dtype(df[col]):
                dimension_cols.append(col)

    # If no dimensions found, add a default one
    if not dimension_cols:
        df['segment'] = 'All Users'
        dimension_cols = ['segment']
        metadata["transformations"].append("Added default 'All Users' segment")

    metadata["dimension_columns"] = dimension_cols

    # Detect user ID column
    user_col = None
    for col in df.columns:
        if any(keyword in col for keyword in ['user', 'customer', 'visitor', 'uid', 'account']):
            if df[col].nunique() > len(df) * 0.1:  # High cardinality
                user_col = col
                break

    # Build aggregation spec
    agg_spec = {}

    # Count events/sessions
    agg_spec['events'] = ('date', 'count')

    if user_col:
        agg_spec['dau'] = (user_col, 'nunique')
        metadata["transformations"].append(f"Calculated DAU from {user_col}")

    # Detect revenue columns
    revenue_cols = [
        col for col in df.columns
        if any(keyword in col for keyword in ['revenue', 'amount', 'price', 'value', 'spend'])
        and pd.api.types.is_numeric_dtype(df[col])
    ]

    for rev_col in revenue_cols:
        agg_spec[rev_col] = (rev_col, 'sum')
        metadata["transformations"].append(f"Aggregated {rev_col}")

    # Detect conversion/success columns
    conversion_cols = [
        col for col in df.columns
        if any(keyword in col for keyword in ['converted', 'purchased', 'success', 'completed'])
        and df[col].dtype in ['bool', 'object', 'int64']
    ]

    for conv_col in conversion_cols:
        # Try to convert to boolean
        if df[conv_col].dtype == 'object':
            df[conv_col] = df[conv_col].map({'true': 1, 'True': 1, 'TRUE': 1,
                                              'false': 0, 'False': 0, 'FALSE': 0,
                                              'yes': 1, 'Yes': 1, 'no': 0, 'No': 0,
                                              '1': 1, '0': 0})
        agg_spec[f'{conv_col}_count'] = (conv_col, 'sum')
        metadata["transformations"].append(f"Aggregated conversions from {conv_col}")

    # Group by date and dimensions
    group_cols = ['date'] + dimension_cols

    if not agg_spec:
        # If no metrics detected, just count events
        agg_spec = {'events': ('date', 'count')}

    # Perform aggregation
    agg_df = df.groupby(group_cols).agg(**agg_spec).reset_index()

    # Calculate derived metrics
    if user_col and 'events' in agg_df.columns:
        agg_df['sessions_per_user'] = agg_df['events'] / agg_df['dau']
        metadata["transformations"].append("Calculated sessions per user")

    for rev_col in revenue_cols:
        if user_col and rev_col in agg_df.columns:
            arpdau_col = f'arpdau_{rev_col}' if len(revenue_cols) > 1 else 'arpdau'
            agg_df[arpdau_col] = agg_df[rev_col] / agg_df['dau']
            metadata["transformations"].append(f"Calculated ARPDAU from {rev_col}")

    for conv_col in conversion_cols:
        conv_count = f'{conv_col}_count'
        if conv_count in agg_df.columns and 'events' in agg_df.columns:
            rate_col = f'{conv_col}_rate'
            agg_df[rate_col] = agg_df[conv_count] / agg_df['events']
            metadata["transformations"].append(f"Calculated conversion rate from {conv_col}")

    # Rename 'date' back to proper date column
    agg_df = agg_df.rename(columns={'date': 'date'})

    metadata["final_rows"] = len(agg_df)
    metadata["final_columns"] = list(agg_df.columns)

    return agg_df, metadata


def detect_wide_format(df: pd.DataFrame) -> bool:
    """Detect if data is in wide format (metrics as columns, one row per date).

    Args:
        df: Input dataframe

    Returns:
        True if data appears to be in wide format
    """
    # Wide format typically has:
    # - A date column
    # - Many numeric columns
    # - Few rows relative to columns

    numeric_cols = df.select_dtypes(include=[np.number]).columns

    # If most columns are numeric and we have a date column, likely wide format
    if len(numeric_cols) / len(df.columns) > 0.5:
        has_date = any(
            col for col in df.columns
            if any(keyword in col for keyword in ['date', 'time', 'day', 'period'])
        )
        if has_date and len(df) < len(df.columns) * 2:
            return True

    return False


def convert_wide_to_long(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Convert wide format to long format (unpivot).

    Args:
        df: Wide format dataframe

    Returns:
        Tuple of (long format dataframe, transformation metadata)
    """
    metadata = {
        "transformation_type": "wide_to_long",
        "original_shape": df.shape,
        "transformations": []
    }

    # Detect date column
    date_col = None
    for col in df.columns:
        if any(keyword in col for keyword in ['date', 'time', 'day', 'period']):
            date_col = col
            break

    if not date_col:
        raise ValueError("Could not detect date column for wide-to-long conversion")

    # Identify dimension columns (non-numeric, non-date)
    dimension_cols = []
    for col in df.columns:
        if col != date_col and not pd.api.types.is_numeric_dtype(df[col]):
            dimension_cols.append(col)

    # Identify value columns (numeric)
    value_cols = [col for col in df.columns if pd.api.types.is_numeric_dtype(df[col])]

    # Keep date and dimensions, melt the rest
    id_vars = [date_col] + dimension_cols

    long_df = pd.melt(
        df,
        id_vars=id_vars,
        value_vars=value_cols,
        var_name='metric',
        value_name='value'
    )

    metadata["transformations"].append(f"Melted {len(value_cols)} metric columns into long format")
    metadata["final_shape"] = long_df.shape

    return long_df, metadata


def auto_transform_data(file_path: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Automatically detect and transform raw data into analysis-ready format.

    This is the main entry point that handles:
    - Event-level data → aggregated timeseries
    - Wide format → long format (if needed)
    - Basic cleaning and validation

    Args:
        file_path: Path to raw CSV file

    Returns:
        Tuple of (transformed dataframe, transformation metadata)
    """
    metadata = {
        "input_file": file_path,
        "transformation_timestamp": datetime.now().isoformat(),
        "steps": []
    }

    # Step 1: Read with auto-detection
    encoding = detect_encoding(file_path)
    delimiter = detect_delimiter(file_path, encoding)

    df = pd.read_csv(file_path, encoding=encoding, sep=delimiter)
    metadata["original_shape"] = df.shape
    metadata["encoding"] = encoding
    metadata["delimiter"] = delimiter

    # Step 2: Standardize column names
    original_columns = df.columns.tolist()
    df.columns = [standardize_column_name(col) for col in df.columns]
    metadata["steps"].append({
        "step": "standardize_columns",
        "column_mapping": dict(zip(original_columns, df.columns))
    })

    # Step 3: Detect and parse date columns
    date_col, df = detect_date_column(df)
    if date_col:
        metadata["steps"].append({
            "step": "parse_dates",
            "date_column": date_col
        })

    # Step 4: Parse numeric columns
    for col in df.columns:
        if df[col].dtype == 'object':
            parsed = parse_numeric_column(df[col])
            if not parsed.equals(df[col]) and parsed.notna().sum() > len(df) * 0.5:
                df[col] = parsed

    # Step 5: Detect format and transform
    if detect_event_data_format(df):
        # Event data → aggregate to timeseries
        metadata["detected_format"] = "event_level"
        df, agg_metadata = aggregate_event_data(df)
        metadata["steps"].append({
            "step": "aggregate_events",
            "details": agg_metadata
        })
    elif detect_wide_format(df):
        # Wide format → convert to long (optional, depends on use case)
        metadata["detected_format"] = "wide_format"
        # For now, we'll keep wide format as it's already suitable
        # But we note it for future transformations
        metadata["steps"].append({
            "step": "detected_wide_format",
            "note": "Data is in wide format, keeping as-is for analysis"
        })
    else:
        # Assume it's already in good timeseries format
        metadata["detected_format"] = "timeseries"
        metadata["steps"].append({
            "step": "format_validation",
            "note": "Data appears to be in timeseries format"
        })

    # Step 6: Final validation
    # Ensure we have a date column
    if date_col is None:
        # Try to detect again after transformations
        date_col, df = detect_date_column(df)
        if date_col is None:
            metadata["warnings"] = metadata.get("warnings", [])
            metadata["warnings"].append("No date column detected - some analyses may be limited")

    # Ensure we have at least one numeric column
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) == 0:
        raise ValueError("No numeric columns found in transformed data")

    metadata["final_shape"] = df.shape
    metadata["final_columns"] = list(df.columns)
    metadata["numeric_columns"] = list(numeric_cols)
    metadata["date_column"] = date_col

    return df, metadata


def preview_transformation(file_path: str, max_rows: int = 10) -> Dict[str, Any]:
    """Preview what transformations would be applied without executing them.

    Args:
        file_path: Path to raw CSV file
        max_rows: Number of rows to show in preview

    Returns:
        Dictionary with preview information
    """
    encoding = detect_encoding(file_path)
    delimiter = detect_delimiter(file_path, encoding)

    df = pd.read_csv(file_path, encoding=encoding, sep=delimiter, nrows=100)

    original_columns = df.columns.tolist()
    df.columns = [standardize_column_name(col) for col in df.columns]

    preview = {
        "original_shape": df.shape,
        "original_columns": original_columns,
        "standardized_columns": list(df.columns),
        "sample_data": df.head(max_rows).to_dict(orient='records'),
    }

    # Detect format
    if detect_event_data_format(df):
        preview["detected_format"] = "event_level"
        preview["planned_transformation"] = "Will aggregate events to daily metrics"
    elif detect_wide_format(df):
        preview["detected_format"] = "wide_format"
        preview["planned_transformation"] = "Already in suitable format for analysis"
    else:
        preview["detected_format"] = "timeseries"
        preview["planned_transformation"] = "Already in timeseries format"

    # Detect date column
    date_col, _ = detect_date_column(df)
    preview["date_column"] = date_col

    # Count numeric columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    preview["numeric_columns"] = list(numeric_cols)
    preview["numeric_count"] = len(numeric_cols)

    return preview
