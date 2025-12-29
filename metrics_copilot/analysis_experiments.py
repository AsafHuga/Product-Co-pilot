"""A/B test and experiment analysis."""

import pandas as pd
import numpy as np
from typing import List, Optional
from scipy import stats
from metrics_copilot.schemas import ExperimentResult


def analyze_experiment(
    df: pd.DataFrame, experiment_col: str, kpi_columns: List[str], alpha: float = 0.05
) -> List[ExperimentResult]:
    """Analyze A/B test results.

    Args:
        df: Input dataframe
        experiment_col: Column containing experiment variants
        kpi_columns: List of KPI columns to analyze
        alpha: Significance level for hypothesis testing

    Returns:
        List of experiment results
    """
    results = []

    # Identify control and test groups
    variants = df[experiment_col].unique()
    variants = [v for v in variants if pd.notna(v)]

    if len(variants) < 2:
        return results

    # Try to identify control group
    control_variant = identify_control_variant(variants)
    test_variants = [v for v in variants if v != control_variant]

    # Analyze each KPI for each test variant
    for kpi in kpi_columns:
        if kpi not in df.columns:
            continue

        for test_variant in test_variants:
            control_data = df[df[experiment_col] == control_variant][kpi].dropna()
            test_data = df[df[experiment_col] == test_variant][kpi].dropna()

            if len(control_data) == 0 or len(test_data) == 0:
                continue

            # Calculate statistics
            control_mean = control_data.mean()
            test_mean = test_data.mean()
            control_std = control_data.std()
            test_std = test_data.std()
            control_count = len(control_data)
            test_count = len(test_data)

            uplift_abs = test_mean - control_mean
            uplift_pct = (uplift_abs / control_mean * 100) if control_mean != 0 else 0

            # Calculate confidence interval (using bootstrap)
            ci_lower, ci_upper = bootstrap_ci(control_data, test_data)

            # Perform t-test
            t_stat, p_value = stats.ttest_ind(test_data, control_data, equal_var=False)

            # Determine if significant
            significant = p_value < alpha and ci_lower * ci_upper > 0  # CI doesn't cross zero

            # Generate warnings
            warnings = generate_experiment_warnings(
                control_count, test_count, control_std, test_std, control_mean, test_mean
            )

            results.append(
                ExperimentResult(
                    kpi=kpi,
                    control_mean=round(control_mean, 6),
                    test_mean=round(test_mean, 6),
                    control_std=round(control_std, 6),
                    test_std=round(test_std, 6),
                    control_count=control_count,
                    test_count=test_count,
                    uplift_abs=round(uplift_abs, 6),
                    uplift_pct=round(uplift_pct, 2),
                    ci_lower=round(ci_lower, 2),
                    ci_upper=round(ci_upper, 2),
                    p_value=round(p_value, 4),
                    significant=significant,
                    warnings=warnings,
                )
            )

    return results


def identify_control_variant(variants: List) -> any:
    """Identify which variant is the control group.

    Args:
        variants: List of variant values

    Returns:
        Control variant value
    """
    variants_str = [str(v).lower() for v in variants]

    # Check for explicit control labels
    control_keywords = ['control', 'baseline', 'original', 'a']
    for i, v_str in enumerate(variants_str):
        if any(keyword in v_str for keyword in control_keywords):
            return variants[i]

    # Default to first variant
    return variants[0]


def bootstrap_ci(
    control: pd.Series, test: pd.Series, n_bootstrap: int = 1000, confidence: float = 0.95
) -> tuple[float, float]:
    """Calculate confidence interval for uplift using bootstrap.

    Args:
        control: Control group data
        test: Test group data
        n_bootstrap: Number of bootstrap samples
        confidence: Confidence level

    Returns:
        Tuple of (lower_ci, upper_ci) for uplift percentage
    """
    control_arr = control.values
    test_arr = test.values

    uplifts = []

    for _ in range(n_bootstrap):
        # Resample with replacement
        control_sample = np.random.choice(control_arr, size=len(control_arr), replace=True)
        test_sample = np.random.choice(test_arr, size=len(test_arr), replace=True)

        control_mean = np.mean(control_sample)
        test_mean = np.mean(test_sample)

        if control_mean != 0:
            uplift_pct = (test_mean - control_mean) / control_mean * 100
            uplifts.append(uplift_pct)

    # Calculate percentile-based CI
    alpha = 1 - confidence
    lower = np.percentile(uplifts, alpha / 2 * 100)
    upper = np.percentile(uplifts, (1 - alpha / 2) * 100)

    return lower, upper


def generate_experiment_warnings(
    control_count: int,
    test_count: int,
    control_std: float,
    test_std: float,
    control_mean: float,
    test_mean: float,
) -> List[str]:
    """Generate warnings about experiment quality.

    Args:
        control_count: Number of control observations
        test_count: Number of test observations
        control_std: Control standard deviation
        test_std: Test standard deviation
        control_mean: Control mean
        test_mean: Test mean

    Returns:
        List of warning messages
    """
    warnings = []

    # Sample size warnings
    min_sample_size = 100
    if control_count < min_sample_size or test_count < min_sample_size:
        warnings.append(
            f"Small sample size (control: {control_count}, test: {test_count}). "
            f"Results may not be reliable. Recommend at least {min_sample_size} per group."
        )

    # Sample ratio mismatch
    ratio = max(control_count, test_count) / min(control_count, test_count)
    if ratio > 2:
        warnings.append(
            f"Unbalanced sample sizes (ratio: {ratio:.1f}:1). "
            "This may indicate a sampling bias or implementation issue."
        )

    # High variance warning
    if control_std / control_mean > 1 or test_std / test_mean > 1:
        warnings.append("High variance detected. Results may be noisy or require longer test duration.")

    # Variance difference warning (Simpson's paradox risk)
    if max(control_std, test_std) / min(control_std, test_std) > 2:
        warnings.append(
            "Large difference in variance between groups. "
            "Consider checking for segment-level effects (Simpson's paradox)."
        )

    return warnings


def calculate_required_sample_size(
    baseline_mean: float,
    baseline_std: float,
    mde: float,  # Minimum detectable effect in percentage
    alpha: float = 0.05,
    power: float = 0.8,
) -> int:
    """Calculate required sample size per group.

    Args:
        baseline_mean: Baseline metric mean
        baseline_std: Baseline metric standard deviation
        mde: Minimum detectable effect (percentage)
        alpha: Significance level
        power: Statistical power

    Returns:
        Required sample size per group
    """
    # Convert MDE to absolute effect
    effect_size = baseline_mean * (mde / 100)

    # Cohen's d
    d = effect_size / baseline_std

    # Z-scores
    z_alpha = stats.norm.ppf(1 - alpha / 2)
    z_beta = stats.norm.ppf(power)

    # Sample size calculation
    n = 2 * ((z_alpha + z_beta) / d) ** 2

    return int(np.ceil(n))


def detect_peeking_risk(df: pd.DataFrame, date_col: Optional[str], experiment_col: str) -> List[str]:
    """Detect if there are signs of repeated significance testing (peeking).

    Args:
        df: Input dataframe
        date_col: Date column name
        experiment_col: Experiment column name

    Returns:
        List of warnings
    """
    warnings = []

    if date_col is None:
        return warnings

    # Check if experiment ran for reasonable duration
    date_series = df[date_col].dropna()
    if len(date_series) == 0:
        return warnings

    duration_days = (date_series.max() - date_series.min()).days

    if duration_days < 7:
        warnings.append(
            f"Experiment ran for only {duration_days} days. "
            "Short duration increases risk of false positives. Recommend at least 1-2 weeks."
        )

    # Check for day-of-week bias
    df_copy = df.copy()
    df_copy['day_of_week'] = pd.to_datetime(df_copy[date_col]).dt.dayofweek
    dow_counts = df_copy['day_of_week'].value_counts()

    if len(dow_counts) < 7 and duration_days >= 7:
        warnings.append(
            "Experiment doesn't cover all days of the week. "
            "Results may be biased by day-of-week effects."
        )

    return warnings
