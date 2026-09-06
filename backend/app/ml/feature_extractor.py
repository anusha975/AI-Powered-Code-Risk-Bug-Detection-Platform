"""
Feature Extraction Engine for Code Risk Scoring.

Extracts normalized 16-dimensional numeric feature vectors from source code
and static analysis findings for machine learning ingestion and baseline scoring.
"""

from typing import List, Dict, Any, Optional
import ast
import re

FEATURE_NAMES: List[str] = [
    "critical_findings_count",
    "high_findings_count",
    "medium_findings_count",
    "low_findings_count",
    "security_category_count",
    "complexity_category_count",
    "error_handling_category_count",
    "style_category_count",
    "ast_analyzer_findings",
    "bandit_analyzer_findings",
    "max_finding_confidence",
    "avg_finding_confidence",
    "cyclomatic_complexity",
    "max_nesting_depth",
    "finding_density_per_100_lines",
    "has_secrets_flag",
]


class CodeMetricsVisitor(ast.NodeVisitor):
    """AST visitor to compute structural complexity and nesting depth."""

    def __init__(self) -> None:
        self.complexity: int = 1
        self.max_depth: int = 0
        self._current_depth: int = 0

    def _enter_block(self) -> None:
        self._current_depth += 1
        if self._current_depth > self.max_depth:
            self.max_depth = self._current_depth

    def _exit_block(self) -> None:
        self._current_depth = max(0, self._current_depth - 1)

    def visit_If(self, node: ast.If) -> None:
        self.complexity += 1
        self._enter_block()
        self.generic_visit(node)
        self._exit_block()

    def visit_For(self, node: ast.For) -> None:
        self.complexity += 1
        self._enter_block()
        self.generic_visit(node)
        self._exit_block()

    def visit_AsyncFor(self, node: ast.AsyncFor) -> None:
        self.complexity += 1
        self._enter_block()
        self.generic_visit(node)
        self._exit_block()

    def visit_While(self, node: ast.While) -> None:
        self.complexity += 1
        self._enter_block()
        self.generic_visit(node)
        self._exit_block()

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:
        self.complexity += 1
        self._enter_block()
        self.generic_visit(node)
        self._exit_block()

    def visit_With(self, node: ast.With) -> None:
        self._enter_block()
        self.generic_visit(node)
        self._exit_block()

    def visit_AsyncWith(self, node: ast.AsyncWith) -> None:
        self._enter_block()
        self.generic_visit(node)
        self._exit_block()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._enter_block()
        self.generic_visit(node)
        self._exit_block()

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._enter_block()
        self.generic_visit(node)
        self._exit_block()

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self._enter_block()
        self.generic_visit(node)
        self._exit_block()

    def visit_BoolOp(self, node: ast.BoolOp) -> None:
        self.complexity += max(0, len(node.values) - 1)
        self.generic_visit(node)


def extract_features(
    content: str,
    findings: List[Dict[str, Any]],
    secrets_count: int = 0
) -> Dict[str, float]:
    """
    Extract a dictionary of 16 numerical features from source code and static analysis findings.

    Args:
        content: Raw source code string.
        findings: List of finding dicts with severity, category, confidence, analyzer.
        secrets_count: Number of secrets detected by secret scanner.

    Returns:
        Dictionary mapping feature name to float value.
    """
    total_lines = max(1, len([line for line in content.splitlines() if line.strip()]))

    # Severities
    crit_count = sum(1 for f in findings if str(f.get("severity", "")).upper() == "CRITICAL")
    high_count = sum(1 for f in findings if str(f.get("severity", "")).upper() == "HIGH")
    med_count = sum(1 for f in findings if str(f.get("severity", "")).upper() == "MEDIUM")
    low_count = sum(1 for f in findings if str(f.get("severity", "")).upper() == "LOW")

    # Categories
    sec_count = sum(1 for f in findings if str(f.get("category", "")).upper() in ("SECURITY", "VULNERABILITY"))
    comp_count = sum(1 for f in findings if str(f.get("category", "")).upper() in ("COMPLEXITY", "MAINTAINABILITY"))
    err_count = sum(1 for f in findings if str(f.get("category", "")).upper() in ("ERROR_HANDLING", "EXCEPTION"))
    style_count = sum(1 for f in findings if str(f.get("category", "")).upper() in ("STYLE", "CONFIG", "QUALITY"))

    # Analyzers
    ast_count = sum(1 for f in findings if str(f.get("analyzer", "")).lower() == "ast")
    bandit_count = sum(1 for f in findings if str(f.get("analyzer", "")).lower() == "bandit")

    # Confidences
    confidences = [float(f.get("confidence", 0.5)) for f in findings]
    max_conf = max(confidences) if confidences else 0.0
    avg_conf = sum(confidences) / len(confidences) if confidences else 0.0

    # AST Metrics
    cyclomatic = 1.0
    nesting_depth = 0.0
    try:
        parsed_tree = ast.parse(content)
        visitor = CodeMetricsVisitor()
        visitor.visit(parsed_tree)
        cyclomatic = float(visitor.complexity)
        nesting_depth = float(visitor.max_depth)
    except Exception:
        # Fallback heuristic for non-Python or syntax-error code
        for line in content.splitlines():
            indent = len(line) - len(line.lstrip())
            depth = indent // 4
            if depth > nesting_depth:
                nesting_depth = float(depth)
        branching_keywords = len(re.findall(r"\b(if|elif|else|for|while|try|catch|except|switch|case)\b", content))
        cyclomatic = float(max(1, branching_keywords + 1))

    # Finding density
    total_findings = len(findings)
    density = (float(total_findings) / float(total_lines)) * 100.0

    # Secrets flag
    has_secrets = 1.0 if (secrets_count > 0 or any("SECRET" in str(f.get("title", "")).upper() for f in findings)) else 0.0

    features: Dict[str, float] = {
        "critical_findings_count": float(crit_count),
        "high_findings_count": float(high_count),
        "medium_findings_count": float(med_count),
        "low_findings_count": float(low_count),
        "security_category_count": float(sec_count),
        "complexity_category_count": float(comp_count),
        "error_handling_category_count": float(err_count),
        "style_category_count": float(style_count),
        "ast_analyzer_findings": float(ast_count),
        "bandit_analyzer_findings": float(bandit_count),
        "max_finding_confidence": round(max_conf, 4),
        "avg_finding_confidence": round(avg_conf, 4),
        "cyclomatic_complexity": round(cyclomatic, 2),
        "max_nesting_depth": round(nesting_depth, 2),
        "finding_density_per_100_lines": round(density, 2),
        "has_secrets_flag": has_secrets,
    }

    return features


def feature_dict_to_vector(features: Dict[str, float]) -> List[float]:
    """Convert feature dictionary to an ordered numeric list matching FEATURE_NAMES."""
    return [float(features.get(name, 0.0)) for name in FEATURE_NAMES]
