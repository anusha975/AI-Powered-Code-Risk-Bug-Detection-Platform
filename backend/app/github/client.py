"""
GitHub REST API Client.

Safe, read-only HTTP client to fetch Pull Request metadata and diff files
via the official GitHub REST API without cloning repositories or executing code.
"""

import re
import json
import urllib.request
import urllib.error
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass

from app.utils.logger import logger


@dataclass
class GitHubPRMetadata:
    """Metadata for a GitHub Pull Request."""
    owner: str
    repo: str
    pull_number: int
    title: str
    author: str
    state: str
    html_url: str
    base_branch: str
    head_branch: str
    additions: int
    deletions: int
    changed_files: int
    created_at: str
    updated_at: str


@dataclass
class GitHubFileChange:
    """A changed file entry within a GitHub Pull Request."""
    filename: str
    status: str          # added, modified, removed, renamed
    additions: int
    deletions: int
    changes: int
    patch: Optional[str]
    raw_url: Optional[str]


def mask_token(token: Optional[str]) -> str:
    """Mask a sensitive GitHub token for safe logging/display."""
    if not token:
        return "[NO_TOKEN]"
    clean = token.strip()
    if len(clean) <= 8:
        return "****"
    return f"{clean[:4]}****{clean[-4:]}"


class GitHubClient:
    """Read-only GitHub REST API client."""

    PR_URL_PATTERN = re.compile(
        r"^(?:https?://)?(?:www\.)?github\.com/(?P<owner>[a-zA-Z0-9_\-\.]+)/(?P<repo>[a-zA-Z0-9_\-\.]+)/pull/(?P<pull_number>\d+)(?:[/?#].*)?$"
    )

    SHORTHAND_PATTERN = re.compile(
        r"^(?P<owner>[a-zA-Z0-9_\-\.]+)/(?P<repo>[a-zA-Z0-9_\-\.]+)#(?P<pull_number>\d+)$"
    )

    def __init__(self, base_url: str = "https://api.github.com"):
        self.base_url = base_url.rstrip("/")

    @classmethod
    def parse_pr_url(cls, pr_url_or_shorthand: str) -> Tuple[str, str, int]:
        """
        Parse a GitHub PR URL or shorthand string into (owner, repo, pull_number).

        Examples:
        - "https://github.com/octocat/Hello-World/pull/42" -> ("octocat", "Hello-World", 42)
        - "octocat/Hello-World#42" -> ("octocat", "Hello-World", 42)
        """
        raw = pr_url_or_shorthand.strip()

        url_match = cls.PR_URL_PATTERN.match(raw)
        if url_match:
            return (
                url_match.group("owner"),
                url_match.group("repo"),
                int(url_match.group("pull_number"))
            )

        short_match = cls.SHORTHAND_PATTERN.match(raw)
        if short_match:
            return (
                short_match.group("owner"),
                short_match.group("repo"),
                int(short_match.group("pull_number"))
            )

        raise ValueError(
            f"Invalid GitHub Pull Request URL or format: '{pr_url_or_shorthand}'. "
            "Expected format: 'https://github.com/owner/repo/pull/123' or 'owner/repo#123'."
        )

    def _build_headers(self, token: Optional[str] = None) -> Dict[str, str]:
        """Build request headers for GitHub REST API v3."""
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Privacy-Preserving-AI-Code-Security/1.0"
        }
        if token and token.strip():
            clean_token = token.strip()
            # Standard Bearer or token authorization
            if clean_token.startswith("Bearer ") or clean_token.startswith("token "):
                headers["Authorization"] = clean_token
            else:
                headers["Authorization"] = f"Bearer {clean_token}"
        return headers

    def _execute_request(self, endpoint: str, token: Optional[str] = None) -> Any:
        """Execute a safe GET request against the GitHub REST API."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        headers = self._build_headers(token)
        req = urllib.request.Request(url, headers=headers, method="GET")

        logger.info(f"Executing GitHub API request: {endpoint} | Auth: {mask_token(token)}")

        try:
            with urllib.request.urlopen(req, timeout=10.0) as resp:
                data = resp.read().decode("utf-8")
                return json.loads(data)
        except urllib.error.HTTPError as exc:
            status = exc.code
            error_body = ""
            try:
                error_body = exc.read().decode("utf-8")
                error_json = json.loads(error_body)
                api_msg = error_json.get("message", "")
            except Exception:
                api_msg = error_body

            logger.error(f"GitHub API Error [{status}]: {api_msg}")

            if status == 404:
                raise ValueError(
                    f"GitHub Pull Request or repository not found (404). "
                    f"Verify repository owner/name and PR number. (API response: {api_msg})"
                )
            elif status in (401, 403):
                raise PermissionError(
                    f"GitHub API Authentication / Rate Limit Error ({status}): {api_msg}. "
                    f"Consider supplying a GitHub Personal Access Token (PAT)."
                )
            elif status == 422:
                raise ValueError(f"GitHub API Unprocessable Entity (422): {api_msg}")
            else:
                raise RuntimeError(f"GitHub API returned unexpected status {status}: {api_msg}")
        except urllib.error.URLError as exc:
            logger.error(f"Network error communicating with GitHub API: {str(exc.reason)}")
            raise ConnectionError(f"Could not connect to GitHub API: {str(exc.reason)}")

    def get_pr_metadata(
        self,
        owner: str,
        repo: str,
        pull_number: int,
        token: Optional[str] = None
    ) -> GitHubPRMetadata:
        """Fetch Pull Request top-level metadata."""
        endpoint = f"repos/{owner}/{repo}/pulls/{pull_number}"
        data = self._execute_request(endpoint, token=token)

        return GitHubPRMetadata(
            owner=owner,
            repo=repo,
            pull_number=pull_number,
            title=data.get("title", f"Pull Request #{pull_number}"),
            author=data.get("user", {}).get("login", "unknown"),
            state=data.get("state", "open"),
            html_url=data.get("html_url", f"https://github.com/{owner}/{repo}/pull/{pull_number}"),
            base_branch=data.get("base", {}).get("ref", "main"),
            head_branch=data.get("head", {}).get("ref", "feature"),
            additions=data.get("additions", 0),
            deletions=data.get("deletions", 0),
            changed_files=data.get("changed_files", 0),
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", "")
        )

    def get_pr_files(
        self,
        owner: str,
        repo: str,
        pull_number: int,
        token: Optional[str] = None,
        max_files: int = 50
    ) -> List[GitHubFileChange]:
        """Fetch changed files and patches for a Pull Request."""
        endpoint = f"repos/{owner}/{repo}/pulls/{pull_number}/files?per_page={max_files}"
        data = self._execute_request(endpoint, token=token)

        if not isinstance(data, list):
            return []

        files: List[GitHubFileChange] = []
        for item in data:
            files.append(GitHubFileChange(
                filename=item.get("filename", "unknown"),
                status=item.get("status", "modified"),
                additions=item.get("additions", 0),
                deletions=item.get("deletions", 0),
                changes=item.get("changes", 0),
                patch=item.get("patch"),
                raw_url=item.get("raw_url")
            ))

        return files


# Global Singleton
github_client = GitHubClient()
