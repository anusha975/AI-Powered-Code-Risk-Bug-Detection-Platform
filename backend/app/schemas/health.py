"""
Pydantic Schemas for System Health and Diagnostics.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class DatabaseHealth(BaseModel):
    """Database connectivity and telemetry model."""
    status: str = Field(..., description="Connection status: CONNECTED or DISCONNECTED")
    database_type: str = Field(..., description="RDBMS provider (PostgreSQL)")
    host: str = Field(..., description="Configured database host")
    database_name: str = Field(..., description="Configured database name")
    latency_ms: Optional[float] = Field(None, description="Query round-trip latency in milliseconds")
    message: str = Field(..., description="Status summary or diagnostic message")


class PrivacyGuardrails(BaseModel):
    """Active privacy configuration parameters."""
    analysis_mode: str = Field(..., description="Active analysis policy (e.g. LOCAL_STATIC_ONLY)")
    secret_redaction_enforced: bool = Field(..., description="True if automatic secret redaction is active")
    remote_llm_allowed: bool = Field(..., description="True if third-party LLM transmission is permitted")
    max_snippet_lines: int = Field(..., description="Maximum allowed lines per extracted AST snippet")


class ModuleInfo(BaseModel):
    """Metadata regarding a platform subsystem."""
    id: str = Field(..., description="Unique module identifier")
    name: str = Field(..., description="Module display title")
    status: str = Field(..., description="Module state: ACTIVE or PLANNED")
    description: str = Field(..., description="Module architectural responsibility")


class HealthResponse(BaseModel):
    """Comprehensive system health response."""
    status: str = Field(..., description="Overall platform status (OPERATIONAL / DEGRADED)")
    app_name: str = Field(..., description="Platform title")
    version: str = Field(..., description="Semantic version string")
    environment: str = Field(..., description="Deployment environment (development/production)")
    uptime_seconds: float = Field(..., description="Seconds elapsed since backend startup")
    timestamp: str = Field(..., description="UTC ISO timestamp of the health check request")
    database: DatabaseHealth = Field(..., description="Database telemetry and state")
    privacy_guardrails: PrivacyGuardrails = Field(..., description="Privacy enforcement settings")
    active_modules: List[ModuleInfo] = Field(..., description="List of platform modules and roadmap status")
