"""
System constants and Enumerations for the Security & Risk Analysis Platform.
"""

from enum import Enum


class AnalysisMode(str, Enum):
    """Supported analysis operational modes."""
    LOCAL_STATIC_ONLY = "LOCAL_STATIC_ONLY"  # Default: Zero LLM / Zero External Transmission
    REDACTED_HYBRID = "REDACTED_HYBRID"      # Local static + redacted snippet enrichment
    SELF_HOSTED_LLM = "SELF_HOSTED_LLM"      # Local static + on-premise air-gapped LLM


class ComponentStatus(str, Enum):
    """Operational status of system components."""
    OPERATIONAL = "OPERATIONAL"
    CONNECTED = "CONNECTED"
    DISCONNECTED = "DISCONNECTED"
    DEGRADED = "DEGRADED"
    STANDBY = "STANDBY"


class PrivacyLevel(str, Enum):
    """Privacy enforcement levels."""
    STRICT_AIRGAP = "STRICT_AIRGAP"
    LOCAL_ONLY = "LOCAL_ONLY"
    SECRET_REDACTED = "SECRET_REDACTED"


class SupportedLanguage(str, Enum):
    """Supported source code programming languages."""
    PYTHON = "python"
    JAVA = "java"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"


class ProviderMode(str, Enum):
    """Supported AI provider operation modes."""
    EXTERNAL = "external"  # Cloud TLS API (OpenAI / Azure)
    LOCAL = "local"        # Private on-premise / air-gapped LLM (Ollama / vLLM)
    MOCK = "mock"          # Offline synthetic mock (testing / zero runtime)


# System Module Registry
ACTIVE_MODULES = [
    {
        "id": "module-1",
        "name": "Core Foundation & Health Telemetry",
        "status": "ACTIVE",
        "description": "FastAPI backend, PostgreSQL session handling, telemetry endpoints, and React dashboard."
    },
    {
        "id": "module-2",
        "name": "Secure Code Ingestion Layer",
        "status": "ACTIVE",
        "description": "Safe code paste & file upload ingestion, language detection, path traversal defenses, transient buffering, and zero code execution."
    },
    {
        "id": "module-3",
        "name": "Secret Detection & Redaction Engine",
        "status": "ACTIVE",
        "description": "Entropy analysis, credential regex matching, automated AST-level snippet masking, and zero-leak privacy protection."
    },
    {
        "id": "module-4",
        "name": "Local Static Code Analysis Engine",
        "status": "ACTIVE",
        "description": "Python AST security visitor, Bandit SAST integration, injection pattern matching, and zero-execution code diagnostics."
    },
    {
        "id": "module-5",
        "name": "ML Risk & Vulnerability Predictor",
        "status": "ACTIVE",
        "description": "5-stage Scikit-Learn RandomForest risk regression pipeline and human-interpretable risk scoring engine."
    },
    {
        "id": "module-6",
        "name": "Privacy-Aware AI Analysis Layer",
        "status": "ACTIVE",
        "description": "7-stage privacy minimization pipeline, LLMProvider abstraction, sanitized context window extraction, and zero-code audit logging."
    },
    {
        "id": "module-7",
        "name": "AI Developer Explanation & Remediation Engine",
        "status": "ACTIVE",
        "description": "Tripartite epistemic explanations (DETECTED FACT, AI INTERPRETATION, RECOMMENDATION), anti-hallucination guards, and verified safer code refactoring."
    },
    {
        "id": "module-8",
        "name": "Private AI / Local LLM Support",
        "status": "ACTIVE",
        "description": "LocalLLMProvider abstraction supporting Ollama and OpenAI-compatible local/air-gapped servers with zero data egress."
    },
    {
        "id": "module-9",
        "name": "Privacy-Aware Engineering Knowledge RAG",
        "status": "ACTIVE",
        "description": "Vector similarity search and grounded AI explanation engine backed by curated security guidelines, OWASP standards, and historical incident post-mortems with strict source attribution."
    },
    {
        "id": "module-10",
        "name": "GitHub Pull Request Security & Risk Analysis",
        "status": "ACTIVE",
        "description": "Passive, non-executing GitHub PR security scanning, multi-file diff parsing, secret detection, local AST/SAST analysis, PR risk aggregation, and RAG-grounded AI remediation."
    },
    {
        "id": "module-11",
        "name": "Professional Engineering Security Dashboard",
        "status": "ACTIVE",
        "description": "Production-grade multi-page developer dashboard, real telemetry analytics engine, universal findings catalog, session history, and prominent privacy indicators."
    },
    {
        "id": "module-12",
        "name": "Authentication, Authorization & Security Audit",
        "status": "ACTIVE",
        "description": "Enterprise-grade user registration, JWT authentication, RBAC (ADMIN/DEVELOPER), user-scoped analysis history, zero-leak security audit trail, rate limiting, and security defense headers."
    }
]


