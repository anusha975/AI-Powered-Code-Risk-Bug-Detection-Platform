"""
Security Validator & Sanitization Utilities.
Protects against path traversal, malicious filenames, binary injection, and oversized payloads.
"""

import os
import re
from typing import Tuple
from app.core.config import settings

# Windows Reserved Device Names (case-insensitive)
WINDOWS_RESERVED_NAMES = {
    "CON", "PRN", "AUX", "NUL",
    "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9",
    "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9"
}

# Known Binary / Executable Magic Signatures
BINARY_MAGIC_SIGNATURES = [
    b"\x7fELF",                # Linux ELF binary
    b"MZ",                      # Windows PE/DOS executable / DLL
    b"\xca\xfe\xba\xbe",        # Mach-O / Java bytecode class
    b"\xce\xfa\xed\xfe",        # Mach-O 32-bit
    b"\xcf\xfa\xed\xfe",        # Mach-O 64-bit
    b"PK\x03\x04",              # ZIP / JAR archive
    b"\x1f\x8b",                # GZIP archive
    b"7z\xbc\xaf\x27\x1c",      # 7-Zip archive
    b"Rar!\x1a\x07",            # RAR archive
    b"%PDF-",                   # PDF document
    b"\x89PNG\r\n\x1a\n",       # PNG image
    b"GIF87a", b"GIF89a",       # GIF image
    b"\xff\xd8\xff"             # JPEG image
]


class SecurityValidationError(ValueError):
    """Raised when an ingestion security constraint is violated."""
    pass


def check_path_traversal(raw_filename: str) -> bool:
    """
    Check if the input filename contains directory traversal indicators.
    Returns True if malicious traversal patterns are detected.
    """
    if not raw_filename:
        return False
    
    # Check for null bytes or URL encoded variations
    if "\x00" in raw_filename or "%00" in raw_filename.lower():
        return True
    
    # Check for relative directory navigation
    if ".." in raw_filename or "%2e%2e" in raw_filename.lower():
        return True
    
    # Check for slash or backslash separators in the basename
    if "/" in raw_filename or "\\" in raw_filename or "%2f" in raw_filename.lower() or "%5c" in raw_filename.lower():
        return True
        
    return False


def sanitize_filename(raw_filename: str, default_fallback: str = "snippet.py") -> str:
    """
    Sanitizes an untrusted filename:
    - Strips path components
    - Removes null bytes and control characters
    - Validates against Windows device names
    - Enforces safe character set [a-zA-Z0-9_.-]
    """
    if not raw_filename or not raw_filename.strip():
        return default_fallback

    # Extract base name only (strip any directory structure)
    cleaned = os.path.basename(raw_filename.replace("\\", "/"))
    
    # Remove null bytes and non-printable characters
    cleaned = re.sub(r"[\x00-\x1f\x7f-\x9f]", "", cleaned).strip()

    # Split name and extension
    name_part, ext_part = os.path.splitext(cleaned)

    # Check for Windows reserved names (e.g. CON, PRN, AUX.py)
    if name_part.upper() in WINDOWS_RESERVED_NAMES:
        name_part = f"safe_{name_part.lower()}"

    # Replace invalid/unsafe characters with underscores
    name_part = re.sub(r"[^a-zA-Z0-9_\-]", "_", name_part)
    
    # Sanitize extension (only allow alphanumeric + dot)
    ext_part = re.sub(r"[^a-zA-Z0-9.]", "", ext_part)

    # If name became empty, assign safe base
    if not name_part or name_part == "_" or name_part.startswith("."):
        name_part = "ingested_code"

    result = f"{name_part}{ext_part}"
    return result if result else default_fallback


def is_binary_data(data: bytes) -> Tuple[bool, str]:
    """
    Determine whether raw byte data is a binary file rather than source code.
    Returns (is_binary: bool, reason: str).
    """
    if not data:
        return False, "Empty data"

    # 1. Check against binary header magic bytes
    for signature in BINARY_MAGIC_SIGNATURES:
        if data.startswith(signature):
            return True, f"Detected binary executable/archive header signature ({signature[:4]!r})"

    # 2. Check for null bytes in initial sample (source code must never contain null bytes)
    sample = data[:4096]
    if b"\x00" in sample:
        return True, "Detected null bytes (\x00), which indicates compiled/binary content"

    # 3. Check for high ratio of non-printable control characters
    # Printable ASCII range: 32-126 + standard whitespace (9=tab, 10=LF, 13=CR)
    control_chars = [b for b in sample if b < 9 or (b > 13 and b < 32)]
    if control_chars and (len(control_chars) / len(sample)) > 0.15:
        return True, "Content exceeds control-character threshold (probable binary payload)"

    return False, "Valid text content"


def validate_source_code_constraints(content: str, filename: str) -> None:
    """
    Validate size, length, and non-emptiness constraints.
    Raises SecurityValidationError on violation.
    """
    if not content or not content.strip():
        raise SecurityValidationError("Source code content cannot be empty or purely whitespace.")

    char_count = len(content)
    if char_count > settings.MAX_CODE_LENGTH_CHARS:
        raise SecurityValidationError(
            f"Source code exceeds maximum allowed length ({char_count:,} characters > {settings.MAX_CODE_LENGTH_CHARS:,} limit)."
        )

    byte_size = len(content.encode("utf-8"))
    if byte_size > settings.MAX_FILE_SIZE_BYTES:
        raise SecurityValidationError(
            f"Source code exceeds maximum allowed size ({byte_size:,} bytes > {settings.MAX_FILE_SIZE_BYTES:,} bytes limit)."
        )
