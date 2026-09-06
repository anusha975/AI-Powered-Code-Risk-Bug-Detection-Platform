"""
Redaction & Privacy Sanitization Pipeline.
Performs deterministic in-place replacement of detected secrets with standardized placeholders.
Guarantees that raw secret values never escape the security layer.
"""

from typing import List, Tuple, Dict, Any
from app.security.secret_detector import InternalSecretMatch


def redact_code_and_strip_secrets(
    code: str,
    filename: str,
    matches: List[InternalSecretMatch]
) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Apply redacting replacements to source code and produce sanitized finding metadata.
    
    1. Replaces secret occurrences with placeholder tags from right-to-left.
    2. Builds public finding records that completely omit the secret value.
    3. Runs post-redaction assertion verifying zero leakage of detected secrets.
    """
    if not matches:
        return code, []

    # Sort matches descending by start position to safely replace in-place without index drifting
    sorted_matches = sorted(matches, key=lambda m: m.start, reverse=True)
    sanitized_code = code

    # Public finding list (safe for API response, logs, and database)
    public_findings: List[Dict[str, Any]] = []

    for match in sorted_matches:
        # Perform replacement
        prefix = sanitized_code[:match.start]
        suffix = sanitized_code[match.end:]
        sanitized_code = f"{prefix}{match.placeholder}{suffix}"

        # Build clean finding descriptor WITHOUT raw secret
        public_findings.append({
            "secret_type": match.secret_type,
            "file": filename,
            "line_number": match.line_number,
            "confidence": match.confidence,
            "redaction_status": "REDACTED",
            "placeholder": match.placeholder
        })

    # Reverse back to ascending order for natural reading in response
    public_findings.reverse()

    # Absolute Security Validation: Assert that none of the captured secrets linger in the sanitized code
    for match in matches:
        if match.secret_raw and match.secret_raw in sanitized_code:
            # If standard replacement didn't wipe an edge case, apply brute string replacement
            sanitized_code = sanitized_code.replace(match.secret_raw, match.placeholder)

    return sanitized_code, public_findings
