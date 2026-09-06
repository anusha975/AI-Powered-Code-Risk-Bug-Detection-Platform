"""
Comprehensive Unit & Integration Test Suite for Secret Detection & Privacy Protection Engine.
Strictly verifies that no raw secrets appear in sanitized code or API responses.
"""

import json
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings

client = TestClient(app)


# Sample Secret Fixtures for Verification
SAMPLE_SECRETS = {
    "AWS_KEY": "AKIAIOSFODNN7EXAMPLE",
    "GITHUB_TOKEN": "ghp_1234567890abcdefghijklmnopqrstuvwxyzAB",
    "OPENAI_KEY": "sk-proj-abc123456789012345678901234567890123456789012345",
    "STRIPE_KEY": "sk_test_51MockDemoKey00000000000000000000",
    "GOOGLE_KEY": "AIzaSyD2AbcDefGhIjKlMnOpQrStUvWxYz01234",
    "SLACK_TOKEN": "xoxb" + "-123456789012" + "-1234567890123" + "-MockSlackToken123456789",
    "JWT_TOKEN": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c",
    "DB_URI": "postgresql://postgres:superSecretDbPass123@db.prod.internal:5432/finance_db",
    "PASSWORD": "UltraSecretMasterPassword99!",
    "PRIVATE_KEY": "-----BEGIN RSA PRIVATE KEY-----\nMIIEowIBAAKCAQEA0Y3y1...\n-----END RSA PRIVATE KEY-----"
}


# ==============================================================================
# 1. AWS Key Redaction Test
# ==============================================================================

def test_aws_access_key_detection_and_redaction():
    """Verify AWS Access Key ID is detected and replaced with [REDACTED_AWS_ACCESS_KEY]."""
    raw_secret = SAMPLE_SECRETS["AWS_KEY"]
    code = f'AWS_ACCESS_KEY_ID = "{raw_secret}"\ndef connect_s3(): pass\n'

    response = client.post(f"{settings.API_PREFIX}/security/scan", json={"filename": "aws_config.py", "content": code})
    assert response.status_code == 200
    data = response.json()

    # Verify detection
    assert data["secrets_detected_count"] == 1
    assert data["redaction_applied"] is True
    finding = data["findings"][0]
    assert finding["secret_type"] == "AWS_ACCESS_KEY"
    assert finding["line_number"] == 1
    assert finding["placeholder"] == "[REDACTED_AWS_ACCESS_KEY]"

    # Verify sanitized content
    assert f'AWS_ACCESS_KEY_ID = "[REDACTED_AWS_ACCESS_KEY]"' in data["sanitized_content"]

    # ZERO LEAKAGE ASSERTION
    assert raw_secret not in data["sanitized_content"]
    assert raw_secret not in json.dumps(data)


# ==============================================================================
# 2. Database Connection URI Redaction Test
# ==============================================================================

def test_database_uri_detection_and_redaction():
    """Verify database connection URI with embedded password is fully redacted."""
    raw_uri = SAMPLE_SECRETS["DB_URI"]
    code = f'DATABASE_URL = "{raw_uri}"\nengine = create_engine(DATABASE_URL)\n'

    response = client.post(f"{settings.API_PREFIX}/security/scan", json={"filename": "db.py", "content": code})
    assert response.status_code == 200
    data = response.json()

    assert data["secrets_detected_count"] == 1
    assert data["findings"][0]["secret_type"] == "DATABASE_URI"
    assert data["findings"][0]["placeholder"] == "[REDACTED_DATABASE_URI]"

    # Verify zero secret leakage
    assert raw_uri not in data["sanitized_content"]
    assert "superSecretDbPass123" not in data["sanitized_content"]
    assert "superSecretDbPass123" not in json.dumps(data)


# ==============================================================================
# 3. GitHub and SaaS API Tokens Test
# ==============================================================================

def test_github_token_redaction():
    """Verify GitHub Personal Access Token is detected and redacted."""
    raw_token = SAMPLE_SECRETS["GITHUB_TOKEN"]
    code = f'GITHUB_TOKEN = "{raw_token}"\n'

    response = client.post(f"{settings.API_PREFIX}/security/scan", json={"filename": "ci.py", "content": code})
    assert response.status_code == 200
    data = response.json()

    assert data["secrets_detected_count"] == 1
    assert data["findings"][0]["secret_type"] == "GITHUB_TOKEN"
    assert raw_token not in data["sanitized_content"]
    assert raw_token not in json.dumps(data)


def test_openai_api_key_redaction():
    """Verify OpenAI API Key is detected and redacted."""
    raw_key = SAMPLE_SECRETS["OPENAI_KEY"]
    code = f'client = OpenAI(api_key="{raw_key}")\n'

    response = client.post(f"{settings.API_PREFIX}/security/scan", json={"filename": "llm.py", "content": code})
    assert response.status_code == 200
    data = response.json()

    assert data["secrets_detected_count"] == 1
    assert data["findings"][0]["secret_type"] == "OPENAI_API_KEY"
    assert raw_key not in data["sanitized_content"]
    assert raw_key not in json.dumps(data)


def test_stripe_api_key_redaction():
    """Verify Stripe Live API Key is detected and redacted."""
    raw_key = SAMPLE_SECRETS["STRIPE_KEY"]
    code = f'stripe.api_key = "{raw_key}"\n'

    response = client.post(f"{settings.API_PREFIX}/security/scan", json={"filename": "billing.py", "content": code})
    assert response.status_code == 200
    data = response.json()

    assert data["secrets_detected_count"] == 1
    assert data["findings"][0]["secret_type"] == "STRIPE_KEY"
    assert raw_key not in data["sanitized_content"]
    assert raw_key not in json.dumps(data)


# ==============================================================================
# 4. JSON Web Token (JWT) Test
# ==============================================================================

def test_jwt_token_redaction():
    """Verify JWT token is detected and replaced with [REDACTED_JWT_TOKEN]."""
    raw_jwt = SAMPLE_SECRETS["JWT_TOKEN"]
    code = f'auth_header = "Bearer {raw_jwt}"\n'

    response = client.post(f"{settings.API_PREFIX}/security/scan", json={"filename": "auth.js", "content": code})
    assert response.status_code == 200
    data = response.json()

    assert data["secrets_detected_count"] == 1
    assert data["findings"][0]["secret_type"] == "JWT_TOKEN"
    assert raw_jwt not in data["sanitized_content"]
    assert raw_jwt not in json.dumps(data)


# ==============================================================================
# 5. Private Key Block Test
# ==============================================================================

def test_private_key_block_redaction():
    """Verify RSA/OpenSSH Private Key block is completely redacted."""
    raw_key = SAMPLE_SECRETS["PRIVATE_KEY"]
    code = f'SERVER_KEY = """{raw_key}"""\n'

    response = client.post(f"{settings.API_PREFIX}/security/scan", json={"filename": "crypto.py", "content": code})
    assert response.status_code == 200
    data = response.json()

    assert data["secrets_detected_count"] == 1
    assert data["findings"][0]["secret_type"] == "PRIVATE_KEY"
    assert "BEGIN RSA PRIVATE KEY" not in data["sanitized_content"]
    assert "MIIEowIBAAKCAQEA0Y3y1" not in data["sanitized_content"]
    assert "[REDACTED_PRIVATE_KEY]" in data["sanitized_content"]


# ==============================================================================
# 6. Hardcoded Password Test
# ==============================================================================

def test_hardcoded_password_redaction():
    """Verify hardcoded password assignments are detected and redacted."""
    raw_pass = SAMPLE_SECRETS["PASSWORD"]
    code = f'db_password = "{raw_pass}"\n'

    response = client.post(f"{settings.API_PREFIX}/security/scan", json={"filename": "config.py", "content": code})
    assert response.status_code == 200
    data = response.json()

    assert data["secrets_detected_count"] == 1
    assert data["findings"][0]["secret_type"] == "PASSWORD"
    assert raw_pass not in data["sanitized_content"]
    assert raw_pass not in json.dumps(data)


# ==============================================================================
# 7. Multi-Secret File Test
# ==============================================================================

def test_multiple_secrets_in_single_file():
    """Verify a file with multiple diverse secrets redacts all instances accurately."""
    aws_key = SAMPLE_SECRETS["AWS_KEY"]
    github_tok = SAMPLE_SECRETS["GITHUB_TOKEN"]
    db_uri = SAMPLE_SECRETS["DB_URI"]

    code = f"""import os

# Cloud Configuration
AWS_KEY = "{aws_key}"
GH_TOKEN = "{github_tok}"
DB = "{db_uri}"

def start():
    pass
"""

    response = client.post(f"{settings.API_PREFIX}/security/scan", json={"filename": "service.py", "content": code})
    assert response.status_code == 200
    data = response.json()

    assert data["secrets_detected_count"] == 3
    assert data["redaction_applied"] is True
    assert len(data["findings"]) == 3

    # Check that each raw secret is purged from the response
    for secret in [aws_key, github_tok, db_uri]:
        assert secret not in data["sanitized_content"]
        assert secret not in json.dumps(data)


# ==============================================================================
# 8. Clean Code Without Secrets Test
# ==============================================================================

def test_clean_code_without_secrets():
    """Verify clean code without secrets is returned unmodified with 0 findings."""
    clean_code = """def add_numbers(a: int, b: int) -> int:
    # Calculate sum of two integers
    return a + b

class MathService:
    def multiply(self, x: float, y: float) -> float:
        return x * y
"""
    response = client.post(f"{settings.API_PREFIX}/security/scan", json={"filename": "math_utils.py", "content": clean_code})
    assert response.status_code == 200
    data = response.json()

    assert data["secrets_detected_count"] == 0
    assert data["redaction_applied"] is False
    assert len(data["findings"]) == 0
    assert data["sanitized_content"] == clean_code
