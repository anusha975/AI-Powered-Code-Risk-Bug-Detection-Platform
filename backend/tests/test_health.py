"""
Unit Tests for Health Check & Diagnostics Endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings

client = TestClient(app)


def test_root_endpoint():
    """Verify root landing endpoint returns operational status."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["app"] == settings.APP_NAME
    assert data["status"] == "OPERATIONAL"
    assert data["docs_url"] == "/docs"
    assert data["health_endpoint"] == f"{settings.API_PREFIX}/health"


def test_api_health_endpoint():
    """Verify /api/health returns 200 and conforms to HealthResponse schema."""
    response = client.get(f"{settings.API_PREFIX}/health")
    assert response.status_code == 200
    data = response.json()
    
    # Assert core fields
    assert "status" in data
    assert data["app_name"] == settings.APP_NAME
    assert data["version"] == settings.APP_VERSION
    assert data["environment"] == settings.ENVIRONMENT
    assert "uptime_seconds" in data
    assert "timestamp" in data
    
    # Assert database telemetry
    assert "database" in data
    assert data["database"]["database_type"] == "PostgreSQL"
    assert data["database"]["status"] in ["CONNECTED", "DISCONNECTED"]
    
    # Assert privacy guardrails
    assert "privacy_guardrails" in data
    assert data["privacy_guardrails"]["analysis_mode"] == "LOCAL_STATIC_ONLY"
    assert data["privacy_guardrails"]["secret_redaction_enforced"] is True
    assert data["privacy_guardrails"]["remote_llm_allowed"] is False
    assert data["privacy_guardrails"]["max_snippet_lines"] == 50
    
    # Assert module list
    assert "active_modules" in data
    assert len(data["active_modules"]) > 0
    assert data["active_modules"][0]["id"] == "module-1"
    assert data["active_modules"][0]["status"] == "ACTIVE"


def test_api_v1_health_endpoint():
    """Verify /api/v1/health is equivalent to /api/health."""
    response = client.get(f"{settings.API_PREFIX}/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["app_name"] == settings.APP_NAME
    assert "uptime_seconds" in data
