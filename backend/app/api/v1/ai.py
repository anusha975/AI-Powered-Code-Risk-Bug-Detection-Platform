"""
Privacy-Aware AI Analysis, Provider Discovery, and Audit API Endpoints.
"""

from typing import List
from fastapi import APIRouter, HTTPException, status, Query

from app.schemas.ai import AIAnalysisRequest, AIAnalysisResponse, AIAuditEvent
from app.schemas.provider import (
    ProviderCatalogResponse,
    ProviderTestRequest,
    ProviderTestResponse
)
from app.services.ai_service import AIService
from app.services.provider_service import ProviderService
from app.ai.audit_logger import audit_logger
from app.core.security_validator import SecurityValidationError
from app.services.language_detector import UnsupportedLanguageError

router = APIRouter(tags=["Privacy-Aware AI Analysis & Local Providers"])


@router.post(
    "/analyze",
    response_model=AIAnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="Run Privacy-Preserving AI Code Analysis",
    description=(
        "Executes full 7-stage privacy pipeline: secret detection & redaction, "
        "local static code analysis, risk scoring, context minimization (±4 lines), "
        "and AI provider remediation advice (Local air-gapped, Cloud TLS, or Mock) "
        "with guaranteed non-blocking fallback."
    )
)
async def run_privacy_ai_analysis(payload: AIAnalysisRequest) -> AIAnalysisResponse:
    """Execute privacy-preserving AI analysis on submitted code."""
    try:
        return await AIService.analyze_with_privacy_ai(
            content=payload.content,
            filename=payload.filename,
            explicit_language=payload.language,
            ai_enabled=payload.ai_enabled,
            provider_override=payload.provider_override
        )
    except (SecurityValidationError, UnsupportedLanguageError) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc)
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during AI code analysis: {str(exc)}"
        )


@router.get(
    "/providers",
    response_model=ProviderCatalogResponse,
    status_code=status.HTTP_200_OK,
    summary="Get AI Providers Catalog & Health Status",
    description=(
        "Returns available AI provider configurations (Local Air-Gapped, External Cloud, Mock), "
        "their live reachability status, air-gapped compliance scores, and diagnostic messages."
    )
)
async def get_ai_providers_catalog() -> ProviderCatalogResponse:
    """Discover and probe operational health across all supported AI provider modes."""
    try:
        return await ProviderService.get_provider_catalog()
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to query provider catalog: {str(exc)}"
        )


@router.post(
    "/providers/test",
    response_model=ProviderTestResponse,
    status_code=status.HTTP_200_OK,
    summary="Test AI Provider Connectivity",
    description="Probes connectivity to a local Ollama server, local OpenAI-compatible endpoint, or external cloud API."
)
async def test_ai_provider_connection(payload: ProviderTestRequest) -> ProviderTestResponse:
    """Test live connectivity and latency for a specified provider endpoint."""
    try:
        return await ProviderService.test_provider_connection(payload)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error executing provider connectivity test: {str(exc)}"
        )


@router.get(
    "/audit",
    response_model=List[AIAuditEvent],
    status_code=status.HTTP_200_OK,
    summary="Get Privacy Audit Log Telemetry",
    description=(
        "Returns recent AI analysis audit events. "
        "INVIOLABLE GUARANTEE: Contains zero source code, zero prompts, and zero secret values."
    )
)
def get_ai_audit_events(
    limit: int = Query(50, ge=1, le=200, description="Max audit events to return")
) -> List[AIAuditEvent]:
    """Retrieve telemetry audit events for AI analysis executions."""
    return audit_logger.get_recent_events(limit=limit)
