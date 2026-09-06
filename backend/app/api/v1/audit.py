"""
Security Audit API Router.
Provides compliance audit trail retrieval, event filtering, and audit metrics.
"""

from typing import Dict, List, Optional
from fastapi import APIRouter, Depends, Query
from app.api.deps import get_current_user, require_admin, require_developer
from app.schemas.auth import (
    AuditEventRecord,
    AuditEventType,
    AuditLogSummaryResponse,
    UserRecord,
    UserRole
)
from app.security.audit_logger import audit_logger

router = APIRouter(prefix="/audit", tags=["Security Audit & Compliance"])


@router.get(
    "/events",
    summary="Query security audit trail events"
)
async def get_audit_events(
    event_type: Optional[AuditEventType] = Query(None, description="Filter by event type"),
    user_id: Optional[str] = Query(None, description="Filter by specific user ID (Admin only)"),
    status: Optional[str] = Query(None, description="Filter by status (SUCCESS, FAILURE, WARNING)"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Records per page"),
    current_user: UserRecord = Depends(get_current_user)
):
    """
    Retrieve paginated security audit log records.
    - ADMIN role: Can view all audit events across all users.
    - DEVELOPER role: Automatically scoped to their own audit events only.
    """
    is_admin = (
        current_user.role == UserRole.ADMIN or
        (isinstance(current_user.role, str) and current_user.role.upper() == "ADMIN")
    )

    effective_user_id = user_id if is_admin else current_user.id

    records, total = audit_logger.get_events(
        event_type=event_type,
        user_id=effective_user_id,
        status=status,
        page=page,
        page_size=page_size
    )

    return {
        "records": records,
        "total_count": total,
        "page": page,
        "page_size": page_size,
        "is_admin_view": is_admin
    }


@router.get(
    "/summary",
    response_model=AuditLogSummaryResponse,
    summary="Get aggregated security audit summary"
)
async def get_audit_summary(
    current_user: UserRecord = Depends(require_developer)
):
    """
    Get audit event breakdown and recent telemetry.
    """
    return audit_logger.get_summary()
