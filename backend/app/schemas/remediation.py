"""
Pydantic Schemas for AI Developer Explanation and Remediation Engine.

Enforces strict tripartite epistemic segregation:
1. DETECTED FACT: Local static analysis truth (AST/Bandit)
2. AI INTERPRETATION: Developer explanation, impact, and uncertainty statement
3. RECOMMENDATION: Step-by-step remediation and validated safer code example
"""

from typing import List, Dict, Any, Optional
from enum import Enum
from datetime import datetime, timezone
from pydantic import BaseModel, Field

from app.schemas.analysis import NormalizedFinding, FindingSeverity
from app.schemas.risk import RiskLevel


class EpistemicCategory(str, Enum):
    """Epistemic classification of information presented to the developer."""
    DETECTED_FACT = "DETECTED_FACT"
    AI_INTERPRETATION = "AI_INTERPRETATION"
    RECOMMENDATION = "RECOMMENDATION"


class DetectedFact(BaseModel):
    """
    Epistemic Tier 1: Ground-truth findings verified by local AST/Bandit static analysis.
    The AI layer NEVER invents or alters these properties.
    """
    epistemic_tier: str = Field(default=EpistemicCategory.DETECTED_FACT.value, description="Tier identifier")
    analyzer: str = Field(..., description="Authoritative static analyzer (e.g. ast_visitor, bandit)")
    issue_id: str = Field(..., description="Standardized finding ID")
    title: str = Field(..., description="Issue title")
    category: str = Field(..., description="Vulnerability category")
    severity: str = Field(..., description="Severity level: CRITICAL, HIGH, MEDIUM, LOW")
    line_number: int = Field(..., description="Exact 1-indexed source code line number")
    code_snippet: str = Field(..., description="Sanitized snippet directly flagged by analyzer")
    detection_confidence: float = Field(..., ge=0.0, le=1.0, description="Static analyzer confidence score")


class AIInterpretation(BaseModel):
    """
    Epistemic Tier 2: Model synthesis of why the issue exists and its potential runtime impact.
    Explicitly includes confidence and uncertainty boundaries.
    """
    epistemic_tier: str = Field(default=EpistemicCategory.AI_INTERPRETATION.value, description="Tier identifier")
    developer_explanation: str = Field(..., description="Plain-English explanation of the finding")
    why_it_matters: str = Field(..., description="Rationale detailing why this code pattern is problematic")
    potential_impact: str = Field(..., description="Potential security, stability, or data consequences if exploited")
    confidence_statement: str = Field(..., description="Explicit statement of certainty vs. uncertainty")
    is_insufficient_evidence: bool = Field(default=False, description="True if evidence was insufficient for confident explanation")


class RemediationRecommendation(BaseModel):
    """
    Epistemic Tier 3: Actionable engineering advice and safer code replacement.
    Purely for developer guidance—never automatically executed.
    """
    epistemic_tier: str = Field(default=EpistemicCategory.RECOMMENDATION.value, description="Tier identifier")
    recommended_remediation: str = Field(..., description="Clear, step-by-step guidance on fixing the issue")
    safer_code_example: Optional[str] = Field(None, description="Concrete safe replacement code snippet")
    remediation_steps: List[str] = Field(default_factory=list, description="Ordered bullet points for remediation")


class DeveloperRemediation(BaseModel):
    """Composite tripartite explanation structure for a single static analysis finding."""
    finding_id: str = Field(..., description="Associated issue identifier")
    fact: DetectedFact = Field(..., description="Verified static analysis fact")
    interpretation: AIInterpretation = Field(..., description="AI contextual interpretation")
    recommendation: RemediationRecommendation = Field(..., description="Actionable remediation advice")
    model_used: str = Field(default="privacy-guard-llm-v1", description="Model used for interpretation")


class RemediationRequest(BaseModel):
    """Request schema for generating developer explanations."""
    content: str = Field(..., min_length=1, description="Source code text")
    filename: Optional[str] = Field("snippet.py", description="Logical filename")
    language: Optional[str] = Field("python", description="Programming language")
    max_explanations: Optional[int] = Field(3, ge=1, le=10, description="Max top findings to generate explanations for")
    provider_override: Optional[str] = Field(None, description="Optional provider override: 'local', 'external', 'mock'")


class RemediationResponse(BaseModel):
    """Composite response containing full tripartite explanations, static findings, and risk metrics."""
    analysis_id: str = Field(..., description="Unique analysis ID")
    filename: str = Field(..., description="Analyzed filename")
    language: str = Field(..., description="Resolved programming language")
    risk_score: int = Field(..., ge=0, le=100, description="Overall risk score (0-100)")
    risk_level: RiskLevel = Field(..., description="Categorical risk tier")
    total_findings_count: int = Field(..., description="Total static findings detected")
    secrets_detected_count: int = Field(default=0, description="Number of redacted secrets")
    remediations: List[DeveloperRemediation] = Field(default_factory=list, description="Tripartite explanations for findings")
    summary_message: str = Field(..., description="High-level diagnostic summary")
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat(), description="UTC timestamp")
    epistemic_notice: str = Field(
        default="Epistemic Tripartite Guarantee: DETECTED FACT represents deterministic AST/SAST discoveries. AI INTERPRETATION represents probabilistic model reasoning. RECOMMENDATION represents non-executable engineering advice.",
        description="Epistemic integrity disclaimer"
    )
