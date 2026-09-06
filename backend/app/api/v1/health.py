"""
Health Check and System Status Endpoints.
"""

from fastapi import APIRouter, status
from app.schemas.health import HealthResponse
from app.services.health_service import health_service

router = APIRouter(tags=["Health & Telemetry"])


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="System Health and Telemetry",
    description="Returns backend status, database connection, uptime, active privacy guardrails, and module states."
)
def get_health() -> HealthResponse:
    """Retrieve comprehensive platform telemetry and component health."""
    return health_service.get_health()
