"""Insight generation and decision recommendations."""

import pandas as pd
from typing import List, Dict, Any, Literal, Optional
from metrics_copilot.schemas import (
    Hypothesis,
    NextCheck,
    RecommendedDecision,
    AnalysisReport,
    ExperimentResult,
    ChangePoint,
    SegmentDriver,
    TrendSummary,
)

# Optional LLM integration
try:
    from .llm_insights import create_llm_generator, is_llm_available
    LLM_ENABLED = True
except ImportError:
    LLM_ENABLED = False


def generate_hypotheses(
    report: AnalysisReport,
    df: pd.DataFrame,
    use_llm: bool = True
) -> List[Hypothesis]:
    """Generate hypotheses about what happened in the data.

    Args:
        report: Analysis report with all findings
        df: Original dataframe
        use_llm: Whether to use LLM for enhanced insights (default: True)

    Returns:
        List of hypotheses
    """
    # Try LLM-enhanced hypotheses first
    if use_llm and LLM_ENABLED and is_llm_available():
        try:
            llm_generator = create_llm_generator()
            if llm_generator:
                llm_hypotheses = llm_generator.enhance_hypotheses(report, max_hypotheses=10)
                if llm_hypotheses:
                    return llm_hypotheses
        except Exception as e:
            print(f"LLM hypothesis generation failed, falling back to rule-based: {e}")

    # Fallback to rule-based hypotheses
    hypotheses = []

    # Hypotheses from change points
    hypotheses.extend(generate_changepoint_hypotheses(report.change_points, report.segment_drivers))

    # Hypotheses from segment drivers
    hypotheses.extend(generate_segment_hypotheses(report.segment_drivers, report.overall_trends))

    # Hypotheses from experiment results
    hypotheses.extend(generate_experiment_hypotheses(report.experiment_results))

    # Hypotheses from anomalies
    hypotheses.extend(generate_anomaly_hypotheses(report.anomalies))

    # Sort by confidence
    confidence_order = {"high": 0, "medium": 1, "low": 2}
    hypotheses.sort(key=lambda h: confidence_order[h.confidence])

    return hypotheses[:10]  # Top 10


def generate_changepoint_hypotheses(
    change_points: List[ChangePoint], segment_drivers: List[SegmentDriver]
) -> List[Hypothesis]:
    """Generate hypotheses from detected change points.

    Args:
        change_points: List of detected change points
        segment_drivers: List of segment drivers

    Returns:
        List of hypotheses
    """
    hypotheses = []

    for cp in change_points[:3]:  # Top 3 change points
        evidence = [
            f"{cp.kpi} changed from {cp.before_mean:.4f} to {cp.after_mean:.4f} on {cp.date}",
            f"Magnitude: {cp.delta_pct:+.1f}%",
        ]

        # Check if any segment drives this change
        related_segments = []
        for driver in segment_drivers:
            if driver.kpi == cp.kpi and abs(driver.contribution_pct) > 20:
                related_segments.append(f"{driver.segment_column}={driver.segment_value}")
                evidence.append(
                    f"{driver.segment_column}={driver.segment_value} contributed {driver.contribution_pct:.1f}%"
                )

        if related_segments:
            description = (
                f"{cp.kpi} {'increased' if cp.delta_pct > 0 else 'decreased'} by {abs(cp.delta_pct):.1f}% "
                f"on {cp.date}, primarily driven by changes in {', '.join(related_segments[:2])}"
            )
            confidence = "high"
        else:
            description = (
                f"{cp.kpi} {'increased' if cp.delta_pct > 0 else 'decreased'} by {abs(cp.delta_pct):.1f}% "
                f"on {cp.date} across all segments"
            )
            confidence = cp.confidence

        hypotheses.append(
            Hypothesis(
                description=description,
                confidence=confidence,
                supporting_evidence=evidence,
                related_kpis=[cp.kpi],
                related_segments=related_segments,
            )
        )

    return hypotheses


def generate_segment_hypotheses(
    segment_drivers: List[SegmentDriver], trends: List[TrendSummary]
) -> List[Hypothesis]:
    """Generate hypotheses from segment analysis.

    Args:
        segment_drivers: List of segment drivers
        trends: List of trend summaries

    Returns:
        List of hypotheses
    """
    hypotheses = []

    # Group drivers by KPI
    kpi_groups: Dict[str, List[SegmentDriver]] = {}
    for driver in segment_drivers:
        if driver.kpi not in kpi_groups:
            kpi_groups[driver.kpi] = []
        kpi_groups[driver.kpi].append(driver)

    for kpi, drivers in kpi_groups.items():
        # Top positive and negative contributors
        positive_drivers = [d for d in drivers if d.contribution_pct > 0]
        negative_drivers = [d for d in drivers if d.contribution_pct < 0]

        if positive_drivers:
            top_positive = positive_drivers[0]
            evidence = [
                f"{top_positive.segment_column}={top_positive.segment_value} has mean {top_positive.segment_mean:.4f}",
                f"Contributes {top_positive.contribution_pct:.1f}% to overall {kpi}",
                f"Segment size: {top_positive.segment_size} observations",
            ]

            description = (
                f"{kpi} performance is strongly influenced by {top_positive.segment_column}={top_positive.segment_value}, "
                f"contributing {top_positive.contribution_pct:.1f}% to the total"
            )

            hypotheses.append(
                Hypothesis(
                    description=description,
                    confidence="high" if abs(top_positive.contribution_pct) > 30 else "medium",
                    supporting_evidence=evidence,
                    related_kpis=[kpi],
                    related_segments=[f"{top_positive.segment_column}={top_positive.segment_value}"],
                )
            )

        if negative_drivers:
            top_negative = negative_drivers[0]
            evidence = [
                f"{top_negative.segment_column}={top_negative.segment_value} has mean {top_negative.segment_mean:.4f}",
                f"Drags down {kpi} by {abs(top_negative.contribution_pct):.1f}%",
                f"Segment size: {top_negative.segment_size} observations",
            ]

            description = (
                f"{top_negative.segment_column}={top_negative.segment_value} is a drag on {kpi}, "
                f"reducing it by {abs(top_negative.contribution_pct):.1f}%"
            )

            hypotheses.append(
                Hypothesis(
                    description=description,
                    confidence="high" if abs(top_negative.contribution_pct) > 30 else "medium",
                    supporting_evidence=evidence,
                    related_kpis=[kpi],
                    related_segments=[f"{top_negative.segment_column}={top_negative.segment_value}"],
                )
            )

    return hypotheses[:5]


def generate_experiment_hypotheses(experiments: List[ExperimentResult]) -> List[Hypothesis]:
    """Generate hypotheses from experiment results.

    Args:
        experiments: List of experiment results

    Returns:
        List of hypotheses
    """
    hypotheses = []

    for exp in experiments[:3]:  # Top 3 experiments
        evidence = [
            f"Control mean: {exp.control_mean:.4f}, Test mean: {exp.test_mean:.4f}",
            f"Uplift: {exp.uplift_pct:+.2f}%",
            f"95% CI: [{exp.ci_lower:.2f}%, {exp.ci_upper:.2f}%]",
            f"p-value: {exp.p_value:.4f}",
            f"Sample sizes: control={exp.control_count}, test={exp.test_count}",
        ]

        if exp.warnings:
            evidence.extend([f"Warning: {w}" for w in exp.warnings])

        if exp.significant:
            if exp.uplift_pct > 0:
                description = (
                    f"Test variant shows significant positive impact on {exp.kpi} "
                    f"({exp.uplift_pct:+.2f}% uplift, p={exp.p_value:.4f})"
                )
            else:
                description = (
                    f"Test variant shows significant negative impact on {exp.kpi} "
                    f"({exp.uplift_pct:.2f}% decline, p={exp.p_value:.4f})"
                )
            confidence = "high" if not exp.warnings else "medium"
        else:
            description = f"No significant difference detected for {exp.kpi} (p={exp.p_value:.4f})"
            confidence = "medium"

        hypotheses.append(
            Hypothesis(
                description=description,
                confidence=confidence,
                supporting_evidence=evidence,
                related_kpis=[exp.kpi],
                related_segments=[],
            )
        )

    return hypotheses


def generate_anomaly_hypotheses(anomalies: List[Any]) -> List[Hypothesis]:
    """Generate hypotheses from detected anomalies.

    Args:
        anomalies: List of anomalies

    Returns:
        List of hypotheses
    """
    hypotheses = []

    for anomaly in anomalies[:3]:
        if anomaly.type == "data_quality":
            description = f"Data quality issue detected: {anomaly.description}"
            confidence = "high"
            evidence = [anomaly.description]
            if anomaly.affected_column:
                evidence.append(f"Affected column: {anomaly.affected_column}")
            if anomaly.affected_rows:
                evidence.append(f"Affected rows: {anomaly.affected_rows}")

            hypotheses.append(
                Hypothesis(
                    description=description,
                    confidence=confidence,
                    supporting_evidence=evidence,
                    related_kpis=[anomaly.affected_column] if anomaly.affected_column else [],
                    related_segments=[],
                )
            )

    return hypotheses


def generate_next_checks(report: AnalysisReport) -> List[NextCheck]:
    """Generate recommended follow-up investigations.

    Args:
        report: Analysis report

    Returns:
        List of recommended checks
    """
    checks = []

    # Checks from change points
    for cp in report.change_points[:3]:
        checks.append(
            NextCheck(
                question=f"What caused {cp.kpi} to change on {cp.date}?",
                sql_like_query=f"SELECT * FROM events WHERE date = '{cp.date}' ORDER BY {cp.kpi} DESC",
                priority="high" if abs(cp.delta_pct) > 30 else "medium",
                why=f"Investigate {abs(cp.delta_pct):.1f}% change in {cp.kpi}",
            )
        )

    # Checks from segment drivers
    for driver in report.segment_drivers[:3]:
        if abs(driver.contribution_pct) > 20:
            checks.append(
                NextCheck(
                    question=f"Why is {driver.segment_column}={driver.segment_value} contributing {driver.contribution_pct:.1f}% to {driver.kpi}?",
                    sql_like_query=f"SELECT * FROM data WHERE {driver.segment_column} = '{driver.segment_value}' AND {driver.kpi} IS NOT NULL",
                    priority="high",
                    why=f"Major contributor to {driver.kpi}",
                )
            )

    # Checks from experiment results
    for exp in report.experiment_results:
        if exp.warnings:
            checks.append(
                NextCheck(
                    question=f"Are the warnings for {exp.kpi} experiment valid concerns?",
                    sql_like_query=f"SELECT variant, COUNT(*), AVG({exp.kpi}), STDDEV({exp.kpi}) FROM experiment GROUP BY variant",
                    priority="high" if exp.significant else "medium",
                    why="; ".join(exp.warnings),
                )
            )

    # Checks from anomalies
    for anomaly in report.anomalies[:3]:
        if anomaly.severity == "high":
            checks.append(
                NextCheck(
                    question=f"How should we handle: {anomaly.description}?",
                    sql_like_query=f"SELECT * FROM data WHERE {anomaly.affected_column} IS NULL"
                    if anomaly.affected_column
                    else "SELECT * FROM data",
                    priority="high",
                    why=f"Data quality issue with {anomaly.severity} severity",
                )
            )

    # Sort by priority
    priority_order = {"high": 0, "medium": 1, "low": 2}
    checks.sort(key=lambda c: priority_order[c.priority])

    return checks[:10]


def generate_decisions(report: AnalysisReport) -> List[RecommendedDecision]:
    """Generate recommended decisions based on analysis.

    Args:
        report: Analysis report

    Returns:
        List of recommended decisions
    """
    decisions = []

    # Decision from experiment results
    if report.experiment_results:
        primary_exp = report.experiment_results[0]  # Assume first is primary

        if primary_exp.significant:
            if primary_exp.uplift_pct > 0:
                decision = "Ship the experiment"
                confidence = "high" if not primary_exp.warnings else "medium"
                risks = primary_exp.warnings if primary_exp.warnings else ["None identified"]
                rationale = (
                    f"{primary_exp.kpi} shows significant positive uplift of {primary_exp.uplift_pct:+.2f}% "
                    f"(p={primary_exp.p_value:.4f}, 95% CI: [{primary_exp.ci_lower:.2f}%, {primary_exp.ci_upper:.2f}%])"
                )
                additional_data = []
                if primary_exp.warnings:
                    additional_data.append("Longer test duration to increase confidence")
                    additional_data.append("Segment-level analysis to check for heterogeneous effects")
            else:
                decision = "Don't ship the experiment"
                confidence = "high" if not primary_exp.warnings else "medium"
                risks = ["Opportunity cost of not shipping", "Type I error (false negative)"]
                rationale = (
                    f"{primary_exp.kpi} shows significant negative impact of {primary_exp.uplift_pct:.2f}% "
                    f"(p={primary_exp.p_value:.4f})"
                )
                additional_data = ["Root cause analysis of negative impact"]
        else:
            decision = "Continue running experiment or iterate"
            confidence = "medium"
            risks = ["Insufficient statistical power", "Type II error (false negative)"]
            rationale = f"No significant effect detected on {primary_exp.kpi} (p={primary_exp.p_value:.4f})"
            additional_data = [
                "Calculate required sample size for desired effect",
                "Consider testing a larger effect size",
                "Run for longer duration",
            ]

        decisions.append(
            RecommendedDecision(
                decision=decision,
                confidence=confidence,
                supporting_metrics=[primary_exp.kpi],
                risks=risks,
                additional_data_needed=additional_data,
                rationale=rationale,
            )
        )

    # Decision from trends
    declining_kpis = [t for t in report.overall_trends if t.direction == "decreasing" and t.recent_change_pct < -10]

    if declining_kpis:
        primary_decline = declining_kpis[0]
        decision = f"Investigate decline in {primary_decline.kpi}"
        confidence = "high"

        # Find related segments
        related_drivers = [d for d in report.segment_drivers if d.kpi == primary_decline.kpi]
        if related_drivers:
            rationale = (
                f"{primary_decline.kpi} declined {primary_decline.recent_change_pct:.1f}% recently. "
                f"Top driver: {related_drivers[0].segment_column}={related_drivers[0].segment_value}"
            )
        else:
            rationale = f"{primary_decline.kpi} declined {primary_decline.recent_change_pct:.1f}% recently across all segments"

        decisions.append(
            RecommendedDecision(
                decision=decision,
                confidence=confidence,
                supporting_metrics=[primary_decline.kpi],
                risks=["Continued decline if not addressed", "Impact on dependent metrics"],
                additional_data_needed=["Segment-level breakdown", "User feedback or qualitative data"],
                rationale=rationale,
            )
        )

    # Decision from segment drivers
    strong_drivers = [d for d in report.segment_drivers if abs(d.contribution_pct) > 40]
    if strong_drivers:
        driver = strong_drivers[0]
        if driver.contribution_pct > 0:
            decision = f"Focus optimization efforts on {driver.segment_column}={driver.segment_value}"
        else:
            decision = f"Address performance issues in {driver.segment_column}={driver.segment_value}"

        decisions.append(
            RecommendedDecision(
                decision=decision,
                confidence="high",
                supporting_metrics=[driver.kpi],
                risks=["Over-indexing on single segment", "Neglecting other segments"],
                additional_data_needed=[f"Deeper analysis of {driver.segment_column}={driver.segment_value} behavior"],
                rationale=f"This segment contributes {abs(driver.contribution_pct):.1f}% to {driver.kpi}",
            )
        )

    # Decision from data quality
    high_severity_anomalies = [a for a in report.anomalies if a.severity == "high"]
    if high_severity_anomalies:
        decision = "Investigate and fix data quality issues before making decisions"
        decisions.append(
            RecommendedDecision(
                decision=decision,
                confidence="high",
                supporting_metrics=[],
                risks=["Making decisions based on incorrect data"],
                additional_data_needed=["Data pipeline audit", "Data validation rules"],
                rationale=f"Found {len(high_severity_anomalies)} high-severity data quality issues",
            )
        )

    # Sort by confidence
    confidence_order = {"high": 0, "medium": 1, "low": 2}
    decisions.sort(key=lambda d: confidence_order[d.confidence])

    return decisions[:5]


def generate_executive_summary(report: AnalysisReport, use_llm: bool = True) -> List[str]:
    """Generate executive summary bullets.

    Args:
        report: Analysis report
        use_llm: Whether to use LLM for enhanced summary (default: True)

    Returns:
        List of summary bullets
    """
    # Try LLM-enhanced summary first
    if use_llm and LLM_ENABLED and is_llm_available():
        try:
            llm_generator = create_llm_generator()
            if llm_generator:
                llm_summary = llm_generator.generate_executive_summary(report)
                if llm_summary:
                    # Return as bullet list (split by periods or newlines)
                    return [s.strip() for s in llm_summary.split('.') if s.strip()]
        except Exception as e:
            print(f"LLM summary generation failed, falling back to rule-based: {e}")

    # Fallback to rule-based summary
    bullets = []

    # Data overview
    bullets.append(
        f"Analyzed {report.data_profile.row_count:,} rows across {report.data_profile.column_count} columns "
        f"({report.data_profile.data_mode} mode)"
    )

    # Time range
    if report.time_range:
        bullets.append(f"Time range: {report.time_range['start']} to {report.time_range['end']}")

    # Key KPIs
    primary_kpis = [k for k in report.kpis_detected if k.is_primary]
    if primary_kpis:
        bullets.append(f"Primary KPIs: {', '.join([k.column_name for k in primary_kpis[:3]])}")

    # Major findings
    if report.change_points:
        cp = report.change_points[0]
        bullets.append(
            f"Largest change: {cp.kpi} {'increased' if cp.delta_pct > 0 else 'decreased'} "
            f"{abs(cp.delta_pct):.1f}% on {cp.date}"
        )

    if report.experiment_results:
        sig_results = [e for e in report.experiment_results if e.significant]
        if sig_results:
            bullets.append(f"Found {len(sig_results)} significant experiment results")
        else:
            bullets.append("No significant experiment results detected")

    # Data quality
    high_issues = [a for a in report.anomalies if a.severity == "high"]
    if high_issues:
        bullets.append(f"⚠️  {len(high_issues)} high-severity data quality issues detected")

    return bullets[:6]
