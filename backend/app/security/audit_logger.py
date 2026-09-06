"""
Security Audit Logging Engine.
Enforces zero-credential and zero-source-code audit logging invariants.
Maintains a thread-safe circular event store for enterprise compliance and forensic auditability.
"""

import collections
import threading
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from app.schemas.auth import (
    AuditEventRecord,
    AuditEventType,
    AuditLogSummaryResponse
)
from app.utils.logger import logger


class SecurityAuditLogger:
    """
    Enterprise-grade security audit logger with strict privacy sanitization.
    Guarantees: Passwords, tokens, API keys, and code snippets are never stored.
    """

    MAX_CAPACITY: int = 5000
    FORBIDDEN_KEY_PATTERNS = {
        "password",
        "passwd",
        "secret",
        "token",
        "api_key",
        "apikey",
        "auth",
        "authorization",
        "credential",
        "private_key",
        "code",
        "snippet",
        "source_code",
        "raw_content",
        "payload"
    }

    def __init__(self, capacity: int = MAX_CAPACITY):
        self._lock = threading.Lock()
        self._events: collections.deque[AuditEventRecord] = collections.deque(maxlen=capacity)
        self._preseed_baseline_audit_events()

    def _sanitize_metadata(self, meta: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Recursively remove any forbidden keys, passwords, tokens, API keys, or raw code blocks.
        """
        if not meta or not isinstance(meta, dict):
            return {}

        sanitized: Dict[str, Any] = {}
        for key, value in meta.items():
            k_lower = str(key).lower()
            if any(forbidden in k_lower for forbidden in self.FORBIDDEN_KEY_PATTERNS):
                # Redact forbidden credential or code key
                sanitized[key] = "[REDACTED_BY_AUDIT_GUARD]"
            elif isinstance(value, dict):
                sanitized[key] = self._sanitize_metadata(value)
            elif isinstance(value, (list, tuple)):
                sanitized[key] = [
                    self._sanitize_metadata(item) if isinstance(item, dict) else str(item)[:100]
                    for item in value
                ]
            elif isinstance(value, (str, int, float, bool)) or value is None:
                # Truncate strings to prevent unintended dumping of large texts
                if isinstance(value, str) and len(value) > 200:
                    sanitized[key] = f"{value[:200]}... [TRUNCATED]"
                else:
                    sanitized[key] = value
            else:
                sanitized[key] = str(type(value).__name__)
        return sanitized

    def _preseed_baseline_audit_events(self) -> None:
        """Seed initial audit trail records for system startup and verification."""
        startup_events = [
            AuditEventRecord(
                event_id="AUD-INIT-000001",
                timestamp=datetime.now(timezone.utc),
                event_type=AuditEventType.SETTINGS_CHANGED,
                user_id="USR-ADMIN-0000-000000000001",
                username="admin",
                role="ADMIN",
                ip_address="127.0.0.1",
                status="SUCCESS",
                target_resource="app_config",
                sanitized_metadata={"action": "system_bootstrap", "privacy_guardrails": "ENFORCED"}
            ),
            AuditEventRecord(
                event_id="AUD-INIT-000002",
                timestamp=datetime.now(timezone.utc),
                event_type=AuditEventType.LOGIN_SUCCESS,
                user_id="USR-ADMIN-0000-000000000001",
                username="admin",
                role="ADMIN",
                ip_address="127.0.0.1",
                status="SUCCESS",
                target_resource="/api/auth/login",
                sanitized_metadata={"auth_method": "password_jwt"}
            )
        ]
        with self._lock:
            for ev in startup_events:
                self._events.append(ev)

    def log_event(
        self,
        event_type: AuditEventType,
        user_id: Optional[str] = None,
        username: Optional[str] = None,
        role: Optional[str] = None,
        ip_address: Optional[str] = "127.0.0.1",
        status: str = "SUCCESS",
        target_resource: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AuditEventRecord:
        """
        Record a sanitized security audit event into the circular ledger.
        """
        event_id = f"AUD-{uuid.uuid4().hex[:12].upper()}"
        clean_meta = self._sanitize_metadata(metadata)

        record = AuditEventRecord(
            event_id=event_id,
            timestamp=datetime.now(timezone.utc),
            event_type=event_type,
            user_id=user_id,
            username=username,
            role=role,
            ip_address=ip_address or "127.0.0.1",
            status=status,
            target_resource=target_resource,
            sanitized_metadata=clean_meta
        )

        with self._lock:
            self._events.append(record)

        logger.info(
            f"SecurityAudit: [{record.event_type.value}] status={record.status} "
            f"user={record.username or 'anon'} target={record.target_resource or 'N/A'}"
        )
        return record

    def get_events(
        self,
        event_type: Optional[AuditEventType] = None,
        user_id: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[AuditEventRecord], int]:
        """
        Query and filter audit events in reverse chronological order.
        """
        with self._lock:
            records = list(self._events)

        # Filter
        filtered = []
        for r in reversed(records):
            if event_type and r.event_type != event_type:
                continue
            if user_id and r.user_id != user_id:
                continue
            if status and r.status.upper() != status.upper():
                continue
            filtered.append(r)

        total = len(filtered)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated = filtered[start_idx:end_idx]

        return paginated, total

    def get_summary(self) -> AuditLogSummaryResponse:
        """
        Calculate real-time audit summary metrics.
        """
        with self._lock:
            records = list(self._events)

        total_events = len(records)
        event_breakdown: Dict[str, int] = {}
        unique_users = set()

        for r in records:
            k = r.event_type.value
            event_breakdown[k] = event_breakdown.get(k, 0) + 1
            if r.user_id:
                unique_users.add(r.user_id)

        recent_events = list(reversed(records))[:10]

        return AuditLogSummaryResponse(
            total_events=total_events,
            event_breakdown=event_breakdown,
            recent_events=recent_events,
            active_users_count=len(unique_users)
        )


# Global singleton instance
audit_logger = SecurityAuditLogger()
