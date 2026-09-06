"""
GitHub Pull Request Security and Risk Analysis Service.

Coordinates multi-file PR diff parsing, secret redaction, local AST/SAST scanning,
ML risk scoring, RAG knowledge retrieval, and tripartite AI remediation.
"""

import os
import time
import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any, Tuple

from app.github.client import github_client, GitHubPRMetadata, GitHubFileChange, mask_token
from app.github.diff_parser import DiffParser, ParsedDiffPatch
from app.analytics.session_store import session_store
from app.services.security_service import SecurityService
from app.services.analysis_service import AnalysisService

from app.services.risk_service import RiskService
from app.services.rag_service import RAGService
from app.services.remediation_service import RemediationService
from app.ai.providers import get_llm_provider
from app.schemas.github_pr import (
    PRUrlParseRequest,
    PRUrlParseResponse,
    PRSeverityBreakdown,
    PRFileFinding,
    PRFileAnalysis,
    PRAnalysisRequest,
    PRAnalysisResponse
)
from app.schemas.analysis import FindingSeverity
from app.schemas.security import SecretFinding
from app.schemas.remediation import DeveloperRemediation
from app.schemas.rag import RetrievedSource, RAGSearchRequest
from app.utils.logger import logger


SEVERITY_ORDER = {
    "CRITICAL": 0,
    "HIGH": 1,
    "MEDIUM": 2,
    "LOW": 3,
    FindingSeverity.CRITICAL: 0,
    FindingSeverity.HIGH: 1,
    FindingSeverity.MEDIUM: 2,
    FindingSeverity.LOW: 3
}


class GitHubPRService:

    """Service to orchestrate passive, non-executing GitHub Pull Request security audits."""

    @staticmethod
    def parse_url(pr_url: str) -> PRUrlParseResponse:
        """Validate and parse a GitHub PR URL or shorthand."""
        try:
            owner, repo, pull_number = github_client.parse_pr_url(pr_url)
            canonical = f"https://github.com/{owner}/{repo}/pull/{pull_number}"
            return PRUrlParseResponse(
                valid=True,
                owner=owner,
                repo=repo,
                pull_number=pull_number,
                canonical_url=canonical
            )
        except Exception as exc:
            raise ValueError(f"Invalid PR URL: {str(exc)}")

    @classmethod
    async def analyze_pull_request(
        cls,
        request: PRAnalysisRequest,
        header_token: Optional[str] = None
    ) -> PRAnalysisResponse:
        """
        Execute full multi-module GitHub Pull Request Security Audit:
        1. Resolve PR coordinates (URL or owner/repo/number).
        2. Resolve authentication token (Header, Request Body, or Env).
        3. Fetch metadata & changed files via safe GitHub REST API.
        4. Parse diff patches & filter out lockfiles/binaries.
        5. For each code file: Secret Redaction (M3) + AST/SAST Analysis (M4) + Risk Scoring (M5).
        6. Compute aggregate PR Risk Score, severity breakdown, and explainability reasons.
        7. Augment findings with Engineering Knowledge RAG (M9).
        8. Generate grounded tripartite AI developer remediations (M7 / M8).
        """
        start_time = time.perf_counter()
        analysis_id = str(uuid.uuid4())

        # 1. Resolve coordinates
        if request.pr_url:
            owner, repo, pull_number = github_client.parse_pr_url(request.pr_url)
        elif request.owner and request.repo and request.pull_number:
            owner = request.owner.strip()
            repo = request.repo.strip()
            pull_number = int(request.pull_number)
        else:
            raise ValueError("Must provide either 'pr_url' or ('owner', 'repo', 'pull_number').")

        # 2. Resolve token
        token = (
            header_token or
            request.github_token or
            os.environ.get("GITHUB_TOKEN", "")
        ).strip() or None

        logger.info(
            f"Starting GitHub PR Analysis | Audit ID: {analysis_id} | "
            f"Target: {owner}/{repo}#{pull_number} | Auth: {mask_token(token)}"
        )

        # 3. Fetch PR metadata & changed files
        pr_meta = github_client.get_pr_metadata(owner, repo, pull_number, token=token)
        changed_files_raw = github_client.get_pr_files(
            owner, repo, pull_number, token=token, max_files=request.max_files
        )

        file_analyses: List[PRFileAnalysis] = []
        all_findings: List[PRFileFinding] = []
        all_secrets: List[SecretFinding] = []
        supporting_docs_map: Dict[str, RetrievedSource] = {}

        crit_count = 0
        high_count = 0
        med_count = 0
        low_count = 0
        scanned_count = 0

        # 4. Multi-File Analysis Loop
        for f in changed_files_raw:
            filename = f.filename
            is_ignorable = DiffParser.is_ignorable_file(filename)

            if is_ignorable or not f.patch:
                file_analyses.append(PRFileAnalysis(
                    filename=filename,
                    status=f.status,
                    additions=f.additions,
                    deletions=f.deletions,
                    is_scanned=False,
                    language=None,
                    secrets_count=0,
                    findings_count=0,
                    file_risk_score=0.0,
                    file_risk_level="LOW",
                    findings=[],
                    secrets=[],
                    patch_snippet=f.patch[:300] if f.patch else None
                ))
                continue

            # Parse patch
            patch_data = DiffParser.parse_patch(filename, f.patch)
            if not patch_data.added_code_content.strip():
                file_analyses.append(PRFileAnalysis(
                    filename=filename,
                    status=f.status,
                    additions=f.additions,
                    deletions=f.deletions,
                    is_scanned=False,
                    language=None,
                    secrets_count=0,
                    findings_count=0,
                    file_risk_score=0.0,
                    file_risk_level="LOW",
                    findings=[],
                    secrets=[],
                    patch_snippet=f.patch[:300] if f.patch else None
                ))
                continue

            scanned_count += 1
            code_to_scan = patch_data.added_code_content

            # A. Secret Detection & Redaction (Module 3)
            security_res = SecurityService.scan_and_redact(
                content=code_to_scan,
                filename=filename
            )
            file_secrets: List[SecretFinding] = []
            for sec in security_res.findings:
                # Map line number to PR diff line
                actual_line = patch_data.line_number_mapping.get(sec.line_number, sec.line_number)
                mapped_sec = sec.model_copy(update={"line_number": actual_line, "file": filename})
                file_secrets.append(mapped_sec)
                all_secrets.append(mapped_sec)

            sanitized_code = security_res.sanitized_content

            # B. Local Static Code Analysis (Module 4)
            analysis_res = AnalysisService.analyze_code(
                content=sanitized_code,
                filename=filename
            )

            file_findings: List[PRFileFinding] = []
            for finding in analysis_res.findings:
                actual_line = patch_data.line_number_mapping.get(finding.line_number, finding.line_number)
                pr_finding = PRFileFinding(
                    file=filename,
                    line_number=actual_line,
                    issue_id=finding.issue_id,
                    title=finding.title,
                    category=finding.category.value if hasattr(finding.category, "value") else str(finding.category),
                    severity=finding.severity,
                    confidence=finding.confidence,
                    code_snippet=finding.code_snippet,
                    recommendation=finding.recommendation,
                    analyzer=finding.analyzer
                )
                file_findings.append(pr_finding)
                all_findings.append(pr_finding)

                # Count severities
                sev_val = str(finding.severity).upper()
                if sev_val == "CRITICAL":
                    crit_count += 1
                elif sev_val == "HIGH":
                    high_count += 1
                elif sev_val == "MEDIUM":
                    med_count += 1
                elif sev_val == "LOW":
                    low_count += 1

            # Also treat secrets as Critical/High security findings in severity counts
            if file_secrets:
                high_count += len(file_secrets)
                conf_map = {"HIGH": 0.95, "MEDIUM": 0.80, "LOW": 0.60}
                for sec in file_secrets:
                    sec_conf = conf_map.get(str(sec.confidence).upper(), 0.90) if isinstance(sec.confidence, str) else float(sec.confidence)
                    all_findings.append(PRFileFinding(
                        file=filename,
                        line_number=sec.line_number,
                        issue_id=f"SECRET-{sec.secret_type.upper()}",
                        title=f"Exposed {sec.secret_type} Detected",
                        category="SECRETS",
                        severity="HIGH",
                        confidence=sec_conf,
                        code_snippet="[REDACTED SENSITIVE CREDENTIAL]",
                        recommendation="Remove secret immediately and rotate credential in environment.",
                        analyzer="secret_entropy_scanner"
                    ))



            # C. Per-File Risk Scoring (Module 5)
            risk_res = RiskService.calculate_risk(
                content=sanitized_code,
                filename=filename,
                provided_findings=[f.model_dump() for f in analysis_res.findings],
                provided_secrets_count=len(file_secrets)
            )

            file_analyses.append(PRFileAnalysis(
                filename=filename,
                status=f.status,
                additions=f.additions,
                deletions=f.deletions,
                is_scanned=True,
                language=analysis_res.language,
                secrets_count=len(file_secrets),
                findings_count=len(file_findings),
                file_risk_score=risk_res.risk_score,
                file_risk_level=risk_res.risk_level.value if hasattr(risk_res.risk_level, "value") else str(risk_res.risk_level),
                findings=file_findings,
                secrets=file_secrets,
                patch_snippet=f.patch[:400] if f.patch else None
            ))

        # 5. Aggregate PR-Level Risk Score & Reasons
        severity_breakdown = PRSeverityBreakdown(
            critical=crit_count,
            high=high_count,
            medium=med_count,
            low=low_count
        )

        max_file_risk = max([fa.file_risk_score for fa in file_analyses], default=0.0)
        avg_file_risk = sum([fa.file_risk_score for fa in file_analyses if fa.is_scanned]) / max(scanned_count, 1)

        # Baseline composite score
        composite_score = (0.7 * max_file_risk) + (0.3 * avg_file_risk)

        # Apply deterministic rule floors
        risk_reasons: List[str] = []

        if crit_count > 0:
            composite_score = max(composite_score, 85.0 + min(crit_count * 5.0, 15.0))
            risk_reasons.append(f"PR introduces {crit_count} CRITICAL security vulnerability finding(s).")

        if len(all_secrets) > 0:
            composite_score = max(composite_score, 80.0 + min(len(all_secrets) * 4.0, 15.0))
            risk_reasons.append(f"PR introduces {len(all_secrets)} exposed/hardcoded credential(s).")

        if high_count > 0 and crit_count == 0 and len(all_secrets) == 0:
            composite_score = max(composite_score, 65.0 + min(high_count * 3.0, 15.0))
            risk_reasons.append(f"PR introduces {high_count} HIGH severity finding(s).")

        if med_count > 0 and crit_count == 0 and high_count == 0 and len(all_secrets) == 0:
            composite_score = max(composite_score, 40.0 + min(med_count * 2.0, 15.0))
            risk_reasons.append(f"PR introduces {med_count} MEDIUM severity finding(s).")

        if not risk_reasons:
            if scanned_count > 0:
                risk_reasons.append("No critical vulnerabilities or exposed secrets detected in scanned diffs.")
            else:
                risk_reasons.append("No supported code files were modified in this PR.")

        final_risk_score = round(min(max(composite_score, 0.0), 100.0), 1)

        if final_risk_score >= 80.0:
            final_risk_level = "CRITICAL"
        elif final_risk_score >= 60.0:
            final_risk_level = "HIGH"
        elif final_risk_score >= 30.0:
            final_risk_level = "MEDIUM"
        else:
            final_risk_level = "LOW"

        # 6. Sort Top Findings for AI Remediation & RAG
        sorted_findings = sorted(
            all_findings,
            key=lambda item: (SEVERITY_ORDER.get(item.severity, 99), -item.confidence)
        )
        top_findings = sorted_findings[:3]

        # 7. RAG Knowledge Search for Top Findings (Module 9)
        if request.enable_rag:
            for tf in top_findings:
                search_query = f"{tf.title} {tf.category} {tf.recommendation}"
                rag_results = RAGService.search_sources(RAGSearchRequest(
                    query=search_query,
                    top_k=2,
                    similarity_threshold=0.35
                ))
                for s in rag_results.sources:
                    if s.doc_id not in supporting_docs_map:
                        supporting_docs_map[s.doc_id] = s


        # 8. Generate Tripartite AI Remediations (Module 7 / Module 8)
        remediations: List[DeveloperRemediation] = []

        if top_findings and request.analysis_mode != "LOCAL_STATIC_ONLY":
            try:
                # Find matching file content for the top finding
                top_file = top_findings[0].file
                matched_file_analysis = next((fa for fa in file_analyses if fa.filename == top_file), None)
                if matched_file_analysis:
                    matched_patch = next((f.patch for f in changed_files_raw if f.filename == top_file), "")
                    parsed_p = DiffParser.parse_patch(top_file, matched_patch)
                    if parsed_p.added_code_content:
                        remediation_res = await RemediationService.generate_developer_remediations(
                            content=parsed_p.added_code_content,
                            filename=top_file,
                            max_explanations=2,
                            provider_override=request.provider_override
                        )
                        remediations = remediation_res.remediations
            except Exception as rem_exc:
                logger.warning(f"AI remediation generation failed for PR: {str(rem_exc)}")

        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)

        # Record in Dashboard Session Store (Module 11)
        try:
            findings_dicts = [f.model_dump() for f in all_findings]
            secrets_dicts = [s.model_dump() for s in all_secrets]
            session_store.record_session(
                analysis_id=analysis_id,
                analysis_type="GITHUB_PR",
                target_name=f"{owner}/{repo}#{pull_number}",
                risk_score=final_risk_score,
                risk_level=final_risk_level,
                risk_reasons=risk_reasons,
                scan_latency_ms=elapsed_ms,
                findings=findings_dicts,
                secrets=secrets_dicts,
                language="python",
                sanitized_content=f"GitHub PR #{pull_number}: {pr_meta.title}\nRepository: {owner}/{repo}\nChanged Files: {len(changed_files_raw)}",
                ai_mode=request.analysis_mode,
                remediations=remediations,
                supporting_documents=list(supporting_docs_map.values())
            )
        except Exception as sess_exc:
            logger.warning(f"Failed to record session in session_store: {str(sess_exc)}")

        return PRAnalysisResponse(
            analysis_id=analysis_id,
            pr_number=pull_number,
            repository=f"{owner}/{repo}",
            pr_title=pr_meta.title,
            pr_author=pr_meta.author,
            pr_url=pr_meta.html_url,
            base_branch=pr_meta.base_branch,
            head_branch=pr_meta.head_branch,
            state=pr_meta.state,
            changed_files_count=len(changed_files_raw),
            scanned_files_count=scanned_count,
            additions=pr_meta.additions,
            deletions=pr_meta.deletions,
            findings_count=len(all_findings),
            secrets_detected_count=len(all_secrets),
            severity_breakdown=severity_breakdown,
            overall_risk_score=final_risk_score,
            overall_risk_level=final_risk_level,
            risk_reasons=risk_reasons,
            files=file_analyses,
            remediations=remediations,
            supporting_documents=list(supporting_docs_map.values()),
            scan_latency_ms=elapsed_ms,
            analyzed_at=datetime.now(timezone.utc).isoformat()
        )

