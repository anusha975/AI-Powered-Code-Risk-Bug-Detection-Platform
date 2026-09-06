"""
Test Suite for Module 5: Code Risk Scoring Engine & ML Pipeline.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.ml.feature_extractor import extract_features, feature_dict_to_vector, FEATURE_NAMES
from app.ml.preprocessor import FeaturePreprocessor
from app.ml.model_trainer import RiskModelTrainer, get_risk_model_trainer
from app.ml.inference import infer_risk_score, calculate_deterministic_score, map_score_to_risk_level
from app.services.risk_service import RiskService
from app.schemas.risk import RiskLevel


@pytest.fixture
def client():
    return TestClient(app)


def test_feature_names_dimension():
    """Verify that feature dimension is exactly 16."""
    assert len(FEATURE_NAMES) == 16


def test_feature_extraction_clean_code():
    """Extract features from clean code with 0 findings."""
    code = "def add(a: int, b: int) -> int:\n    return a + b\n"
    features = extract_features(content=code, findings=[], secrets_count=0)

    assert features["critical_findings_count"] == 0.0
    assert features["high_findings_count"] == 0.0
    assert features["has_secrets_flag"] == 0.0
    assert features["cyclomatic_complexity"] >= 1.0
    assert len(feature_dict_to_vector(features)) == 16


def test_feature_extraction_vulnerable_code():
    """Extract features when critical findings and secrets are present."""
    code = "def run(cmd):\n    eval(cmd)\n"
    findings = [
        {
            "issue_id": "AST-SEC-001",
            "title": "Dangerous Dynamic Code Execution (eval)",
            "category": "SECURITY",
            "severity": "CRITICAL",
            "confidence": 1.0,
            "analyzer": "ast"
        }
    ]
    features = extract_features(content=code, findings=findings, secrets_count=1)

    assert features["critical_findings_count"] == 1.0
    assert features["security_category_count"] == 1.0
    assert features["has_secrets_flag"] == 1.0
    assert features["max_finding_confidence"] == 1.0


def test_preprocessor_fitting_and_transform():
    """Verify FeaturePreprocessor scales data properly without NaN."""
    preprocessor = FeaturePreprocessor()
    X_synthetic = [
        [0.0] * 16,
        [1.0] * 16,
        [2.0, 1.0, 3.0, 0.0, 2.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.9, 0.8, 5.0, 3.0, 10.0, 1.0]
    ]
    X_scaled = preprocessor.fit_transform(X_synthetic)

    assert X_scaled.shape == (3, 16)
    assert not any(any(val != val for val in row) for row in X_scaled)  # No NaNs


def test_model_trainer_synthetic_evaluation():
    """Verify that RiskModelTrainer trains and achieves high synthetic R2 score."""
    trainer = RiskModelTrainer(random_state=42)
    metrics = trainer.train(n_samples=500)

    assert trainer.is_trained is True
    assert "r2_score" in metrics
    assert metrics["r2_score"] >= 0.85
    assert metrics["mae"] < 10.0


def test_deterministic_baseline_scoring():
    """Verify deterministic scoring calculations and floor enforcement."""
    clean_features = {
        "critical_findings_count": 0.0,
        "high_findings_count": 0.0,
        "medium_findings_count": 0.0,
        "low_findings_count": 0.0,
        "cyclomatic_complexity": 1.0,
        "max_nesting_depth": 0.0,
        "has_secrets_flag": 0.0,
        "finding_density_per_100_lines": 0.0
    }
    score, reasons = calculate_deterministic_score(clean_features, findings=[], secrets_count=0)
    assert score == 0.0
    assert any("Clean code profile" in r for r in reasons)

    vuln_features = {
        "critical_findings_count": 1.0,
        "high_findings_count": 1.0,
        "medium_findings_count": 0.0,
        "low_findings_count": 0.0,
        "cyclomatic_complexity": 5.0,
        "max_nesting_depth": 2.0,
        "has_secrets_flag": 1.0,
        "finding_density_per_100_lines": 25.0
    }
    v_score, v_reasons = calculate_deterministic_score(vuln_features, findings=[{}], secrets_count=1)
    assert v_score >= 80.0
    assert any("critical-severity" in r for r in v_reasons)
    assert any("secrets/credentials" in r for r in v_reasons)


def test_risk_level_mapping():
    """Verify score to RiskLevel enum mapping."""
    assert map_score_to_risk_level(10.0) == RiskLevel.LOW
    assert map_score_to_risk_level(35.0) == RiskLevel.MEDIUM
    assert map_score_to_risk_level(65.0) == RiskLevel.HIGH
    assert map_score_to_risk_level(90.0) == RiskLevel.CRITICAL


def test_end_to_end_risk_clean_code():
    """End-to-end risk evaluation for clean Python code."""
    code = """
def calculate_sum(a: int, b: int) -> int:
    # Pure clean math function
    return a + b
"""
    result = RiskService.calculate_risk(content=code, filename="math_utils.py")
    assert result.risk_score <= 15
    assert result.risk_level == RiskLevel.LOW
    assert len(result.reasons) > 0
    assert result.breakdown.total_findings_count == 0


def test_end_to_end_risk_critical_code():
    """End-to-end risk evaluation for critical RCE vulnerability."""
    code = """
import os

def execute_payload(user_input):
    eval(user_input)
    os.system(user_input)
"""
    result = RiskService.calculate_risk(content=code, filename="payload.py")
    assert result.risk_score >= 80
    assert result.risk_level == RiskLevel.CRITICAL
    assert any("critical" in r.lower() for r in result.reasons)


def test_end_to_end_risk_secret_exposure():
    """End-to-end risk evaluation for exposed API credentials."""
    code = """
AWS_ACCESS_KEY = "AKIA1234567890EXAMPLE"
AWS_SECRET = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"

def fetch_data():
    pass
"""
    result = RiskService.calculate_risk(content=code, filename="credentials.py")
    assert result.risk_score >= 75
    assert result.risk_level in (RiskLevel.HIGH, RiskLevel.CRITICAL)
    assert result.breakdown.secrets_detected_count >= 1


def test_api_risk_score_endpoint(client):
    """Test POST /api/risk/score endpoint."""
    payload = {
        "content": "def divide(a, b):\n    try:\n        return a / b\n    except:\n        pass\n",
        "filename": "calc.py",
        "language": "python"
    }
    response = client.post("/api/risk/score", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert "risk_score" in data
    assert "risk_level" in data
    assert "reasons" in data
    assert "breakdown" in data
    assert "model_metadata" in data
    assert isinstance(data["risk_score"], int)
    assert len(data["reasons"]) > 0


def test_api_risk_score_v1_endpoint(client):
    """Test POST /api/v1/risk/score versioned endpoint."""
    payload = {
        "content": "def hello():\n    return 'world'\n",
        "filename": "hello.py"
    }
    response = client.post("/api/v1/risk/score", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["risk_level"] == "LOW"
