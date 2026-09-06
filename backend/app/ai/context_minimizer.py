"""
Privacy Context Minimization Engine.

Extracts minimal bounded code windows (±4 lines) around target static analysis findings
from secret-redacted source code to minimize exposure to external AI providers.
"""

from typing import List, Dict, Any, Optional
from app.schemas.ai import MinimizedContext


SEVERITY_ORDER: Dict[str, int] = {
    "CRITICAL": 4,
    "HIGH": 3,
    "MEDIUM": 2,
    "LOW": 1,
}


def extract_minimized_context(
    sanitized_code: str,
    finding: Dict[str, Any],
    max_window: int = 4
) -> MinimizedContext:
    """
    Extract a minimal bounded snippet around a finding's line number.

    Args:
        sanitized_code: Source code that has already passed through the Secret Redaction Engine.
        finding: Finding dictionary with issue_id, title, severity, line_number.
        max_window: Number of lines to include before and after the finding line.

    Returns:
        MinimizedContext object with line-numbered minimal context.
    """
    lines = sanitized_code.splitlines()
    total_lines = len(lines)

    # 1-indexed target line
    target_line = int(finding.get("line_number", 1) or 1)
    target_line = max(1, min(target_line, total_lines if total_lines > 0 else 1))

    start_line = max(1, target_line - max_window)
    end_line = min(total_lines, target_line + max_window) if total_lines > 0 else 1

    # Extract window with line number annotations
    context_lines = []
    if total_lines > 0:
        for idx in range(start_line, end_line + 1):
            line_content = lines[idx - 1]
            prefix = ">> " if idx == target_line else "   "
            context_lines.append(f"{prefix}{idx:3d} | {line_content}")
    else:
        context_lines.append("   1 | [empty snippet]")

    snippet_text = "\n".join(context_lines)
    has_redactions = "[REDACTED_" in snippet_text

    return MinimizedContext(
        finding_id=str(finding.get("issue_id", "UNKNOWN-001")),
        issue_title=str(finding.get("title", "Security Finding")),
        severity=str(finding.get("severity", "MEDIUM")).upper(),
        line_number=target_line,
        start_line=start_line,
        end_line=end_line,
        context_snippet=snippet_text,
        char_count=len(snippet_text),
        has_redactions=has_redactions,
    )


def minimize_findings_context(
    sanitized_code: str,
    findings: List[Dict[str, Any]],
    max_findings: int = 3,
    max_window: int = 4
) -> List[MinimizedContext]:
    """
    Select top prioritized findings by severity and generate minimized context windows.

    Args:
        sanitized_code: Sanitized source code string.
        findings: List of finding dictionaries.
        max_findings: Maximum number of critical findings to produce context for.
        max_window: Number of context lines before and after.

    Returns:
        List of MinimizedContext objects for top findings.
    """
    if not findings:
        return []

    # Sort by severity descending, then confidence descending
    sorted_findings = sorted(
        findings,
        key=lambda f: (
            SEVERITY_ORDER.get(str(f.get("severity", "LOW")).upper(), 0),
            float(f.get("confidence", 0.5))
        ),
        reverse=True
    )

    selected = sorted_findings[:max_findings]
    return [
        extract_minimized_context(sanitized_code=sanitized_code, finding=f, max_window=max_window)
        for f in selected
    ]
