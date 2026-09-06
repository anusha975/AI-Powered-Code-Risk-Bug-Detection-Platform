"""
Shannon Entropy Calculator for High-Entropy Secret Detection.
Identifies cryptographic keys, hashes, and pseudo-random credentials in source code.
"""

import math
import re
from typing import List, Tuple
from collections import Counter


def calculate_shannon_entropy(data: str) -> float:
    """
    Compute the Shannon entropy of a string: H(X) = -sum(P(x) * log2(P(x))).
    Higher values (e.g. > 3.8 for alphanumeric) indicate pseudo-random cryptographic keys or hashes.
    """
    if not data:
        return 0.0

    length = len(data)
    counts = Counter(data)
    entropy = 0.0

    for count in counts.values():
        probability = count / length
        entropy -= probability * math.log2(probability)

    return round(entropy, 4)


def is_high_entropy_token(token: str, threshold: float = 3.8, min_length: int = 16) -> bool:
    """
    Determine if a string literal has high entropy indicative of a secret key or token.
    Ignores common whitespace, punctuation, and natural language words.
    """
    if len(token) < min_length:
        return False

    # Ignore strings with spaces (likely natural text or prose)
    if " " in token or "\t" in token or "\n" in token:
        return False

    # Check if string is predominantly alphanumeric or base64 characters
    if not re.match(r"^[A-Za-z0-9+/=_\-\.]+$", token):
        return False

    # Ignore repeated characters or single-character spam
    if len(set(token)) < 8:
        return False

    entropy = calculate_shannon_entropy(token)
    return entropy >= threshold


def find_high_entropy_strings(code: str, threshold: float = 3.8, min_length: int = 16) -> List[Tuple[int, int, str, float]]:
    """
    Scan source code for high-entropy string literals.
    Returns list of (start_index, end_index, secret_content, entropy_score).
    """
    matches = []
    # Match double or single quoted string literals
    string_pattern = re.compile(r"""(?:["'])([^"'\r\n]{16,})(?:["'])""")

    for match in string_pattern.finditer(code):
        literal = match.group(1)
        if is_high_entropy_token(literal, threshold=threshold, min_length=min_length):
            entropy = calculate_shannon_entropy(literal)
            # Store span of the inner literal (without the quotes)
            start_idx = match.start(1)
            end_idx = match.end(1)
            matches.append((start_idx, end_idx, literal, entropy))

    return matches
