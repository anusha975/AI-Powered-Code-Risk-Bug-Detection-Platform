"""
Risk Scoring API Endpoints.
Provides the POST /api/risk/score endpoint for calculating ML and deterministic code risk scores.
"""

from fastapi import APIRouter, HTTPException, status
from app.schemas.risk import RiskScoreRequest, RiskScoreResponse
from app.services.risk_service import RiskService
from app.core.security_validator import SecurityValidationError
from app.services.language_detector import UnsupportedLanguageError

router = APIRouter(tags=["Code Risk Scoring"])


@router.post(
    "/score",
    response_model=RiskScoreResponse,
    status_code=status.HTTP_200_OK,
    summary="Calculate Code Risk Score",
    description=(
        "Calculates an explainable 0-100 risk score combining deterministic heuristics "
        "and a Scikit-learn RandomForest regression pipeline. Includes feature extraction, "
        "structural metrics, and human-interpretable reasons."
    )
)
def calculate_risk_score(payload: RiskScoreRequest) -> RiskScoreResponse:
    """Calculate an overall risk score and explainability breakdown for submitted code."""
    try:
        return RiskService.calculate_risk(
            content=payload.content,
            filename=payload.filename,
            explicit_language=payload.language,
            provided_findings=payload.findings,
            provided_secrets_count=payload.secrets_count
        )
    except (SecurityValidationError, UnsupportedLanguageError) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc)
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while computing the risk score: {str(exc)}"
        )
