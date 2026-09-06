"""
Bandit SAST Engine Integration.
Executes Bandit security linting in an isolated transient sandbox and normalizes output into standard findings.
"""

import json
import shutil
import subprocess
import sys
from typing import List
from app.analyzers.base import BaseAnalyzer
from app.schemas.analysis import NormalizedFinding, FindingSeverity, FindingCategory
from app.utils.temp_storage import safe_transient_code_file
from app.utils.logger import logger

# Severity & Confidence Mappings
SEVERITY_MAP = {
    "LOW": FindingSeverity.LOW.value,
    "MEDIUM": FindingSeverity.MEDIUM.value,
    "HIGH": FindingSeverity.HIGH.value,
    "CRITICAL": FindingSeverity.CRITICAL.value,
}

CONFIDENCE_MAP = {
    "LOW": 0.60,
    "MEDIUM": 0.80,
    "HIGH": 0.95,
}


class BanditAnalyzer(BaseAnalyzer):
    """Bandit Static Application Security Testing (SAST) analyzer."""

    analyzer_id = "bandit"
    name = "Bandit Python Security Linter"
    supported_languages = ["python"]

    def analyze(self, code: str, filename: str = "snippet.py") -> List[NormalizedFinding]:
        """Execute Bandit on transient isolated source code and extract findings."""
        if not code or not code.strip():
            return []

        normalized_findings: List[NormalizedFinding] = []

        try:
            with safe_transient_code_file(code, suffix=".py") as temp_file_path:
                # Resolve bandit executable path in current Python environment
                python_exe = sys.executable
                cmd = [
                    python_exe,
                    "-m",
                    "bandit",
                    "-f",
                    "json",
                    "-q",
                    str(temp_file_path)
                ]

                # Run bandit safely with strict timeout
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=10,
                    check=False
                )

                stdout_text = result.stdout.strip()
                if not stdout_text:
                    return []

                try:
                    data = json.loads(stdout_text)
                except json.JSONDecodeError:
                    logger.debug(f"Bandit non-JSON output: {stdout_text[:200]}")
                    return []

                results = data.get("results", [])
                for item in results:
                    test_id = item.get("test_id", "BND-000")
                    test_name = item.get("test_name", "Bandit Security Issue")
                    issue_text = item.get("issue_text", "")
                    raw_sev = item.get("issue_severity", "MEDIUM").upper()
                    raw_conf = item.get("issue_confidence", "MEDIUM").upper()
                    line_no = item.get("line_number", 1)
                    code_snippet = item.get("code", "").strip()
                    more_info = item.get("more_info", "https://bandit.readthedocs.io/")

                    severity = SEVERITY_MAP.get(raw_sev, FindingSeverity.MEDIUM.value)
                    confidence = CONFIDENCE_MAP.get(raw_conf, 0.80)

                    # Compose actionable recommendation
                    recommendation = f"Remediate {test_name} ({test_id}). Refer to Bandit documentation: {more_info}"

                    normalized_findings.append(
                        NormalizedFinding(
                            issue_id=f"BND-{test_id}",
                            title=f"{issue_text} ({test_name})",
                            category=FindingCategory.SECURITY.value,
                            severity=severity,
                            confidence=confidence,
                            file=filename,
                            line_number=line_no,
                            code_snippet=code_snippet or "<code snippet unavailable>",
                            recommendation=recommendation,
                            analyzer=self.analyzer_id
                        )
                    )

        except Exception as exc:
            logger.warning(f"Bandit analyzer execution notice: {exc}")

        return normalized_findings
