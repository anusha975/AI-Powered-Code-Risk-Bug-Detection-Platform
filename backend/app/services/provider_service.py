"""
AI Provider Management & Telemetry Service.

Coordinates provider catalog discovery, live health checks, reachability probes,
and on-demand connectivity testing across External, Local, and Mock providers.
"""

from typing import List, Optional, Dict, Any
import time
import httpx

from app.schemas.provider import (
    ProviderType,
    ProviderStatus,
    ProviderHealthInfo,
    ProviderTestRequest,
    ProviderTestResponse,
    ProviderCatalogResponse
)
from app.ai.providers import (
    get_llm_provider,
    LocalLLMProvider,
    ExternalLLMProvider,
    MockLLMProvider
)
from app.core.config import settings
from app.utils.logger import logger


class ProviderService:
    """Service to discover, query health, and test AI providers."""

    @staticmethod
    async def get_provider_catalog() -> ProviderCatalogResponse:
        """
        Inspect all supported providers, probe live health, and return catalog.
        """
        active_type = ProviderService._resolve_active_provider_type()
        active_model = settings.LLM_MODEL_NAME if active_type != ProviderType.LOCAL else settings.LOCAL_LLM_MODEL

        # Instantiate providers
        mock_p = MockLLMProvider()
        ext_p = ExternalLLMProvider()
        local_p = LocalLLMProvider()

        # Run health checks concurrently
        mock_health = await mock_p.health_check()
        ext_health = await ext_p.health_check()
        local_health = await local_p.health_check()

        providers_info: List[ProviderHealthInfo] = [
            ProviderHealthInfo(
                provider_type=ProviderType.LOCAL,
                provider_name=local_p.provider_name,
                status=ProviderStatus(local_health.get("status", "STANDBY")),
                is_active=(active_type == ProviderType.LOCAL),
                model_name=local_p.model_name,
                endpoint_url=local_health.get("endpoint_url"),
                air_gapped=True,
                privacy_score=100,
                latency_ms=local_health.get("latency_ms"),
                diagnostic_message=local_health.get("diagnostic_message")
            ),
            ProviderHealthInfo(
                provider_type=ProviderType.EXTERNAL,
                provider_name=ext_p.provider_name,
                status=ProviderStatus(ext_health.get("status", "STANDBY")),
                is_active=(active_type == ProviderType.EXTERNAL),
                model_name=ext_p.model_name,
                endpoint_url=ext_health.get("endpoint_url"),
                air_gapped=False,
                privacy_score=50,
                latency_ms=ext_health.get("latency_ms"),
                diagnostic_message=ext_health.get("diagnostic_message")
            ),
            ProviderHealthInfo(
                provider_type=ProviderType.MOCK,
                provider_name=mock_p.provider_name,
                status=ProviderStatus(mock_health.get("status", "OPERATIONAL")),
                is_active=(active_type == ProviderType.MOCK),
                model_name=mock_p.model_name,
                endpoint_url=mock_health.get("endpoint_url"),
                air_gapped=True,
                privacy_score=100,
                latency_ms=mock_health.get("latency_ms"),
                diagnostic_message=mock_health.get("diagnostic_message")
            )
        ]

        return ProviderCatalogResponse(
            active_provider=active_type,
            active_model=active_model,
            ai_enabled=settings.AI_ENABLED,
            providers=providers_info
        )

    @staticmethod
    async def test_provider_connection(req: ProviderTestRequest) -> ProviderTestResponse:
        """
        Test live connectivity to a specific provider endpoint on demand.
        """
        start_time = time.perf_counter()

        if req.provider_type == ProviderType.MOCK:
            return ProviderTestResponse(
                success=True,
                provider_type=ProviderType.MOCK,
                endpoint_url="memory://offline_mock",
                model_name="synthetic-vulnerability-evaluator",
                latency_ms=0.2,
                status=ProviderStatus.OPERATIONAL,
                message="Deterministic offline mock engine ready. Zero network egress.",
                models_available=["mock-security-eval-v1"],
                air_gapped=True
            )

        elif req.provider_type == ProviderType.LOCAL:
            api_url = req.api_url or settings.LOCAL_LLM_URL
            model_name = req.model_name or settings.LOCAL_LLM_MODEL
            api_type = req.api_type or settings.LOCAL_LLM_API_TYPE

            local_provider = LocalLLMProvider(
                api_url=api_url,
                model_name=model_name,
                api_type=api_type,
                timeout_seconds=req.timeout_seconds
            )
            health = await local_provider.health_check()
            latency_ms = (time.perf_counter() - start_time) * 1000.0

            is_ok = health.get("status") == "OPERATIONAL"
            return ProviderTestResponse(
                success=is_ok,
                provider_type=ProviderType.LOCAL,
                endpoint_url=api_url,
                model_name=model_name,
                latency_ms=round(latency_ms, 2),
                status=ProviderStatus(health.get("status", "UNREACHABLE")),
                message=health.get("diagnostic_message", "Local server tested."),
                models_available=health.get("models_available", []),
                air_gapped=True
            )

        elif req.provider_type == ProviderType.EXTERNAL:
            api_url = req.api_url or settings.LLM_API_URL or "https://api.openai.com/v1/models"
            api_key = req.api_key or settings.LLM_API_KEY
            model_name = req.model_name or settings.LLM_MODEL_NAME

            if not api_key:
                return ProviderTestResponse(
                    success=False,
                    provider_type=ProviderType.EXTERNAL,
                    endpoint_url=api_url,
                    model_name=model_name,
                    latency_ms=0.0,
                    status=ProviderStatus.MISSING_API_KEY,
                    message="External API Key is missing. Provide 'api_key' to test external connection.",
                    models_available=[],
                    air_gapped=False
                )

            headers = {"Authorization": f"Bearer {api_key}"}
            try:
                async with httpx.AsyncClient(timeout=float(req.timeout_seconds or 5)) as client:
                    probe_url = api_url if "/models" in api_url else "https://api.openai.com/v1/models"
                    res = await client.get(probe_url, headers=headers)
                    latency_ms = (time.perf_counter() - start_time) * 1000.0
                    if res.status_code == 200:
                        data = res.json()
                        available = [m.get("id") for m in data.get("data", []) if "id" in m][:10]
                        return ProviderTestResponse(
                            success=True,
                            provider_type=ProviderType.EXTERNAL,
                            endpoint_url=api_url,
                            model_name=model_name,
                            latency_ms=round(latency_ms, 2),
                            status=ProviderStatus.OPERATIONAL,
                            message=f"Connected to Cloud API in {round(latency_ms, 1)}ms.",
                            models_available=available,
                            air_gapped=False
                        )
                    else:
                        return ProviderTestResponse(
                            success=False,
                            provider_type=ProviderType.EXTERNAL,
                            endpoint_url=api_url,
                            model_name=model_name,
                            latency_ms=round(latency_ms, 2),
                            status=ProviderStatus.ERROR,
                            message=f"Cloud API returned HTTP {res.status_code}: {res.text[:150]}",
                            models_available=[],
                            air_gapped=False
                        )
            except Exception as exc:
                latency_ms = (time.perf_counter() - start_time) * 1000.0
                return ProviderTestResponse(
                    success=False,
                    provider_type=ProviderType.EXTERNAL,
                    endpoint_url=api_url,
                    model_name=model_name,
                    latency_ms=round(latency_ms, 2),
                    status=ProviderStatus.UNREACHABLE,
                    message=f"External endpoint unreachable: {str(exc)}",
                    models_available=[],
                    air_gapped=False
                )

        return ProviderTestResponse(
            success=False,
            provider_type=req.provider_type,
            endpoint_url=None,
            model_name=None,
            latency_ms=0.0,
            status=ProviderStatus.ERROR,
            message="Unknown provider type requested.",
            models_available=[],
            air_gapped=False
        )

    @staticmethod
    def _resolve_active_provider_type() -> ProviderType:
        raw = settings.LLM_PROVIDER.lower()
        if raw in ("external", "cloud", "openai"):
            return ProviderType.EXTERNAL
        elif raw in ("local", "ollama", "vllm", "llamacpp"):
            return ProviderType.LOCAL
        else:
            return ProviderType.MOCK
