"""
Provider Schemas for Discovery, Health Telemetry, and Connectivity Testing.
"""

from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field


class ProviderType(str, Enum):
    """AI Provider engine type."""
    LOCAL = "local"
    EXTERNAL = "external"
    MOCK = "mock"


class ProviderStatus(str, Enum):
    """Operational health status of a provider."""
    OPERATIONAL = "OPERATIONAL"
    STANDBY = "STANDBY"
    UNREACHABLE = "UNREACHABLE"
    MISSING_API_KEY = "MISSING_API_KEY"
    DISABLED = "DISABLED"
    ERROR = "ERROR"


class ProviderHealthInfo(BaseModel):
    """Health and telemetry report for an AI provider."""
    provider_type: ProviderType = Field(..., description="Provider categorization (local, external, mock)")
    provider_name: str = Field(..., description="Display name of provider")
    status: ProviderStatus = Field(..., description="Current operational status")
    is_active: bool = Field(..., description="Whether this is the currently configured system provider")
    model_name: str = Field(..., description="Configured or detected model name")
    endpoint_url: Optional[str] = Field(None, description="Target endpoint URL (if applicable)")
    air_gapped: bool = Field(..., description="True if provider guarantees 0 external network egress")
    privacy_score: int = Field(..., ge=0, le=100, description="Privacy rating score (100 = full air-gap)")
    latency_ms: Optional[float] = Field(None, description="Round-trip ping latency in milliseconds")
    diagnostic_message: Optional[str] = Field(None, description="Diagnostic message or troubleshooting advice")


class ProviderTestRequest(BaseModel):
    """Request payload to test connectivity to an AI provider."""
    provider_type: ProviderType = Field(..., description="Provider type to test")
    api_url: Optional[str] = Field(None, description="Custom endpoint URL to probe")
    model_name: Optional[str] = Field(None, description="Target model name")
    api_type: Optional[str] = Field("ollama", description="Local API protocol: 'ollama' or 'openai_compatible'")
    api_key: Optional[str] = Field(None, description="API key (only for external provider)")
    timeout_seconds: Optional[int] = Field(5, ge=1, le=30, description="Test timeout in seconds")


class ProviderTestResponse(BaseModel):
    """Result of provider connectivity test."""
    success: bool = Field(..., description="Whether connection test succeeded")
    provider_type: ProviderType = Field(..., description="Provider type tested")
    endpoint_url: Optional[str] = Field(None, description="Tested endpoint URL")
    model_name: Optional[str] = Field(None, description="Model tested")
    latency_ms: float = Field(..., description="Round-trip latency in milliseconds")
    status: ProviderStatus = Field(..., description="Discovered status")
    message: str = Field(..., description="User-friendly status or error explanation")
    models_available: List[str] = Field(default_factory=list, description="List of detected models on host")
    air_gapped: bool = Field(..., description="True if no external data egress")


class ProviderCatalogResponse(BaseModel):
    """Catalog of all supported providers, active provider, and privacy comparison."""
    active_provider: ProviderType = Field(..., description="Currently active provider type")
    active_model: str = Field(..., description="Active model name")
    ai_enabled: bool = Field(..., description="Whether AI analysis is enabled globally")
    providers: List[ProviderHealthInfo] = Field(..., description="List of all supported providers and their live health")
    privacy_notice: str = Field(
        default=(
            "Local LLM mode ensures zero data egress outside your infrastructure. "
            "Your organization retains responsibility for securing host endpoints, "
            "firewalls, and model weights."
        ),
        description="Privacy invariant disclaimer"
    )
