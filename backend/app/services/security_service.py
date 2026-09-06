"""
Security & Privacy Protection Service.
Coordinates secret scanning, zero-leak placeholder substitution, and metadata generation.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional

from app.core.security_validator import sanitize_filename, validate_source_code_constraints
from app.security.secret_detector import detect_secrets
from app.security.redactor import redact_code_and_strip_secrets
from app.schemas.security import SecurityScanResponse, SecretFinding
from app.utils.logger import logger


class SecurityService:
    """Service to scan source code for sensitive credentials and apply redaction."""

    @staticmethod
    def scan_and_redact(
        content: str,
        filename: Optional[str] = None,
        explicit_language: Optional[str] = None
    ) -> SecurityScanResponse:
        """
        Execute the Privacy Sanitization Pipeline:
        Source Code -> Secret Detection -> Placeholder Redaction -> Sanitized Code
        """
        raw_filename = filename or "snippet.py"
        clean_filename = sanitize_filename(raw_filename, default_fallback="snippet.py")

        # 1. Validate constraints
        validate_source_code_constraints(content, clean_filename)

        # 2. Detect Secrets
        matches = detect_secrets(code=content, filename=clean_filename)

        # 3. Redact Secrets & Strip Raw Values
        sanitized_code, public_findings = redact_code_and_strip_secrets(
            code=content,
            filename=clean_filename,
            matches=matches
        )

        scan_id = str(uuid.uuid4())
        secrets_count = len(public_findings)
        redaction_applied = secrets_count > 0

        logger.info(
            f"Security scan completed | Scan ID: {scan_id} | "
            f"File: {clean_filename} | Secrets Detected & Redacted: {secrets_count}"
        )

        return SecurityScanResponse(
            scan_id=scan_id,
            filename=clean_filename,
            secrets_detected_count=secrets_count,
            findings=[SecretFinding(**f) for f in public_findings],
            sanitized_content=sanitized_code,
            redaction_applied=redaction_applied,
            scanned_at=datetime.now(timezone.utc).isoformat()
        )


security_service = SecurityService()
