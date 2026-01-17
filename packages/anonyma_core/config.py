"""
Configuration management for Anonyma Core.

Supports:
- YAML-based configuration
- Environment-specific overrides (dev, prod)
- Environment variable overrides
- Pydantic validation
"""

import os
from pathlib import Path
from typing import Optional, Dict, List, Any
import yaml
from pydantic import BaseModel, Field, validator
from enum import Enum


class LogLevel(str, Enum):
    """Logging levels"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogFormat(str, Enum):
    """Log output formats"""
    TEXT = "text"
    JSON = "json"


class AnonymizationModeEnum(str, Enum):
    """Anonymization modes"""
    REDACT = "redact"
    SUBSTITUTE = "substitute"
    VISUAL_REDACT = "visual_redact"


class DetectionConfig(BaseModel):
    """Detection configuration"""
    confidence_threshold: float = Field(0.7, ge=0.0, le=1.0)
    use_ensemble: bool = False
    use_flair: bool = True
    enable_italian_patterns: bool = True
    supported_languages: List[str] = ["it", "en"]


class FlairModelConfig(BaseModel):
    """Flair model configuration"""
    models: List[str] = ["ner-multi"]
    cache_dir: str = ".flair_cache"
    device: str = "cpu"
    batch_size: int = 32

    @validator('device')
    def validate_device(cls, v):
        if v not in ["cpu", "cuda"]:
            raise ValueError("Device must be 'cpu' or 'cuda'")
        return v


class PresidioConfig(BaseModel):
    """Presidio analyzer configuration"""
    enabled: bool = True
    language_map: Dict[str, str] = {"it": "en", "en": "en"}


class ModelsConfig(BaseModel):
    """Models configuration"""
    flair: FlairModelConfig = FlairModelConfig()
    presidio: PresidioConfig = PresidioConfig()


class AnonymizationConfig(BaseModel):
    """Anonymization configuration"""
    default_mode: AnonymizationModeEnum = AnonymizationModeEnum.REDACT
    redaction_character: str = "█"
    enable_reversibility: bool = True
    faker_locales: Dict[str, str] = {"it": "it_IT", "en": "en_US"}

    @validator('redaction_character')
    def validate_redaction_char(cls, v):
        if len(v) != 1:
            raise ValueError("Redaction character must be a single character")
        return v


class PerformanceConfig(BaseModel):
    """Performance configuration"""
    max_text_length: int = Field(10_000_000, gt=0)
    enable_caching: bool = True
    cache_ttl: int = Field(3600, gt=0)
    enable_parallel_processing: bool = True
    max_workers: int = Field(4, ge=1, le=32)


class LoggingConfig(BaseModel):
    """Logging configuration"""
    level: LogLevel = LogLevel.INFO
    format: LogFormat = LogFormat.TEXT
    file: Optional[str] = None
    console: bool = True


class SecurityConfig(BaseModel):
    """Security configuration"""
    encrypt_mappings: bool = False
    sanitize_logs: bool = True
    max_upload_size: int = Field(52_428_800, gt=0)  # 50MB


class AnonymaConfig(BaseModel):
    """Main configuration model"""
    detection: DetectionConfig = DetectionConfig()
    models: ModelsConfig = ModelsConfig()
    anonymization: AnonymizationConfig = AnonymizationConfig()
    performance: PerformanceConfig = PerformanceConfig()
    logging: LoggingConfig = LoggingConfig()
    security: SecurityConfig = SecurityConfig()

    class Config:
        validate_assignment = True


def load_config(
    config_path: Optional[Path] = None,
    environment: str = "default"
) -> AnonymaConfig:
    """
    Load configuration from YAML files with environment-specific overrides.

    Args:
        config_path: Path to base config file (default: config/config.yaml)
        environment: Environment name for overrides (dev, prod, test)

    Returns:
        AnonymaConfig: Validated configuration object

    Environment Variables:
        ANONYMA_CONFIG_PATH: Override config file path
        ANONYMA_ENV: Override environment (dev, prod, test)
        ANONYMA_LOG_LEVEL: Override log level
        ANONYMA_USE_FLAIR: Override use_flair setting
        ANONYMA_DEVICE: Override device setting (cpu, cuda)
    """
    # Determine config path
    if config_path is None:
        config_dir = Path(__file__).parent.parent / "config"
        config_path = Path(os.getenv("ANONYMA_CONFIG_PATH", config_dir / "config.yaml"))

    # Determine environment
    environment = os.getenv("ANONYMA_ENV", environment)

    # Load base config
    if not config_path.exists():
        # Return default config if file doesn't exist
        config_data = {}
    else:
        with open(config_path, 'r') as f:
            config_data = yaml.safe_load(f) or {}

    # Load environment-specific overrides
    if environment != "default":
        env_config_path = config_path.parent / f"config.{environment}.yaml"
        if env_config_path.exists():
            with open(env_config_path, 'r') as f:
                env_data = yaml.safe_load(f) or {}
                config_data = _deep_merge(config_data, env_data)

    # Apply environment variable overrides
    config_data = _apply_env_overrides(config_data)

    # Validate and return config
    return AnonymaConfig(**config_data)


def _deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """Deep merge two dictionaries"""
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def _apply_env_overrides(config_data: Dict[str, Any]) -> Dict[str, Any]:
    """Apply environment variable overrides to config"""
    # Log level override
    if log_level := os.getenv("ANONYMA_LOG_LEVEL"):
        if "logging" not in config_data:
            config_data["logging"] = {}
        config_data["logging"]["level"] = log_level.upper()

    # Use Flair override
    if use_flair := os.getenv("ANONYMA_USE_FLAIR"):
        if "detection" not in config_data:
            config_data["detection"] = {}
        config_data["detection"]["use_flair"] = use_flair.lower() in ("true", "1", "yes")

    # Device override
    if device := os.getenv("ANONYMA_DEVICE"):
        if "models" not in config_data:
            config_data["models"] = {}
        if "flair" not in config_data["models"]:
            config_data["models"]["flair"] = {}
        config_data["models"]["flair"]["device"] = device

    # Confidence threshold override
    if threshold := os.getenv("ANONYMA_CONFIDENCE_THRESHOLD"):
        if "detection" not in config_data:
            config_data["detection"] = {}
        config_data["detection"]["confidence_threshold"] = float(threshold)

    return config_data


# Global config instance (lazy loaded)
_global_config: Optional[AnonymaConfig] = None


def get_config(reload: bool = False) -> AnonymaConfig:
    """
    Get global configuration instance.

    Args:
        reload: Force reload configuration from files

    Returns:
        AnonymaConfig: Global configuration instance
    """
    global _global_config

    if _global_config is None or reload:
        _global_config = load_config()

    return _global_config
