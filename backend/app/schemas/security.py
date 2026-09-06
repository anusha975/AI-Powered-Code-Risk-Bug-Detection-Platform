"""
Pydantic Schemas for Secret Scanning, Findings, and Redaction Telemetry.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class SecretFinding(BaseModel):
    """Metadata describing a detected secret finding (zero secret leakage)."""
    secret_type: str = Field(..., description="Class of detected credential (e.g. AWS_ACCESS_KEY, JWT_TOKEN)")
    file: str = Field(..., description="Filename containing the finding")
    line_number: int = Field(..., description="1-indexed line number where secret was detected")
    confidence: str = Field(..., description="Confidence level: HIGH, MEDIUM, LOW")
    redaction_status: str = Field("REDACTED", description="Redaction status applied (REDACTED)")
    placeholder: str = Field(..., description="Substituted placeholder string in sanitized code")


class SecurityScanRequest(BaseModel):
    """Payload schema for secret detection and redaction request."""
    language: Optional[str] = Field(None, description="Programming language of the snippet")
    filename: Optional[str] = Field("snippet.py", description="Logical filename")
    content: str = Field(..., min_length=1, description="Raw source code to scan and sanitize")


class SecurityScanResponse(BaseModel):
    """Sanitization report containing public findings and redacted code."""
    scan_id: str = Field(..., description="Unique UUID tracking this scan operation")
    filename: str = Field(..., description="Sanitized logical filename")
    secrets_detected_count: int = Field(..., description="Total number of secrets identified and redacted")
    findings: List[SecretFinding] = Field(..., description="List of detected secret findings (values omitted)")
    sanitized_content: str = Field(..., description="Source code with all secrets replaced by placeholders")
    redaction_applied: bool = Field(..., description="True if one or more secrets were detected and redacted")
    scanned_at: str = Field(..., description="UTC ISO-8601 timestamp of scan completion")
