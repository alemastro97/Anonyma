"""Anonyma Core - Intelligent Document Anonymization Engine"""

from .modes import AnonymizationMode, AnonymizationResult

# Lazy import of engine to avoid dependency issues
def __getattr__(name):
    if name == "AnonymaEngine":
        from .engine import AnonymaEngine
        return AnonymaEngine
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

__version__ = "0.1.0"
__all__ = ["AnonymaEngine", "AnonymizationMode", "AnonymizationResult"]