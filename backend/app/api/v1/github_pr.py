"""
GitHub Pull Request Security & Risk Analysis API Endpoints.
"""

from typing import Optional
from fastapi import APIRouter, Header, HTTPException, status

from app.schemas.github_pr import (
    PRUrlParseRequest,
    PRUrlParseResponse,
    PRAnalysisRequest,
    PRAnalysisResponse
)
from app.services.github_pr_service import GitHubPRService
from app.utils.logger import logger

router = APIRouter(tags=["GitHub Pull Request Security"])


@router.post(
    "/parse-url",
    response_model=PRUrlParseResponse,
    status_code=status.HTTP_200_OK,
    summary="Validate and Parse GitHub PR URL",
    description="Validates a GitHub Pull Request URL or shorthand string and extracts owner, repo, and PR number."
)
def parse_pr_url(payload: PRUrlParseRequest) -> PRUrlParseResponse:
    """Parse and validate GitHub PR URL coordinates."""
    try:
        return GitHubPRService.parse_url(payload.pr_url)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc)
        )


@router.post(
    "/analyze",
    response_model=PRAnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze GitHub Pull Request Security & Risk",
    description="Executes a multi-file security scan on a GitHub Pull Request without cloning or executing repository code."
)
async def analyze_pull_request(
    payload: PRAnalysisRequest,
    x_github_token: Optional[str] = Header(None, alias="X-GitHub-Token")
) -> PRAnalysisResponse:
    """Run full privacy-preserving security and risk assessment on a Pull Request."""
    try:
        return await GitHubPRService.analyze_pull_request(
            request=payload,
            header_token=x_github_token
        )
    except ValueError as val_exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(val_exc)
        )
    except PermissionError as perm_exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(perm_exc)
        )
    except ConnectionError as conn_exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(conn_exc)
        )
    except Exception as exc:
        logger.error(f"PR Security Scan Failed: {str(exc)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze GitHub Pull Request: {str(exc)}"
        )
