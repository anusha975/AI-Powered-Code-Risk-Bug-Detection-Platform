"""
Test Suite for Module 6: Privacy-Aware AI Analysis Layer.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.ai.context_minimizer import extract_minimized_context, minimize_findings_context
from app.ai.providers import MockLLMProvider, get_llm_provider
from app.ai.audit_logger import audit_logger
from app.services.ai_service import AIService
from app.schemas.ai import AIStatus, MinimizedContext


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def clean_audit_log():
    audit_logger.clear()
    yield
    audit_logger.clear()


def test_context_minimizer_window_bounds():
    """Verify that context minimizer extracts bounded ±4 line window with line numbers."""
    code_lines = [f"line_{i} = {i}" for i in range(1, 31)]
    full_code = "\n".join(code_lines)

    finding = {
        "issue_id": "AST-001",
        "title": "Test Issue",
        "severity": "HIGH",
        "line_number": 15
    }

    ctx = extract_minimized_context(sanitized_code=full_code, finding=finding, max_window=4)

    assert ctx.line_number == 15
    assert ctx.start_line == 11
    assert ctx.end_line == 19
    assert ">>  15 | line_15 = 15" in ctx.context_snippet
    assert "   11 | line_11 = 11" in ctx.context_snippet
    assert "   19 | line_19 = 19" in ctx.context_snippet
    # Assert line 1 and line 30 are NOT in context snippet
    assert "line_1 =" not in ctx.context_snippet
    assert "line_30 =" not in ctx.context_snippet
    assert ctx.char_count == len(ctx.context_snippet)


def test_context_minimizer_redacted_secrets():
    """Verify that redacted secret tokens are recognized in context."""
    code = (
        "import os\n"
        "API_KEY = '[REDACTED_AWS_ACCESS_KEY]'\n"
        "eval(user_input)\n"
    )
    finding = {
        "issue_id": "AST-002",
        "title": "Dynamic eval()",
        "severity": "CRITICAL",
        "line_number": 3
    }
    ctx = extract_minimized_context(sanitized_code=code, finding=finding, max_window=3)

    assert ctx.has_redactions is True
    assert "[REDACTED_AWS_ACCESS_KEY]" in ctx.context_snippet


def test_context_minimizer_edge_cases():
    """Verify context extraction on edge boundary lines."""
    single_line_code = "print('hello')"
    finding = {"issue_id": "AST-003", "title": "Print", "severity": "LOW", "line_number": 1}

    ctx = extract_minimized_context(sanitized_code=single_line_code, finding=finding, max_window=4)
    assert ctx.start_line == 1
    assert ctx.end_line == 1
    assert ">>   1 | print('hello')" in ctx.context_snippet


def test_minimize_findings_prioritization():
    """Verify findings are sorted by severity descending and limited to max_findings."""
    code = "\n".join([f"line_{i}" for i in range(1, 20)])
    findings = [
        {"issue_id": "F-LOW", "title": "Low style issue", "severity": "LOW", "line_number": 2, "confidence": 0.5},
        {"issue_id": "F-CRIT", "title": "Critical RCE", "severity": "CRITICAL", "line_number": 10, "confidence": 0.95},
        {"issue_id": "F-MED", "title": "Medium smell", "severity": "MEDIUM", "line_number": 5, "confidence": 0.8},
        {"issue_id": "F-HIGH", "title": "High SQL Injection", "severity": "HIGH", "line_number": 8, "confidence": 0.9}
    ]

    contexts = minimize_findings_context(sanitized_code=code, findings=findings, max_findings=2)
    assert len(contexts) == 2
    assert contexts[0].finding_id == "F-CRIT"
    assert contexts[1].finding_id == "F-HIGH"


@pytest.mark.asyncio
async def test_mock_llm_provider_generation():
    """Verify MockLLMProvider produces structured AIFindingExplanation."""
    provider = MockLLMProvider()
    context = MinimizedContext(
        finding_id="AST-SEC-EVAL-001",
        issue_title="Dangerous Dynamic Code Execution (eval)",
        severity="CRITICAL",
        line_number=5,
        start_line=1,
        end_line=9,
        context_snippet=">>   5 | eval(user_input)",
        char_count=23,
        has_redactions=False
    )

    explanation = await provider.generate_explanation(context)
    assert explanation.finding_id == "AST-SEC-EVAL-001"
    assert "eval()" in explanation.root_cause_explanation
    assert "ast.literal_eval" in explanation.remediation_advice
    assert explanation.secure_code_example is not None
    assert "MockLLMProvider" in explanation.provider_used


@pytest.mark.asyncio
async def test_ai_service_vulnerable_code_full_pipeline():
    """Test full AI analysis pipeline on code with critical RCE and secrets."""
    code = """
AWS_KEY = "AKIA1234567890EXAMPLE"

def handle_request(user_input):
    eval(user_input)
"""
    response = await AIService.analyze_with_privacy_ai(
        content=code,
        filename="handler.py",
        ai_enabled=True,
        provider_override="mock"
    )

    assert response.ai_status == AIStatus.SUCCESS
    assert response.secrets_detected_count >= 1
    assert response.total_findings_count >= 1
    assert response.risk_score >= 80
    assert len(response.minimized_contexts) > 0
    assert len(response.ai_explanations) > 0
    assert response.audit_event is not None
    assert response.audit_event.status == AIStatus.SUCCESS
    assert response.audit_event.findings_count == len(response.ai_explanations)


@pytest.mark.asyncio
async def test_ai_service_clean_code_skipped():
    """Test that clean code skips LLM calls and marks status SKIPPED_CLEAN."""
    code = "def add(a: int, b: int) -> int:\n    return a + b\n"
    response = await AIService.analyze_with_privacy_ai(
        content=code,
        filename="math.py",
        ai_enabled=True,
        provider_override="mock"
    )

    assert response.ai_status == AIStatus.SKIPPED_CLEAN
    assert response.total_findings_count == 0
    assert len(response.ai_explanations) == 0
    assert response.audit_event.status == AIStatus.SKIPPED_CLEAN


@pytest.mark.asyncio
async def test_ai_service_disabled_flag():
    """Test that ai_enabled=False still returns full static analysis results."""
    code = "import os\n\ndef run(cmd):\n    eval(cmd)\n"
    response = await AIService.analyze_with_privacy_ai(
        content=code,
        filename="test.py",
        ai_enabled=False,
        provider_override="mock"
    )

    assert response.ai_status == AIStatus.AI_DISABLED
    assert response.total_findings_count >= 1
    assert response.risk_score >= 80
    assert len(response.ai_explanations) == 0
    assert response.audit_event.status == AIStatus.AI_DISABLED


def test_audit_logger_zero_code_invariant():
    """Verify that audit logger does not store source code or raw prompts."""
    event = audit_logger.record_event(
        provider="MockLLMProvider",
        model="privacy-guard-mock-v1",
        status=AIStatus.SUCCESS,
        findings_count=2,
        payload_chars=340,
        latency_ms=18.5,
        details="Telemetry event"
    )

    # Check fields
    event_dict = event.model_dump()
    assert "source_code" not in event_dict
    assert "prompt" not in event_dict
    assert "code" not in event_dict
    assert event.findings_count == 2
    assert event.payload_chars == 340

    recent = audit_logger.get_recent_events()
    assert len(recent) == 1
    assert recent[0].event_id == event.event_id


def test_api_ai_analyze_endpoint(client):
    """Test POST /api/ai/analyze API endpoint."""
    payload = {
        "content": "def run(x):\n    eval(x)\n",
        "filename": "vuln.py",
        "language": "python",
        "ai_enabled": True
    }
    response = client.post("/api/ai/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert "analysis_id" in data
    assert "ai_status" in data
    assert "findings" in data
    assert "risk_score" in data
    assert "minimized_contexts" in data
    assert "ai_explanations" in data
    assert "audit_event" in data
    assert "privacy_guarantee" in data
    assert data["ai_status"] == "SUCCESS"


def test_api_ai_audit_endpoint(client):
    """Test GET /api/ai/audit endpoint."""
    # Trigger an analysis first
    client.post("/api/ai/analyze", json={"content": "def test(): pass\n"})

    response = client.get("/api/ai/audit?limit=10")
    assert response.status_code == 200
    events = response.json()
    assert isinstance(events, list)
    assert len(events) >= 1
    assert "event_id" in events[0]
    assert "latency_ms" in events[0]
    assert "status" in events[0]
