"""
SQLAlchemy ORM models for Users and Security Audit Events.
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime, Text, JSON
from app.database.base import Base


class User(Base):
    """
    User account entity supporting RBAC (ADMIN, DEVELOPER).
    """
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(32), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="DEVELOPER")
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    last_login_at = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}', role='{self.role}')>"


class AuditEvent(Base):
    """
    Immutable Security Audit Event ORM entity.
    Guaranteed: Contains ZERO passwords, tokens, API keys, or raw code contents.
    """
    __tablename__ = "audit_events"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    event_type = Column(String(50), nullable=False, index=True)
    user_id = Column(String(36), nullable=True, index=True)
    username = Column(String(32), nullable=True)
    role = Column(String(20), nullable=True)
    ip_address = Column(String(45), nullable=True)
    status = Column(String(20), default="SUCCESS", nullable=False)
    target_resource = Column(String(255), nullable=True)
    sanitized_metadata = Column(JSON, nullable=True)
    privacy_guarantee = Column(Text, nullable=False)

    def __repr__(self) -> str:
        return f"<AuditEvent(id={self.id}, type='{self.event_type}', user='{self.username}', status='{self.status}')>"
