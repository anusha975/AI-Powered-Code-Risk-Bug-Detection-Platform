"""
Privacy-Aware AI Analysis Orchestration Service.

Executes the 7-stage privacy pipeline:
Code Ingestion -> Secret Redaction -> Static Analysis -> Risk Scoring ->
Context Minimization -> LLM Provider -> Privacy Audit Logging.
"""

from typing import Optional, List, Dict, Any
import uuid
import time
import asyncio

from app.core.security_validator import sanitize_filename, validate_source_code_constraints
from app.services.language_detector import resolve_language
from app.services.security_service import SecurityService
from app.services.analysis_service import AnalysisService
from app.services.risk_service import RiskService
from app.ai.context_minimizer import minimize_findings_context
from app.ai.providers import (
    get_llm_provider,
    AITimeoutError,
    AIRateLimitError,
    AIProviderError
)
from app.ai.audit_logger import audit_logger
from app.schemas.ai import (
    AIStatus,
    MinimizedContext,
    AIFindingExplanation,
    AIAuditEvent,
    AIAnalysisResponse
)
from app.core.config import settings
from app.utils.logger import logger


class AIService:
    """Coordinates privacy-preserving AI vulnerability analysis and remediation advice."""

    @staticmethod
    async def analyze_with_privacy_ai(
        content: str,
        filename: Optional[str] = None,
        explicit_language: Optional[str] = None,
        ai_enabled: Optional[bool] = None,
        provider_override: Optional[str] = None
    ) -> AIAnalysisResponse:
        """
        Execute full privacy pipeline:
        1. Constraints validation & filename sanitization.
        2. Secret detection & in-place placeholder redaction.
        3. Local AST/Bandit static code analysis.
        4. Hybrid ML & deterministic risk scoring.
        5. Privacy context minimization (±4 lines around findings).
        6. AI provider invocation with timeout and error resilience.
        7. Audit event logging without source code storage.
        """
        start_time = time.perf_counter()
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

        # 4. Local Static Code Analysis (Module 4)
        analysis_result = AnalysisService.analyze_code(
            content=sanitized_code,
            filename=clean_filename,
            explicit_language=language
        )
        findings = analysis_result.findings
        findings_dicts = [f.model_dump() for f in findings]

        # 5. Risk Scoring Engine (Module 5)
        risk_result = RiskService.calculate_risk(
            content=sanitized_code,
            filename=clean_filename,
            explicit_language=language,
            provided_findings=findings_dicts,
            provided_secrets_count=secrets_count
        )

        # Determine AI active state
        is_ai_active = ai_enabled if ai_enabled is not None else settings.AI_ENABLED

        minimized_contexts: List[MinimizedContext] = []
        ai_explanations: List[AIFindingExplanation] = []
        ai_status = AIStatus.SUCCESS
        degradation_detail: Optional[str] = None
        provider = get_llm_provider(provider_override)

        # 6. Check AI Enabled or Clean Code
        if not is_ai_active:
            ai_status = AIStatus.AI_DISABLED
            degradation_detail = "AI analysis is disabled by policy (AI_ENABLED=false). Returning complete static analysis results."
        elif len(findings) == 0:
            ai_status = AIStatus.SKIPPED_CLEAN
            degradation_detail = "Zero security or quality issues detected. AI explanation skipped for clean code."
        else:
            # 7. Privacy Context Minimization
            minimized_contexts = minimize_findings_context(
                sanitized_code=sanitized_code,
                findings=findings_dicts,
                max_findings=settings.LLM_MAX_FINDINGS_TO_EXPLAIN,
                max_window=settings.LLM_MAX_CONTEXT_LINES // 2
            )

            # 8. Provider Invocation
            for ctx in minimized_contexts:
                try:
                    explanation = await provider.generate_explanation(ctx)
                    ai_explanations.append(explanation)
                except AITimeoutError as exc:
                    ai_status = AIStatus.DEGRADED_TIMEOUT
                    degradation_detail = f"AI provider timed out ({str(exc)}). Gracefully returning static findings."
                    logger.warning(f"AI timeout on finding {ctx.finding_id}: {exc}")
                    break
                except AIRateLimitError as exc:
                    ai_status = AIStatus.DEGRADED_RATE_LIMITED
                    degradation_detail = "AI provider rate limit reached (HTTP 429). Gracefully returning static findings."
                    logger.warning(f"AI rate limit on finding {ctx.finding_id}: {exc}")
                    break
                except Exception as exc:
                    ai_status = AIStatus.DEGRADED_ERROR
                    degradation_detail = f"AI provider error ({str(exc)}). Gracefully returning static findings."
                    logger.error(f"AI error on finding {ctx.finding_id}: {exc}")
                    break

        # Calculate Latency
        latency_ms = (time.perf_counter() - start_time) * 1000.0
        payload_chars = sum(ctx.char_count for ctx in minimized_contexts)

        # 9. Privacy Audit Logging (Zero source code recorded)
        audit_event = audit_logger.record_event(
            provider=provider.provider_name,
            model=provider.model_name,
            status=ai_status,
            findings_count=len(ai_explanations),
            payload_chars=payload_chars,
            latency_ms=latency_ms,
            details=degradation_detail
        )

        logger.info(
            f"AI Pipeline completed | Analysis ID: {analysis_id} | "
            f"File: {clean_filename} | AI Status: {ai_status.value} | "
            f"Findings: {len(findings)} | Explanations: {len(ai_explanations)}"
        )

        return AIAnalysisResponse(
            analysis_id=analysis_id,
            filename=clean_filename,
            language=language,
            ai_status=ai_status,
            secrets_detected_count=secrets_count,
            total_findings_count=len(findings),
            risk_score=risk_result.risk_score,
            risk_level=risk_result.risk_level,
            findings=findings,
            minimized_contexts=minimized_contexts,
            ai_explanations=ai_explanations,
            audit_event=audit_event
        )
