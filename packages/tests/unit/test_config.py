"""
Unit tests for configuration system.
"""

import pytest
import os
from pathlib import Path
from anonyma_core.config import (
    AnonymaConfig,
    load_config,
    get_config,
    DetectionConfig,
    LoggingConfig,
    LogLevel,
    LogFormat
)


class TestConfigLoading:
    """Test configuration loading"""

    def test_load_default_config(self):
        """Test loading default configuration"""
        config = load_config()
        assert config is not None
        assert isinstance(config, AnonymaConfig)

    def test_config_has_all_sections(self):
        """Test that config has all required sections"""
        config = load_config()

        assert config.detection is not None
        assert config.models is not None
        assert config.anonymization is not None
        assert config.performance is not None
        assert config.logging is not None
        assert config.security is not None


class TestDetectionConfig:
    """Test detection configuration"""

    def test_detection_config_defaults(self):
        """Test detection config default values"""
        config = DetectionConfig()

        assert config.confidence_threshold == 0.7
        assert config.use_ensemble == False
        assert config.use_flair == True
        assert config.enable_italian_patterns == True

    def test_detection_config_validation(self):
        """Test detection config validation"""
        # Valid confidence threshold
        config = DetectionConfig(confidence_threshold=0.5)
        assert config.confidence_threshold == 0.5

        # Invalid confidence threshold (too high)
        with pytest.raises(Exception):
            DetectionConfig(confidence_threshold=1.5)

        # Invalid confidence threshold (negative)
        with pytest.raises(Exception):
            DetectionConfig(confidence_threshold=-0.1)


class TestLoggingConfig:
    """Test logging configuration"""

    def test_logging_config_defaults(self):
        """Test logging config default values"""
        config = LoggingConfig()

        assert config.level == LogLevel.INFO
        assert config.format == LogFormat.TEXT
        assert config.file is None
        assert config.console == True

    def test_logging_config_levels(self):
        """Test different logging levels"""
        for level in [LogLevel.DEBUG, LogLevel.INFO, LogLevel.WARNING, LogLevel.ERROR, LogLevel.CRITICAL]:
            config = LoggingConfig(level=level)
            assert config.level == level


class TestEnvironmentOverrides:
    """Test environment variable overrides"""

    def test_log_level_env_override(self, monkeypatch):
        """Test log level override via environment variable"""
        monkeypatch.setenv("ANONYMA_LOG_LEVEL", "DEBUG")

        config = load_config()
        assert config.logging.level == LogLevel.DEBUG

    def test_use_flair_env_override(self, monkeypatch):
        """Test use_flair override via environment variable"""
        monkeypatch.setenv("ANONYMA_USE_FLAIR", "false")

        config = load_config()
        assert config.detection.use_flair == False

    def test_device_env_override(self, monkeypatch):
        """Test device override via environment variable"""
        monkeypatch.setenv("ANONYMA_DEVICE", "cuda")

        config = load_config()
        assert config.models.flair.device == "cuda"

    def test_confidence_threshold_env_override(self, monkeypatch):
        """Test confidence threshold override via environment variable"""
        monkeypatch.setenv("ANONYMA_CONFIDENCE_THRESHOLD", "0.85")

        config = load_config()
        assert config.detection.confidence_threshold == 0.85


class TestGlobalConfig:
    """Test global configuration instance"""

    def test_get_global_config(self):
        """Test getting global config instance"""
        config = get_config()
        assert config is not None
        assert isinstance(config, AnonymaConfig)

    def test_global_config_singleton(self):
        """Test that global config is singleton"""
        config1 = get_config()
        config2 = get_config()

        # Should be the same instance
        assert config1 is config2

    def test_global_config_reload(self):
        """Test reloading global config"""
        config1 = get_config()
        config2 = get_config(reload=True)

        # After reload, should be new instance
        # (may be same values but should have reloaded)
        assert isinstance(config2, AnonymaConfig)


class TestConfigValidation:
    """Test configuration validation"""

    def test_invalid_batch_size(self):
        """Test that invalid batch size is rejected"""
        from anonyma_core.config import FlairModelConfig

        # Zero batch size should fail
        with pytest.raises(Exception):
            FlairModelConfig(batch_size=0)

        # Negative batch size should fail
        with pytest.raises(Exception):
            FlairModelConfig(batch_size=-1)

    def test_invalid_device(self):
        """Test that invalid device is rejected"""
        from anonyma_core.config import FlairModelConfig

        with pytest.raises(Exception):
            FlairModelConfig(device="invalid_device")

    def test_invalid_redaction_character(self):
        """Test that invalid redaction character is rejected"""
        from anonyma_core.config import AnonymizationConfig

        # Multiple characters should fail
        with pytest.raises(Exception):
            AnonymizationConfig(redaction_character="███")

        # Empty string should fail
        with pytest.raises(Exception):
            AnonymizationConfig(redaction_character="")

    def test_valid_redaction_character(self):
        """Test that valid redaction character is accepted"""
        from anonyma_core.config import AnonymizationConfig

        config = AnonymizationConfig(redaction_character="*")
        assert config.redaction_character == "*"


class TestPerformanceConfig:
    """Test performance configuration"""

    def test_performance_defaults(self):
        """Test performance config defaults"""
        from anonyma_core.config import PerformanceConfig

        config = PerformanceConfig()

        assert config.max_text_length == 10_000_000
        assert config.enable_caching == True
        assert config.cache_ttl == 3600
        assert config.enable_parallel_processing == True
        assert config.max_workers == 4

    def test_max_workers_validation(self):
        """Test max_workers validation"""
        from anonyma_core.config import PerformanceConfig

        # Valid values
        config = PerformanceConfig(max_workers=8)
        assert config.max_workers == 8

        # Too many workers should fail
        with pytest.raises(Exception):
            PerformanceConfig(max_workers=100)

        # Zero workers should fail
        with pytest.raises(Exception):
            PerformanceConfig(max_workers=0)


class TestSecurityConfig:
    """Test security configuration"""

    def test_security_defaults(self):
        """Test security config defaults"""
        from anonyma_core.config import SecurityConfig

        config = SecurityConfig()

        assert config.encrypt_mappings == False
        assert config.sanitize_logs == True
        assert config.max_upload_size == 52_428_800  # 50MB

    def test_max_upload_size_validation(self):
        """Test max upload size validation"""
        from anonyma_core.config import SecurityConfig

        # Valid size
        config = SecurityConfig(max_upload_size=100_000_000)
        assert config.max_upload_size == 100_000_000

        # Negative size should fail
        with pytest.raises(Exception):
            SecurityConfig(max_upload_size=-1)

        # Zero size should fail
        with pytest.raises(Exception):
            SecurityConfig(max_upload_size=0)
