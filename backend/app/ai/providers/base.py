"""
Abstract Base Class for LLM Providers.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

from app.schemas.ai import MinimizedContext, AIFindingExplanation


class LLMProvider(ABC):
    """Abstract interface defining the privacy-preserving LLM contract."""

    def __init__(self, model_name: str = "privacy-guard-llm-v1") -> None:
        self.model_name = model_name

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return human-readable provider name."""
        pass

    @abstractmethod
    async def generate_explanation(
        self,
        context: MinimizedContext
    ) -> AIFindingExplanation:
        """
        Generate a structured vulnerability explanation and remediation advice
        for the given minimized context window.
        """
        pass

    async def generate_remediation_json(
        self,
        context: MinimizedContext,
        finding: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate raw tripartite remediation fields from the LLM provider.
        """
        # Default fallback implementation converting generate_explanation to dict
        exp = await self.generate_explanation(context)
        return {
            "developer_explanation": exp.root_cause_explanation,
            "why_it_matters": "Identified by static analysis as a potential security or quality hazard.",
            "potential_impact": "Could lead to exploitation or unexpected application behavior if untrusted data reaches this execution node.",
            "recommended_remediation": exp.remediation_advice,
            "safer_code_example": exp.secure_code_example,
            "confidence_statement": f"Evaluated based on minimized context window at line {context.line_number}.",
            "remediation_steps": [
                "Review the minimized context window.",
                "Replace unsafe functions with validated standard library alternatives.",
                "Add test coverage verifying secure behavior."
            ]
        }

    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Verify provider availability and operational readiness."""
        pass
