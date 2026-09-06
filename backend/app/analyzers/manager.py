"""
Analyzer Orchestration Manager.
Coordinates execution of AST, Bandit, and future modular analyzers, aggregating and scoring findings.
"""

from typing import List, Dict, Tuple
from app.analyzers.base import BaseAnalyzer
from app.analyzers.ast_visitor import PythonASTAnalyzer
from app.analyzers.bandit_runner import BanditAnalyzer
from app.schemas.analysis import NormalizedFinding, AnalysisSummary, FindingSeverity

# Severity Ranking for Sorting
SEVERITY_ORDER = {
    FindingSeverity.CRITICAL.value: 0,
    FindingSeverity.HIGH.value: 1,
    FindingSeverity.MEDIUM.value: 2,
    FindingSeverity.LOW.value: 3,
}


class AnalysisManager:
    """Manager coordinating multi-analyzer dispatch and result aggregation."""

    def __init__(self):
        self.analyzers: List[BaseAnalyzer] = [
            PythonASTAnalyzer(),
            BanditAnalyzer()
        ]

    def register_analyzer(self, analyzer: BaseAnalyzer) -> None:
        """Register a new analyzer plugin."""
        self.analyzers.append(analyzer)

    def run_analysis(
        self,
        code: str,
        filename: str = "snippet.py",
        language: str = "python"
    ) -> Tuple[AnalysisSummary, List[NormalizedFinding]]:
        """
        Execute all applicable static analyzers for the requested language.
        Normalizes, deduplicates, and scores all findings.
        """
        all_findings: List[NormalizedFinding] = []
        normalized_lang = language.lower()

        for analyzer in self.analyzers:
            if normalized_lang in analyzer.supported_languages:
                try:
                    findings = analyzer.analyze(code=code, filename=filename)
                    all_findings.extend(findings)
                except Exception as exc:
                    # Individual analyzer failures do not bring down the entire platform
                    pass

        # Deduplication & Conflict Resolution
        deduped_findings: List[NormalizedFinding] = []
        seen_keys = set()

        for finding in all_findings:
            # Key based on line number and approximate title/concept to avoid duplicate noise
            dedup_key = (finding.line_number, finding.category, finding.title[:30])
            if dedup_key not in seen_keys:
                seen_keys.add(dedup_key)
                deduped_findings.append(finding)

        # Sort findings by severity (CRITICAL first), then line number ascending
        deduped_findings.sort(
            key=lambda f: (SEVERITY_ORDER.get(f.severity, 99), f.line_number)
        )

        # Compute Summary Statistics
        critical_count = sum(1 for f in deduped_findings if f.severity == FindingSeverity.CRITICAL.value)
        high_count = sum(1 for f in deduped_findings if f.severity == FindingSeverity.HIGH.value)
        medium_count = sum(1 for f in deduped_findings if f.severity == FindingSeverity.MEDIUM.value)
        low_count = sum(1 for f in deduped_findings if f.severity == FindingSeverity.LOW.value)
        total_issues = len(deduped_findings)

        # Calculate composite risk score (0 to 100)
        raw_score = (critical_count * 35.0) + (high_count * 15.0) + (medium_count * 5.0) + (low_count * 1.5)
        risk_score = round(min(100.0, raw_score), 1)

        summary = AnalysisSummary(
            total_issues=total_issues,
            critical_count=critical_count,
            high_count=high_count,
            medium_count=medium_count,
            low_count=low_count,
            risk_score=risk_score
        )

        return summary, deduped_findings


analysis_manager = AnalysisManager()
