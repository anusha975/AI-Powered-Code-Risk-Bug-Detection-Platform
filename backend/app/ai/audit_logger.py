"""
Privacy-Preserving AI Audit Logger.

Maintains an immutable in-memory telemetry log of all AI layer invocations.
INVIOLABLE GUARANTEE: This logger NEVER accepts or stores source code, raw prompts, or secret tokens.
"""

from typing import List, Optional
import uuid
from datetime import datetime, timezone
import threading
from collections import deque

from app.schemas.ai import AIAuditEvent, AIStatus
from app.utils.logger import logger


class AIAuditLogger:
    """Thread-safe circular telemetry buffer for AI analysis audit records."""

    def __init__(self, max_records: int = 200) -> None:
        self._buffer: deque[AIAuditEvent] = deque(maxlen=max_records)
        self._lock = threading.Lock()

    def record_event(
        self,
        provider: str,
        model: str,
        status: AIStatus,
        findings_count: int,
        payload_chars: int,
        latency_ms: float,
        details: Optional[str] = None
    ) -> AIAuditEvent:
        """
        Record a privacy audit event.

        Notice: Accepts ONLY operational metrics (lengths, counts, latencies).
        Does NOT accept source code strings or prompts.
        """
        event = AIAuditEvent(
            event_id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc).isoformat(),
            provider=provider,
            model=model,
            status=status,
            findings_count=findings_count,
            payload_chars=payload_chars,
            latency_ms=round(latency_ms, 2),
            details=details
        )

        with self._lock:
            self._buffer.appendleft(event)

        logger.info(
            f"AI Audit Event | ID: {event.event_id} | Provider: {provider} | "
            f"Status: {status.value} | Findings: {findings_count} | Latency: {event.latency_ms}ms"
        )

        return event

    def get_recent_events(self, limit: int = 50) -> List[AIAuditEvent]:
        """Retrieve recent audit telemetry events."""
        with self._lock:
            return list(self._buffer)[:limit]

    def clear(self) -> None:
        """Clear audit history (used in test fixtures)."""
        with self._lock:
            self._buffer.clear()


# Global Singleton Audit Logger
audit_logger = AIAuditLogger()
