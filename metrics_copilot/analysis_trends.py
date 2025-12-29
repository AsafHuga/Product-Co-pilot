"""Time series trend analysis and change point detection."""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Literal, Tuple
from metrics_copilot.schemas import TrendSummary, ChangePoint


def analyze_trends(
    df: pd.DataFrame, date_col: str, kpi_columns: List[str], window: int = 7
) -> List[TrendSummary]:
    """Analyze trends for each KPI.

    Args:
        df: Input dataframe
        date_col: Date column name
        kpi_columns: List of KPI column names
        window: Rolling window size for smoothing

    Returns:
        List of trend summaries
    """
    trends = []

    # Sort by date
    df_sorted = df.sort_values(date_col).copy()

    for kpi in kpi_columns:
        if kpi not in df_sorted.columns:
            continue

        # Aggregate by date (in case multiple rows per date)
        daily_data = df_sorted.groupby(date_col)[kpi].mean().dropna()

        if len(daily_data) < 2:
            continue

        # Calculate rolling mean
        rolling_mean = daily_data.rolling(window=min(window, len(daily_data)), center=False).mean()

        # Overall change
        first_val = daily_data.iloc[0]
        last_val = daily_data.iloc[-1]
        overall_change_pct = ((last_val - first_val) / first_val * 100) if first_val != 0 else 0

        # Recent change (last 7 days vs previous 7 days, or last 20% vs previous 20%)
        recent_period = max(7, int(len(daily_data) * 0.2))
        if len(daily_data) >= recent_period * 2:
            recent_val = daily_data.iloc[-recent_period:].mean()
            previous_val = daily_data.iloc[-recent_period * 2 : -recent_period].mean()
            recent_change_pct = ((recent_val - previous_val) / previous_val * 100) if previous_val != 0 else 0
        else:
            recent_change_pct = overall_change_pct

        # Determine direction
        direction = determine_direction(overall_change_pct, recent_change_pct, daily_data)

        # Generate description
        description = generate_trend_description(
            kpi, direction, overall_change_pct, recent_change_pct, first_val, last_val
        )

        trends.append(
            TrendSummary(
                kpi=kpi,
                direction=direction,
                overall_change_pct=round(overall_change_pct, 2),
                recent_change_pct=round(recent_change_pct, 2),
                description=description,
            )
        )

    return trends


def determine_direction(
    overall_change: float, recent_change: float, series: pd.Series
) -> Literal["increasing", "decreasing", "stable", "volatile"]:
    """Determine trend direction.

    Args:
        overall_change: Overall percent change
        recent_change: Recent percent change
        series: Time series data

    Returns:
        Direction label
    """
    # Calculate volatility
    returns = series.pct_change().dropna()
    volatility = returns.std() * 100 if len(returns) > 1 else 0

    # High volatility
    if volatility > 20:
        return "volatile"

    # Stable (less than 5% change)
    if abs(overall_change) < 5 and abs(recent_change) < 5:
        return "stable"

    # Use recent change as primary signal
    if recent_change > 5:
        return "increasing"
    elif recent_change < -5:
        return "decreasing"
    elif overall_change > 5:
        return "increasing"
    elif overall_change < -5:
        return "decreasing"
    else:
        return "stable"


def generate_trend_description(
    kpi: str,
    direction: str,
    overall_change: float,
    recent_change: float,
    first_val: float,
    last_val: float,
) -> str:
    """Generate human-readable trend description.

    Args:
        kpi: KPI name
        direction: Trend direction
        overall_change: Overall percent change
        recent_change: Recent percent change
        first_val: First value
        last_val: Last value

    Returns:
        Description string
    """
    if direction == "stable":
        return f"{kpi} remained stable (±{abs(overall_change):.1f}% overall)"
    elif direction == "volatile":
        return f"{kpi} is highly volatile with frequent fluctuations"
    elif direction == "increasing":
        return f"{kpi} increased {overall_change:+.1f}% overall (recent: {recent_change:+.1f}%)"
    elif direction == "decreasing":
        return f"{kpi} decreased {overall_change:.1f}% overall (recent: {recent_change:.1f}%)"
    else:
        return f"{kpi} changed {overall_change:+.1f}%"


def detect_change_points(
    df: pd.DataFrame, date_col: str, kpi_columns: List[str], min_size: int = 5
) -> List[ChangePoint]:
    """Detect significant change points in time series.

    Args:
        df: Input dataframe
        date_col: Date column name
        kpi_columns: List of KPI column names
        min_size: Minimum segment size for change detection

    Returns:
        List of detected change points
    """
    change_points = []

    # Sort by date
    df_sorted = df.sort_values(date_col).copy()

    for kpi in kpi_columns:
        if kpi not in df_sorted.columns:
            continue

        # Aggregate by date
        daily_data = df_sorted.groupby(date_col)[kpi].mean().dropna()

        if len(daily_data) < min_size * 2:
            continue

        # Simple change point detection using rolling window comparison
        cps = detect_change_points_simple(daily_data, min_size)

        for cp_idx in cps:
            if cp_idx >= len(daily_data) or cp_idx < min_size:
                continue

            # Calculate before/after statistics
            before_data = daily_data.iloc[max(0, cp_idx - min_size) : cp_idx]
            after_data = daily_data.iloc[cp_idx : min(len(daily_data), cp_idx + min_size)]

            if len(before_data) == 0 or len(after_data) == 0:
                continue

            before_mean = before_data.mean()
            after_mean = after_data.mean()
            delta_abs = after_mean - before_mean
            delta_pct = (delta_abs / before_mean * 100) if before_mean != 0 else 0

            # Only report significant changes
            if abs(delta_pct) < 10:
                continue

            # Determine confidence based on magnitude and consistency
            confidence = determine_changepoint_confidence(before_data, after_data, delta_pct)

            change_points.append(
                ChangePoint(
                    date=str(daily_data.index[cp_idx]),
                    kpi=kpi,
                    before_mean=round(before_mean, 4),
                    after_mean=round(after_mean, 4),
                    delta_abs=round(delta_abs, 4),
                    delta_pct=round(delta_pct, 2),
                    confidence=confidence,
                )
            )

    # Sort by absolute delta
    change_points.sort(key=lambda cp: abs(cp.delta_pct), reverse=True)

    return change_points[:10]  # Return top 10


def detect_change_points_simple(series: pd.Series, min_size: int = 5) -> List[int]:
    """Simple change point detection using rolling statistics.

    Args:
        series: Time series data
        min_size: Minimum segment size

    Returns:
        List of change point indices
    """
    if len(series) < min_size * 2:
        return []

    change_points = []
    values = series.values

    # Use sliding window to detect shifts
    for i in range(min_size, len(values) - min_size):
        before = values[i - min_size : i]
        after = values[i : i + min_size]

        before_mean = np.mean(before)
        after_mean = np.mean(after)
        before_std = np.std(before)

        if before_std == 0:
            continue

        # Calculate z-score of the change
        z_score = abs(after_mean - before_mean) / before_std

        # If change is significant (z > 2)
        if z_score > 2:
            # Check if this is a new change point (not too close to previous)
            if not change_points or i - change_points[-1] >= min_size:
                change_points.append(i)

    return change_points


def determine_changepoint_confidence(
    before: pd.Series, after: pd.Series, delta_pct: float
) -> Literal["high", "medium", "low"]:
    """Determine confidence level of change point.

    Args:
        before: Data before change point
        after: Data after change point
        delta_pct: Percent change

    Returns:
        Confidence level
    """
    # High confidence: large change with low variance
    before_cv = (before.std() / before.mean()) if before.mean() != 0 else 1
    after_cv = (after.std() / after.mean()) if after.mean() != 0 else 1

    if abs(delta_pct) > 30 and before_cv < 0.2 and after_cv < 0.2:
        return "high"
    elif abs(delta_pct) > 20 or (before_cv < 0.3 and after_cv < 0.3):
        return "medium"
    else:
        return "low"


def find_largest_deltas(
    df: pd.DataFrame, date_col: str, kpi_columns: List[str], top_n: int = 3
) -> List[Dict[str, any]]:
    """Find the largest delta windows (spikes/drops).

    Args:
        df: Input dataframe
        date_col: Date column name
        kpi_columns: List of KPI column names
        top_n: Number of top deltas to return

    Returns:
        List of delta windows
    """
    deltas = []

    df_sorted = df.sort_values(date_col).copy()

    for kpi in kpi_columns:
        if kpi not in df_sorted.columns:
            continue

        daily_data = df_sorted.groupby(date_col)[kpi].mean().dropna()

        if len(daily_data) < 2:
            continue

        # Calculate day-over-day percent changes
        pct_changes = daily_data.pct_change() * 100

        for idx in pct_changes.abs().nlargest(top_n).index:
            if pd.isna(pct_changes[idx]):
                continue

            deltas.append(
                {
                    "kpi": kpi,
                    "date": str(idx),
                    "value": round(daily_data[idx], 4),
                    "previous_value": round(daily_data[daily_data.index < idx].iloc[-1], 4)
                    if len(daily_data[daily_data.index < idx]) > 0
                    else None,
                    "delta_pct": round(pct_changes[idx], 2),
                    "type": "spike" if pct_changes[idx] > 0 else "drop",
                }
            )

    # Sort by absolute delta
    deltas.sort(key=lambda d: abs(d["delta_pct"]), reverse=True)

    return deltas[:top_n]
