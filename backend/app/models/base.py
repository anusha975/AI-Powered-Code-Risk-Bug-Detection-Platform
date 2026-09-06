"""
Base ORM Model and Initial Audit Log Schema.
Stores scan execution logs and audit records without storing sensitive raw source code.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON
from app.database.base import Base


class SystemAuditLog(Base):
    """
    Audit log tracking system operations, analyzer runs, and health events.
    Never stores unredacted source code.
    """
    __tablename__ = "system_audit_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    event_type = Column(String(50), nullable=False, index=True)
    status = Column(String(30), nullable=False, default="SUCCESS")
    details = Column(JSON, nullable=True)
    message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    def __repr__(self) -> str:
        return f"<SystemAuditLog(id={self.id}, event_type='{self.event_type}', status='{self.status}')>"
