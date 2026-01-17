"""Anonyma Core - Intelligent Document Anonymization Engine"""

from .modes import AnonymizationMode, AnonymizationResult
from .engine import AnonymaEngine

__version__ = "0.1.0"
__all__ = ["AnonymaEngine", "AnonymizationMode", "AnonymizationResult"]