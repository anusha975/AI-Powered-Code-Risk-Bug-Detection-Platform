"""
Security Scanning and Privacy API Endpoints.
Provides the /api/security/scan endpoint for secret detection and redaction.
"""

from fastapi import APIRouter, HTTPException, status
from app.schemas.security import SecurityScanRequest, SecurityScanResponse
from app.services.security_service import security_service
from app.core.security_validator import SecurityValidationError

router = APIRouter(tags=["Security & Privacy"])


@router.post(
    "/scan",
    response_model=SecurityScanResponse,
    status_code=status.HTTP_200_OK,
    summary="Scan and Redact Secrets in Source Code",
    description=(
        "Scans source code for sensitive credentials (API keys, tokens, passwords, private keys, "
        "database connection URIs, JWTs, and cloud credentials) and applies deterministic placeholder redaction. "
        "Guarantees zero raw secret leakage in the response."
    )
)
def scan_and_redact_code(payload: SecurityScanRequest) -> SecurityScanResponse:
    """Scan and redact source code without exposing detected secrets."""
    try:
        return security_service.scan_and_redact(
            content=payload.content,
            filename=payload.filename,
            explicit_language=payload.language
        )
    except SecurityValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc)
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while executing the security privacy scan."
        )
