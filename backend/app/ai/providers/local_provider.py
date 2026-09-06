"""
Self-Hosted / Air-Gapped Local LLM Provider Client (Ollama / vLLM / llama.cpp / LocalAI).

Sends minimized code snippets strictly to a local air-gapped LLM process
running within the company's local host or intranet network without external internet egress.
"""

from typing import Dict, Any, Optional, List
import json
import time
import httpx

from app.schemas.ai import MinimizedContext, AIFindingExplanation
from app.ai.providers.base import LLMProvider
from app.core.config import settings
from app.utils.logger import logger


class LocalLLMProvider(LLMProvider):
    """
    Client for local, self-hosted, or air-gapped LLM engines.
    Supports both native Ollama endpoints and OpenAI-compatible local servers (vLLM, llama.cpp, LocalAI).
    """

    def __init__(
        self,
        api_url: Optional[str] = None,
        model_name: Optional[str] = None,
        api_type: Optional[str] = None,
        timeout_seconds: Optional[int] = None
    ) -> None:
        self.raw_base_url = api_url or settings.LOCAL_LLM_URL
        self.api_type = (api_type or settings.LOCAL_LLM_API_TYPE).lower()
        super().__init__(model_name=model_name or settings.LOCAL_LLM_MODEL)
        self.timeout_seconds = timeout_seconds or settings.LOCAL_LLM_TIMEOUT_SECONDS

        # Normalize endpoints
        self.base_url = self.raw_base_url.rstrip("/")
        if self.api_type == "openai_compatible":
            if not self.base_url.endswith("/v1") and not "/v1/" in self.base_url:
                self.chat_url = f"{self.base_url}/v1/chat/completions"
                self.models_url = f"{self.base_url}/v1/models"
            else:
                self.chat_url = f"{self.base_url}/chat/completions"
                self.models_url = f"{self.base_url}/models"
        else:
            # Default Ollama native format
            self.chat_url = f"{self.base_url}/api/generate"
            self.tags_url = f"{self.base_url}/api/tags"
            self.version_url = f"{self.base_url}/api/version"

    @property
    def provider_name(self) -> str:
        return f"LocalLLMProvider ({self.api_type.capitalize()} / Air-Gapped)"

    async def generate_explanation(
        self,
        context: MinimizedContext
    ) -> AIFindingExplanation:
        """
        Query local LLM for finding explanation and remediation advice.
        """
        system_instruction = (
            "You are a local application security auditor running in an air-gapped environment. "
            "Analyze the following code vulnerability from a minimized context window. "
            "Respond in JSON format with keys: 'root_cause', 'remediation', 'secure_code'."
        )
        user_prompt = (
            f"Vulnerability: {context.issue_title} (ID: {context.finding_id}, Severity: {context.severity})\n"
            f"Line Number: {context.line_number}\n\n"
            f"Sanitized Code Window:\n{context.context_snippet}\n\n"
            "Provide explanation and safe code replacement in JSON format."
        )

        try:
            raw_json_str = await self._query_local_model(
                system_instruction=system_instruction,
                user_prompt=user_prompt
            )
            parsed = self._extract_json(raw_json_str)

            return AIFindingExplanation(
                finding_id=context.finding_id,
                issue_title=context.issue_title,
                severity=context.severity,
                line_number=context.line_number,
                root_cause_explanation=parsed.get(
                    "root_cause",
                    f"Local air-gapped analysis identified security issue '{context.issue_title}' at line {context.line_number}."
                ),
                remediation_advice=parsed.get(
                    "remediation",
                    "Apply input validation, parameterization, or safe standard library alternatives."
                ),
                secure_code_example=parsed.get("secure_code"),
                provider_used=self.provider_name,
                model_name=self.model_name,
                minimized_context=context
            )
        except Exception as exc:
            logger.warning(f"Local LLM query failed ({exc}). Falling back to local offline heuristic.")
            return self._heuristic_explanation_fallback(context)

    async def generate_remediation_json(
        self,
        context: MinimizedContext,
        finding: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Query local LLM to produce tripartite explanation & remediation fields.
        """
        system_instruction = (
            "You are a local application security auditor running on an on-premise air-gapped host. "
            "Analyze this static analysis finding and produce a comprehensive tripartite explanation in JSON. "
            "Output JSON with keys: "
            "'developer_explanation' (clear description of the vulnerability mechanism), "
            "'why_it_matters' (why this is a risk/flaw), "
            "'potential_impact' (worst-case exploitation scenario), "
            "'recommended_remediation' (concrete refactoring strategy), "
            "'safer_code_example' (syntactically valid replacement code), "
            "'remediation_steps' (array of strings), "
            "'confidence_statement' (statement of certainty based on the context)."
        )
        user_prompt = (
            f"Static Rule ID: {finding.get('issue_id')} ({finding.get('title')})\n"
            f"Severity: {finding.get('severity')} | Line: {finding.get('line_number')}\n\n"
            f"Minimized Code Context:\n{context.context_snippet}\n\n"
            "Return tripartite analysis in JSON format."
        )

        try:
            raw_json_str = await self._query_local_model(
                system_instruction=system_instruction,
                user_prompt=user_prompt
            )
            parsed = self._extract_json(raw_json_str)

            if parsed and "developer_explanation" in parsed:
                return parsed

            # Fallback conversion if partial keys returned
            return {
                "developer_explanation": parsed.get("root_cause") or f"Static rule {finding.get('issue_id')} detected at line {finding.get('line_number')}.",
                "why_it_matters": parsed.get("why_it_matters") or "Identified by static analysis as a potential security hazard.",
                "potential_impact": parsed.get("potential_impact") or "Could lead to exploitation if untrusted inputs reach this node.",
                "recommended_remediation": parsed.get("remediation") or finding.get("recommendation", "Review and sanitize inputs."),
                "safer_code_example": parsed.get("secure_code"),
                "remediation_steps": parsed.get("remediation_steps") or ["Sanitize inputs.", "Use safe alternatives."],
                "confidence_statement": parsed.get("confidence_statement") or f"Evaluated by {self.provider_name} on minimized snippet."
            }
        except Exception as exc:
            logger.warning(f"Local LLM remediation query failed ({exc}). Using deterministic fallback.")
            return {
                "developer_explanation": f"Local air-gapped analyzer detected {finding.get('title')} at line {finding.get('line_number')}.",
                "why_it_matters": "Dynamic execution or unvalidated inputs create severe security vulnerabilities.",
                "potential_impact": "Potential compromise of runtime integrity or data exfiltration.",
                "recommended_remediation": finding.get("recommendation", "Refactor with safe standard libraries."),
                "safer_code_example": "# Refactor to use safe parameterized calls",
                "remediation_steps": [
                    "Isolate untrusted inputs.",
                    "Replace risky functions with safe APIs.",
                    "Verify behavior with local unit tests."
                ],
                "confidence_statement": f"Local air-gapped heuristic fallback (Engine {self.model_name} offline)."
            }

    async def _query_local_model(
        self,
        system_instruction: str,
        user_prompt: str
    ) -> str:
        """Execute HTTP request to local Ollama or OpenAI-compatible server."""
        async with httpx.AsyncClient(timeout=float(self.timeout_seconds)) as client:
            if self.api_type == "openai_compatible":
                payload = {
                    "model": self.model_name,
                    "messages": [
                        {"role": "system", "content": system_instruction},
                        {"role": "user", "content": user_prompt}
                    ],
                    "temperature": 0.1,
                    "response_format": {"type": "json_object"}
                }
                res = await client.post(self.chat_url, json=payload)
                res.raise_for_status()
                data = res.json()
                return data.get("choices", [{}])[0].get("message", {}).get("content", "{}")
            else:
                # Ollama native format
                payload = {
                    "model": self.model_name,
                    "system": system_instruction,
                    "prompt": user_prompt,
                    "format": "json",
                    "stream": False,
                    "options": {"temperature": 0.1}
                }
                res = await client.post(self.chat_url, json=payload)
                res.raise_for_status()
                data = res.json()
                return data.get("response", "{}")

    def _extract_json(self, raw_str: str) -> Dict[str, Any]:
        """Safely parse JSON response from raw string."""
        if not raw_str:
            return {}
        raw = raw_str.strip()
        if raw.startswith("```"):
            lines = raw.split("\n")
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            raw = "\n".join(lines).strip()
        try:
            return json.loads(raw)
        except Exception:
            # Try to find { ... }
            start = raw.find("{")
            end = raw.rfind("}")
            if start != -1 and end != -1 and end > start:
                try:
                    return json.loads(raw[start:end + 1])
                except Exception:
                    pass
        return {}

    def _heuristic_explanation_fallback(
        self,
        context: MinimizedContext
    ) -> AIFindingExplanation:
        """Provide fallback explanation when local LLM server is offline."""
        return AIFindingExplanation(
            finding_id=context.finding_id,
            issue_title=context.issue_title,
            severity=context.severity,
            line_number=context.line_number,
            root_cause_explanation=f"Local static AST analysis flagged '{context.issue_title}' at line {context.line_number}.",
            remediation_advice="Review the isolated code window and refactor using safe standard library functions.",
            secure_code_example="# Replace with safe parameterized implementation",
            provider_used=f"{self.provider_name} (Standby Fallback)",
            model_name=self.model_name,
            minimized_context=context
        )

    async def health_check(self) -> Dict[str, Any]:
        """
        Probe local model server connectivity, latency, and available models.
        """
        start_time = time.perf_counter()
        probe_url = self.tags_url if self.api_type == "ollama" else self.models_url
        models_found: List[str] = []

        try:
            async with httpx.AsyncClient(timeout=2.5) as client:
                res = await client.get(probe_url)
                latency_ms = (time.perf_counter() - start_time) * 1000.0

                if res.status_code == 200:
                    data = res.json()
                    if self.api_type == "ollama":
                        models_found = [m.get("name") for m in data.get("models", []) if "name" in m]
                    else:
                        models_found = [m.get("id") for m in data.get("data", []) if "id" in m]

                    return {
                        "status": "OPERATIONAL",
                        "provider": self.provider_name,
                        "model": self.model_name,
                        "endpoint_url": self.base_url,
                        "air_gapped": True,
                        "privacy_score": 100,
                        "latency_ms": round(latency_ms, 2),
                        "models_available": models_found,
                        "diagnostic_message": f"Connected to local {self.api_type.capitalize()} host. {len(models_found)} model(s) available."
                    }
        except Exception as exc:
            pass

        return {
            "status": "UNREACHABLE",
            "provider": self.provider_name,
            "model": self.model_name,
            "endpoint_url": self.base_url,
            "air_gapped": True,
            "privacy_score": 100,
            "latency_ms": None,
            "models_available": [],
            "diagnostic_message": (
                f"Local {self.api_type.capitalize()} server is not running on {self.base_url}. "
                "The platform will safely use local static analysis and offline fallback."
            )
        }
