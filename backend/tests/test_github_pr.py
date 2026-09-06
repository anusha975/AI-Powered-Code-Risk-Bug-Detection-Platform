"""
Unit & Integration Tests for Module 10: GitHub Pull Request Security & Risk Analysis.
"""

import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from app.main import app
from app.github.client import GitHubClient, GitHubPRMetadata, GitHubFileChange, mask_token
from app.github.diff_parser import DiffParser
from app.services.github_pr_service import GitHubPRService
from app.schemas.github_pr import PRAnalysisRequest, PRUrlParseRequest


client = TestClient(app)


# Sample Mock Diffs
VULNERABLE_SQLI_PATCH = """@@ -1,5 +1,11 @@
 def get_user_records(request, cursor):
     user_id = request.GET.get('id')
+    # Query database directly
+    query = "SELECT * FROM users WHERE id = '" + user_id + "'"
+    cursor.execute(query)
+    results = cursor.fetchall()
+    return results
"""

SECRET_EXPOSURE_PATCH = """@@ -1,4 +1,6 @@
 import os
+AWS_SECRET_KEY = "AKIA1234567890ABCDEF1234567890ABCDEF12"
+DATABASE_PASSWORD = "SuperSecretPassword123!"
 
 def connect():
     pass
"""

CLEAN_REFACTOR_PATCH = """@@ -1,5 +1,8 @@
 def calculate_discount(price, rate):
-    return price * (1 - rate)
+    # Safe discount computation with validation
+    if rate < 0 or rate > 1:
+        raise ValueError("Invalid rate")
+    return round(price * (1.0 - rate), 2)
"""



# ---------------------------------------------------------
# Unit Tests: URL Parsing & Diff Parsing
# ---------------------------------------------------------

def test_parse_pr_url_valid():
    """Verify URL parser extracts owner, repo, and PR number correctly."""
    owner, repo, pr_no = GitHubClient.parse_pr_url("https://github.com/octocat/Hello-World/pull/42")
    assert owner == "octocat"
    assert repo == "Hello-World"
    assert pr_no == 42

    owner2, repo2, pr_no2 = GitHubClient.parse_pr_url("https://github.com/org/security-platform/pull/1089/")
    assert owner2 == "org"
    assert repo2 == "security-platform"
    assert pr_no2 == 1089

    owner3, repo3, pr_no3 = GitHubClient.parse_pr_url("org/repo#99")
    assert owner3 == "org"
    assert repo3 == "repo"
    assert pr_no3 == 99


def test_parse_pr_url_invalid():
    """Verify parser rejects malformed and non-GitHub URLs."""
    with pytest.raises(ValueError):
        GitHubClient.parse_pr_url("https://gitlab.com/owner/repo/merge_requests/1")

    with pytest.raises(ValueError):
        GitHubClient.parse_pr_url("not-a-valid-url")

    with pytest.raises(ValueError):
        GitHubClient.parse_pr_url("https://github.com/owner/repo")


def test_token_masking():
    """Verify sensitive tokens are masked."""
    assert mask_token("ghp_1234567890abcdefghijklmnopqrstuvwxyz") == "ghp_****wxyz"
    assert mask_token(None) == "[NO_TOKEN]"
    assert mask_token("") == "[NO_TOKEN]"
    assert mask_token("short") == "****"


def test_diff_parser_extracts_hunks_and_maps_lines():
    """Verify unified diff parser extracts additions and maps line numbers."""
    parsed = DiffParser.parse_patch("app/db.py", VULNERABLE_SQLI_PATCH)
    assert parsed.is_supported_source is True
    assert parsed.added_lines_count == 5
    assert "SELECT * FROM users WHERE id" in parsed.added_code_content
    assert len(parsed.line_number_mapping) > 0



def test_diff_parser_filters_ignored_files():
    """Verify lockfiles, binaries, and generated assets are marked non-scannable."""
    assert DiffParser.is_ignorable_file("package-lock.json") is True
    assert DiffParser.is_ignorable_file("yarn.lock") is True
    assert DiffParser.is_ignorable_file("assets/logo.png") is True
    assert DiffParser.is_ignorable_file("node_modules/axios/index.js") is True
    assert DiffParser.is_ignorable_file(".git/config") is True
    assert DiffParser.is_ignorable_file("app/main.py") is False


# ---------------------------------------------------------
# Integration Tests: PR Security Analysis Pipeline
# ---------------------------------------------------------

@pytest.mark.asyncio
async def test_github_pr_analysis_high_risk_pr():
    """Verify PR with SQL injection and hardcoded secret generates high risk score and findings."""
    mock_meta = GitHubPRMetadata(
        owner="test-org",
        repo="vulnerable-service",
        pull_number=101,
        title="Add user query and AWS config",
        author="alice",
        state="open",
        html_url="https://github.com/test-org/vulnerable-service/pull/101",
        base_branch="main",
        head_branch="feature/user-query",
        additions=8,
        deletions=0,
        changed_files=2,
        created_at="2026-09-06T10:00:00Z",
        updated_at="2026-09-06T10:30:00Z"
    )

    mock_files = [
        GitHubFileChange(
            filename="app/db.py",
            status="modified",
            additions=6,
            deletions=0,
            changes=6,
            patch=VULNERABLE_SQLI_PATCH,
            raw_url=None
        ),
        GitHubFileChange(
            filename="config/aws.py",
            status="added",
            additions=2,
            deletions=0,
            changes=2,
            patch=SECRET_EXPOSURE_PATCH,
            raw_url=None
        )
    ]

    with patch("app.github.client.github_client.get_pr_metadata", return_value=mock_meta), \
         patch("app.github.client.github_client.get_pr_files", return_value=mock_files):

        req = PRAnalysisRequest(
            pr_url="https://github.com/test-org/vulnerable-service/pull/101",
            analysis_mode="REDACTED_HYBRID",
            enable_rag=True
        )

        response = await GitHubPRService.analyze_pull_request(req)

        assert response.pr_number == 101
        assert response.repository == "test-org/vulnerable-service"
        assert response.scanned_files_count == 2
        assert response.findings_count > 0
        assert response.secrets_detected_count > 0
        assert response.overall_risk_score >= 80.0
        assert response.overall_risk_level == "CRITICAL"
        assert len(response.risk_reasons) > 0
        assert len(response.files) == 2


@pytest.mark.asyncio
async def test_github_pr_analysis_clean_pr():
    """Verify clean PR with safe refactoring returns low risk score."""
    mock_meta = GitHubPRMetadata(
        owner="test-org",
        repo="clean-service",
        pull_number=45,
        title="Refactor discount calculation",
        author="bob",
        state="open",
        html_url="https://github.com/test-org/clean-service/pull/45",
        base_branch="main",
        head_branch="refactor/discount",
        additions=4,
        deletions=1,
        changed_files=1,
        created_at="2026-09-06T11:00:00Z",
        updated_at="2026-09-06T11:15:00Z"
    )

    mock_files = [
        GitHubFileChange(
            filename="app/pricing.py",
            status="modified",
            additions=4,
            deletions=1,
            changes=5,
            patch=CLEAN_REFACTOR_PATCH,
            raw_url=None
        )
    ]

    with patch("app.github.client.github_client.get_pr_metadata", return_value=mock_meta), \
         patch("app.github.client.github_client.get_pr_files", return_value=mock_files):

        req = PRAnalysisRequest(
            owner="test-org",
            repo="clean-service",
            pull_number=45,
            analysis_mode="REDACTED_HYBRID"
        )

        response = await GitHubPRService.analyze_pull_request(req)

        assert response.pr_number == 45
        assert response.secrets_detected_count == 0
        assert response.overall_risk_score < 40.0
        assert response.overall_risk_level in ("LOW", "MEDIUM")


@pytest.mark.asyncio
async def test_github_pr_analysis_multi_file_with_ignored():
    """Verify PR containing lockfiles and non-code assets ignores non-code files."""
    mock_meta = GitHubPRMetadata(
        owner="test-org",
        repo="frontend-app",
        pull_number=12,
        title="Update dependencies and docs",
        author="carol",
        state="open",
        html_url="https://github.com/test-org/frontend-app/pull/12",
        base_branch="main",
        head_branch="chore/deps",
        additions=500,
        deletions=200,
        changed_files=2,
        created_at="2026-09-06T11:00:00Z",
        updated_at="2026-09-06T11:15:00Z"
    )

    mock_files = [
        GitHubFileChange(
            filename="package-lock.json",
            status="modified",
            additions=490,
            deletions=200,
            changes=690,
            patch="@@ -1,5 +1,10 @@\n- old\n+ new",
            raw_url=None
        ),
        GitHubFileChange(
            filename="app/utils.py",
            status="modified",
            additions=10,
            deletions=0,
            changes=10,
            patch=CLEAN_REFACTOR_PATCH,
            raw_url=None
        )
    ]

    with patch("app.github.client.github_client.get_pr_metadata", return_value=mock_meta), \
         patch("app.github.client.github_client.get_pr_files", return_value=mock_files):

        req = PRAnalysisRequest(pr_url="https://github.com/test-org/frontend-app/pull/12")
        response = await GitHubPRService.analyze_pull_request(req)

        assert response.changed_files_count == 2
        assert response.scanned_files_count == 1  # Only app/utils.py was scanned
        # Lockfile entry exists in files but is marked is_scanned=False
        lock_file = next(f for f in response.files if f.filename == "package-lock.json")
        assert lock_file.is_scanned is False


@pytest.mark.asyncio
async def test_github_pr_no_llm_mode():
    """Verify analysis works in LOCAL_STATIC_ONLY mode with zero AI remediation calls."""
    mock_meta = GitHubPRMetadata(
        owner="test-org",
        repo="sec-app",
        pull_number=1,
        title="Test PR",
        author="dev",
        state="open",
        html_url="https://github.com/test-org/sec-app/pull/1",
        base_branch="main",
        head_branch="test",
        additions=6,
        deletions=0,
        changed_files=1,
        created_at="2026-09-06T11:00:00Z",
        updated_at="2026-09-06T11:15:00Z"
    )
    mock_files = [
        GitHubFileChange(
            filename="app/db.py",
            status="modified",
            additions=6,
            deletions=0,
            changes=6,
            patch=VULNERABLE_SQLI_PATCH,
            raw_url=None
        )
    ]

    with patch("app.github.client.github_client.get_pr_metadata", return_value=mock_meta), \
         patch("app.github.client.github_client.get_pr_files", return_value=mock_files):

        req = PRAnalysisRequest(
            pr_url="https://github.com/test-org/sec-app/pull/1",
            analysis_mode="LOCAL_STATIC_ONLY"
        )
        response = await GitHubPRService.analyze_pull_request(req)

        assert response.findings_count > 0
        assert response.overall_risk_score >= 40.0
        assert len(response.remediations) == 0  # Zero AI remediations generated in local-only mode



# ---------------------------------------------------------
# API Endpoints Test
# ---------------------------------------------------------

def test_api_parse_pr_url_endpoint():
    """Test POST /api/github/pr/parse-url endpoint."""
    resp = client.post(
        "/api/github/pr/parse-url",
        json={"pr_url": "https://github.com/octocat/Spoon-Knife/pull/50"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["valid"] is True
    assert data["owner"] == "octocat"
    assert data["repo"] == "Spoon-Knife"
    assert data["pull_number"] == 50


def test_api_parse_pr_url_invalid_endpoint():
    """Test POST /api/github/pr/parse-url with invalid URL."""
    resp = client.post(
        "/api/github/pr/parse-url",
        json={"pr_url": "invalid-url"}
    )
    assert resp.status_code == 400


def test_api_analyze_pr_endpoint_mocked():
    """Test POST /api/github/pr/analyze endpoint with mocked GitHub API client."""
    mock_meta = GitHubPRMetadata(
        owner="demo-org",
        repo="api-demo",
        pull_number=7,
        title="Demo PR",
        author="dave",
        state="open",
        html_url="https://github.com/demo-org/api-demo/pull/7",
        base_branch="main",
        head_branch="demo-feature",
        additions=4,
        deletions=1,
        changed_files=1,
        created_at="2026-09-06T11:00:00Z",
        updated_at="2026-09-06T11:15:00Z"
    )
    mock_files = [
        GitHubFileChange(
            filename="app/calc.py",
            status="modified",
            additions=4,
            deletions=1,
            changes=5,
            patch=CLEAN_REFACTOR_PATCH,
            raw_url=None
        )
    ]

    with patch("app.github.client.github_client.get_pr_metadata", return_value=mock_meta), \
         patch("app.github.client.github_client.get_pr_files", return_value=mock_files):

        resp = client.post(
            "/api/github/pr/analyze",
            json={
                "pr_url": "https://github.com/demo-org/api-demo/pull/7",
                "enable_rag": True
            },
            headers={"X-GitHub-Token": "ghp_mocktoken1234567890"}
        )

        assert resp.status_code == 200
        data = resp.json()
        assert data["pr_number"] == 7
        assert data["repository"] == "demo-org/api-demo"
        assert "privacy_guarantee" in data
        assert "security_notice" in data
