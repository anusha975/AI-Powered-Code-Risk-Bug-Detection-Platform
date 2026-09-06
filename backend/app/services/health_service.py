"""
Health Check and Telemetry Service.
Coordinates component status checks and system health metrics.
"""

import time
from datetime import datetime, timezone
from app.core.config import settings
from app.core.constants import ACTIVE_MODULES, ComponentStatus
from app.database.session import check_database_connection
from app.schemas.health import (
    HealthResponse,
    DatabaseHealth,
    PrivacyGuardrails,
    ModuleInfo
)

# Record application startup timestamp
START_TIME = time.time()


class HealthService:
    """Service to compile overall platform health and telemetry."""

    @staticmethod
    def get_health() -> HealthResponse:
        """Inspect all system subsystems and compile a unified health report."""
        uptime = round(time.time() - START_TIME, 2)
        db_status = check_database_connection()
        
        # Overall status is OPERATIONAL if the backend is running; flagged DEGRADED if DB is down
        overall_status = (
            ComponentStatus.OPERATIONAL.value 
            if db_status["status"] == ComponentStatus.CONNECTED.value 
            else ComponentStatus.DEGRADED.value
        )
        
        return HealthResponse(
            status=overall_status,
            app_name=settings.APP_NAME,
            version=settings.APP_VERSION,
            environment=settings.ENVIRONMENT,
            uptime_seconds=uptime,
            timestamp=datetime.now(timezone.utc).isoformat(),
            database=DatabaseHealth(**db_status),
            privacy_guardrails=PrivacyGuardrails(
                analysis_mode=settings.ANALYSIS_MODE.value,
                secret_redaction_enforced=settings.ENFORCE_SECRET_REDACTION,
                remote_llm_allowed=settings.ALLOW_REMOTE_LLM,
                max_snippet_lines=settings.MAX_SNIPPET_LINE_LIMIT
            ),
            active_modules=[ModuleInfo(**m) for m in ACTIVE_MODULES]
        )


health_service = HealthService()
