"""
External Cloud LLM Provider Client (OpenAI / Compatible API).

Sends strictly minimized, sanitized context payloads over TLS to external AI providers
with configured timeout guards, rate-limit resilience, and strict error boundaries.
"""

from typing import Dict, Any, Optional
import json
import httpx

from app.schemas.ai import MinimizedContext, AIFindingExplanation
from app.ai.providers.base import LLMProvider
from app.core.config import settings
from app.utils.logger import logger


class AIProviderError(Exception):
    """Base exception for AI provider communication issues."""
    pass


class AITimeoutError(AIProviderError):
    """Raised when LLM call exceeds timeout threshold."""
    pass


class AIRateLimitError(AIProviderError):
    """Raised when LLM provider returns HTTP 429 rate limit."""
    pass


class ExternalLLMProvider(LLMProvider):
    """Client for external OpenAI / compatible LLM endpoints."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_url: Optional[str] = None,
        model_name: Optional[str] = None,
        timeout_seconds: Optional[int] = None
    ) -> None:
        super().__init__(model_name=model_name or settings.LLM_MODEL_NAME)
        self.api_key = api_key or settings.LLM_API_KEY
        self.api_url = api_url or settings.LLM_API_URL or "https://api.openai.com/v1/chat/completions"
        self.timeout_seconds = timeout_seconds or settings.LLM_TIMEOUT_SECONDS

    @property
    def provider_name(self) -> str:
        return "ExternalLLMProvider (Cloud TLS)"

    async def generate_explanation(
        self,
        context: MinimizedContext
    ) -> AIFindingExplanation:
        """
        Send strictly minimized context to external LLM provider.
        """
        if not self.api_key:
            raise AIProviderError("External LLM API key is not configured.")

        system_prompt = (
            "You are a specialized application security AI assistant. "
            "You will be given a small, isolated code snippet (±4 lines) around a flagged static analysis finding. "
            "Analyze the vulnerability and provide a structured JSON response with keys: "
            "'root_cause', 'remediation', and 'secure_code'."
        )

        user_prompt = (
            f"Issue: {context.issue_title} (ID: {context.finding_id}, Severity: {context.severity})\n"
            f"Target Line: {context.line_number}\n\n"
            f"Minimized Code Window:\n{context.context_snippet}\n\n"
            "Provide explanation and secure remediation in JSON format."
        )

        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.2,
            "response_format": {"type": "json_object"}
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        try:
            async with httpx.AsyncClient(timeout=float(self.timeout_seconds)) as client:
                response = await client.post(self.api_url, json=payload, headers=headers)

                if response.status_code == 429:
                    raise AIRateLimitError("External LLM rate limit exceeded (HTTP 429).")

                response.raise_for_status()
                data = response.json()

                # Extract response text
                raw_content = data.get("choices", [{}])[0].get("message", {}).get("content", "{}")
                parsed = {}
                try:
                    parsed = json.loads(raw_content)
                except Exception:
                    parsed = {"root_cause": raw_content, "remediation": "Review code against security policies.", "secure_code": ""}

                return AIFindingExplanation(
                    finding_id=context.finding_id,
                    issue_title=context.issue_title,
                    severity=context.severity,
                    line_number=context.line_number,
                    root_cause_explanation=parsed.get("root_cause", "Vulnerability detected in minimized snippet."),
                    remediation_advice=parsed.get("remediation", "Apply parameterization or safe APIs."),
                    secure_code_example=parsed.get("secure_code"),
                    provider_used=self.provider_name,
                    model_name=self.model_name,
                    minimized_context=context
                )

        except httpx.TimeoutException as exc:
            logger.warning(f"External LLM call timed out after {self.timeout_seconds}s: {exc}")
            raise AITimeoutError(f"External LLM request timed out after {self.timeout_seconds}s.") from exc
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 429:
                raise AIRateLimitError("External LLM rate limit exceeded (HTTP 429).") from exc
            logger.error(f"External LLM returned HTTP error {exc.response.status_code}: {exc}")
            raise AIProviderError(f"External LLM returned HTTP error {exc.response.status_code}") from exc
        except (AIRateLimitError, AITimeoutError):
            raise
        except Exception as exc:
            logger.error(f"External LLM call failed: {exc}")
            raise AIProviderError(f"External LLM call failed: {str(exc)}") from exc

    async def health_check(self) -> Dict[str, Any]:
        has_key = bool(self.api_key and len(self.api_key) > 5)
        return {
            "status": "OPERATIONAL" if has_key else "MISSING_API_KEY",
            "provider": self.provider_name,
            "model": self.model_name,
            "endpoint_url": self.api_url,
            "air_gapped": False,
            "privacy_score": 50,
            "latency_ms": None,
            "diagnostic_message": (
                "Cloud TLS API is configured with secret redaction and context window minimization."
                if has_key else
                "External API key is not configured. Set LLM_API_KEY in .env or switch to Local LLM mode."
            )
        }
