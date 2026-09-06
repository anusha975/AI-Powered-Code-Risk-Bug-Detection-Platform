"""
Dashboard Analytics & Session History Service.

Coordinates executive overview calculations, audit history querying,
deep-dive analysis session retrieval, and findings catalog search.
"""

from typing import List, Optional, Dict, Any

from app.analytics.session_store import session_store
from app.schemas.analytics import (
    DashboardOverviewMetrics,
    AnalysisSummaryRecord,
    AnalysisDetailRecord,
    AggregatedFinding,
    HistoryFilterRequest
)
from app.utils.logger import logger


class AnalyticsService:
    """Service layer for dashboard analytics, history logs, and findings catalog."""

    @staticmethod
    def get_overview_metrics() -> DashboardOverviewMetrics:
        """Fetch aggregated executive dashboard metrics with real live data."""
        return session_store.get_overview_metrics()

    @staticmethod
    def get_history(req: HistoryFilterRequest, user_id: Optional[str] = None) -> List[AnalysisSummaryRecord]:
        """Fetch filtered analysis history logs with optional user-level scoping."""
        return session_store.list_history(
            analysis_type=req.analysis_type,
            risk_level=req.risk_level,
            user_id=user_id,
            limit=req.limit,
            offset=req.offset
        )

    @staticmethod
    def get_session_detail(analysis_id: str) -> Optional[AnalysisDetailRecord]:
        """Fetch complete deep-dive record for a specific analysis session."""
        return session_store.get_analysis_detail(analysis_id)

    @staticmethod
    def search_findings(
        severity: Optional[str] = None,
        category: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[AggregatedFinding]:
        """Search and filter the universal findings catalog."""
        return session_store.list_all_findings(
            severity=severity,
            category=category,
            search=search,
            limit=limit,
            offset=offset
        )
