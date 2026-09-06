"""
Test Suite for Module 7: AI Developer Explanation and Remediation Engine.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.ai.response_validator import (
    validate_and_parse_llm_response,
    clean_and_extract_json,
    sanitize_code_example,
    INSUFFICIENT_EVIDENCE_MESSAGE
)
from app.services.remediation_service import RemediationService
from app.schemas.remediation import EpistemicCategory, DeveloperRemediation


@pytest.fixture
def client():
    return TestClient(app)


def test_tripartite_schema_structure():
    """Verify that DeveloperRemediation rigorously enforces tripartite epistemic tiers."""
    finding = {
        "issue_id": "AST-SEC-EVAL-001",
        "title": "Use of dangerous dynamic eval() function",
        "category": "SECURITY",
        "severity": "CRITICAL",
        "line_number": 12,
        "code_snippet": "eval(user_payload)",
        "confidence": 0.95,
        "analyzer": "ast_visitor"
    }

    mock_llm_json = {
        "developer_explanation": "The eval() function executes arbitrary Python code strings at runtime.",
        "why_it_matters": "Untrusted input reaching eval() enables full code execution.",
        "potential_impact": "Remote Code Execution (RCE).",
        "recommended_remediation": "Use ast.literal_eval() instead.",
        "safer_code_example": "import ast\nsafe_data = ast.literal_eval(payload)",
        "confidence_statement": "High certainty: Direct AST call node at line 12."
    }

    remediation = validate_and_parse_llm_response(
        raw_response=mock_llm_json,
        finding=finding,
        context_snippet=">> 12 | eval(user_payload)"
    )

    # 1. Tier 1: Fact
    assert remediation.fact.epistemic_tier == EpistemicCategory.DETECTED_FACT.value
    assert remediation.fact.analyzer == "ast_visitor"
    assert remediation.fact.issue_id == "AST-SEC-EVAL-001"
    assert remediation.fact.line_number == 12
    assert remediation.fact.detection_confidence == 0.95

    # 2. Tier 2: Interpretation
    assert remediation.interpretation.epistemic_tier == EpistemicCategory.AI_INTERPRETATION.value
    assert "eval()" in remediation.interpretation.developer_explanation
    assert remediation.interpretation.is_insufficient_evidence is False

    # 3. Tier 3: Recommendation
    assert remediation.recommendation.epistemic_tier == EpistemicCategory.RECOMMENDATION.value
    assert "ast.literal_eval" in remediation.recommendation.safer_code_example


def test_insufficient_evidence_low_confidence_threshold():
    """Verify that static confidence < 0.40 triggers insufficient evidence fallback."""
    finding = {
        "issue_id": "AST-AMBIGUOUS-001",
        "title": "Ambiguous control flow branch",
        "category": "QUALITY",
        "severity": "LOW",
        "line_number": 5,
        "code_snippet": "data.process()",
        "confidence": 0.25,  # Below 0.40 threshold
        "analyzer": "ast_visitor"
    }

    mock_llm_json = {
        "developer_explanation": "This is definitely a critical bug.",  # Overclaiming certainty
        "why_it_matters": "Huge impact.",
        "potential_impact": "High."
    }

    remediation = validate_and_parse_llm_response(
        raw_response=mock_llm_json,
        finding=finding,
        context_snippet=">>  5 | data.process()",
        confidence_threshold=0.40
    )

    assert remediation.interpretation.is_insufficient_evidence is True
    assert remediation.interpretation.developer_explanation == INSUFFICIENT_EVIDENCE_MESSAGE
    assert remediation.recommendation.safer_code_example is None


def test_response_validator_malformed_json():
    """Verify validator recovers gracefully from malformed LLM outputs."""
    finding = {
        "issue_id": "BND-B102",
        "title": "Use of exec",
        "severity": "CRITICAL",
        "line_number": 8,
        "confidence": 0.9,
        "analyzer": "bandit"
    }

    malformed_string = "Here is my advice: The function exec is dangerous at line 8. Please avoid it."

    remediation = validate_and_parse_llm_response(
        raw_response=malformed_string,
        finding=finding,
        context_snippet=">>  8 | exec(cmd)"
    )

    assert remediation.finding_id == "BND-B102"
    assert len(remediation.interpretation.developer_explanation) > 0
    assert len(remediation.recommendation.recommended_remediation) > 0


def test_response_validator_markdown_wrapped_json():
    """Verify validator cleanly parses JSON wrapped in markdown code blocks."""
    raw_markdown = """```json
{
  "developer_explanation": "Dynamic execution is hazardous.",
  "why_it_matters": "Allows unconstrained code paths.",
  "potential_impact": "RCE",
  "recommended_remediation": "Sanitize inputs.",
  "safer_code_example": "print('safe')"
}
```"""
    parsed = clean_and_extract_json(raw_markdown)
    assert parsed.get("potential_impact") == "RCE"
    assert parsed.get("safer_code_example") == "print('safe')"


def test_response_validator_missing_fields():
    """Verify validator supplies robust fallback defaults when JSON fields are omitted."""
    finding = {
        "issue_id": "AST-009",
        "title": "SQL Injection",
        "severity": "HIGH",
        "line_number": 15,
        "confidence": 0.85
    }

    remediation = validate_and_parse_llm_response(
        raw_response={},  # Empty dict
        finding=finding,
        context_snippet=">> 15 | cursor.execute(query)"
    )

    assert remediation.interpretation.why_it_matters != ""
    assert remediation.interpretation.potential_impact != ""
    assert remediation.recommendation.recommended_remediation != ""
    assert len(remediation.recommendation.remediation_steps) > 0


def test_code_sanitizer_non_execution():
    """Verify sanitize_code_example strips non-printable control chars and markdown."""
    raw_code = "```python\nprint('hello\x00world')\n```"
    sanitized = sanitize_code_example(raw_code)
    assert "\x00" not in sanitized
    assert not sanitized.startswith("```")
    assert not sanitized.endswith("```")
    assert sanitized == "print('helloworld')"


@pytest.mark.asyncio
async def test_remediation_service_vulnerable_code_e2e():
    """End-to-end test of RemediationService on code with SQL & Command injection."""
    code = """
import os
import sqlite3

def handle_user(user_id, host):
    os.system(f"ping -c 1 {host}")
    conn = sqlite3.connect("db.sqlite")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = '%s'" % user_id)
"""
    response = await RemediationService.generate_developer_remediations(
        content=code,
        filename="service.py",
        max_explanations=2
    )

    assert response.total_findings_count >= 2
    assert response.risk_score >= 70
    assert len(response.remediations) == 2

    # Check that first remediation is structured tripartite
    first = response.remediations[0]
    assert first.fact.epistemic_tier == "DETECTED_FACT"
    assert first.interpretation.epistemic_tier == "AI_INTERPRETATION"
    assert first.recommendation.epistemic_tier == "RECOMMENDATION"
    assert first.recommendation.safer_code_example is not None


@pytest.mark.asyncio
async def test_remediation_service_clean_code_e2e():
    """End-to-end test of RemediationService on pristine clean code."""
    code = "def multiply(a: int, b: int) -> int:\n    return a * b\n"
    response = await RemediationService.generate_developer_remediations(
        content=code,
        filename="math.py"
    )

    assert response.total_findings_count == 0
    assert response.risk_score <= 15
    assert len(response.remediations) == 0
    assert "Clean code profile" in response.summary_message


def test_api_remediation_explain_endpoint(client):
    """Test POST /api/remediation/explain endpoint."""
    payload = {
        "content": "def run(payload):\n    eval(payload)\n",
        "filename": "eval_test.py",
        "language": "python",
        "max_explanations": 1
    }
    response = client.post("/api/remediation/explain", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert "analysis_id" in data
    assert "risk_score" in data
    assert "remediations" in data
    assert "epistemic_notice" in data
    assert len(data["remediations"]) == 1

    rem = data["remediations"][0]
    assert "fact" in rem
    assert "interpretation" in rem
    assert "recommendation" in rem
    assert rem["fact"]["analyzer"] != ""
    assert rem["interpretation"]["developer_explanation"] != ""
    assert rem["recommendation"]["recommended_remediation"] != ""
