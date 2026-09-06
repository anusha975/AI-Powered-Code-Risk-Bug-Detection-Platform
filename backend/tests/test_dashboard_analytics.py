"""
Unit & Integration Tests for Module 11: Professional Engineering Security Dashboard Analytics.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.analytics.session_store import AnalysisSessionStore, session_store
from app.services.analytics_service import AnalyticsService
from app.schemas.analytics import HistoryFilterRequest


client = TestClient(app)


def test_session_store_overview_metrics_calculation():
    """Verify live dashboard overview metrics reflect accurately without fake data."""
    store = AnalysisSessionStore(max_records=50)
    metrics = store.get_overview_metrics()

    assert metrics.total_analyses_performed >= 3
    assert metrics.average_risk_score > 0.0
    assert metrics.high_risk_analyses_count >= 2
    assert metrics.critical_findings_count >= 1
    assert metrics.security_findings_count >= 2
    assert "critical" in metrics.severity_distribution
    assert "SECURITY" in metrics.category_distribution
    assert len(metrics.recent_analyses) > 0
    assert metrics.privacy_assurance == "Secrets detected and redacted before AI analysis."


def test_session_store_record_and_retrieve():
    """Verify recording a new scan updates the session store and allows deep retrieval."""
    store = AnalysisSessionStore(max_records=50)

    test_findings = [
        {
            "issue_id": "SEC-TEST-001",
            "title": "Test Command Injection",
            "category": "SECURITY",
            "severity": "CRITICAL",
            "confidence": 0.95,
            "file": "test_cmd.py",
            "line_number": 12,
            "code_snippet": "os.system(user_cmd)",
            "recommendation": "Use subprocess.run without shell=True",
            "analyzer": "ast_analyzer"
        }
    ]
    test_secrets = [
        {
            "secret_type": "AWS_KEY",
            "file": "test_cmd.py",
            "line_number": 2,
            "confidence": "HIGH",
            "redaction_status": "REDACTED",
            "placeholder": "[REDACTED_AWS_KEY]"
        }
    ]

    record = store.record_session(
        analysis_id="SES-CUSTOM-TEST-001",
        analysis_type="CODE_SNIPPET",
        target_name="test_cmd.py",
        risk_score=92.0,
        risk_level="CRITICAL",
        risk_reasons=["Critical command injection detected"],
        scan_latency_ms=18.5,
        findings=test_findings,
        secrets=test_secrets,
        language="python",
        sanitized_content="import os\n# [REDACTED_AWS_KEY]\nos.system(user_cmd)",
        ai_mode="Private/Local LLM"
    )

    assert record.analysis_id == "SES-CUSTOM-TEST-001"
    assert record.risk_score == 92.0
    assert len(record.findings) == 1
    assert len(record.secrets) == 1

    # Verify direct retrieval by ID
    retrieved = store.get_analysis_detail("SES-CUSTOM-TEST-001")
    assert retrieved is not None
    assert retrieved.target_name == "test_cmd.py"
    assert retrieved.findings[0].issue_id == "SEC-TEST-001"


def test_session_store_history_filtering():
    """Verify history queries can be filtered by analysis type and risk tier."""
    store = AnalysisSessionStore(max_records=50)

    # Filter by GITHUB_PR
    pr_history = store.list_history(analysis_type="GITHUB_PR", limit=10)
    assert len(pr_history) >= 1
    for r in pr_history:
        assert r.analysis_type == "GITHUB_PR"

    # Filter by CRITICAL
    crit_history = store.list_history(risk_level="CRITICAL", limit=10)
    assert len(crit_history) >= 1
    for r in crit_history:
        assert r.risk_level == "CRITICAL"


def test_findings_catalog_search_and_filters():
    """Verify universal findings catalog allows keyword searching and severity filters."""
    store = AnalysisSessionStore(max_records=50)

    # Search for "eval"
    eval_findings = store.list_all_findings(search="eval")
    assert len(eval_findings) >= 1
    assert any("eval" in f.title.lower() or "eval" in f.issue_id.lower() for f in eval_findings)

    # Filter by CRITICAL
    crit_findings = store.list_all_findings(severity="CRITICAL")
    assert len(crit_findings) >= 1
    for f in crit_findings:
        assert f.severity == "CRITICAL"


# ---------------------------------------------------------
# API Endpoints Integration Tests
# ---------------------------------------------------------

def test_api_overview_endpoint():
    """Test GET /api/analytics/overview returns valid schema and metrics."""
    resp = client.get("/api/analytics/overview")
    assert resp.status_code == 200
    data = resp.json()

    assert "total_analyses_performed" in data
    assert "average_risk_score" in data
    assert "critical_findings_count" in data
    assert "severity_distribution" in data
    assert "recent_analyses" in data
    assert data["total_analyses_performed"] >= 1


def test_api_history_endpoint():
    """Test GET /api/analytics/history returns array of summary records."""
    resp = client.get("/api/analytics/history?limit=10")
    assert resp.status_code == 200
    data = resp.json()

    assert isinstance(data, list)
    assert len(data) >= 1
    assert "analysis_id" in data[0]
    assert "risk_score" in data[0]


def test_api_session_detail_endpoint():
    """Test GET /api/analytics/history/{analysis_id} deep-dive."""
    resp = client.get("/api/analytics/history/SES-2026-INIT-001")
    assert resp.status_code == 200
    data = resp.json()

    assert data["analysis_id"] == "SES-2026-INIT-001"
    assert data["target_name"] == "payment_gateway.py"
    assert len(data["findings"]) >= 1
    assert len(data["secrets"]) >= 1


def test_api_session_detail_404_not_found():
    """Test GET /api/analytics/history/{invalid_id} returns 404."""
    resp = client.get("/api/analytics/history/SES-NON-EXISTENT-999")
    assert resp.status_code == 404


def test_api_findings_catalog_endpoint():
    """Test GET /api/analytics/findings returns findings with query filtering."""
    resp = client.get("/api/analytics/findings?severity=CRITICAL")
    assert resp.status_code == 200
    data = resp.json()

    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["severity"] == "CRITICAL"
