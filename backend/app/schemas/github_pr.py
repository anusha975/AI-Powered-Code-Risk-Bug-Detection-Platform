"""
Pydantic Schemas for Module 10: GitHub Pull Request Security and Risk Analysis.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

from app.schemas.analysis import FindingSeverity, NormalizedFinding
from app.schemas.security import SecretFinding
from app.schemas.remediation import DeveloperRemediation
from app.schemas.rag import RetrievedSource


class PRUrlParseRequest(BaseModel):
    """Request payload to parse and validate a GitHub Pull Request URL."""
    pr_url: str = Field(
        ...,
        min_length=5,
        description="GitHub Pull Request URL (e.g. https://github.com/owner/repo/pull/42) or shorthand (owner/repo#42)"
    )


class PRUrlParseResponse(BaseModel):
    """Validated components extracted from a GitHub Pull Request URL."""
    valid: bool = Field(..., description="Whether the URL or shorthand is valid")
    owner: str = Field(..., description="Repository owner/organization")
    repo: str = Field(..., description="Repository name")
    pull_number: int = Field(..., description="Pull request number")
    canonical_url: str = Field(..., description="Canonical HTTPS GitHub PR URL")


class PRSeverityBreakdown(BaseModel):
    """Aggregated severity breakdown across all changed files in the PR."""
    critical: int = Field(default=0, ge=0, description="Count of critical severity findings")
    high: int = Field(default=0, ge=0, description="Count of high severity findings")
    medium: int = Field(default=0, ge=0, description="Count of medium severity findings")
    low: int = Field(default=0, ge=0, description="Count of low severity findings")


class PRFileFinding(BaseModel):
    """A finding mapped to a specific changed file and diff line number in a PR."""
    file: str = Field(..., description="Changed file path")
    line_number: Optional[int] = Field(None, description="Actual new line number in PR diff")
    issue_id: str = Field(..., description="Unique finding code or rule identifier")
    title: str = Field(..., description="Brief title of the finding")
    category: str = Field(..., description="Category (SECURITY, SECRETS, QUALITY, COMPLEXITY)")
    severity: str = Field(..., description="Finding severity (CRITICAL, HIGH, MEDIUM, LOW)")

    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    code_snippet: str = Field(..., description="Sanitized relevant snippet")
    recommendation: str = Field(..., description="Deterministic guidance")
    analyzer: str = Field(..., description="Origin analyzer (bandit, ast_security, secret_engine)")


class PRFileAnalysis(BaseModel):
    """Security and static analysis results for a single changed file in a PR."""
    filename: str = Field(..., description="Relative file path in repository")
    status: str = Field(..., description="Git change status (added, modified, removed, renamed)")
    additions: int = Field(..., ge=0, description="Number of added lines")
    deletions: int = Field(..., ge=0, description="Number of deleted lines")
    is_scanned: bool = Field(..., description="Whether the file was scanned (skipped if binary/lockfile)")
    language: Optional[str] = Field(None, description="Detected programming language")
    secrets_count: int = Field(default=0, ge=0, description="Number of credentials redacted in this file")
    findings_count: int = Field(default=0, ge=0, description="Number of static findings in this file")
    file_risk_score: float = Field(default=0.0, ge=0.0, le=100.0, description="Per-file calculated risk score")
    file_risk_level: str = Field(default="LOW", description="Per-file risk tier (LOW, MEDIUM, HIGH, CRITICAL)")
    findings: List[PRFileFinding] = Field(default_factory=list, description="Findings in this file")
    secrets: List[SecretFinding] = Field(default_factory=list, description="Redacted secret findings")
    patch_snippet: Optional[str] = Field(None, description="Truncated preview of diff patch")


class PRAnalysisRequest(BaseModel):
    """Request payload to initiate a GitHub Pull Request security scan."""
    pr_url: Optional[str] = Field(
        None,
        description="Full GitHub PR URL (e.g. https://github.com/owner/repo/pull/123)"
    )
    owner: Optional[str] = Field(None, description="Repository owner/org if not using full URL")
    repo: Optional[str] = Field(None, description="Repository name if not using full URL")
    pull_number: Optional[int] = Field(None, description="PR number if not using full URL")
    github_token: Optional[str] = Field(
        None,
        description="Optional GitHub Personal Access Token (PAT) for private repos or higher rate limits"
    )
    analysis_mode: str = Field(
        default="REDACTED_HYBRID",
        description="Operational mode (LOCAL_STATIC_ONLY, REDACTED_HYBRID, SELF_HOSTED_LLM)"
    )
    provider_override: Optional[str] = Field(
        None,
        description="Optional AI provider override ('local', 'external', 'mock')"
    )
    enable_rag: bool = Field(
        default=True,
        description="Whether to augment explanations with Engineering Knowledge RAG"
    )
    max_files: int = Field(
        default=25,
        ge=1,
        le=100,
        description="Maximum number of changed files to analyze in PR"
    )


class PRAnalysisResponse(BaseModel):
    """Complete, comprehensive GitHub Pull Request Security & Risk Analysis Report."""
    analysis_id: str = Field(..., description="Unique UUID for this PR security audit")
    pr_number: int = Field(..., description="GitHub Pull Request number")
    repository: str = Field(..., description="Repository in 'owner/repo' format")
    pr_title: str = Field(..., description="Title of the Pull Request")
    pr_author: str = Field(..., description="Author GitHub login")
    pr_url: str = Field(..., description="Web URL to the GitHub Pull Request")
    base_branch: str = Field(..., description="Base target branch (e.g. main)")
    head_branch: str = Field(..., description="Source feature branch")
    state: str = Field(..., description="PR state (open, closed, merged)")
    
    # Aggregated Diff Metrics
    changed_files_count: int = Field(..., ge=0, description="Total number of files modified in PR")
    scanned_files_count: int = Field(..., ge=0, description="Number of code files analyzed for security")
    additions: int = Field(..., ge=0, description="Total added lines in PR")
    deletions: int = Field(..., ge=0, description="Total deleted lines in PR")
    
    # Aggregated Security Findings
    findings_count: int = Field(..., ge=0, description="Total static & security findings detected")
    secrets_detected_count: int = Field(..., ge=0, description="Total credentials redacted")
    severity_breakdown: PRSeverityBreakdown = Field(..., description="Severity counts across PR")
    
    # Risk Assessment
    overall_risk_score: float = Field(..., ge=0.0, le=100.0, description="Overall PR risk score (0-100)")
    overall_risk_level: str = Field(..., description="Overall PR risk level (LOW, MEDIUM, HIGH, CRITICAL)")
    risk_reasons: List[str] = Field(default_factory=list, description="Explainable reasons for PR risk score")
    
    # Detailed File Breakdown
    files: List[PRFileAnalysis] = Field(default_factory=list, description="Per-file security diagnostics")
    
    # Grounded AI Remediation & Knowledge
    remediations: List[DeveloperRemediation] = Field(
        default_factory=list,
        description="Tripartite developer remediation plans for top findings in PR"
    )
    supporting_documents: List[RetrievedSource] = Field(
        default_factory=list,
        description="Curated engineering guidelines, OWASP standards, and post-mortems cited via RAG"
    )
    
    # Telemetry & Compliance
    scan_latency_ms: float = Field(..., description="Total PR scan execution time in ms")
    analyzed_at: str = Field(..., description="ISO UTC timestamp of analysis")
    privacy_guarantee: str = Field(
        default="Zero-Execution & Context-Minimization Invariant: Repository code was never cloned or executed. Only minimal sanitized diff patches were analyzed.",
        description="Privacy and security guarantee statement"
    )
    security_notice: str = Field(
        default="Passive Security Analysis: No Pull Requests were automatically merged, modified, or closed.",
        description="Non-mutation notice"
    )
