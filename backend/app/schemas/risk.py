"""
Pydantic Schemas for Code Risk Scoring and Interpretability Explanations.
"""

from typing import List, Dict, Any, Optional
from enum import Enum
from datetime import datetime, timezone
from pydantic import BaseModel, Field


class RiskLevel(str, Enum):
    """Categorical risk tiers based on composite risk score."""
    LOW = "LOW"            # 0 - 24
    MEDIUM = "MEDIUM"      # 25 - 54
    HIGH = "HIGH"          # 55 - 79
    CRITICAL = "CRITICAL"  # 80 - 100


class RiskScoreBreakdown(BaseModel):
    """Detailed diagnostic metrics and sub-scores for the risk calculation."""
    deterministic_score: float = Field(..., description="Rule-weighted baseline score (0.0 to 100.0)")
    ml_predicted_score: float = Field(..., description="Scikit-learn regressor predicted score (0.0 to 100.0)")
    model_confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in model scoring")
    feature_metrics: Dict[str, float] = Field(..., description="Raw 16 extracted features used in calculation")
    feature_contributions: Dict[str, float] = Field(default_factory=dict, description="Estimated percentage contribution of key features")
    total_findings_count: int = Field(default=0, description="Total static analysis findings count")
    secrets_detected_count: int = Field(default=0, description="Total exposed secrets count")
    cyclomatic_complexity: float = Field(default=1.0, description="AST McCabe cyclomatic complexity")
    max_nesting_depth: float = Field(default=0.0, description="Deepest block nesting level")


class RiskScoreRequest(BaseModel):
    """Payload schema for computing code risk score."""
    language: Optional[str] = Field("python", description="Programming language")
    filename: Optional[str] = Field("snippet.py", description="Logical filename")
    content: str = Field(..., min_length=1, description="Source code text to evaluate for risk")
    findings: Optional[List[Dict[str, Any]]] = Field(None, description="Optional pre-calculated static analysis findings")
    secrets_count: Optional[int] = Field(None, description="Optional pre-calculated secrets count")


class RiskScoreResponse(BaseModel):
    """Interpretable risk scoring result."""
    risk_score: int = Field(..., ge=0, le=100, description="Overall composite risk score (0 to 100)")
    risk_level: RiskLevel = Field(..., description="Risk tier: LOW, MEDIUM, HIGH, CRITICAL")
    reasons: List[str] = Field(..., description="Human-readable explanations for why the score was assigned")
    breakdown: RiskScoreBreakdown = Field(..., description="Detailed sub-score breakdown and feature telemetry")
    filename: str = Field(default="snippet.py", description="Analyzed file basename")
    calculated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat(), description="UTC ISO-8601 timestamp")
    model_metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Machine learning pipeline diagnostics, evaluation metrics, and feature dimensions"
    )
    disclaimer: str = Field(
        default="Risk score is generated using a combination of deterministic heuristics and a Scikit-learn model trained on synthetic code risk profiles.",
        description="Scientific methodology note"
    )
