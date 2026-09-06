"""
Risk Scoring Service.

Coordinates static findings compilation, secret scanning integration,
feature extraction, and Scikit-learn ML inference to produce explainable risk assessments.
"""

from typing import Optional, List, Dict, Any
import uuid

from app.core.security_validator import sanitize_filename, validate_source_code_constraints
from app.services.language_detector import resolve_language
from app.services.analysis_service import AnalysisService
from app.services.security_service import SecurityService
from app.schemas.risk import RiskScoreRequest, RiskScoreResponse
from app.ml.inference import infer_risk_score
from app.utils.logger import logger


class RiskService:
    """Service to evaluate code risk scores and generate explainability breakdowns."""

    @staticmethod
    def calculate_risk(
        content: str,
        filename: Optional[str] = None,
        explicit_language: Optional[str] = None,
        provided_findings: Optional[List[Dict[str, Any]]] = None,
        provided_secrets_count: Optional[int] = None
    ) -> RiskScoreResponse:
        """
        Evaluate full risk score for given source code.
        If findings/secrets are not explicitly provided, runs local AST/SAST analysis
        and secret scanner automatically.
        """
        raw_filename = filename or "snippet.py"
        clean_filename = sanitize_filename(raw_filename, default_fallback="snippet.py")

        # 1. Validate constraints
        validate_source_code_constraints(content, clean_filename)

        # 2. Resolve language
        language = resolve_language(
            filename=clean_filename,
            explicit_language=explicit_language,
            content=content
        )

        # 3. Determine findings
        if provided_findings is not None:
            findings = [
                f if isinstance(f, dict) else f.model_dump()
                for f in provided_findings
            ]
        else:
            analysis_result = AnalysisService.analyze_code(
                content=content,
                filename=clean_filename,
                explicit_language=language
            )
            findings = [f.model_dump() for f in analysis_result.findings]

        # 4. Determine secrets count
        if provided_secrets_count is not None:
            secrets_count = provided_secrets_count
        else:
            security_result = SecurityService.scan_and_redact(
                content=content,
                filename=clean_filename,
                explicit_language=language
            )
            secrets_count = security_result.secrets_detected_count

        # 5. Run Risk Scoring Inference (Deterministic + Scikit-learn ML)
        response = infer_risk_score(
            content=content,
            findings=findings,
            language=language,
            secrets_count=secrets_count,
            filename=clean_filename
        )

        logger.info(
            f"Risk scoring completed | File: {clean_filename} | "
            f"Score: {response.risk_score} | Level: {response.risk_level} | "
            f"Findings: {len(findings)} | Secrets: {secrets_count}"
        )

        return response
