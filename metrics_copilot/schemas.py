"""Data schemas and type definitions for the metrics copilot."""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Literal
from datetime import datetime


@dataclass
class DataProfile:
    """Profile of the ingested dataset."""
    row_count: int
    column_count: int
    duplicate_count: int
    date_column: Optional[str]
    time_range: Optional[Dict[str, str]]
    columns: Dict[str, Dict[str, Any]]
    quality_issues: List[Dict[str, Any]]
    data_mode: Literal["timeseries", "experiment", "both", "static"]


@dataclass
class KPIDetection:
    """Detected KPI metadata."""
    column_name: str
    kpi_type: Literal["rate", "count", "money", "duration", "ratio"]
    numerator: Optional[str] = None
    denominator: Optional[str] = None
    unit: Optional[str] = None
    is_primary: bool = False


@dataclass
class ChangePoint:
    """Detected change point in time series."""
    date: str
    kpi: str
    before_mean: float
    after_mean: float
    delta_abs: float
    delta_pct: float
    confidence: Literal["high", "medium", "low"]


@dataclass
class ExperimentResult:
    """Results of A/B test analysis."""
    kpi: str
    control_mean: float
    test_mean: float
    control_std: float
    test_std: float
    control_count: int
    test_count: int
    uplift_abs: float
    uplift_pct: float
    ci_lower: float
    ci_upper: float
    p_value: float
    significant: bool
    warnings: List[str]


@dataclass
class SegmentDriver:
    """Segment contribution to overall change."""
    segment_column: str
    segment_value: str
    kpi: str
    contribution_abs: float
    contribution_pct: float
    segment_mean: float
    segment_size: int


@dataclass
class Anomaly:
    """Detected anomaly or data quality issue."""
    type: Literal["data_quality", "outlier", "suspicious_change", "schema_shift"]
    severity: Literal["high", "medium", "low"]
    description: str
    affected_rows: Optional[int] = None
    affected_column: Optional[str] = None
    evidence: Optional[Dict[str, Any]] = None


@dataclass
class Hypothesis:
    """Generated hypothesis about what happened."""
    description: str
    confidence: Literal["high", "medium", "low"]
    supporting_evidence: List[str]
    related_kpis: List[str]
    related_segments: List[str] = field(default_factory=list)


@dataclass
class NextCheck:
    """Recommended follow-up investigation."""
    question: str
    sql_like_query: str
    priority: Literal["high", "medium", "low"]
    why: str


@dataclass
class RecommendedDecision:
    """Recommended decision based on analysis."""
    decision: str
    confidence: Literal["high", "medium", "low"]
    supporting_metrics: List[str]
    risks: List[str]
    additional_data_needed: List[str]
    rationale: str


@dataclass
class TrendSummary:
    """Summary of trend for a KPI."""
    kpi: str
    direction: Literal["increasing", "decreasing", "stable", "volatile"]
    overall_change_pct: float
    recent_change_pct: float  # Last 7 days or last period
    description: str


@dataclass
class AnalysisReport:
    """Complete analysis report."""
    data_profile: DataProfile
    kpis_detected: List[KPIDetection]
    time_range: Optional[Dict[str, str]]
    overall_trends: List[TrendSummary]
    change_points: List[ChangePoint]
    experiment_results: List[ExperimentResult]
    segment_drivers: List[SegmentDriver]
    anomalies: List[Anomaly]
    hypotheses: List[Hypothesis]
    next_checks: List[NextCheck]
    recommended_decisions: List[RecommendedDecision]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "data_profile": {
                "row_count": self.data_profile.row_count,
                "column_count": self.data_profile.column_count,
                "duplicate_count": self.data_profile.duplicate_count,
                "date_column": self.data_profile.date_column,
                "time_range": self.data_profile.time_range,
                "columns": self.data_profile.columns,
                "quality_issues": self.data_profile.quality_issues,
                "data_mode": self.data_profile.data_mode,
            },
            "kpis_detected": [
                {
                    "column_name": k.column_name,
                    "kpi_type": k.kpi_type,
                    "numerator": k.numerator,
                    "denominator": k.denominator,
                    "unit": k.unit,
                    "is_primary": k.is_primary,
                }
                for k in self.kpis_detected
            ],
            "time_range": self.time_range,
            "overall_trends": [
                {
                    "kpi": t.kpi,
                    "direction": t.direction,
                    "overall_change_pct": t.overall_change_pct,
                    "recent_change_pct": t.recent_change_pct,
                    "description": t.description,
                }
                for t in self.overall_trends
            ],
            "change_points": [
                {
                    "date": cp.date,
                    "kpi": cp.kpi,
                    "before_mean": cp.before_mean,
                    "after_mean": cp.after_mean,
                    "delta_abs": cp.delta_abs,
                    "delta_pct": cp.delta_pct,
                    "confidence": cp.confidence,
                }
                for cp in self.change_points
            ],
            "experiment_results": [
                {
                    "kpi": e.kpi,
                    "control_mean": e.control_mean,
                    "test_mean": e.test_mean,
                    "control_std": e.control_std,
                    "test_std": e.test_std,
                    "control_count": e.control_count,
                    "test_count": e.test_count,
                    "uplift_abs": e.uplift_abs,
                    "uplift_pct": e.uplift_pct,
                    "ci_lower": e.ci_lower,
                    "ci_upper": e.ci_upper,
                    "p_value": e.p_value,
                    "significant": e.significant,
                    "warnings": e.warnings,
                }
                for e in self.experiment_results
            ],
            "segment_drivers": [
                {
                    "segment_column": s.segment_column,
                    "segment_value": s.segment_value,
                    "kpi": s.kpi,
                    "contribution_abs": s.contribution_abs,
                    "contribution_pct": s.contribution_pct,
                    "segment_mean": s.segment_mean,
                    "segment_size": s.segment_size,
                }
                for s in self.segment_drivers
            ],
            "anomalies": [
                {
                    "type": a.type,
                    "severity": a.severity,
                    "description": a.description,
                    "affected_rows": a.affected_rows,
                    "affected_column": a.affected_column,
                    "evidence": a.evidence,
                }
                for a in self.anomalies
            ],
            "hypotheses": [
                {
                    "description": h.description,
                    "confidence": h.confidence,
                    "supporting_evidence": h.supporting_evidence,
                    "related_kpis": h.related_kpis,
                    "related_segments": h.related_segments,
                }
                for h in self.hypotheses
            ],
            "next_checks": [
                {
                    "question": n.question,
                    "sql_like_query": n.sql_like_query,
                    "priority": n.priority,
                    "why": n.why,
                }
                for n in self.next_checks
            ],
            "recommended_decisions": [
                {
                    "decision": d.decision,
                    "confidence": d.confidence,
                    "supporting_metrics": d.supporting_metrics,
                    "risks": d.risks,
                    "additional_data_needed": d.additional_data_needed,
                    "rationale": d.rationale,
                }
                for d in self.recommended_decisions
            ],
        }
