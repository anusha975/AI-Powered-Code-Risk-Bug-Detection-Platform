"""
Pydantic Schemas for Module 11: Professional Engineering Security Dashboard.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

from app.schemas.analysis import FindingSeverity, NormalizedFinding
from app.schemas.security import SecretFinding
from app.schemas.remediation import DeveloperRemediation
from app.schemas.rag import RetrievedSource


class AggregatedFinding(BaseModel):
    """Standardized finding representation for the global Findings Catalog."""
    finding_id: str = Field(..., description="Unique finding UUID")
    analysis_id: str = Field(..., description="Originating analysis session UUID")
    file: str = Field(..., description="Target file path")
    line_number: Optional[int] = Field(None, description="Line number")
    issue_id: str = Field(..., description="Issue identifier code")
    title: str = Field(..., description="Finding title")
    category: str = Field(..., description="Category (SECURITY, SECRETS, QUALITY, COMPLEXITY)")
    severity: str = Field(..., description="Severity level: CRITICAL, HIGH, MEDIUM, LOW")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    code_snippet: str = Field(..., description="Sanitized relevant snippet")
    recommendation: str = Field(..., description="Guidance to resolve issue")
    analyzer: str = Field(..., description="Originating engine (ast_analyzer, bandit, secret_entropy_scanner)")
    timestamp: str = Field(..., description="Timestamp of detection")


class AnalysisSummaryRecord(BaseModel):
    """Brief summary of an analysis session for history tables and recent activity feeds."""
    analysis_id: str = Field(..., description="Unique UUID for this analysis session")
    analysis_type: str = Field(..., description="Type of scan: CODE_SNIPPET, FILE_UPLOAD, GITHUB_PR")
    target_name: str = Field(..., description="File name or GitHub repository PR target")
    timestamp: str = Field(..., description="ISO UTC timestamp of analysis")
    user_id: Optional[str] = Field(None, description="User identifier triggering scan")
    username: Optional[str] = Field(None, description="Username associated with scan")
    risk_score: float = Field(..., ge=0.0, le=100.0, description="Calculated composite risk score")
    risk_level: str = Field(..., description="Risk tier: LOW, MEDIUM, HIGH, CRITICAL")
    findings_count: int = Field(..., ge=0, description="Total static & security findings")
    secrets_count: int = Field(..., ge=0, description="Total credentials redacted")
    ai_mode: str = Field(..., description="AI operational mode: DISABLED, EXTERNAL, LOCAL")
    status: str = Field(default="COMPLETED", description="Execution status: COMPLETED, FAILED, RUNNING")
    scan_latency_ms: float = Field(..., description="Execution time in ms")


class AnalysisDetailRecord(BaseModel):
    """Complete deep-dive inspection record for a specific analysis session."""
    analysis_id: str = Field(..., description="Unique UUID")
    analysis_type: str = Field(..., description="Type of scan: CODE_SNIPPET, FILE_UPLOAD, GITHUB_PR")
    target_name: str = Field(..., description="Target file or PR coordinate")
    timestamp: str = Field(..., description="ISO UTC timestamp")
    user_id: Optional[str] = Field(None, description="User identifier triggering scan")
    username: Optional[str] = Field(None, description="Username associated with scan")
    language: Optional[str] = Field(None, description="Source programming language")
    
    # Risk & Telemetry
    risk_score: float = Field(..., ge=0.0, le=100.0, description="Overall risk score")
    risk_level: str = Field(..., description="Risk tier")
    risk_reasons: List[str] = Field(default_factory=list, description="Risk attribution reasons")
    scan_latency_ms: float = Field(..., description="Scan duration in ms")
    ai_mode: str = Field(..., description="AI mode during analysis")
    
    # Sanitized Code / Diff
    sanitized_content: Optional[str] = Field(None, description="Sanitized source code or diff patch")
    
    # Findings & Redacted Secrets
    findings: List[AggregatedFinding] = Field(default_factory=list, description="All detected findings")
    secrets: List[SecretFinding] = Field(default_factory=list, description="Redacted secret metadata (no raw values)")
    
    # AI Remediations & Grounded Knowledge
    remediations: List[DeveloperRemediation] = Field(default_factory=list, description="Tripartite developer remediations")
    supporting_documents: List[RetrievedSource] = Field(default_factory=list, description="Curated RAG standards cited")
    
    # Compliance & Notice
    privacy_guarantee: str = Field(
        default="Zero-Execution & Context-Minimization Invariant: Secrets were redacted before any AI processing. Code was analyzed locally.",
        description="Privacy enforcement statement"
    )


class DashboardOverviewMetrics(BaseModel):
    """Aggregated live telemetry metrics for the Executive Overview Dashboard."""
    total_analyses_performed: int = Field(..., ge=0, description="Total number of code and PR analyses completed")
    high_risk_analyses_count: int = Field(..., ge=0, description="Count of analyses with Risk Level HIGH or CRITICAL")
    critical_findings_count: int = Field(..., ge=0, description="Total critical severity vulnerabilities detected")
    security_findings_count: int = Field(..., ge=0, description="Total security category issues detected")
    secrets_redacted_count: int = Field(..., ge=0, description="Total exposed credentials intercepted and masked")
    average_risk_score: float = Field(..., ge=0.0, le=100.0, description="Mean risk score across all sessions")
    
    # Active System State
    active_ai_mode: str = Field(..., description="Active AI provider mode: Disabled, External LLM, Private/Local LLM")
    privacy_assurance: str = Field(
        default="Secrets detected and redacted before AI analysis.",
        description="Core privacy guarantee message"
    )
    
    # Severity & Category Breakdowns
    severity_distribution: Dict[str, int] = Field(
        default_factory=lambda: {"critical": 0, "high": 0, "medium": 0, "low": 0},
        description="Counts per severity tier"
    )
    category_distribution: Dict[str, int] = Field(
        default_factory=lambda: {"SECURITY": 0, "SECRETS": 0, "CODE_QUALITY": 0, "COMPLEXITY": 0},
        description="Counts per issue category"
    )
    
    # Recent Activity Feed
    recent_analyses: List[AnalysisSummaryRecord] = Field(
        default_factory=list,
        description="Latest analysis sessions"
    )
    
    last_updated: str = Field(..., description="Timestamp of metrics computation")


class HistoryFilterRequest(BaseModel):
    """Query parameters for filtering analysis history."""
    analysis_type: Optional[str] = Field(None, description="Filter by scan type (CODE_SNIPPET, FILE_UPLOAD, GITHUB_PR)")
    risk_level: Optional[str] = Field(None, description="Filter by risk tier (LOW, MEDIUM, HIGH, CRITICAL)")
    limit: int = Field(default=20, ge=1, le=100, description="Max records to return")
    offset: int = Field(default=0, ge=0, description="Pagination offset")
