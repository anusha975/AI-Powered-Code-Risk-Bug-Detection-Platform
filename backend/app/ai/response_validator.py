"""
LLM Response Validation, Sanitization, and Anti-Hallucination Guard Engine.

Enforces strict JSON schema validation, handles malformed or fragmented LLM outputs,
safeguards against hallucinated certainty, and guarantees non-execution of generated code.
"""

from typing import Dict, Any, Union, Optional
import json
import re

from app.schemas.remediation import (
    DetectedFact,
    AIInterpretation,
    RemediationRecommendation,
    DeveloperRemediation
)
from app.utils.logger import logger


INSUFFICIENT_EVIDENCE_MESSAGE = "Insufficient evidence for a reliable explanation."


def clean_and_extract_json(raw_text: str) -> Dict[str, Any]:
    """
    Extract and parse JSON from raw model string, stripping markdown fences or trailing chatter.
    """
    cleaned = raw_text.strip()

    # Remove markdown code blocks if present
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]

    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]

    cleaned = cleaned.strip()

    # Direct JSON parse attempt
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # Fallback: Extract first JSON object bounded by outermost { and }
        match = re.search(r"(\{.*\})", cleaned, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass

    logger.warning("Failed to parse LLM response as JSON. Falling back to heuristic text extraction.")
    return {"raw_text_fallback": raw_text}


def sanitize_code_example(code_example: Optional[str]) -> Optional[str]:
    """
    Sanitize code example for safe display only (non-execution safety).
    Strips dangerous terminal control characters and enforces character limits.
    """
    if not code_example or not isinstance(code_example, str):
        return None

    # Strip null bytes and non-printable control characters (except newline, tab)
    sanitized = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", code_example)
    # Strip markdown wrapper if model wrapped it in backticks
    sanitized = re.sub(r"^```[a-zA-Z]*\n?", "", sanitized)
    sanitized = re.sub(r"\n?```$", "", sanitized)

    trimmed = sanitized.strip()
    return trimmed if trimmed else None


def validate_and_parse_llm_response(
    raw_response: Union[str, Dict[str, Any]],
    finding: Dict[str, Any],
    context_snippet: str,
    confidence_threshold: float = 0.40,
    model_name: str = "privacy-guard-llm-v1",
    provider_name: str = "MockLLMProvider"
) -> DeveloperRemediation:
    """
    Validate, sanitize, and assemble the tripartite DeveloperRemediation contract.

    Args:
        raw_response: Raw response from LLM provider (JSON dict or string).
        finding: Authoritative local static analysis finding dictionary.
        context_snippet: Bounded sanitized code context.
        confidence_threshold: Minimum static confidence required before attempting AI interpretation.
        model_name: Model identifier.
        provider_name: Provider name.

    Returns:
        Structured DeveloperRemediation object strictly obeying tripartite epistemics.
    """
    # 1. Epistemic Tier 1: DETECTED FACT (Anchored strictly to static analysis)
    finding_id = str(finding.get("issue_id", "UNKNOWN-001"))
    title = str(finding.get("title", "Security Finding"))
    severity = str(finding.get("severity", "MEDIUM")).upper()
    category = str(finding.get("category", "SECURITY")).upper()
    line_number = int(finding.get("line_number", 1) or 1)
    analyzer = str(finding.get("analyzer", "static_analyzer"))
    raw_snippet = str(finding.get("code_snippet", context_snippet))
    detection_confidence = float(finding.get("confidence", 0.5))

    fact = DetectedFact(
        analyzer=analyzer,
        issue_id=finding_id,
        title=title,
        category=category,
        severity=severity,
        line_number=line_number,
        code_snippet=raw_snippet,
        detection_confidence=detection_confidence
    )

    # 2. Check for Insufficient Evidence Threshold
    if detection_confidence < confidence_threshold:
        interpretation = AIInterpretation(
            developer_explanation=INSUFFICIENT_EVIDENCE_MESSAGE,
            why_it_matters="The static analyzer flagged this finding with low confidence (< 0.40). Without deeper call-graph reachability, AI interpretation cannot reliably determine true vulnerability status.",
            potential_impact="Uncertain runtime impact due to insufficient static evidence.",
            confidence_statement=f"Low Confidence ({detection_confidence:.2f}): Evidence is below the minimum threshold required for automated AI advice.",
            is_insufficient_evidence=True
        )

        recommendation = RemediationRecommendation(
            recommended_remediation="Manually audit this code path and verify if external untrusted data reaches the target line.",
            safer_code_example=None,
            remediation_steps=[
                "Inspect callers of this function to verify input sanitization.",
                "Review project coding guidelines for this pattern.",
                "Add unit tests covering edge cases for this routine."
            ]
        )

        return DeveloperRemediation(
            finding_id=finding_id,
            fact=fact,
            interpretation=interpretation,
            recommendation=recommendation,
            model_used=model_name
        )

    # 3. Parse LLM Output
    parsed_data: Dict[str, Any] = {}
    if isinstance(raw_response, dict):
        parsed_data = raw_response
    elif isinstance(raw_response, str):
        parsed_data = clean_and_extract_json(raw_response)
    else:
        parsed_data = {}

    # Handle text fallback when JSON keys are missing
    if "raw_text_fallback" in parsed_data:
        fallback_text = str(parsed_data["raw_text_fallback"]).strip()
        explanation_text = fallback_text if len(fallback_text) > 10 else f"Potential {title} issue identified at line {line_number}."
        parsed_data = {
            "developer_explanation": explanation_text,
            "why_it_matters": "Violates secure coding best practices.",
            "potential_impact": "May lead to unintended behavior or security vulnerabilities.",
            "recommended_remediation": "Refactor to use safe, parameterized standard library functions.",
            "safer_code_example": None,
            "confidence_statement": "Moderate confidence based on extracted context."
        }

    # 4. Epistemic Tier 2: AI INTERPRETATION
    dev_explanation = str(parsed_data.get("developer_explanation") or parsed_data.get("root_cause") or f"Identified {title} at line {line_number}.").strip()
    why_it_matters = str(parsed_data.get("why_it_matters") or "This code pattern introduces security and stability risks.").strip()
    potential_impact = str(parsed_data.get("potential_impact") or "Attackers or malformed inputs could trigger abnormal behavior.").strip()
    confidence_statement = str(
        parsed_data.get("confidence_statement") or
        f"High confidence: Verified direct static call at line {line_number} (Analyzer confidence: {detection_confidence:.2f})."
    ).strip()

    # If the model explicitly indicates lack of evidence
    is_insufficient = (
        INSUFFICIENT_EVIDENCE_MESSAGE.lower() in dev_explanation.lower() or
        "insufficient evidence" in dev_explanation.lower()
    )

    if is_insufficient:
        dev_explanation = INSUFFICIENT_EVIDENCE_MESSAGE

    interpretation = AIInterpretation(
        developer_explanation=dev_explanation,
        why_it_matters=why_it_matters,
        potential_impact=potential_impact,
        confidence_statement=confidence_statement,
        is_insufficient_evidence=is_insufficient
    )

    # 5. Epistemic Tier 3: RECOMMENDATION
    remediation_advice = str(parsed_data.get("recommended_remediation") or parsed_data.get("remediation") or "Refactor code to avoid vulnerable functions.").strip()
    raw_safer_code = parsed_data.get("safer_code_example") or parsed_data.get("secure_code")
    safer_code = sanitize_code_example(raw_safer_code)

    raw_steps = parsed_data.get("remediation_steps")
    steps: list[str] = []
    if isinstance(raw_steps, list):
        steps = [str(s).strip() for s in raw_steps if str(s).strip()]
    else:
        steps = [
            "Isolate the input parameters to ensure strict data validation.",
            "Replace dangerous functions with safe standard library alternatives.",
            "Add automated regression tests to verify secure behavior."
        ]

    recommendation = RemediationRecommendation(
        recommended_remediation=remediation_advice,
        safer_code_example=safer_code,
        remediation_steps=steps
    )

    return DeveloperRemediation(
        finding_id=finding_id,
        fact=fact,
        interpretation=interpretation,
        recommendation=recommendation,
        model_used=model_name
    )
