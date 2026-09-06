"""
Static Code Analysis API Endpoints.
Provides the /api/analysis/static endpoint for local security, injection, complexity, and bug scanning.
"""

from fastapi import APIRouter, HTTPException, status
from app.schemas.analysis import AnalysisRequest, AnalysisResponse
from app.services.analysis_service import analysis_service
from app.core.security_validator import SecurityValidationError
from app.services.language_detector import UnsupportedLanguageError

router = APIRouter(tags=["Static Code Analysis"])


@router.post(
    "/static",
    response_model=AnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="Run Local Static Code Analysis",
    description=(
        "Performs offline, zero-execution static analysis on source code using Python AST and Bandit. "
        "Detects dangerous functions (eval, exec), command & SQL injection patterns, unsafe deserialization (pickle), "
        "broad/empty exception handlers, weak crypto, and excessive complexity."
    )
)
def run_static_analysis(payload: AnalysisRequest) -> AnalysisResponse:
    """Execute local static analysis on submitted code."""
    try:
        return analysis_service.analyze_code(
            content=payload.content,
            filename=payload.filename,
            explicit_language=payload.language
        )
    except (SecurityValidationError, UnsupportedLanguageError) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc)
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while executing static code analysis."
        )
