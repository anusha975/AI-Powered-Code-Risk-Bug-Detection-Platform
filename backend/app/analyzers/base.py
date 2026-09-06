"""
Base Abstract Class for Modular Code Analyzers.
Allows extensible integration of Python AST, Bandit, and future JavaScript/Java analyzers.
"""

from abc import ABC, abstractmethod
from typing import List
from app.schemas.analysis import NormalizedFinding


class BaseAnalyzer(ABC):
    """Abstract Base Class for all static code analyzers."""

    analyzer_id: str
    name: str
    supported_languages: List[str]

    @abstractmethod
    def analyze(self, code: str, filename: str) -> List[NormalizedFinding]:
        """
        Execute static analysis on the source code string.
        Must NOT execute the submitted code.
        Returns a list of NormalizedFinding objects.
        """
        pass
