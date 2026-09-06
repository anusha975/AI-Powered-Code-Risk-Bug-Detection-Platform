"""
Language Detection & Extension Normalization Service.
Validates supported source code languages and maps file extensions safely.
"""

import os
import re
from typing import Optional
from app.core.constants import SupportedLanguage

# Extension-to-Language Mapping
EXTENSION_MAP = {
    # Python
    ".py": SupportedLanguage.PYTHON.value,
    ".pyw": SupportedLanguage.PYTHON.value,
    ".pyi": SupportedLanguage.PYTHON.value,
    
    # Java
    ".java": SupportedLanguage.JAVA.value,
    
    # JavaScript
    ".js": SupportedLanguage.JAVASCRIPT.value,
    ".jsx": SupportedLanguage.JAVASCRIPT.value,
    ".mjs": SupportedLanguage.JAVASCRIPT.value,
    ".cjs": SupportedLanguage.JAVASCRIPT.value,
    
    # TypeScript
    ".ts": SupportedLanguage.TYPESCRIPT.value,
    ".tsx": SupportedLanguage.TYPESCRIPT.value,
    ".mts": SupportedLanguage.TYPESCRIPT.value,
    ".cts": SupportedLanguage.TYPESCRIPT.value,
}

# Inverted Language-to-Primary-Extension Mapping
PRIMARY_EXTENSIONS = {
    SupportedLanguage.PYTHON.value: ".py",
    SupportedLanguage.JAVA.value: ".java",
    SupportedLanguage.JAVASCRIPT.value: ".js",
    SupportedLanguage.TYPESCRIPT.value: ".ts",
}

SUPPORTED_LANGUAGES_SET = {lang.value for lang in SupportedLanguage}


class UnsupportedLanguageError(ValueError):
    """Raised when an unsupported language or extension is submitted."""
    pass


def normalize_language_name(lang_input: Optional[str]) -> Optional[str]:
    """Normalize language aliases (e.g., 'py' -> 'python', 'ts' -> 'typescript')."""
    if not lang_input:
        return None
    
    cleaned = lang_input.strip().lower()
    alias_map = {
        "python": SupportedLanguage.PYTHON.value,
        "py": SupportedLanguage.PYTHON.value,
        "python3": SupportedLanguage.PYTHON.value,
        "java": SupportedLanguage.JAVA.value,
        "javascript": SupportedLanguage.JAVASCRIPT.value,
        "js": SupportedLanguage.JAVASCRIPT.value,
        "node": SupportedLanguage.JAVASCRIPT.value,
        "typescript": SupportedLanguage.TYPESCRIPT.value,
        "ts": SupportedLanguage.TYPESCRIPT.value,
    }
    return alias_map.get(cleaned)


def detect_language_from_content(content: str) -> Optional[str]:
    """Lightweight syntax heuristic fallback for extensionless snippets."""
    if not content:
        return None
    
    # Python indicators
    if re.search(r"^(import\s+\w+|from\s+\w+\s+import|def\s+\w+\s*\(|class\s+\w+.*:)", content, re.MULTILINE):
        return SupportedLanguage.PYTHON.value
    
    # Java indicators
    if re.search(r"(public\s+class\s+\w+|package\s+[\w.]+;|public\s+static\s+void\s+main)", content):
        return SupportedLanguage.JAVA.value
    
    # TypeScript indicators (types, interfaces, generics)
    if re.search(r"(interface\s+\w+\s*\{|type\s+\w+\s*=|:\s*(string|number|boolean|any)\b)", content):
        return SupportedLanguage.TYPESCRIPT.value
    
    # JavaScript indicators
    if re.search(r"(function\s+\w+\s*\(|const\s+\w+\s*=|let\s+\w+\s*=|var\s+\w+\s*=|console\.log\()", content):
        return SupportedLanguage.JAVASCRIPT.value
    
    return None


def resolve_language(
    filename: Optional[str] = None,
    explicit_language: Optional[str] = None,
    content: Optional[str] = None
) -> str:
    """
    Resolve and validate language:
    1. If explicit language is provided, validate it.
    2. Check file extension in filename.
    3. Fall back to content heuristics.
    4. Raise UnsupportedLanguageError if invalid or unsupported.
    """
    # 1. Check explicit language
    normalized_explicit = normalize_language_name(explicit_language)
    if explicit_language and not normalized_explicit:
        raise UnsupportedLanguageError(
            f"Unsupported language '{explicit_language}'. Initially supported: Python, Java, JavaScript, TypeScript."
        )

    # 2. Check filename extension
    ext_language = None
    if filename:
        _, ext = os.path.splitext(filename.lower())
        if ext in EXTENSION_MAP:
            ext_language = EXTENSION_MAP[ext]
        elif ext:
            # An extension was provided, but is not in our supported list
            raise UnsupportedLanguageError(
                f"Unsupported file extension '{ext}'. Initially supported: .py, .java, .js, .jsx, .ts, .tsx."
            )

    # 3. Reconcile explicit vs extension
    if normalized_explicit and ext_language:
        # If both are provided and match or are compatible (e.g. JS & TS)
        return normalized_explicit
    
    if ext_language:
        return ext_language
    
    if normalized_explicit:
        return normalized_explicit

    # 4. Fallback heuristic
    if content:
        heuristic_lang = detect_language_from_content(content)
        if heuristic_lang:
            return heuristic_lang

    # Default to Python if completely ambiguous and no extension
    return SupportedLanguage.PYTHON.value
