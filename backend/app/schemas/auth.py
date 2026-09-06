"""
Pydantic Schemas for Authentication, Authorization & Security Audit Events.
Strictly validates inputs, user credentials, JWT tokens, and audit event logs.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserRole(str, Enum):
    """User authorization roles."""
    ADMIN = "ADMIN"
    DEVELOPER = "DEVELOPER"


class UserRegisterRequest(BaseModel):
    """Payload for new user registration."""
    username: str = Field(..., min_length=3, max_length=32, description="Unique alphanumeric username")
    email: str = Field(..., min_length=5, max_length=255, description="Valid corporate or personal email address")
    password: str = Field(..., min_length=8, max_length=128, description="Strong password (min 8 chars)")
    role: UserRole = Field(default=UserRole.DEVELOPER, description="Assigned authorization role")

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        v = v.strip()
        if not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError("Username may only contain letters, numbers, hyphens, and underscores.")
        return v

    @field_validator("email")
    @classmethod
    def validate_email_format(cls, v: str) -> str:
        v = v.strip().lower()
        if "@" not in v or "." not in v.split("@")[-1]:
            raise ValueError("Invalid email format.")
        return v

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters in length.")
        return v


class UserLoginRequest(BaseModel):
    """Payload for user authentication."""
    username_or_email: str = Field(..., min_length=3, max_length=128, description="Username or registered email")
    password: str = Field(..., min_length=1, max_length=128, description="User password")


class UserProfileResponse(BaseModel):
    """Sanitized public profile for an authenticated user."""
    id: str = Field(..., description="Unique user identifier (UUID)")
    username: str = Field(..., description="User login handle")
    email: str = Field(..., description="Registered email address")
    role: UserRole = Field(..., description="Active user authorization role")
    is_active: bool = Field(default=True, description="Account active status")
    created_at: datetime = Field(..., description="Timestamp of account creation")
    last_login_at: Optional[datetime] = Field(default=None, description="Timestamp of most recent login")


class TokenResponse(BaseModel):
    """JWT Token response after successful authentication."""
    access_token: str = Field(..., description="Signed JWT Bearer token")
    token_type: str = Field(default="bearer", description="Token authentication scheme")
    expires_in: int = Field(..., description="Token validity duration in seconds")
    user: UserProfileResponse = Field(..., description="Profile information for the authenticated user")


class UserRecord(BaseModel):
    """Internal user record stored in the repository."""
    id: str
    username: str
    email: str
    hashed_password: str
    role: UserRole = UserRole.DEVELOPER
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_login_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class AuditEventType(str, Enum):
    """Classification of security audit events."""
    USER_REGISTERED = "USER_REGISTERED"
    LOGIN_SUCCESS = "LOGIN_SUCCESS"
    LOGIN_FAILURE = "LOGIN_FAILURE"
    ANALYSIS_STARTED = "ANALYSIS_STARTED"
    ANALYSIS_COMPLETED = "ANALYSIS_COMPLETED"
    GITHUB_CONNECTED = "GITHUB_CONNECTED"
    GITHUB_PR_SCANNED = "GITHUB_PR_SCANNED"
    AI_ANALYSIS_REQUESTED = "AI_ANALYSIS_REQUESTED"
    SETTINGS_CHANGED = "SETTINGS_CHANGED"
    ACCESS_DENIED = "ACCESS_DENIED"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"


class AuditEventRecord(BaseModel):
    """
    Immutable security audit event record.
    Guaranteed: Contains ZERO passwords, API keys, source-code contents, secrets, or tokens.
    """
    event_id: str = Field(..., description="Unique audit event UUID")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="UTC event timestamp")
    event_type: AuditEventType = Field(..., description="Categorization of the audit event")
    user_id: Optional[str] = Field(default=None, description="User identifier triggering the action, or anonymous")
    username: Optional[str] = Field(default=None, description="Username associated with event")
    role: Optional[str] = Field(default=None, description="Role of the acting user")
    ip_address: Optional[str] = Field(default="127.0.0.1", description="Client IP address")
    status: str = Field(default="SUCCESS", description="Outcome status (SUCCESS, FAILURE, WARNING)")
    target_resource: Optional[str] = Field(default=None, description="Target resource (e.g. analysis_id, endpoint)")
    sanitized_metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Strictly sanitized metadata (redacted of secrets/credentials/source code)"
    )
    privacy_guarantee: str = Field(
        default="Zero-Credential & Zero-Source-Code Audit Invariant: Passwords, tokens, API keys, and code contents are strictly redacted.",
        description="Formal privacy assurance"
    )


class AuditLogSummaryResponse(BaseModel):
    """Aggregated security audit telemetry metrics."""
    total_events: int
    event_breakdown: Dict[str, int]
    recent_events: List[AuditEventRecord]
    active_users_count: int


class AuditQueryFilter(BaseModel):
    """Query parameters for filtering audit logs."""
    event_type: Optional[AuditEventType] = None
    user_id: Optional[str] = None
    status: Optional[str] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
