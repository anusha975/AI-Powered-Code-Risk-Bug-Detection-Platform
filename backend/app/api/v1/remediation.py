"""
Developer Explanation and Remediation API Endpoints.
"""

from fastapi import APIRouter, HTTPException, status
from app.schemas.remediation import RemediationRequest, RemediationResponse
from app.services.remediation_service import RemediationService
from app.core.security_validator import SecurityValidationError
from app.services.language_detector import UnsupportedLanguageError

router = APIRouter(tags=["AI Developer Remediation"])


@router.post(
    "/explain",
    response_model=RemediationResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate Developer Explanations and Safer Code Replacements",
    description=(
        "Generates structured, tripartite developer remediation explanations for static analysis findings. "
        "Strictly segregates DETECTED FACT (AST/SAST), AI INTERPRETATION (developer explanation, impact, uncertainty), "
        "and RECOMMENDATION (safer replacement code). Never hallucinates new vulnerabilities independently."
    )
)
async def explain_and_remediate_code(payload: RemediationRequest) -> RemediationResponse:
    """Generate developer-friendly explanations and safer code examples."""
    try:
        return await RemediationService.generate_developer_remediations(
            content=payload.content,
            filename=payload.filename,
            explicit_language=payload.language,
            max_explanations=payload.max_explanations or 3,
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
            detail=f"An error occurred while generating developer remediation: {str(exc)}"
        )
