"""
Unit and Integration Tests for Module 8: Private AI & Local LLM Provider.
"""

import pytest
import httpx
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi.testclient import TestClient

from app.main import app
from app.ai.providers import (
    get_llm_provider,
    LocalLLMProvider,
    ExternalLLMProvider,
    MockLLMProvider
)
from app.schemas.ai import MinimizedContext, AIStatus
from app.schemas.analysis import FindingSeverity
from app.schemas.provider import ProviderType, ProviderStatus
from app.services.provider_service import ProviderService
from app.services.ai_service import AIService
from app.services.remediation_service import RemediationService

client = TestClient(app)


def test_provider_factory_resolution():
    """Verify factory returns appropriate provider instance based on type."""
    assert isinstance(get_llm_provider("local"), LocalLLMProvider)
    assert isinstance(get_llm_provider("ollama"), LocalLLMProvider)
    assert isinstance(get_llm_provider("vllm"), LocalLLMProvider)
    assert isinstance(get_llm_provider("external"), ExternalLLMProvider)
    assert isinstance(get_llm_provider("openai"), ExternalLLMProvider)
    assert isinstance(get_llm_provider("mock"), MockLLMProvider)
    assert isinstance(get_llm_provider("unknown_mode"), MockLLMProvider)


@pytest.mark.asyncio
async def test_local_provider_ollama_query_simulated():
    """Verify LocalLLMProvider handles native Ollama format correctly."""
    provider = LocalLLMProvider(
        api_url="http://127.0.0.1:11434",
        model_name="llama3.2:1b",
        api_type="ollama"
    )

    ctx = MinimizedContext(
        finding_id="FINDING-1",
        issue_title="Dynamic Code Execution",
        severity=FindingSeverity.CRITICAL,
        line_number=5,
        start_line=1,
        end_line=9,
        context_snippet="5: eval(payload)\n",
        char_count=18
    )

    mock_ollama_response = {
        "response": (
            '{"root_cause": "Unsanitized eval parses raw payload string as bytecode.", '
            '"remediation": "Replace eval with ast.literal_eval.", '
            '"secure_code": "ast.literal_eval(payload)"}'
        )
    }

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = mock_ollama_response
    mock_resp.raise_for_status = MagicMock()

    with patch("httpx.AsyncClient.post", new=AsyncMock(return_value=mock_resp)):
        explanation = await provider.generate_explanation(ctx)

        assert explanation.finding_id == "FINDING-1"
        assert "eval" in explanation.root_cause_explanation
        assert "literal_eval" in explanation.remediation_advice
        assert "ast.literal_eval" in explanation.secure_code_example
        assert "LocalLLMProvider" in explanation.provider_used


@pytest.mark.asyncio
async def test_local_provider_openai_compatible_query_simulated():
    """Verify LocalLLMProvider handles OpenAI-compatible format (vLLM/LocalAI)."""
    provider = LocalLLMProvider(
        api_url="http://127.0.0.1:8000/v1",
        model_name="qwen2.5-coder:7b",
        api_type="openai_compatible"
    )

    ctx = MinimizedContext(
        finding_id="FINDING-2",
        issue_title="Raw SQL Injection",
        severity=FindingSeverity.HIGH,
        line_number=8,
        start_line=4,
        end_line=12,
        context_snippet="8: cursor.execute(query % id)\n",
        char_count=30
    )

    mock_openai_response = {
        "choices": [
            {
                "message": {
                    "content": (
                        '{"root_cause": "String formatting concatenates untrusted input into SQL query.", '
                        '"remediation": "Use parameterized queries with placeholder binding.", '
                        '"secure_code": "cursor.execute(\\"SELECT * FROM users WHERE id = ?\\", (id,))"}'
                    )
                }
            }
        ]
    }

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = mock_openai_response
    mock_resp.raise_for_status = MagicMock()

    with patch("httpx.AsyncClient.post", new=AsyncMock(return_value=mock_resp)):
        explanation = await provider.generate_explanation(ctx)

        assert explanation.finding_id == "FINDING-2"
        assert "SQL" in explanation.root_cause_explanation
        assert "parameterized" in explanation.remediation_advice.lower()
        assert "cursor.execute" in explanation.secure_code_example


@pytest.mark.asyncio
async def test_local_provider_remediation_json_generation():
    """Verify LocalLLMProvider produces tripartite remediation fields."""
    provider = LocalLLMProvider(
        api_url="http://127.0.0.1:11434",
        model_name="codellama:7b",
        api_type="ollama"
    )

    ctx = MinimizedContext(
        finding_id="FINDING-3",
        issue_title="OS Command Injection",
        severity=FindingSeverity.CRITICAL,
        line_number=3,
        start_line=1,
        end_line=5,
        context_snippet="3: os.system('ping ' + ip)\n",
        char_count=26
    )
    finding = {
        "issue_id": "AST-SEC-CMD-001",
        "title": "OS Command Injection",
        "severity": "CRITICAL",
        "line_number": 3
    }

    mock_json = {
        "developer_explanation": "Direct concatenation of IP address string into shell process.",
        "why_it_matters": "Allows arbitrary shell command injection via semicolons.",
        "potential_impact": "Host system compromise.",
        "recommended_remediation": "Use subprocess.run with argument array.",
        "safer_code_example": "subprocess.run(['ping', '-c', '1', ip], check=True)",
        "remediation_steps": ["Avoid shell=True.", "Pass arguments as list."],
        "confidence_statement": "High certainty from static AST node."
    }

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"response": str(mock_json).replace("'", '"')}
    mock_resp.raise_for_status = MagicMock()

    with patch("httpx.AsyncClient.post", new=AsyncMock(return_value=mock_resp)):
        res = await provider.generate_remediation_json(ctx, finding)

        assert "developer_explanation" in res
        assert "why_it_matters" in res
        assert "potential_impact" in res
        assert "recommended_remediation" in res
        assert "safer_code_example" in res


@pytest.mark.asyncio
async def test_local_provider_offline_fallback():
    """Verify LocalLLMProvider gracefully falls back when local server is unreachable."""
    provider = LocalLLMProvider(
        api_url="http://127.0.0.1:9999",  # Unreachable port
        model_name="llama3.2:1b",
        api_type="ollama",
        timeout_seconds=1
    )

    ctx = MinimizedContext(
        finding_id="FINDING-4",
        issue_title="Hardcoded Password",
        severity=FindingSeverity.HIGH,
        line_number=2,
        start_line=1,
        end_line=4,
        context_snippet="2: DB_PASS = 'secret'\n",
        char_count=21
    )

    # Simulate network failure
    with patch("httpx.AsyncClient.post", side_effect=httpx.ConnectError("Connection refused")):
        explanation = await provider.generate_explanation(ctx)

        # Invariant: Must not crash, returns valid fallback explanation
        assert explanation is not None
        assert explanation.finding_id == "FINDING-4"
        assert "Fallback" in explanation.provider_used
        assert len(explanation.root_cause_explanation) > 10


@pytest.mark.asyncio
async def test_local_provider_health_check():
    """Verify health check probe against local server."""
    provider = LocalLLMProvider(api_url="http://127.0.0.1:11434", api_type="ollama")

    # 1. Test Online Probe
    mock_tags = {"models": [{"name": "llama3.2:1b"}, {"name": "codellama:7b"}]}
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = mock_tags

    with patch("httpx.AsyncClient.get", new=AsyncMock(return_value=mock_resp)):
        health = await provider.health_check()
        assert health["status"] == "OPERATIONAL"
        assert health["air_gapped"] is True
        assert health["privacy_score"] == 100
        assert len(health["models_available"]) == 2

    # 2. Test Offline Probe
    with patch("httpx.AsyncClient.get", side_effect=httpx.ConnectError("Connection refused")):
        health_off = await provider.health_check()
        assert health_off["status"] == "UNREACHABLE"
        assert health_off["air_gapped"] is True
        assert health_off["privacy_score"] == 100


def test_api_providers_catalog_endpoint():
    """Verify GET /api/ai/providers returns full provider catalog."""
    res = client.get("/api/ai/providers")
    assert res.status_code == 200
    data = res.json()

    assert "active_provider" in data
    assert "providers" in data
    assert len(data["providers"]) == 3  # local, external, mock

    types = [p["provider_type"] for p in data["providers"]]
    assert "local" in types
    assert "external" in types
    assert "mock" in types


def test_api_providers_test_endpoint():
    """Verify POST /api/ai/providers/test allows testing providers."""
    # 1. Test Mock Provider
    mock_req = {"provider_type": "mock"}
    res_mock = client.post("/api/ai/providers/test", json=mock_req)
    assert res_mock.status_code == 200
    data_mock = res_mock.json()
    assert data_mock["success"] is True
    assert data_mock["air_gapped"] is True

    # 2. Test Local Provider on simulated unreachable URL
    local_req = {
        "provider_type": "local",
        "api_url": "http://127.0.0.1:54321",
        "timeout_seconds": 1
    }
    res_local = client.post("/api/ai/providers/test", json=local_req)
    assert res_local.status_code == 200
    data_local = res_local.json()
    assert data_local["provider_type"] == "local"
    assert data_local["air_gapped"] is True
    assert data_local["status"] in ("UNREACHABLE", "STANDBY")


@pytest.mark.asyncio
async def test_no_ai_mode_full_pipeline():
    """Verify static analysis, secret redaction, and risk scoring work with AI disabled."""
    code = (
        "import os\n"
        "AWS_KEY = 'AKIA1234567890EXAMPLE'\n"
        "def run_cmd(user_in):\n"
        "    eval(user_in)\n"
    )

    res = await AIService.analyze_with_privacy_ai(
        content=code,
        filename="test_no_ai.py",
        explicit_language="python",
        ai_enabled=False
    )

    # Invariants:
    # 1. Secrets must still be detected & redacted
    assert res.secrets_detected_count >= 1
    # 2. Static AST findings must still be detected
    assert res.total_findings_count >= 1
    # 3. Risk scoring must still compute score
    assert res.risk_score >= 80
    # 4. AI status must indicate AI_DISABLED
    assert res.ai_status == AIStatus.AI_DISABLED
    # 5. Explanations array is empty (no LLM calls made)
    assert len(res.ai_explanations) == 0


@pytest.mark.asyncio
async def test_air_gapped_zero_key_requirement():
    """Verify Local and Mock providers operate with 100% fidelity without API keys."""
    code = "def insecure(x):\n    eval(x)\n"

    # Local LLM with offline mock fallback
    res = await RemediationService.generate_developer_remediations(
        content=code,
        filename="airgap.py",
        explicit_language="python",
        provider_override="local"
    )

    assert res.total_findings_count >= 1
    assert len(res.remediations) >= 1
    assert res.remediations[0].fact.epistemic_tier == "DETECTED_FACT"
    assert res.remediations[0].interpretation.epistemic_tier == "AI_INTERPRETATION"
    assert res.remediations[0].recommendation.epistemic_tier == "RECOMMENDATION"
