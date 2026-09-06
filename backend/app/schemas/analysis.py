"""
Pydantic Schemas for Local Static Code Analysis Findings and Reports.
"""

from typing import List, Optional
from enum import Enum
from pydantic import BaseModel, Field


class FindingSeverity(str, Enum):
    """Normalized vulnerability and code issue severity levels."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class FindingCategory(str, Enum):
    """Class of code issue detected."""
    SECURITY = "SECURITY"
    CODE_QUALITY = "CODE_QUALITY"
    COMPLEXITY = "COMPLEXITY"
    ERROR_HANDLING = "ERROR_HANDLING"
    INSECURE_CONFIG = "INSECURE_CONFIG"


class NormalizedFinding(BaseModel):
    """Standardized finding representation across all analyzers."""
    issue_id: str = Field(..., description="Unique issue code (e.g. SEC-EVAL-001, BND-B102)", examples=["SEC-EVAL-001"])
    title: str = Field(..., description="Concise summary of the detected issue", examples=["Use of dangerous eval() function"])
    category: str = Field(..., description="Category: SECURITY, CODE_QUALITY, COMPLEXITY, ERROR_HANDLING, INSECURE_CONFIG", examples=["SECURITY"])
    severity: str = Field(..., description="Severity level: LOW, MEDIUM, HIGH, CRITICAL", examples=["HIGH"])
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score between 0.0 and 1.0", examples=[0.95])
    file: str = Field(..., description="Target filename containing the finding", examples=["payment.py"])
    line_number: int = Field(..., ge=1, description="1-indexed line number in source code", examples=[42])
    code_snippet: str = Field(..., description="Extracted code line or AST node context", examples=["eval(user_input)"])
    recommendation: str = Field(..., description="Remediation guidance to resolve the issue", examples=["Avoid using eval(). Use ast.literal_eval() or explicit parsing logic."])
    analyzer: str = Field(..., description="Engine that produced the finding (e.g. ast_analyzer, bandit)", examples=["ast_analyzer"])


class AnalysisSummary(BaseModel):
    """Summary metrics of the static analysis run."""
    total_issues: int = Field(..., description="Total number of issues detected")
    critical_count: int = Field(0, description="Count of CRITICAL severity issues")
    high_count: int = Field(0, description="Count of HIGH severity issues")
    medium_count: int = Field(0, description="Count of MEDIUM severity issues")
    low_count: int = Field(0, description="Count of LOW severity issues")
    risk_score: float = Field(..., description="Calculated composite risk score (0.0 to 100.0)")


class AnalysisRequest(BaseModel):
    """Payload schema for local static code analysis."""
    language: Optional[str] = Field("python", description="Target programming language")
    filename: Optional[str] = Field("snippet.py", description="Logical filename")
    content: str = Field(..., min_length=1, description="Source code text to analyze statically")


class AnalysisResponse(BaseModel):
    """Static analysis report payload."""
    analysis_id: str = Field(..., description="Unique UUID tracking this analysis session")
    filename: str = Field(..., description="Sanitized filename")
    language: str = Field(..., description="Target programming language")
    summary: AnalysisSummary = Field(..., description="Aggregate issue breakdown and risk score")
    findings: List[NormalizedFinding] = Field(..., description="List of normalized findings sorted by severity")
    analyzed_at: str = Field(..., description="UTC ISO-8601 timestamp of analysis completion")
    disclaimer: str = Field(
        default="Static analysis identifies known syntactic patterns and potential risk indicators. It does not guarantee 100% bug or vulnerability detection.",
        description="Static analysis boundary notice"
    )
