"""Segment-level decomposition and driver analysis."""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Tuple
from metrics_copilot.schemas import SegmentDriver


def analyze_segment_drivers(
    df: pd.DataFrame,
    segment_columns: List[str],
    kpi_columns: List[str],
    date_col: Optional[str] = None,
    top_n: int = 10,
) -> List[SegmentDriver]:
    """Analyze which segments drive changes in KPIs.

    Args:
        df: Input dataframe
        segment_columns: List of segment column names
        kpi_columns: List of KPI column names
        date_col: Date column name (for before/after analysis)
        top_n: Number of top drivers to return per KPI

    Returns:
        List of segment drivers
    """
    drivers = []

    for kpi in kpi_columns:
        if kpi not in df.columns:
            continue

        for seg_col in segment_columns:
            if seg_col not in df.columns:
                continue

            # Calculate segment contributions
            seg_drivers = calculate_segment_contribution(df, seg_col, kpi, date_col)
            drivers.extend(seg_drivers)

    # Sort by absolute contribution
    drivers.sort(key=lambda d: abs(d.contribution_abs), reverse=True)

    return drivers[:top_n]


def calculate_segment_contribution(
    df: pd.DataFrame, segment_col: str, kpi: str, date_col: Optional[str] = None
) -> List[SegmentDriver]:
    """Calculate how each segment value contributes to overall KPI change.

    Args:
        df: Input dataframe
        segment_col: Segment column name
        kpi: KPI column name
        date_col: Date column for before/after analysis

    Returns:
        List of segment drivers
    """
    drivers = []

    # If we have time series, do before/after analysis
    if date_col and date_col in df.columns:
        drivers = calculate_temporal_contribution(df, segment_col, kpi, date_col)
    else:
        # Static analysis: compare segment means to overall mean
        drivers = calculate_static_contribution(df, segment_col, kpi)

    return drivers


def calculate_temporal_contribution(
    df: pd.DataFrame, segment_col: str, kpi: str, date_col: str
) -> List[SegmentDriver]:
    """Calculate segment contribution over time (before vs after analysis).

    Args:
        df: Input dataframe
        segment_col: Segment column name
        kpi: KPI column name
        date_col: Date column name

    Returns:
        List of segment drivers
    """
    drivers = []

    # Split into before/after periods (use median date as split)
    df_sorted = df.sort_values(date_col)
    median_idx = len(df_sorted) // 2

    before_df = df_sorted.iloc[:median_idx]
    after_df = df_sorted.iloc[median_idx:]

    # Calculate overall change
    overall_before = before_df[kpi].mean()
    overall_after = after_df[kpi].mean()
    overall_change = overall_after - overall_before

    if overall_change == 0 or pd.isna(overall_change):
        return drivers

    # Calculate per-segment contribution
    for segment_value in df[segment_col].unique():
        if pd.isna(segment_value):
            continue

        seg_before = before_df[before_df[segment_col] == segment_value][kpi]
        seg_after = after_df[after_df[segment_col] == segment_value][kpi]

        if len(seg_before) == 0 or len(seg_after) == 0:
            continue

        seg_before_mean = seg_before.mean()
        seg_after_mean = seg_after.mean()
        seg_change = seg_after_mean - seg_before_mean

        # Calculate segment size (as proportion)
        seg_size_before = len(seg_before)
        seg_size_after = len(seg_after)
        avg_seg_size = (seg_size_before + seg_size_after) / 2

        # Contribution: segment change weighted by segment size
        contribution_abs = seg_change * (avg_seg_size / len(df))
        contribution_pct = (contribution_abs / abs(overall_change) * 100) if overall_change != 0 else 0

        drivers.append(
            SegmentDriver(
                segment_column=segment_col,
                segment_value=str(segment_value),
                kpi=kpi,
                contribution_abs=round(contribution_abs, 6),
                contribution_pct=round(contribution_pct, 2),
                segment_mean=round(seg_after_mean, 6),
                segment_size=int(avg_seg_size),
            )
        )

    return drivers


def calculate_static_contribution(df: pd.DataFrame, segment_col: str, kpi: str) -> List[SegmentDriver]:
    """Calculate segment contribution in static data (no time dimension).

    Args:
        df: Input dataframe
        segment_col: Segment column name
        kpi: KPI column name

    Returns:
        List of segment drivers
    """
    drivers = []

    overall_mean = df[kpi].mean()

    for segment_value in df[segment_col].unique():
        if pd.isna(segment_value):
            continue

        seg_data = df[df[segment_col] == segment_value][kpi].dropna()

        if len(seg_data) == 0:
            continue

        seg_mean = seg_data.mean()
        seg_size = len(seg_data)

        # Contribution: difference from overall mean, weighted by size
        deviation = seg_mean - overall_mean
        contribution_abs = deviation * (seg_size / len(df))
        contribution_pct = (contribution_abs / overall_mean * 100) if overall_mean != 0 else 0

        drivers.append(
            SegmentDriver(
                segment_column=segment_col,
                segment_value=str(segment_value),
                kpi=kpi,
                contribution_abs=round(contribution_abs, 6),
                contribution_pct=round(contribution_pct, 2),
                segment_mean=round(seg_mean, 6),
                segment_size=seg_size,
            )
        )

    return drivers


def find_anomalous_segments(
    df: pd.DataFrame, segment_columns: List[str], kpi_columns: List[str], threshold: float = 2.0
) -> List[Dict[str, any]]:
    """Find segments with anomalous KPI values.

    Args:
        df: Input dataframe
        segment_columns: List of segment column names
        kpi_columns: List of KPI column names
        threshold: Z-score threshold for anomaly detection

    Returns:
        List of anomalous segments
    """
    anomalies = []

    for kpi in kpi_columns:
        if kpi not in df.columns:
            continue

        overall_mean = df[kpi].mean()
        overall_std = df[kpi].std()

        if overall_std == 0:
            continue

        for seg_col in segment_columns:
            if seg_col not in df.columns:
                continue

            for seg_value in df[seg_col].unique():
                if pd.isna(seg_value):
                    continue

                seg_data = df[df[seg_col] == seg_value][kpi].dropna()

                if len(seg_data) < 10:  # Skip small segments
                    continue

                seg_mean = seg_data.mean()

                # Calculate z-score
                z_score = (seg_mean - overall_mean) / overall_std

                if abs(z_score) > threshold:
                    anomalies.append(
                        {
                            "segment_column": seg_col,
                            "segment_value": str(seg_value),
                            "kpi": kpi,
                            "segment_mean": round(seg_mean, 6),
                            "overall_mean": round(overall_mean, 6),
                            "z_score": round(z_score, 2),
                            "segment_size": len(seg_data),
                            "direction": "above" if z_score > 0 else "below",
                        }
                    )

    # Sort by z-score magnitude
    anomalies.sort(key=lambda a: abs(a["z_score"]), reverse=True)

    return anomalies[:20]  # Return top 20


def decompose_kpi(
    df: pd.DataFrame, kpi: str, numerator: Optional[str] = None, denominator: Optional[str] = None
) -> Dict[str, any]:
    """Decompose a KPI into its components (numerator/denominator analysis).

    Args:
        df: Input dataframe
        kpi: KPI column name
        numerator: Numerator column name (if rate/ratio)
        denominator: Denominator column name (if rate/ratio)

    Returns:
        Dictionary with decomposition results
    """
    result = {"kpi": kpi, "type": "simple"}

    # If we have numerator and denominator
    if numerator and denominator and numerator in df.columns and denominator in df.columns:
        num_mean = df[numerator].mean()
        denom_mean = df[denominator].mean()
        kpi_mean = df[kpi].mean()

        # Calculate what happens if we change each component
        num_change_impact = (num_mean * 1.1) / denom_mean - kpi_mean  # 10% increase in numerator
        denom_change_impact = num_mean / (denom_mean * 1.1) - kpi_mean  # 10% increase in denominator

        result.update(
            {
                "type": "ratio",
                "numerator": numerator,
                "denominator": denominator,
                "numerator_mean": round(num_mean, 6),
                "denominator_mean": round(denom_mean, 6),
                "kpi_mean": round(kpi_mean, 6),
                "numerator_sensitivity": round(num_change_impact / kpi_mean * 100, 2),
                "denominator_sensitivity": round(denom_change_impact / kpi_mean * 100, 2),
            }
        )
    else:
        result.update({"kpi_mean": round(df[kpi].mean(), 6), "kpi_std": round(df[kpi].std(), 6)})

    return result
