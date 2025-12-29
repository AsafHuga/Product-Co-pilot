"""Command-line interface for Product Metrics Copilot."""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional
import pandas as pd

from metrics_copilot.ingest import ingest_csv
from metrics_copilot.profiling import profile_data, detect_kpis, detect_segment_columns, detect_experiment_column
from metrics_copilot.analysis_trends import analyze_trends, detect_change_points, find_largest_deltas
from metrics_copilot.analysis_experiments import analyze_experiment, detect_peeking_risk
from metrics_copilot.decomposition import analyze_segment_drivers, find_anomalous_segments
from metrics_copilot.insights import (
    generate_hypotheses,
    generate_next_checks,
    generate_decisions,
    generate_executive_summary,
)
from metrics_copilot.schemas import AnalysisReport, Anomaly


def analyze_csv(
    file_path: str,
    output_json: Optional[str] = None,
    output_markdown: Optional[str] = None,
    use_llm: bool = True
) -> AnalysisReport:
    """Main analysis pipeline.

    Args:
        file_path: Path to CSV file
        output_json: Path to save JSON report
        output_markdown: Path to save markdown report
        use_llm: Whether to use LLM for enhanced insights

    Returns:
        Analysis report
    """
    print("=" * 80)
    print("PRODUCT METRICS COPILOT")
    print("=" * 80)
    print(f"\nAnalyzing: {file_path}\n")

    # Step 1: Ingest data
    print("📊 Step 1/7: Ingesting and cleaning data...")
    df, metadata = ingest_csv(file_path)
    date_col = metadata.get("date_column")
    print(f"  ✓ Loaded {len(df):,} rows, {len(df.columns)} columns")
    if date_col:
        print(f"  ✓ Date column: {date_col}")

    # Step 2: Profile data
    print("\n🔍 Step 2/7: Profiling data...")
    profile = profile_data(df, date_col, metadata)
    print(f"  ✓ Data mode: {profile.data_mode}")
    print(f"  ✓ Quality issues: {len(profile.quality_issues)}")

    # Step 3: Detect KPIs
    print("\n📈 Step 3/7: Detecting KPIs...")
    kpis = detect_kpis(df, profile.columns)
    kpi_columns = [k.column_name for k in kpis]
    print(f"  ✓ Detected {len(kpis)} KPI columns")
    primary_kpis = [k.column_name for k in kpis if k.is_primary]
    if primary_kpis:
        print(f"  ✓ Primary KPIs: {', '.join(primary_kpis)}")

    # Step 4: Analyze trends (if time series)
    trends = []
    change_points = []
    if date_col and profile.data_mode in ["timeseries", "both"]:
        print("\n📉 Step 4/7: Analyzing trends...")
        trends = analyze_trends(df, date_col, kpi_columns)
        print(f"  ✓ Analyzed trends for {len(trends)} KPIs")

        change_points = detect_change_points(df, date_col, kpi_columns)
        print(f"  ✓ Detected {len(change_points)} change points")
    else:
        print("\n⏭️  Step 4/7: Skipping trend analysis (no time series)")

    # Step 5: Analyze experiments (if experiment mode)
    experiment_results = []
    experiment_col = detect_experiment_column(df)
    if experiment_col:
        print(f"\n🧪 Step 5/7: Analyzing experiment (column: {experiment_col})...")
        experiment_results = analyze_experiment(df, experiment_col, kpi_columns)
        print(f"  ✓ Analyzed {len(experiment_results)} KPIs")
        significant = [e for e in experiment_results if e.significant]
        print(f"  ✓ Significant results: {len(significant)}")

        # Check for peeking
        if date_col:
            peeking_warnings = detect_peeking_risk(df, date_col, experiment_col)
            for warning in peeking_warnings:
                print(f"  ⚠️  {warning}")
    else:
        print("\n⏭️  Step 5/7: Skipping experiment analysis (no experiment detected)")

    # Step 6: Segment analysis
    print("\n🎯 Step 6/7: Analyzing segments...")
    segment_cols = detect_segment_columns(df, profile.columns)
    segment_drivers = []
    if segment_cols:
        print(f"  ✓ Detected {len(segment_cols)} segment columns: {', '.join(segment_cols)}")
        segment_drivers = analyze_segment_drivers(df, segment_cols, kpi_columns, date_col)
        print(f"  ✓ Identified {len(segment_drivers)} segment drivers")
    else:
        print("  ⚠️  No segment columns detected")

    # Step 7: Generate insights
    print("\n💡 Step 7/7: Generating insights...")

    # Convert quality issues and anomalous segments to Anomaly objects
    anomalies = []
    for issue in profile.quality_issues:
        anomalies.append(
            Anomaly(
                type=issue.get("type", "data_quality"),
                severity=issue.get("severity", "medium"),
                description=issue.get("description", ""),
                affected_column=issue.get("column"),
            )
        )

    # Create report object
    report = AnalysisReport(
        data_profile=profile,
        kpis_detected=kpis,
        time_range=profile.time_range,
        overall_trends=trends,
        change_points=change_points,
        experiment_results=experiment_results,
        segment_drivers=segment_drivers,
        anomalies=anomalies,
        hypotheses=[],
        next_checks=[],
        recommended_decisions=[],
    )

    # Generate insights
    if use_llm:
        print("  🤖 Using LLM-enhanced insights...")
    report.hypotheses = generate_hypotheses(report, df, use_llm=use_llm)
    report.next_checks = generate_next_checks(report)
    report.recommended_decisions = generate_decisions(report)

    print(f"  ✓ Generated {len(report.hypotheses)} hypotheses")
    print(f"  ✓ Generated {len(report.next_checks)} follow-up checks")
    print(f"  ✓ Generated {len(report.recommended_decisions)} decisions")

    # Generate executive summary
    exec_summary = generate_executive_summary(report, use_llm=use_llm)

    # Print summary to console
    print_summary(report, exec_summary)

    # Save outputs
    if output_json:
        save_json_report(report, output_json)
        print(f"\n💾 Saved JSON report to: {output_json}")

    if output_markdown:
        save_markdown_report(report, exec_summary, output_markdown)
        print(f"💾 Saved Markdown report to: {output_markdown}")

    return report


def print_summary(report: AnalysisReport, exec_summary: list[str]):
    """Print human-friendly summary to console.

    Args:
        report: Analysis report
        exec_summary: Executive summary bullets
    """
    print("\n" + "=" * 80)
    print("EXECUTIVE SUMMARY")
    print("=" * 80)
    for bullet in exec_summary:
        print(f"• {bullet}")

    print("\n" + "=" * 80)
    print("WHAT HAPPENED")
    print("=" * 80)

    # Trends
    if report.overall_trends:
        print("\n📊 Overall Trends:")
        for trend in report.overall_trends[:5]:
            direction_emoji = {"increasing": "📈", "decreasing": "📉", "stable": "➡️", "volatile": "📊"}
            emoji = direction_emoji.get(trend.direction, "")
            print(f"  {emoji} {trend.description}")

    # Change points
    if report.change_points:
        print("\n🔔 Major Change Points:")
        for cp in report.change_points[:5]:
            direction = "↑" if cp.delta_pct > 0 else "↓"
            print(f"  {direction} {cp.date}: {cp.kpi} changed {cp.delta_pct:+.1f}% (confidence: {cp.confidence})")

    # Experiments
    if report.experiment_results:
        print("\n🧪 Experiment Results:")
        for exp in report.experiment_results[:5]:
            sig = "✓" if exp.significant else "✗"
            print(
                f"  {sig} {exp.kpi}: {exp.uplift_pct:+.2f}% uplift "
                f"(p={exp.p_value:.4f}, CI=[{exp.ci_lower:.2f}%, {exp.ci_upper:.2f}%])"
            )
            if exp.warnings:
                for warning in exp.warnings:
                    print(f"     ⚠️  {warning}")

    print("\n" + "=" * 80)
    print("KEY DRIVERS & SEGMENTS")
    print("=" * 80)

    if report.segment_drivers:
        print("\n🎯 Top Segment Drivers:")
        for driver in report.segment_drivers[:10]:
            direction = "+" if driver.contribution_pct > 0 else ""
            print(
                f"  • {driver.segment_column}={driver.segment_value}: "
                f"{direction}{driver.contribution_pct:.1f}% contribution to {driver.kpi}"
            )

    print("\n" + "=" * 80)
    print("ANOMALIES & WARNINGS")
    print("=" * 80)

    if report.anomalies:
        for anomaly in report.anomalies:
            emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}
            print(f"  {emoji.get(anomaly.severity, '')} {anomaly.description}")
    else:
        print("  ✓ No major anomalies detected")

    print("\n" + "=" * 80)
    print("HYPOTHESES (What might have caused this?)")
    print("=" * 80)

    for i, hyp in enumerate(report.hypotheses[:5], 1):
        conf_emoji = {"high": "🟢", "medium": "🟡", "low": "🔴"}
        print(f"\n{i}. {hyp.description}")
        print(f"   Confidence: {conf_emoji.get(hyp.confidence, '')} {hyp.confidence.upper()}")
        print(f"   Evidence:")
        for ev in hyp.supporting_evidence[:3]:
            print(f"     - {ev}")

    print("\n" + "=" * 80)
    print("RECOMMENDED NEXT STEPS")
    print("=" * 80)

    if report.next_checks:
        print("\n🔍 Investigations to Run:")
        for i, check in enumerate(report.next_checks[:5], 1):
            priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}
            print(f"\n{i}. {check.question}")
            print(f"   Priority: {priority_emoji.get(check.priority, '')} {check.priority.upper()}")
            print(f"   Why: {check.why}")
            print(f"   SQL: {check.sql_like_query}")

    print("\n" + "=" * 80)
    print("RECOMMENDED DECISIONS")
    print("=" * 80)

    for i, decision in enumerate(report.recommended_decisions, 1):
        conf_emoji = {"high": "🟢", "medium": "🟡", "low": "🔴"}
        print(f"\n{i}. {decision.decision}")
        print(f"   Confidence: {conf_emoji.get(decision.confidence, '')} {decision.confidence.upper()}")
        print(f"   Rationale: {decision.rationale}")
        if decision.risks:
            print(f"   Risks: {', '.join(decision.risks[:2])}")
        if decision.additional_data_needed:
            print(f"   Additional data needed: {', '.join(decision.additional_data_needed[:2])}")

    print("\n" + "=" * 80)


def save_json_report(report: AnalysisReport, output_path: str):
    """Save report as JSON.

    Args:
        report: Analysis report
        output_path: Output file path
    """
    with open(output_path, 'w') as f:
        json.dump(report.to_dict(), f, indent=2, default=str)


def save_markdown_report(report: AnalysisReport, exec_summary: list[str], output_path: str):
    """Save report as Markdown.

    Args:
        report: Analysis report
        exec_summary: Executive summary bullets
        output_path: Output file path
    """
    lines = [
        "# Product Metrics Analysis Report",
        "",
        "## Executive Summary",
        "",
    ]

    for bullet in exec_summary:
        lines.append(f"- {bullet}")

    lines.extend(["", "## What Happened", ""])

    if report.overall_trends:
        lines.append("### Overall Trends")
        for trend in report.overall_trends[:5]:
            lines.append(f"- {trend.description}")
        lines.append("")

    if report.change_points:
        lines.append("### Major Change Points")
        for cp in report.change_points[:5]:
            lines.append(f"- **{cp.date}**: {cp.kpi} changed {cp.delta_pct:+.1f}% (confidence: {cp.confidence})")
        lines.append("")

    if report.experiment_results:
        lines.append("### Experiment Results")
        for exp in report.experiment_results[:5]:
            sig = "Significant" if exp.significant else "Not significant"
            lines.append(
                f"- **{exp.kpi}**: {exp.uplift_pct:+.2f}% uplift ({sig}, p={exp.p_value:.4f}, "
                f"CI=[{exp.ci_lower:.2f}%, {exp.ci_upper:.2f}%])"
            )
        lines.append("")

    lines.extend(["## Key Drivers", ""])

    if report.segment_drivers:
        for driver in report.segment_drivers[:10]:
            lines.append(
                f"- **{driver.segment_column}={driver.segment_value}**: "
                f"{driver.contribution_pct:+.1f}% contribution to {driver.kpi}"
            )
        lines.append("")

    lines.extend(["## Hypotheses", ""])

    for i, hyp in enumerate(report.hypotheses[:5], 1):
        lines.append(f"### {i}. {hyp.description}")
        lines.append(f"**Confidence**: {hyp.confidence.upper()}")
        lines.append("")
        lines.append("**Evidence**:")
        for ev in hyp.supporting_evidence[:3]:
            lines.append(f"- {ev}")
        lines.append("")

    lines.extend(["## Recommended Decisions", ""])

    for i, decision in enumerate(report.recommended_decisions, 1):
        lines.append(f"### {i}. {decision.decision}")
        lines.append(f"**Confidence**: {decision.confidence.upper()}")
        lines.append(f"**Rationale**: {decision.rationale}")
        if decision.risks:
            lines.append(f"**Risks**: {', '.join(decision.risks)}")
        if decision.additional_data_needed:
            lines.append(f"**Additional data needed**: {', '.join(decision.additional_data_needed)}")
        lines.append("")

    with open(output_path, 'w') as f:
        f.write('\n'.join(lines))


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Product Metrics Copilot - Automated product analytics and insights",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument("csv_file", help="Path to CSV file to analyze")
    parser.add_argument(
        "--out", "-o", dest="output_json", help="Path to save JSON report (optional)", default=None
    )
    parser.add_argument(
        "--markdown", "-m", dest="output_markdown", help="Path to save Markdown report (optional)", default=None
    )
    parser.add_argument(
        "--use-llm", dest="use_llm", action="store_true",
        help="Use OpenAI LLM for enhanced insights (requires OPENAI_API_KEY env var)"
    )
    parser.add_argument(
        "--no-llm", dest="use_llm", action="store_false",
        help="Disable LLM and use rule-based insights only"
    )
    parser.set_defaults(use_llm=True)  # Default to True if available

    args = parser.parse_args()

    # Validate input file
    if not Path(args.csv_file).exists():
        print(f"Error: File not found: {args.csv_file}", file=sys.stderr)
        sys.exit(1)

    try:
        analyze_csv(args.csv_file, args.output_json, args.output_markdown, use_llm=args.use_llm)
    except Exception as e:
        print(f"\n❌ Error during analysis: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
