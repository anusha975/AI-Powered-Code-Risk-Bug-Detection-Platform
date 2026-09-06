"""
Static Code Analysis Service.
Coordinates local, zero-execution security and risk scanning.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional

from app.core.security_validator import sanitize_filename, validate_source_code_constraints
from app.services.language_detector import resolve_language
from app.analyzers.manager import analysis_manager
from app.analytics.session_store import session_store
from app.schemas.analysis import AnalysisResponse
from app.schemas.auth import AuditEventType
from app.security.audit_logger import audit_logger
from app.utils.logger import logger


class AnalysisService:
    """Service executing local static code analysis."""

    @staticmethod
    def analyze_code(
        content: str,
        filename: Optional[str] = None,
        explicit_language: Optional[str] = None,
        user_id: Optional[str] = None,
        username: Optional[str] = None
    ) -> AnalysisResponse:
        """
        Execute full local static code analysis without external AI or code execution.
        """
        raw_filename = filename or "snippet.py"
        clean_filename = sanitize_filename(raw_filename, default_fallback="snippet.py")

        # 1. Log Analysis Started Audit Event (zero raw code content)
        audit_logger.log_event(
            event_type=AuditEventType.ANALYSIS_STARTED,
            user_id=user_id,
            username=username,
            target_resource=clean_filename,
            metadata={"filename": clean_filename, "explicit_language": explicit_language}
        )

        # 2. Validate constraints
        validate_source_code_constraints(content, clean_filename)

        # 3. Resolve Language
        language = resolve_language(
            filename=clean_filename,
            explicit_language=explicit_language,
            content=content
        )

        # 4. Dispatch to Analyzer Manager
        summary, findings = analysis_manager.run_analysis(
            code=content,
            filename=clean_filename,
            language=language
        )

        analysis_id = str(uuid.uuid4())

        logger.info(
            f"Static analysis completed | ID: {analysis_id} | "
            f"File: {clean_filename} | Issues: {summary.total_issues} | Risk Score: {summary.risk_score}"
        )

        # Record in Dashboard Session Store (Module 11)
        try:
            findings_dicts = [f.model_dump() for f in findings]
            risk_level_str = "CRITICAL" if summary.risk_score >= 80 else "HIGH" if summary.risk_score >= 60 else "MEDIUM" if summary.risk_score >= 30 else "LOW"
            session_store.record_session(
                analysis_id=analysis_id,
                analysis_type="CODE_SNIPPET",
                target_name=clean_filename,
                risk_score=summary.risk_score,
                risk_level=risk_level_str,
                risk_reasons=[f"{summary.total_issues} total issue(s) detected."],
                scan_latency_ms=25.0,
                findings=findings_dicts,
                secrets=[],
                language=language,
                sanitized_content=content,
                ai_mode="Local Static Only",
                user_id=user_id,
                username=username
            )
        except Exception as sess_exc:
            logger.warning(f"Failed to record session in session_store: {str(sess_exc)}")

        # 5. Log Analysis Completed Audit Event (zero code / secrets in event)
        audit_logger.log_event(
            event_type=AuditEventType.ANALYSIS_COMPLETED,
            user_id=user_id,
            username=username,
            target_resource=clean_filename,
            status="SUCCESS",
            metadata={
                "analysis_id": analysis_id,
                "filename": clean_filename,
                "issues_count": summary.total_issues,
                "risk_score": summary.risk_score
            }
        )

        return AnalysisResponse(
            analysis_id=analysis_id,
            filename=clean_filename,
            language=language,
            summary=summary,
            findings=findings,
            analyzed_at=datetime.now(timezone.utc).isoformat()
        )



analysis_service = AnalysisService()
