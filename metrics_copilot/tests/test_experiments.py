"""Tests for experiment analysis module."""

import pytest
import pandas as pd
import numpy as np
from metrics_copilot.analysis_experiments import (
    analyze_experiment,
    identify_control_variant,
    bootstrap_ci,
)


def test_identify_control_variant():
    """Test control variant identification."""
    # Explicit control
    variants = ["control", "test"]
    assert identify_control_variant(variants) == "control"

    # A/B naming
    variants = ["A", "B"]
    assert identify_control_variant(variants) == "A"

    # Baseline naming
    variants = ["baseline", "treatment"]
    assert identify_control_variant(variants) == "baseline"


def test_bootstrap_ci():
    """Test bootstrap confidence interval calculation."""
    np.random.seed(42)

    # Create two samples with known difference
    control = pd.Series(np.random.normal(100, 10, 1000))
    test = pd.Series(np.random.normal(110, 10, 1000))  # 10% uplift

    ci_lower, ci_upper = bootstrap_ci(control, test, n_bootstrap=100)

    # Should detect positive uplift
    assert ci_lower > 0
    assert ci_upper > ci_lower
    # Should be approximately 10% uplift
    assert 5 < ci_lower < 15
    assert 5 < ci_upper < 15


def test_analyze_experiment():
    """Test experiment analysis."""
    np.random.seed(42)

    # Create experiment data
    n = 1000
    df = pd.DataFrame(
        {
            "variant": ["control"] * n + ["test"] * n,
            "conversion": [1 if np.random.random() < 0.05 else 0 for _ in range(n)]
            + [1 if np.random.random() < 0.06 else 0 for _ in range(n)],  # 5% baseline  # 6% test (20% uplift)
            "revenue": np.random.gamma(2, 50, n * 2),
        }
    )

    results = analyze_experiment(df, "variant", ["conversion", "revenue"])

    assert len(results) == 2  # Should analyze both KPIs

    # Check conversion result
    conv_result = next(r for r in results if r.kpi == "conversion")
    assert conv_result.control_count == n
    assert conv_result.test_count == n
    assert conv_result.uplift_pct > 0  # Should show positive uplift

    # Check that warnings are generated for any issues
    assert isinstance(conv_result.warnings, list)
