"""Data ingestion and cleaning utilities."""

import pandas as pd
import numpy as np
from typing import Tuple, List, Optional
import re
from datetime import datetime
import chardet


def detect_encoding(file_path: str) -> str:
    """Detect file encoding.

    Args:
        file_path: Path to the CSV file

    Returns:
        Detected encoding (e.g., 'utf-8', 'latin-1')
    """
    with open(file_path, 'rb') as f:
        result = chardet.detect(f.read(100000))
    return result['encoding'] or 'utf-8'


def detect_delimiter(file_path: str, encoding: str) -> str:
    """Detect CSV delimiter.

    Args:
        file_path: Path to the CSV file
        encoding: File encoding

    Returns:
        Detected delimiter
    """
    with open(file_path, 'r', encoding=encoding) as f:
        first_line = f.readline()

    # Try common delimiters
    delimiters = [',', '\t', ';', '|']
    counts = {d: first_line.count(d) for d in delimiters}
    return max(counts, key=counts.get)


def standardize_column_name(col: str) -> str:
    """Convert column name to snake_case.

    Args:
        col: Original column name

    Returns:
        Standardized column name
    """
    # Remove special characters, replace spaces/dashes with underscores
    col = re.sub(r'[^\w\s-]', '', col)
    col = re.sub(r'[-\s]+', '_', col)
    # Convert to lowercase
    col = col.lower().strip('_')
    return col


def parse_numeric_column(series: pd.Series) -> pd.Series:
    """Parse numeric column that may contain commas, %, $, etc.

    Args:
        series: Pandas series to parse

    Returns:
        Parsed numeric series
    """
    if pd.api.types.is_numeric_dtype(series):
        return series

    # Convert to string and clean
    cleaned = series.astype(str).str.replace(',', '').str.replace('$', '').str.replace('%', '').str.strip()

    # Try to convert to numeric
    try:
        return pd.to_numeric(cleaned, errors='coerce')
    except:
        return series


def detect_date_column(df: pd.DataFrame) -> Tuple[Optional[str], pd.DataFrame]:
    """Detect and parse the best date column.

    Args:
        df: Input dataframe

    Returns:
        Tuple of (date_column_name, dataframe with parsed date)
    """
    date_candidates = []

    for col in df.columns:
        # Check column name
        if any(keyword in col for keyword in ['date', 'time', 'day', 'dt', 'timestamp', 'ts']):
            date_candidates.append(col)
            continue

        # Check if values look like dates
        sample = df[col].dropna().head(100).astype(str)
        if sample.empty:
            continue

        # Try to parse as date
        try:
            parsed = pd.to_datetime(sample, errors='coerce')
            if parsed.notna().sum() / len(sample) > 0.8:  # 80% successfully parsed
                date_candidates.append(col)
        except:
            continue

    if not date_candidates:
        return None, df

    # Choose the best candidate (prefer 'date' in name, then first found)
    best_candidate = None
    for candidate in date_candidates:
        if 'date' in candidate:
            best_candidate = candidate
            break
    if not best_candidate:
        best_candidate = date_candidates[0]

    # Parse the date column
    df[best_candidate] = pd.to_datetime(df[best_candidate], errors='coerce')

    return best_candidate, df


def infer_column_type(series: pd.Series) -> str:
    """Infer the semantic type of a column.

    Args:
        series: Pandas series

    Returns:
        Column type: 'numeric', 'categorical', 'datetime', 'text', 'id'
    """
    # Remove nulls for analysis
    non_null = series.dropna()

    if len(non_null) == 0:
        return 'unknown'

    # Check if datetime
    if pd.api.types.is_datetime64_any_dtype(series):
        return 'datetime'

    # Check if numeric
    if pd.api.types.is_numeric_dtype(series):
        return 'numeric'

    # Check cardinality
    cardinality = series.nunique()
    total_count = len(series)

    # High cardinality suggests ID or text
    if cardinality / total_count > 0.95:
        # Check if looks like ID
        sample = non_null.astype(str).head(10)
        if all(len(s) > 10 for s in sample) or all(re.match(r'^[a-f0-9-]+$', s) for s in sample):
            return 'id'
        return 'text'

    # Low cardinality suggests categorical
    if cardinality < 50 or cardinality / total_count < 0.05:
        return 'categorical'

    return 'text'


def clean_and_validate_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
    """Clean data and track validation issues.

    Args:
        df: Input dataframe

    Returns:
        Tuple of (cleaned dataframe, list of validation messages)
    """
    issues = []

    # Check for duplicates
    duplicates = df.duplicated().sum()
    if duplicates > 0:
        issues.append(f"Found {duplicates} duplicate rows ({duplicates/len(df)*100:.1f}%)")

    # Parse numeric columns
    for col in df.columns:
        if df[col].dtype == 'object':
            # Try to parse as numeric
            original_nulls = df[col].isna().sum()
            parsed = parse_numeric_column(df[col])
            new_nulls = parsed.isna().sum()

            if new_nulls - original_nulls <= len(df) * 0.1:  # Less than 10% conversion errors
                if not parsed.equals(df[col]):
                    df[col] = parsed
                    if new_nulls > original_nulls:
                        issues.append(
                            f"Converted '{col}' to numeric, {new_nulls - original_nulls} values became null"
                        )

    # Check for impossible values in common metric types
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            # Check for negative values in columns that shouldn't have them
            if any(keyword in col for keyword in ['count', 'revenue', 'dau', 'users', 'sessions']):
                negatives = (df[col] < 0).sum()
                if negatives > 0:
                    issues.append(f"Found {negatives} negative values in '{col}' (likely invalid)")

            # Check for rates/percentages > 1
            if any(keyword in col for keyword in ['rate', 'conversion', 'retention', 'pct', 'percent']):
                # Check if values are percentages (0-100) or rates (0-1)
                max_val = df[col].max()
                if max_val > 1 and max_val <= 100:
                    # Likely percentage, convert to rate
                    df[col] = df[col] / 100
                    issues.append(f"Converted '{col}' from percentage (0-100) to rate (0-1)")
                elif max_val > 1:
                    invalids = (df[col] > 1).sum()
                    if invalids > 0:
                        issues.append(f"Found {invalids} values > 1 in rate column '{col}' (likely invalid)")

    return df, issues


def ingest_csv(file_path: str) -> Tuple[pd.DataFrame, dict]:
    """Ingest and clean CSV file.

    Args:
        file_path: Path to CSV file

    Returns:
        Tuple of (cleaned dataframe, metadata dict)
    """
    metadata = {
        "original_file": file_path,
        "ingestion_timestamp": datetime.now().isoformat(),
        "transformations": [],
    }

    # Detect encoding
    encoding = detect_encoding(file_path)
    metadata["encoding"] = encoding

    # Detect delimiter
    delimiter = detect_delimiter(file_path, encoding)
    metadata["delimiter"] = delimiter

    # Read CSV
    df = pd.read_csv(file_path, encoding=encoding, sep=delimiter)
    metadata["original_shape"] = df.shape

    # Detect if first row is actually the header (common export issue)
    # Check if current headers look generic (Unnamed, numbered, etc.) but first row looks like column names
    has_unnamed_cols = any('unnamed' in str(col).lower() for col in df.columns)

    if has_unnamed_cols and len(df) > 0:
        first_row = df.iloc[0]
        # Check if first row values look like column names (all strings, no numbers)
        first_row_looks_like_headers = all(
            isinstance(val, str) and not str(val).replace('.', '').replace('-', '').replace('/', '').isdigit()
            for val in first_row if pd.notna(val)
        )

        if first_row_looks_like_headers:
            # Use first row as headers
            new_columns = first_row.tolist()
            df = df.iloc[1:].reset_index(drop=True)
            df.columns = new_columns
            metadata["transformations"].append("Detected actual headers in first data row, promoted to column names")
            metadata["original_shape"] = df.shape

    # Standardize column names
    original_columns = df.columns.tolist()
    df.columns = [standardize_column_name(col) for col in df.columns]
    metadata["column_mapping"] = dict(zip(original_columns, df.columns))
    metadata["transformations"].append("Standardized column names to snake_case")

    # Detect and parse date column
    date_col, df = detect_date_column(df)
    if date_col:
        metadata["date_column"] = date_col
        metadata["transformations"].append(f"Detected and parsed date column: {date_col}")
    else:
        metadata["date_column"] = None
        metadata["transformations"].append("No date column detected")

    # Clean and validate
    df, validation_issues = clean_and_validate_data(df)
    metadata["validation_issues"] = validation_issues
    metadata["final_shape"] = df.shape

    return df, metadata
