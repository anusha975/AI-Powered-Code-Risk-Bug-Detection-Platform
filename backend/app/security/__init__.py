"""
Security & Privacy Module.
Provides secret detection, Shannon entropy scanning, privacy-preserving redaction, user authentication, and security audit logging.
"""

from app.security.entropy import calculate_shannon_entropy, is_high_entropy_token
from app.security.patterns import SECRET_PATTERNS
from app.security.secret_detector import detect_secrets, InternalSecretMatch
from app.security.redactor import redact_code_and_strip_secrets
from app.security.user_store import InMemoryUserStore, user_store
from app.security.audit_logger import SecurityAuditLogger, audit_logger

__all__ = [
    "calculate_shannon_entropy",
    "is_high_entropy_token",
    "SECRET_PATTERNS",
    "detect_secrets",
    "InternalSecretMatch",
    "redact_code_and_strip_secrets",
    "InMemoryUserStore",
    "user_store",
    "SecurityAuditLogger",
    "audit_logger"
]
