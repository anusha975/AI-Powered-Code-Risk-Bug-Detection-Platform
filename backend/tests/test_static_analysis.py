"""
Comprehensive Unit & Integration Test Suite for Local Static Code Analysis Engine.
Tests AST visitor and Bandit SAST rules with safe sample code across all vulnerability classes.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings

client = TestClient(app)


# ==============================================================================
# 1. Dangerous Functions (eval, exec, compile)
# ==============================================================================

def test_eval_exec_detection():
    """Verify detection of eval() and exec() dangerous functions."""
    code = """def dynamic_runner(user_input: str):
    # Dynamic evaluation
    result = eval(user_input)
    exec("print('executed')")
    return result
"""
    response = client.post(f"{settings.API_PREFIX}/analysis/static", json={"filename": "runner.py", "content": code})
    assert response.status_code == 200
    data = response.json()

    assert data["summary"]["total_issues"] >= 2
    assert data["summary"]["critical_count"] >= 2
    
    findings = data["findings"]
    eval_finding = next((f for f in findings if "eval()" in f["title"]), None)
    exec_finding = next((f for f in findings if "exec()" in f["title"]), None)

    assert eval_finding is not None
    assert eval_finding["severity"] == "CRITICAL"
    assert eval_finding["confidence"] >= 0.90
    assert eval_finding["line_number"] == 3
    assert "eval(user_input)" in eval_finding["code_snippet"]

    assert exec_finding is not None
    assert exec_finding["severity"] == "CRITICAL"


# ==============================================================================
# 2. Command Injection Patterns (os.system, subprocess with shell=True)
# ==============================================================================

def test_command_injection_detection():
    """Verify detection of os.system() and subprocess with shell=True."""
    code = """import os
import subprocess

def ping_host(host: str):
    os.system(f"ping {host}")
    subprocess.Popen("echo hello", shell=True)
"""
    response = client.post(f"{settings.API_PREFIX}/analysis/static", json={"filename": "net_utils.py", "content": code})
    assert response.status_code == 200
    data = response.json()

    findings = data["findings"]
    os_finding = next((f for f in findings if "os.system" in f["title"]), None)
    subp_finding = next((f for f in findings if "shell=True" in f["title"]), None)

    assert os_finding is not None
    assert os_finding["severity"] == "CRITICAL"
    assert subp_finding is not None
    assert subp_finding["severity"] == "CRITICAL"


# ==============================================================================
# 3. SQL Injection Patterns
# ==============================================================================

def test_sql_injection_detection():
    """Verify detection of dynamic f-string formatting in SQL execute calls."""
    code = """def get_user_records(cursor, user_id: str):
    # Formatted SQL execution
    query = cursor.execute(f"SELECT * FROM users WHERE id = '{user_id}'")
    return query.fetchall()
"""
    response = client.post(f"{settings.API_PREFIX}/analysis/static", json={"filename": "user_repo.py", "content": code})
    assert response.status_code == 200
    data = response.json()

    sql_finding = next((f for f in data["findings"] if "SQL Injection" in f["title"]), None)
    assert sql_finding is not None
    assert sql_finding["severity"] == "HIGH"
    assert sql_finding["line_number"] == 3
    assert "parameterized queries" in sql_finding["recommendation"].lower()


# ==============================================================================
# 4. Unsafe Deserialization (pickle)
# ==============================================================================

def test_unsafe_pickle_deserialization():
    """Verify detection of unsafe pickle.loads() calls."""
    code = """import pickle

def load_user_session(raw_bytes: bytes):
    return pickle.loads(raw_bytes)
"""
    response = client.post(f"{settings.API_PREFIX}/analysis/static", json={"filename": "session.py", "content": code})
    assert response.status_code == 200
    data = response.json()

    pickle_finding = next((f for f in data["findings"] if "pickle" in f["title"].lower()), None)
    assert pickle_finding is not None
    assert pickle_finding["severity"] in ["CRITICAL", "HIGH"]
    assert pickle_finding["line_number"] == 4


# ==============================================================================
# 5. Weak Cryptography & Insecure Hashes (MD5, SHA1, SSL)
# ==============================================================================

def test_weak_crypto_and_ssl():
    """Verify detection of broken MD5 hashing and unverified SSL context."""
    code = """import hashlib
import ssl

def hash_data(data: bytes):
    ctx = ssl._create_unverified_context()
    return hashlib.md5(data).hexdigest()
"""
    response = client.post(f"{settings.API_PREFIX}/analysis/static", json={"filename": "crypto_ops.py", "content": code})
    assert response.status_code == 200
    data = response.json()

    findings = data["findings"]
    md5_finding = next((f for f in findings if "MD5" in f["title"] or "md5" in f["title"].lower()), None)
    ssl_finding = next((f for f in findings if "SSL" in f["title"]), None)

    assert md5_finding is not None
    assert md5_finding["severity"] in ["MEDIUM", "HIGH"]
    assert ssl_finding is not None
    assert ssl_finding["severity"] in ["MEDIUM", "HIGH"]


# ==============================================================================
# 6. Broad & Empty Exception Handling
# ==============================================================================

def test_exception_handling_flaws():
    """Verify detection of broad and empty 'except: pass' clauses."""
    code = """def process_items(items):
    try:
        val = items[0]
    except Exception:
        pass
"""
    response = client.post(f"{settings.API_PREFIX}/analysis/static", json={"filename": "handler.py", "content": code})
    assert response.status_code == 200
    data = response.json()

    empty_finding = next((f for f in data["findings"] if "empty exception" in f["title"].lower() or "pass" in f["title"].lower()), None)
    assert empty_finding is not None
    assert empty_finding["category"] == "ERROR_HANDLING"


# ==============================================================================
# 7. Suspicious Imports
# ==============================================================================

def test_suspicious_imports():
    """Verify detection of legacy/unencrypted protocol imports."""
    code = """import telnetlib
import ftplib

def connect_remote():
    pass
"""
    response = client.post(f"{settings.API_PREFIX}/analysis/static", json={"filename": "legacy.py", "content": code})
    assert response.status_code == 200
    data = response.json()

    import_findings = [f for f in data["findings"] if "unencrypted protocol" in f["title"].lower() or "telnetlib" in f["title"].lower() or "ftplib" in f["title"].lower()]
    assert len(import_findings) >= 1


# ==============================================================================
# 8. Deeply Nested Code & Excessive Complexity
# ==============================================================================

def test_deeply_nested_code():
    """Verify detection of nested control blocks (depth >= 4)."""
    code = """def deeply_nested_function(a, b, c, d):
    if a:
        if b:
            if c:
                if d:
                    return True
    return False
"""
    response = client.post(f"{settings.API_PREFIX}/analysis/static", json={"filename": "nested.py", "content": code})
    assert response.status_code == 200
    data = response.json()

    nest_finding = next((f for f in data["findings"] if "nested" in f["title"].lower()), None)
    assert nest_finding is not None
    assert nest_finding["category"] == "CODE_QUALITY"


# ==============================================================================
# 9. Clean Safe Code Test
# ==============================================================================

def test_clean_safe_code():
    """Verify clean, secure code produces 0 findings and a risk score of 0.0."""
    code = """def calculate_total(prices: list[float], tax_rate: float) -> float:
    \"\"\"Calculate invoice total with tax.\"\"\"
    subtotal = sum(prices)
    return round(subtotal * (1.0 + tax_rate), 2)
"""
    response = client.post(f"{settings.API_PREFIX}/analysis/static", json={"filename": "invoice.py", "content": code})
    assert response.status_code == 200
    data = response.json()

    assert data["summary"]["total_issues"] == 0
    assert data["summary"]["risk_score"] == 0.0
    assert len(data["findings"]) == 0
    assert "disclaimer" in data


# ==============================================================================
# 10. Normalized Finding Schema Conformance
# ==============================================================================

def test_normalized_finding_schema_contract():
    """Verify all findings conform strictly to the normalized schema contract."""
    code = """import os
def run():
    os.system("ls")
"""
    response = client.post(f"{settings.API_PREFIX}/analysis/static", json={"filename": "test.py", "content": code})
    assert response.status_code == 200
    finding = response.json()["findings"][0]

    # Required contract fields
    assert "issue_id" in finding
    assert "title" in finding
    assert "category" in finding
    assert finding["severity"] in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    assert isinstance(finding["confidence"], (int, float))
    assert 0.0 <= finding["confidence"] <= 1.0
    assert "file" in finding
    assert "line_number" in finding
    assert "code_snippet" in finding
    assert "recommendation" in finding
    assert "analyzer" in finding
