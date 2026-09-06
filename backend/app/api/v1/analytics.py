"""
Professional Engineering Security Dashboard Analytics Endpoints.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.schemas.analytics import (
    DashboardOverviewMetrics,
    AnalysisSummaryRecord,
    AnalysisDetailRecord,
    AggregatedFinding,
    HistoryFilterRequest
)
from app.api.deps import get_optional_current_user
from app.schemas.auth import UserRecord, UserRole
from app.services.analytics_service import AnalyticsService

router = APIRouter(tags=["Engineering Dashboard Analytics"])


@router.get(
    "/overview",
    response_model=DashboardOverviewMetrics,
    status_code=status.HTTP_200_OK,
    summary="Get Executive Dashboard Telemetry Metrics",
    description="Returns real-time aggregated metrics: analyses performed, high-risk counts, critical findings, average risk score, category distribution, and recent activity."
)
def get_dashboard_overview() -> DashboardOverviewMetrics:
    """Retrieve live aggregated telemetry for executive dashboard."""
    return AnalyticsService.get_overview_metrics()


@router.get(
    "/history",
    response_model=List[AnalysisSummaryRecord],
    status_code=status.HTTP_200_OK,
    summary="List Historical Analysis Sessions",
    description="Returns paginated and filterable analysis history logs. Scoped to user for DEVELOPER role."
)
def get_analysis_history(
    analysis_type: Optional[str] = Query(None, description="Filter by CODE_SNIPPET, FILE_UPLOAD, GITHUB_PR"),
    risk_level: Optional[str] = Query(None, description="Filter by LOW, MEDIUM, HIGH, CRITICAL"),
    limit: int = Query(20, ge=1, le=100, description="Max records to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    current_user: Optional[UserRecord] = Depends(get_optional_current_user)
) -> List[AnalysisSummaryRecord]:
    """Retrieve audit history rows with user-level scoping."""
    user_scope = None
    if current_user:
        is_admin = (
            current_user.role == UserRole.ADMIN or
            (isinstance(current_user.role, str) and current_user.role.upper() == "ADMIN")
        )
        if not is_admin:
            user_scope = current_user.id

    req = HistoryFilterRequest(
        analysis_type=analysis_type,
        risk_level=risk_level,
        limit=limit,
        offset=offset
    )
    return AnalyticsService.get_history(req, user_id=user_scope)


@router.get(
    "/history/{analysis_id}",
    response_model=AnalysisDetailRecord,
    status_code=status.HTTP_200_OK,
    summary="Get Analysis Session Deep-Dive Details",
    description="Returns complete diagnostics, line-mapped findings, redacted secrets, and tripartite AI remediations for a specific session."
)
def get_analysis_detail(analysis_id: str) -> AnalysisDetailRecord:
    """Retrieve full inspection details for a specific analysis session."""
    session = AnalyticsService.get_session_detail(analysis_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis session '{analysis_id}' not found in audit store."
        )
    return session


@router.get(
    "/findings",
    response_model=List[AggregatedFinding],
    status_code=status.HTTP_200_OK,
    summary="Universal Findings Catalog Search",
    description="Query and filter all security, secret, and code-quality findings across historical scans."
)
def get_all_findings(
    severity: Optional[str] = Query(None, description="Filter by CRITICAL, HIGH, MEDIUM, LOW"),
    category: Optional[str] = Query(None, description="Filter by SECURITY, SECRETS, CODE_QUALITY, COMPLEXITY"),
    search: Optional[str] = Query(None, description="Keyword search query"),
    limit: int = Query(50, ge=1, le=200, description="Max findings to return"),
    offset: int = Query(0, ge=0, description="Pagination offset")
) -> List[AggregatedFinding]:
    """Search and filter the global findings catalog."""
    return AnalyticsService.search_findings(
        severity=severity,
        category=category,
        search=search,
        limit=limit,
        offset=offset
    )
