"""
Developer Explanation and Remediation Orchestration Service.

Anchors AI explanations strictly to authoritative local static analysis findings,
enforcing tripartite epistemic separation (DETECTED FACT, AI INTERPRETATION, RECOMMENDATION)
and protecting against hallucinated vulnerabilities.
"""

from typing import Optional, List, Dict, Any
import uuid

from app.core.security_validator import sanitize_filename, validate_source_code_constraints
from app.services.language_detector import resolve_language
from app.services.security_service import SecurityService
from app.services.analysis_service import AnalysisService
from app.services.risk_service import RiskService
from app.ai.context_minimizer import extract_minimized_context, SEVERITY_ORDER
from app.ai.providers import get_llm_provider
from app.ai.response_validator import validate_and_parse_llm_response
from app.schemas.remediation import (
    DeveloperRemediation,
    RemediationResponse
)
from app.core.config import settings
from app.utils.logger import logger


class RemediationService:
    """Coordinates the generation of tripartite developer remediation explanations."""

    @staticmethod
    async def generate_developer_remediations(
        content: str,
        filename: Optional[str] = None,
        explicit_language: Optional[str] = None,
        max_explanations: int = 3,
        provider_override: Optional[str] = None
    ) -> RemediationResponse:
        """
        Execute full tripartite explanation pipeline:
        1. Validate constraints & sanitize filename.
        2. Detect & redact secrets.
        3. Authoritative local static code analysis (AST/Bandit).
        4. Code risk score calculation.
        5. Context minimization for top findings.
        6. Query LLM provider for contextual interpretation & safe replacement code.
        7. Validate and sanitize responses against hallucination & non-execution safety.
        """
        raw_filename = filename or "snippet.py"
        clean_filename = sanitize_filename(raw_filename, default_fallback="snippet.py")

        # 1. Validation
        validate_source_code_constraints(content, clean_filename)

        # 2. Language Detection
        language = resolve_language(
            filename=clean_filename,
            explicit_language=explicit_language,
            content=content
        )

        analysis_id = str(uuid.uuid4())

        # 3. Secret Detection & Redaction (Module 3)
        security_scan = SecurityService.scan_and_redact(
            content=content,
            filename=clean_filename,
            explicit_language=language
        )
        sanitized_code = security_scan.sanitized_content
        secrets_count = security_scan.secrets_detected_count

        # 4. Local Static Code Analysis (Module 4) - Authoritative Truth
        analysis_result = AnalysisService.analyze_code(
            content=sanitized_code,
            filename=clean_filename,
            explicit_language=language
        )
        findings = analysis_result.findings
        findings_dicts = [f.model_dump() for f in findings]

        # 5. Risk Scoring (Module 5)
        risk_result = RiskService.calculate_risk(
            content=sanitized_code,
            filename=clean_filename,
            explicit_language=language,
            provided_findings=findings_dicts,
            provided_secrets_count=secrets_count
        )

        # 6. Check for clean code
        if not findings_dicts:
            return RemediationResponse(
                analysis_id=analysis_id,
                filename=clean_filename,
                language=language,
                risk_score=risk_result.risk_score,
                risk_level=risk_result.risk_level,
                total_findings_count=0,
                secrets_detected_count=secrets_count,
                remediations=[],
                summary_message="Clean code profile: Local AST visitors and Bandit SAST detected zero vulnerabilities."
            )

        # 7. Select Top Findings sorted by severity
        sorted_findings = sorted(
            findings_dicts,
            key=lambda f: (
                SEVERITY_ORDER.get(str(f.get("severity", "LOW")).upper(), 0),
                float(f.get("confidence", 0.5))
            ),
            reverse=True
        )
        selected_findings = sorted_findings[:max_explanations]

        provider = get_llm_provider(provider_override)
        remediations: List[DeveloperRemediation] = []

        # 8. Generate Tripartite Explanations
        for f in selected_findings:
            ctx = extract_minimized_context(
                sanitized_code=sanitized_code,
                finding=f,
                max_window=settings.LLM_MAX_CONTEXT_LINES // 2
            )

            try:
                raw_llm_output = await provider.generate_remediation_json(ctx, f)
            except Exception as exc:
                logger.warning(f"Provider failed for finding {f.get('issue_id')}: {exc}. Using heuristic fallback.")
                raw_llm_output = {
                    "developer_explanation": f"Static analysis flagged {f.get('title')} at line {f.get('line_number')}.",
                    "why_it_matters": "Violates secure coding best practices.",
                    "potential_impact": "May introduce security vulnerabilities or runtime regressions.",
                    "recommended_remediation": f.get("recommendation", "Review and sanitize inputs."),
                    "safer_code_example": None,
                    "confidence_statement": "Fallback explanation generated due to provider communication issue."
                }

            # 9. Strict Validation, Sanitization, and Epistemic Separation
            remediation = validate_and_parse_llm_response(
                raw_response=raw_llm_output,
                finding=f,
                context_snippet=ctx.context_snippet,
                confidence_threshold=0.40,
                model_name=provider.model_name,
                provider_name=provider.provider_name
            )
            remediations.append(remediation)

        summary_msg = (
            f"Generated {len(remediations)} tripartite developer remediation explanation(s) "
            f"for {clean_filename} with Risk Score {risk_result.risk_score} ({risk_result.risk_level.value})."
        )

        logger.info(
            f"Remediation Engine completed | ID: {analysis_id} | File: {clean_filename} | "
            f"Findings: {len(findings)} | Explanations: {len(remediations)}"
        )

        return RemediationResponse(
            analysis_id=analysis_id,
            filename=clean_filename,
            language=language,
            risk_score=risk_result.risk_score,
            risk_level=risk_result.risk_level,
            total_findings_count=len(findings),
            secrets_detected_count=secrets_count,
            remediations=remediations,
            summary_message=summary_msg
        )
