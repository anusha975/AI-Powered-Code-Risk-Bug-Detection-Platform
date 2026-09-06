"""
Secure Code Ingestion Service.
Coordinates security validation, sanitization, language detection, integrity hashing,
and transient storage lifecycle with zero code execution.
"""

import hashlib
import uuid
from datetime import datetime, timezone
from typing import Optional

from app.core.security_validator import (
    sanitize_filename,
    check_path_traversal,
    is_binary_data,
    validate_source_code_constraints,
    SecurityValidationError
)
from app.services.language_detector import resolve_language, UnsupportedLanguageError
from app.utils.temp_storage import safe_transient_code_file
from app.schemas.submission import CodeIngestionMetadata
from app.utils.logger import logger


class IngestionService:
    """Core service for safe, zero-execution source code ingestion."""

    @staticmethod
    def process_code_ingestion(
        content: str,
        filename: Optional[str] = None,
        explicit_language: Optional[str] = None
    ) -> CodeIngestionMetadata:
        """
        Safely validate, sanitize, and ingest source code.
        Never executes, imports, or permanently stores the raw source code.
        """
        raw_filename = filename or "snippet.py"

        # 1. Detect and flag path traversal attempts
        has_traversal = check_path_traversal(raw_filename)
        if has_traversal:
            logger.warning(f"Path traversal indicator detected in filename: '{raw_filename}'. Sanitizing safely.")

        # 2. Sanitize filename
        clean_filename = sanitize_filename(raw_filename, default_fallback="snippet.py")

        # 3. Validate content constraints (emptiness, max characters, max size)
        validate_source_code_constraints(content, clean_filename)

        # 4. Check for binary payload injection
        content_bytes = content.encode("utf-8", errors="replace")
        is_binary, binary_reason = is_binary_data(content_bytes)
        if is_binary:
            logger.warning(f"Binary file rejection for '{clean_filename}': {binary_reason}")
            raise SecurityValidationError(f"Invalid source code file: {binary_reason}.")

        # 5. Detect and validate supported programming language
        language = resolve_language(
            filename=clean_filename,
            explicit_language=explicit_language,
            content=content
        )

        # 6. Calculate cryptographic integrity SHA-256 fingerprint
        sha256_hash = hashlib.sha256(content_bytes).hexdigest()

        # 7. Compute code metrics
        raw_lines = content.splitlines()
        line_count = len(raw_lines) if raw_lines else 1
        character_count = len(content)
        size_bytes = len(content_bytes)
        submission_id = str(uuid.uuid4())

        # 8. Test transient storage buffering with automatic deletion
        # This confirms file IO and transient isolation work without persistent leaks
        with safe_transient_code_file(content, suffix=f".{language}") as temp_path:
            # Code is buffered in temp_path for future static analyzer pass (Module 3)
            pass

        logger.info(
            f"Code submission ingested successfully | ID: {submission_id} | "
            f"File: {clean_filename} | Lang: {language} | Lines: {line_count} | Size: {size_bytes}B"
        )

        return CodeIngestionMetadata(
            submission_id=submission_id,
            filename=raw_filename,
            sanitized_filename=clean_filename,
            language=language,
            line_count=line_count,
            character_count=character_count,
            size_bytes=size_bytes,
            sha256_hash=sha256_hash,
            status="ACCEPTED",
            message="Source code safely ingested and validated. Zero code executed.",
            created_at=datetime.now(timezone.utc).isoformat()
        )


ingestion_service = IngestionService()
