"""
Comprehensive Unit & Integration Test Suite for Secure Code Ingestion Layer.
"""

import io
import os
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings
from app.utils.temp_storage import get_temp_storage_dir

client = TestClient(app)


# ==============================================================================
# 1. Valid Code Submissions (Python, Java, JavaScript, TypeScript)
# ==============================================================================

def test_valid_python_submission():
    """Verify ingestion of valid Python snippet."""
    payload = {
        "language": "python",
        "filename": "payment.py",
        "content": "def process_payment(amount: float):\n    return {'status': 'success', 'amount': amount}\n"
    }
    response = client.post(f"{settings.API_PREFIX}/code/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ACCEPTED"
    assert data["language"] == "python"
    assert data["filename"] == "payment.py"
    assert data["sanitized_filename"] == "payment.py"
    assert data["line_count"] == 2
    assert len(data["sha256_hash"]) == 64
    assert "submission_id" in data


def test_valid_java_submission():
    """Verify ingestion of valid Java code."""
    payload = {
        "language": "java",
        "filename": "OrderController.java",
        "content": "public class OrderController {\n    public static void main(String[] args) {\n        System.out.println(\"Order processed\");\n    }\n}\n"
    }
    response = client.post(f"{settings.API_PREFIX}/code/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ACCEPTED"
    assert data["language"] == "java"
    assert data["sanitized_filename"] == "OrderController.java"


def test_valid_javascript_submission():
    """Verify ingestion of valid JavaScript code."""
    payload = {
        "filename": "auth.js",
        "content": "const jwt = require('jsonwebtoken');\nfunction verifyToken(token) { return jwt.verify(token, 'secret'); }"
    }
    response = client.post(f"{settings.API_PREFIX}/code/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ACCEPTED"
    assert data["language"] == "javascript"


def test_valid_typescript_submission():
    """Verify ingestion of valid TypeScript code with interface."""
    payload = {
        "filename": "user.ts",
        "content": "interface User {\n    id: string;\n    email: string;\n}\nexport const getUser = (id: string): User => ({ id, email: 'user@test.com' });"
    }
    response = client.post(f"{settings.API_PREFIX}/code/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ACCEPTED"
    assert data["language"] == "typescript"


# ==============================================================================
# 2. File Upload API (/api/code/upload)
# ==============================================================================

def test_file_upload_valid():
    """Verify multipart file upload endpoint."""
    file_content = b"def calculate_tax(subtotal: float) -> float:\n    return subtotal * 0.08\n"
    files = {"file": ("tax_calculator.py", io.BytesIO(file_content), "text/x-python")}
    
    response = client.post(f"{settings.API_PREFIX}/code/upload", files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ACCEPTED"
    assert data["language"] == "python"
    assert data["sanitized_filename"] == "tax_calculator.py"


# ==============================================================================
# 3. Unsupported Files & Languages
# ==============================================================================

@pytest.mark.parametrize("unsupported_filename", [
    "malware.exe",
    "script.sh",
    "document.pdf",
    "archive.zip",
    "image.png",
    "program.bin",
    "data.txt"
])
def test_unsupported_file_extensions(unsupported_filename):
    """Verify rejection of unsupported file extensions."""
    payload = {
        "filename": unsupported_filename,
        "content": "some text content"
    }
    response = client.post(f"{settings.API_PREFIX}/code/analyze", json=payload)
    assert response.status_code == 400
    assert "unsupported file extension" in response.json()["detail"].lower()


def test_unsupported_explicit_language():
    """Verify rejection of unsupported explicit language."""
    payload = {
        "language": "ruby",
        "filename": "test.rb",
        "content": "puts 'hello'"
    }
    response = client.post(f"{settings.API_PREFIX}/code/analyze", json=payload)
    assert response.status_code == 400
    assert "unsupported" in response.json()["detail"].lower()


# ==============================================================================
# 4. Oversized Files & Payloads
# ==============================================================================

def test_oversized_code_character_length():
    """Verify rejection of content exceeding MAX_CODE_LENGTH_CHARS."""
    oversized_content = "a = 1\n" * (settings.MAX_CODE_LENGTH_CHARS // 5 + 1000)
    payload = {
        "filename": "huge.py",
        "content": oversized_content
    }
    response = client.post(f"{settings.API_PREFIX}/code/analyze", json=payload)
    assert response.status_code == 400
    assert "exceeds maximum allowed length" in response.json()["detail"].lower()


def test_oversized_file_upload():
    """Verify rejection of file uploads exceeding MAX_FILE_SIZE_BYTES."""
    oversized_bytes = b"def dummy(): pass\n" * 150000  # > 2.5 MB
    files = {"file": ("large_file.py", io.BytesIO(oversized_bytes), "text/plain")}
    
    response = client.post(f"{settings.API_PREFIX}/code/upload", files=files)
    assert response.status_code == 400
    assert "maximum limit" in response.json()["detail"].lower() or "exceeds" in response.json()["detail"].lower()


# ==============================================================================
# 5. Malicious Filenames & Path Traversal Defenses
# ==============================================================================

@pytest.mark.parametrize("traversal_name,expected_sanitized_base", [
    ("../../../etc/passwd.py", "passwd.py"),
    ("..\\..\\windows\\system32\\cmd.py", "cmd.py"),
    ("CON.py", "safe_con.py"),
    ("AUX.java", "safe_aux.java"),
    ("PRN.ts", "safe_prn.ts"),
    ("malicious\x00payload.py", "maliciouspayload.py"),
    ("/var/log/app/service.py", "service.py"),
])
def test_malicious_filename_sanitization(traversal_name, expected_sanitized_base):
    """Verify that malicious directory traversal and reserved names are safely sanitized."""
    payload = {
        "filename": traversal_name,
        "content": "def test(): return True\n"
    }
    response = client.post(f"{settings.API_PREFIX}/code/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == traversal_name
    assert data["sanitized_filename"] == expected_sanitized_base


# ==============================================================================
# 6. Empty Files & Blank Content
# ==============================================================================

def test_empty_content_rejection():
    """Verify rejection of empty code strings."""
    payload = {
        "filename": "empty.py",
        "content": "   \n\t  "
    }
    response = client.post(f"{settings.API_PREFIX}/code/analyze", json=payload)
    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()


def test_empty_file_upload():
    """Verify rejection of 0-byte file uploads."""
    files = {"file": ("empty.py", io.BytesIO(b""), "text/x-python")}
    response = client.post(f"{settings.API_PREFIX}/code/upload", files=files)
    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()


# ==============================================================================
# 7. Binary Payload Rejection
# ==============================================================================

def test_binary_executable_rejection():
    """Verify rejection of binary files disguised as source code (e.g. ELF header)."""
    payload = {
        "filename": "fake_python.py",
        "content": "\x7fELF\x02\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00"
    }
    response = client.post(f"{settings.API_PREFIX}/code/analyze", json=payload)
    assert response.status_code == 400
    assert "binary" in response.json()["detail"].lower()


def test_null_byte_binary_rejection():
    """Verify rejection of null bytes in uploaded code."""
    payload = {
        "filename": "corrupt.py",
        "content": "def hello():\n    return 'he\x00llo'"
    }
    response = client.post(f"{settings.API_PREFIX}/code/analyze", json=payload)
    assert response.status_code == 400
    assert "binary" in response.json()["detail"].lower() or "null byte" in response.json()["detail"].lower()


# ==============================================================================
# 8. Transient Storage Cleanup Verification
# ==============================================================================

def test_transient_storage_cleanup():
    """Verify that temporary files are deleted immediately after ingestion."""
    temp_dir = get_temp_storage_dir()
    
    # Ingest a valid snippet
    payload = {
        "filename": "cleanup_test.py",
        "content": "print('Checking transient cleanup')\n"
    }
    response = client.post(f"{settings.API_PREFIX}/code/analyze", json=payload)
    assert response.status_code == 200
    
    # Verify no persistent files remain in temp directory
    leftover_files = list(temp_dir.glob("ingest_*"))
    assert len(leftover_files) == 0, f"Expected 0 leftover temp files, found: {leftover_files}"
