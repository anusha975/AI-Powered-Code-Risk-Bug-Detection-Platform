"""
Multi-Pass Secret Detection Engine.
Combines regex signature scanning and Shannon entropy calculation to locate secrets.
"""

from dataclasses import dataclass
from typing import List, Tuple
from app.security.patterns import SECRET_PATTERNS, SecretPattern
from app.security.entropy import find_high_entropy_strings


@dataclass
class InternalSecretMatch:
    """Internal representation of a detected secret span."""
    secret_type: str
    start: int
    end: int
    line_number: int
    confidence: str
    placeholder: str
    secret_raw: str  # Kept strictly internal for span replacement; stripped before API output


def calculate_line_number(code: str, char_offset: int) -> int:
    """Compute 1-indexed line number from character offset."""
    return code.count("\n", 0, char_offset) + 1


def detect_secrets(code: str, filename: str = "snippet.py") -> List[InternalSecretMatch]:
    """
    Execute multi-pass secret detection on source code.
    Pass 1: Curated regex signature matching (AWS, JWT, DB, Private Keys, SaaS tokens)
    Pass 2: Shannon entropy analysis on string literals
    Pass 3: Conflict resolution and span deduplication
    """
    if not code:
        return []

    raw_matches: List[InternalSecretMatch] = []
    claimed_spans: List[Tuple[int, int]] = []

    # =========================================================================
    # Pass 1: Curated Pattern Scanning
    # =========================================================================
    for secret_rule in SECRET_PATTERNS:
        for match in secret_rule.pattern.finditer(code):
            group_idx = secret_rule.group_index
            start = match.start(group_idx)
            end = match.end(group_idx)
            secret_value = match.group(group_idx)

            if start >= end or not secret_value.strip():
                continue

            # Check if this exact span or overlapping span is already captured
            is_overlapping = any(
                not (end <= c_start or start >= c_end)
                for c_start, c_end in claimed_spans
            )

            if not is_overlapping:
                claimed_spans.append((start, end))
                line_no = calculate_line_number(code, start)
                raw_matches.append(
                    InternalSecretMatch(
                        secret_type=secret_rule.secret_type,
                        start=start,
                        end=end,
                        line_number=line_no,
                        confidence=secret_rule.confidence,
                        placeholder=secret_rule.placeholder,
                        secret_raw=secret_value
                    )
                )

    # =========================================================================
    # Pass 2: Shannon Entropy Analysis on String Literals
    # =========================================================================
    entropy_matches = find_high_entropy_strings(code, threshold=3.8, min_length=16)
    for start, end, secret_value, score in entropy_matches:
        is_overlapping = any(
            not (end <= c_start or start >= c_end)
            for c_start, c_end in claimed_spans
        )

        if not is_overlapping:
            claimed_spans.append((start, end))
            line_no = calculate_line_number(code, start)
            confidence = "HIGH" if score >= 4.2 else "MEDIUM"
            raw_matches.append(
                InternalSecretMatch(
                    secret_type="HIGH_ENTROPY_KEY",
                    start=start,
                    end=end,
                    line_number=line_no,
                    confidence=confidence,
                    placeholder="[REDACTED_HIGH_ENTROPY_KEY]",
                    secret_raw=secret_value
                )
            )

    # Sort matches by start offset ascending
    raw_matches.sort(key=lambda m: m.start)
    return raw_matches
