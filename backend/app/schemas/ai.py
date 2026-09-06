"""
Pydantic Schemas for Privacy-Aware AI Analysis, Context Minimization, and Audit Logging.
"""

from typing import List, Dict, Any, Optional
from enum import Enum
from datetime import datetime, timezone
from pydantic import BaseModel, Field

from app.schemas.analysis import NormalizedFinding
from app.schemas.risk import RiskLevel


class AIStatus(str, Enum):
    """Execution status of the Privacy-Aware AI Analysis Layer."""
    SUCCESS = "SUCCESS"
    AI_DISABLED = "AI_DISABLED"
    DEGRADED_TIMEOUT = "DEGRADED_TIMEOUT"
    DEGRADED_RATE_LIMITED = "DEGRADED_RATE_LIMITED"
    DEGRADED_ERROR = "DEGRADED_ERROR"
    SKIPPED_CLEAN = "SKIPPED_CLEAN"


class MinimizedContext(BaseModel):
    """Sanitized, minimized code context window surrounding a single finding."""
    finding_id: str = Field(..., description="Unique issue identifier")
    issue_title: str = Field(..., description="Normalized issue title")
    severity: str = Field(..., description="Finding severity level")
    line_number: int = Field(..., description="Target line number of finding")
    start_line: int = Field(..., description="Start line of minimized bounding window")
    end_line: int = Field(..., description="End line of minimized bounding window")
    context_snippet: str = Field(..., description="Sanitized ±4 line window with secrets redacted")
    char_count: int = Field(..., description="Character count of minimized snippet")
    has_redactions: bool = Field(default=False, description="True if placeholder redactions exist in snippet")


class AIFindingExplanation(BaseModel):
    """Structured AI explanation and secure remediation advice for a single finding."""
    finding_id: str = Field(..., description="Target issue ID")
    issue_title: str = Field(..., description="Target issue title")
    severity: str = Field(..., description="Target severity")
    line_number: int = Field(..., description="Target line number")
    root_cause_explanation: str = Field(..., description="Explanation of why this pattern is dangerous")
    remediation_advice: str = Field(..., description="Clear instructions to fix the issue securely")
    secure_code_example: Optional[str] = Field(None, description="Recommended secure replacement code snippet")
    provider_used: str = Field(..., description="LLM provider name (e.g. MockLLMProvider, ExternalLLMProvider)")
    model_name: str = Field(..., description="Model identifier used for analysis")
    minimized_context: MinimizedContext = Field(..., description="The minimal sanitized context provided to LLM")


class AIAuditEvent(BaseModel):
    """
    Privacy Audit Event metadata.
    INVIOLABLE CONSTRAINT: Contains ZERO source code, ZERO prompts, and ZERO secrets.
    """
    event_id: str = Field(..., description="Unique UUID for this audit entry")
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat(), description="UTC timestamp")
    provider: str = Field(..., description="LLM provider identifier")
    model: str = Field(..., description="Model identifier")
    status: AIStatus = Field(..., description="Execution outcome")
    findings_count: int = Field(..., description="Number of findings processed")
    payload_chars: int = Field(..., description="Approximate character count of minimized context")
    latency_ms: float = Field(..., description="AI provider execution latency in milliseconds")
    details: Optional[str] = Field(None, description="Diagnostic reason or degradation note")


class AIAnalysisRequest(BaseModel):
    """Payload for requesting privacy-preserving AI analysis."""
    content: str = Field(..., min_length=1, description="Source code text to analyze")
    filename: Optional[str] = Field("snippet.py", description="Logical file basename")
    language: Optional[str] = Field("python", description="Programming language")
    ai_enabled: Optional[bool] = Field(None, description="Optional override to enable/disable AI analysis")
    provider_override: Optional[str] = Field(None, description="Optional override for AI provider: 'local', 'external', 'mock'")


class AIAnalysisResponse(BaseModel):
    """Composite response uniting static analysis, risk scoring, and privacy-minimized AI explanations."""
    analysis_id: str = Field(..., description="Unique analysis execution ID")
    filename: str = Field(..., description="Logical filename")
    language: str = Field(..., description="Detected programming language")
    ai_status: AIStatus = Field(..., description="AI operational status")
    secrets_detected_count: int = Field(default=0, description="Number of secrets redacted prior to analysis")
    total_findings_count: int = Field(default=0, description="Total static findings identified")
    risk_score: int = Field(..., ge=0, le=100, description="Composite risk score (0-100)")
    risk_level: RiskLevel = Field(..., description="Categorical risk tier")
    findings: List[NormalizedFinding] = Field(default_factory=list, description="All local static findings")
    minimized_contexts: List[MinimizedContext] = Field(default_factory=list, description="Sanitized context payloads")
    ai_explanations: List[AIFindingExplanation] = Field(default_factory=list, description="AI explanations for top findings")
    audit_event: Optional[AIAuditEvent] = Field(None, description="Privacy audit event (metadata only)")
    privacy_guarantee: str = Field(
        default="Inviolable Privacy Guarantee: Secrets were redacted before static analysis. Only minimized snippet windows (±4 lines) were exposed to the AI layer. Zero source code is retained in audit logs.",
        description="Privacy enforcement statement"
    )
