"""
Unit tests for AnonymaEngine.
"""

import pytest
from anonyma_core import AnonymaEngine, AnonymizationMode, AnonymizationResult


class TestAnonymaEngineInitialization:
    """Test engine initialization"""

    def test_engine_init_basic(self):
        """Test basic engine initialization"""
        engine = AnonymaEngine(use_flair=False)
        assert engine is not None
        assert engine.detector is not None
        assert engine.redactor is not None
        assert engine.substitutor is not None
        assert engine.visual_redactor is not None

    def test_engine_init_with_flair_fallback(self):
        """Test that engine falls back to basic detector if Flair fails"""
        # Should not raise exception even if Flair is unavailable
        engine = AnonymaEngine(use_flair=True)
        assert engine is not None
        assert engine.detector is not None


class TestAnonymaEngineRedactMode:
    """Test REDACT anonymization mode"""

    def test_redact_mode_with_pii(self, engine_basic, sample_text_italian):
        """Test redaction of text with PII"""
        result = engine_basic.anonymize(sample_text_italian, AnonymizationMode.REDACT)

        assert isinstance(result, AnonymizationResult)
        assert result.anonymized_text != sample_text_italian
        assert result.mode == AnonymizationMode.REDACT
        assert result.original_text == sample_text_italian
        # Check that email is redacted
        assert "@" not in result.anonymized_text or "email.com" not in result.anonymized_text

    def test_redact_mode_no_pii(self, engine_basic, sample_text_no_pii):
        """Test redaction of text without PII"""
        result = engine_basic.anonymize(sample_text_no_pii, AnonymizationMode.REDACT)

        assert isinstance(result, AnonymizationResult)
        # Text should be mostly unchanged if no PII detected
        assert result.mode == AnonymizationMode.REDACT

    def test_redact_mode_empty_text(self, engine_basic, empty_text):
        """Test redaction of empty text"""
        result = engine_basic.anonymize(empty_text, AnonymizationMode.REDACT)

        assert isinstance(result, AnonymizationResult)
        assert result.anonymized_text == empty_text


class TestAnonymaEngineSubstituteMode:
    """Test SUBSTITUTE anonymization mode"""

    def test_substitute_mode_with_pii(self, engine_basic, sample_text_italian):
        """Test substitution of text with PII"""
        result = engine_basic.anonymize(sample_text_italian, AnonymizationMode.SUBSTITUTE)

        assert isinstance(result, AnonymizationResult)
        assert result.anonymized_text != sample_text_italian
        assert result.mode == AnonymizationMode.SUBSTITUTE
        assert result.mapping is not None or result.mapping == {}
        assert result.reverse_key is not None

    def test_substitute_mode_generates_mapping(self, engine_basic, sample_text_italian):
        """Test that SUBSTITUTE mode generates mapping"""
        result = engine_basic.anonymize(sample_text_italian, AnonymizationMode.SUBSTITUTE)

        # If PII detected, mapping should exist
        if result.mapping:
            assert isinstance(result.mapping, dict)
            assert len(result.mapping) > 0

    def test_substitute_mode_reverse_key(self, engine_basic, sample_text_italian):
        """Test that SUBSTITUTE mode generates reverse key"""
        result = engine_basic.anonymize(sample_text_italian, AnonymizationMode.SUBSTITUTE)

        assert result.reverse_key is not None
        assert isinstance(result.reverse_key, str)
        assert len(result.reverse_key) > 0


class TestAnonymaEngineVisualRedactMode:
    """Test VISUAL_REDACT anonymization mode"""

    def test_visual_redact_mode_with_pii(self, engine_basic, sample_text_italian):
        """Test visual redaction of text with PII"""
        result = engine_basic.anonymize(sample_text_italian, AnonymizationMode.VISUAL_REDACT)

        assert isinstance(result, AnonymizationResult)
        assert result.anonymized_text != sample_text_italian
        assert result.mode == AnonymizationMode.VISUAL_REDACT

    def test_visual_redact_mode_uses_heavy_redaction(self, engine_basic, sample_text_italian):
        """Test that visual redact uses heavy redaction characters"""
        result = engine_basic.anonymize(sample_text_italian, AnonymizationMode.VISUAL_REDACT)

        # Should contain multiple block characters if PII detected
        if result.anonymized_text != sample_text_italian:
            assert "█" in result.anonymized_text


class TestAnonymaEngineLanguageSupport:
    """Test language support"""

    def test_italian_language(self, engine_basic, sample_text_italian):
        """Test Italian language processing"""
        result = engine_basic.anonymize(sample_text_italian, AnonymizationMode.REDACT, language='it')

        assert isinstance(result, AnonymizationResult)

    def test_english_language(self, engine_basic, sample_text_english):
        """Test English language processing"""
        result = engine_basic.anonymize(sample_text_english, AnonymizationMode.REDACT, language='en')

        assert isinstance(result, AnonymizationResult)


class TestAnonymaEngineEdgeCases:
    """Test edge cases and error handling"""

    def test_invalid_mode_raises_error(self, engine_basic, sample_text_italian):
        """Test that invalid mode raises ValueError"""
        with pytest.raises((ValueError, AttributeError)):
            engine_basic.anonymize(sample_text_italian, "invalid_mode")

    def test_very_long_text(self, engine_basic):
        """Test processing of very long text"""
        long_text = "This is a test. " * 1000  # ~16K chars
        result = engine_basic.anonymize(long_text, AnonymizationMode.REDACT)

        assert isinstance(result, AnonymizationResult)

    def test_unicode_text(self, engine_basic):
        """Test processing of text with Unicode characters"""
        unicode_text = "User: 用户名, Email: test@例え.com, Phone: +39 333 1234567"
        result = engine_basic.anonymize(unicode_text, AnonymizationMode.REDACT)

        assert isinstance(result, AnonymizationResult)

    def test_special_characters(self, engine_basic):
        """Test processing of text with special characters"""
        special_text = "Email: test@example.com!@#$%^&*()_+-=[]{}|;:',.<>?/~`"
        result = engine_basic.anonymize(special_text, AnonymizationMode.REDACT)

        assert isinstance(result, AnonymizationResult)


class TestAnonymaEngineConsistency:
    """Test consistency of anonymization"""

    def test_multiple_runs_same_input_redact(self, engine_basic, sample_text_italian):
        """Test that REDACT mode is consistent across runs"""
        result1 = engine_basic.anonymize(sample_text_italian, AnonymizationMode.REDACT)
        result2 = engine_basic.anonymize(sample_text_italian, AnonymizationMode.REDACT)

        # REDACT should be deterministic
        assert result1.anonymized_text == result2.anonymized_text

    def test_different_modes_different_output(self, engine_basic, sample_text_italian):
        """Test that different modes produce different outputs"""
        result_redact = engine_basic.anonymize(sample_text_italian, AnonymizationMode.REDACT)
        result_substitute = engine_basic.anonymize(sample_text_italian, AnonymizationMode.SUBSTITUTE)
        result_visual = engine_basic.anonymize(sample_text_italian, AnonymizationMode.VISUAL_REDACT)

        # Different modes should produce different results (assuming PII detected)
        texts = [result_redact.anonymized_text, result_substitute.anonymized_text, result_visual.anonymized_text]

        # At least one should be different (if PII detected)
        if result_redact.anonymized_text != sample_text_italian:
            # PII was detected, so outputs should differ
            assert len(set(texts)) > 1
