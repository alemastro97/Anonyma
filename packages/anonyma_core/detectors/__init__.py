# Lazy imports to avoid dependency issues
def __getattr__(name):
    if name == "PIIDetector":
        from .pii_detector import PIIDetector
        return PIIDetector
    elif name == "EnsemblePIIDetector":
        from .ensemble_detector import EnsemblePIIDetector
        return EnsemblePIIDetector
    elif name == "FlairPIIDetector":
        from .flair_detector import FlairPIIDetector
        return FlairPIIDetector
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

__all__ = ["PIIDetector", "EnsemblePIIDetector", "FlairPIIDetector"]