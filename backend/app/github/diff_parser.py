"""
GitHub Diff and Patch Parser.

Safely parses unified git diff patches from GitHub Pull Requests,
reconstructing added/modified code blocks and mapping line numbers
without executing or cloning repository code.
"""

import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass


IGNORED_EXTENSIONS = {
    # Binaries & Images
    ".png", ".jpg", ".jpeg", ".gif", ".ico", ".svg", ".webp", ".pdf", ".zip", ".tar", ".gz",
    ".exe", ".dll", ".so", ".dylib", ".jar", ".war", ".pyc", ".class",
    # Lockfiles & Generated metadata
    "package-lock.json", "yarn.lock", "pnpm-lock.yaml", "poetry.lock", "Pipfile.lock",
    "composer.lock", "Gemfile.lock", "Cargo.lock",
    # Minified assets
    ".min.js", ".min.css", ".map"
}

IGNORED_PATH_PREFIXES = (
    ".git/",
    "node_modules/",
    "vendor/",
    "dist/",
    "build/",
    "target/",
    ".idea/",
    ".vscode/",
    "__pycache__/"
)


@dataclass
class ParsedHunkLine:
    """A single line within a unified diff patch hunk."""
    diff_type: str       # '+' (added), '-' (deleted), ' ' (context)
    content: str         # The line text without the leading diff character
    old_line_no: Optional[int]
    new_line_no: Optional[int]


@dataclass
class ParsedDiffPatch:
    """Parsed result of a file patch from a pull request."""
    filename: str
    is_supported_source: bool
    added_lines_count: int
    deleted_lines_count: int
    added_code_content: str      # Consolidated added/modified code for static analysis
    hunk_lines: List[ParsedHunkLine]
    line_number_mapping: Dict[int, int]  # Maps reconstructed line (1-indexed) to actual PR new_line_no


class DiffParser:
    """Parser for GitHub unified diff patches."""

    # Regex to match hunk headers: @@ -old_start,old_count +new_start,new_count @@
    HUNK_HEADER_PATTERN = re.compile(
        r"^@@\s+-(?P<old_start>\d+)(?:,(?P<old_count>\d+))?\s+\+(?P<new_start>\d+)(?:,(?P<new_count>\d+))?\s+@@"
    )

    @classmethod
    def is_ignorable_file(cls, filename: str) -> bool:
        """
        Check if a file should be excluded from security/SAST scanning
        (e.g., binaries, lockfiles, vendor directories).
        """
        lower_name = filename.lower()

        # Check ignored path prefixes
        for prefix in IGNORED_PATH_PREFIXES:
            if lower_name.startswith(prefix) or f"/{prefix}" in lower_name:
                return True

        # Check exact lockfiles or extensions
        base_name = filename.split("/")[-1].lower()
        if base_name in IGNORED_EXTENSIONS:
            return True

        for ext in IGNORED_EXTENSIONS:
            if ext.startswith(".") and lower_name.endswith(ext):
                return True

        return False

    @classmethod
    def parse_patch(cls, filename: str, patch_text: Optional[str]) -> ParsedDiffPatch:
        """
        Parse unified diff patch text into structured hunk lines and extract
        the added/modified code block for security & AST scanning.
        """
        if cls.is_ignorable_file(filename) or not patch_text:
            return ParsedDiffPatch(
                filename=filename,
                is_supported_source=not cls.is_ignorable_file(filename),
                added_lines_count=0,
                deleted_lines_count=0,
                added_code_content="",
                hunk_lines=[],
                line_number_mapping={}
            )

        hunk_lines: List[ParsedHunkLine] = []
        added_lines: List[str] = []
        line_mapping: Dict[int, int] = {}  # synthetic_line -> actual_pr_new_line

        current_old_line = 0
        current_new_line = 0
        added_count = 0
        deleted_count = 0
        synthetic_line_idx = 1

        lines = patch_text.splitlines()

        for line in lines:
            hunk_match = cls.HUNK_HEADER_PATTERN.match(line)
            if hunk_match:
                current_old_line = int(hunk_match.group("old_start"))
                current_new_line = int(hunk_match.group("new_start"))
                continue

            if not line:
                continue

            diff_char = line[0]
            line_content = line[1:] if len(line) > 1 else ""

            if diff_char == "+":
                added_count += 1
                hunk_lines.append(ParsedHunkLine(
                    diff_type="+",
                    content=line_content,
                    old_line_no=None,
                    new_line_no=current_new_line
                ))
                added_lines.append(line_content)
                line_mapping[synthetic_line_idx] = current_new_line
                synthetic_line_idx += 1
                current_new_line += 1

            elif diff_char == "-":
                deleted_count += 1
                hunk_lines.append(ParsedHunkLine(
                    diff_type="-",
                    content=line_content,
                    old_line_no=current_old_line,
                    new_line_no=None
                ))
                current_old_line += 1

            elif diff_char == " ":
                # Context line
                hunk_lines.append(ParsedHunkLine(
                    diff_type=" ",
                    content=line_content,
                    old_line_no=current_old_line,
                    new_line_no=current_new_line
                ))
                # Include context lines in reconstructed code to preserve enclosing blocks
                added_lines.append(line_content)
                line_mapping[synthetic_line_idx] = current_new_line
                synthetic_line_idx += 1
                current_old_line += 1
                current_new_line += 1

            elif diff_char == "\\":
                # '\ No newline at end of file'
                continue

        reconstructed_code = "\n".join(added_lines)

        return ParsedDiffPatch(
            filename=filename,
            is_supported_source=True,
            added_lines_count=added_count,
            deleted_lines_count=deleted_count,
            added_code_content=reconstructed_code,
            hunk_lines=hunk_lines,
            line_number_mapping=line_mapping
        )
