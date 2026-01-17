"""
Unit tests for anonymization modes.
"""

import pytest
from anonyma_core.modes.redactor import Redactor
from anonyma_core.modes.substitutor import Substitutor
from anonyma_core.modes.visual_redactor import VisualRedactor


class TestRedactor:
    """Test Redactor mode"""

    def test_redactor_init(self):
        """Test Redactor initialization"""
        redactor = Redactor()
        assert redactor is not None

    def test_redact_simple_detection(self, sample_detections):
        """Test redaction with simple detections"""
        text = "Email is test@example.com and phone is +39 339 1234567"
        detections = [
            {'entity_type': 'EMAIL', 'start': 9, 'end': 26, 'confidence': 0.9, 'text': 'test@example.com'}
        ]

        redactor = Redactor()
        result = redactor.anonymize(text, detections)

        assert result != text
        assert "test@example.com" not in result
        assert "█" in result

    def test_redact_preserves_length(self):
        """Test that redaction preserves original text length"""
        text = "Email: test@example.com"
        detections = [
            {'entity_type': 'EMAIL', 'start': 7, 'end': 23, 'confidence': 0.9, 'text': 'test@example.com'}
        ]

        redactor = Redactor()
        result = redactor.anonymize(text, detections)

        # Length should be preserved
        assert len(result) == len(text)

    def test_redact_multiple_detections(self):
        """Test redaction with multiple detections"""
        text = "Email: test@example.com, Phone: +39 339 1234567"
        detections = [
            {'entity_type': 'EMAIL', 'start': 7, 'end': 23, 'confidence': 0.9, 'text': 'test@example.com'},
            {'entity_type': 'PHONE', 'start': 32, 'end': 48, 'confidence': 0.9, 'text': '+39 339 1234567'}
        ]

        redactor = Redactor()
        result = redactor.anonymize(text, detections)

        assert "test@example.com" not in result
        assert "+39 339 1234567" not in result
        assert "█" in result

    def test_redact_empty_detections(self):
        """Test redaction with no detections"""
        text = "This is a normal text"
        detections = []

        redactor = Redactor()
        result = redactor.anonymize(text, detections)

        # Text should remain unchanged
        assert result == text

    def test_redact_overlapping_detections(self):
        """Test redaction with overlapping detections"""
        text = "Email: test@example.com"
        detections = [
            {'entity_type': 'EMAIL', 'start': 7, 'end': 23, 'confidence': 0.9, 'text': 'test@example.com'},
            {'entity_type': 'DOMAIN', 'start': 12, 'end': 23, 'confidence': 0.8, 'text': 'example.com'}
        ]

        redactor = Redactor()
        result = redactor.anonymize(text, detections)

        # Should handle overlaps gracefully
        assert isinstance(result, str)


class TestSubstitutor:
    """Test Substitutor mode"""

    def test_substitutor_init(self):
        """Test Substitutor initialization"""
        substitutor = Substitutor()
        assert substitutor is not None
        assert substitutor.faker_it is not None
        assert substitutor.faker_en is not None

    def test_substitute_simple_detection(self):
        """Test substitution with simple detection"""
        text = "Email: test@example.com"
        detections = [
            {'entity_type': 'EMAIL', 'start': 7, 'end': 23, 'confidence': 0.9, 'text': 'test@example.com'}
        ]

        substitutor = Substitutor()
        result, mapping, reverse_key = substitutor.anonymize(text, detections)

        assert result != text
        assert "test@example.com" not in result
        assert "@" in result  # Should still have an email format
        assert isinstance(mapping, dict)
        assert isinstance(reverse_key, str)

    def test_substitute_generates_mapping(self):
        """Test that substitution generates mapping"""
        text = "Email: test@example.com, Name: Mario Rossi"
        detections = [
            {'entity_type': 'EMAIL', 'start': 7, 'end': 23, 'confidence': 0.9, 'text': 'test@example.com'}
        ]

        substitutor = Substitutor()
        result, mapping, reverse_key = substitutor.anonymize(text, detections)

        assert len(mapping) > 0
        assert 'test@example.com' in mapping

    def test_substitute_reverse_key_generated(self):
        """Test that reverse key is generated"""
        text = "Email: test@example.com"
        detections = [
            {'entity_type': 'EMAIL', 'start': 7, 'end': 23, 'confidence': 0.9, 'text': 'test@example.com'}
        ]

        substitutor = Substitutor()
        result, mapping, reverse_key = substitutor.anonymize(text, detections)

        assert reverse_key is not None
        assert len(reverse_key) > 0
        assert isinstance(reverse_key, str)

    def test_substitute_empty_detections(self):
        """Test substitution with no detections"""
        text = "This is a normal text"
        detections = []

        substitutor = Substitutor()
        result, mapping, reverse_key = substitutor.anonymize(text, detections)

        # Text should remain unchanged
        assert result == text
        assert mapping == {}
        assert reverse_key is not None

    def test_substitute_person_name(self):
        """Test substitution of person names"""
        text = "Person: Mario Rossi"
        detections = [
            {'entity_type': 'PERSON', 'start': 8, 'end': 19, 'confidence': 0.9, 'text': 'Mario Rossi'}
        ]

        substitutor = Substitutor()
        result, mapping, reverse_key = substitutor.anonymize(text, detections)

        assert "Mario Rossi" not in result
        # Should have a different name
        assert result != text

    def test_substitute_italian_codice_fiscale(self):
        """Test substitution of Italian Codice Fiscale"""
        text = "CF: RSSMRA85C15H501X"
        detections = [
            {'entity_type': 'CODICE_FISCALE', 'start': 4, 'end': 20, 'confidence': 0.9, 'text': 'RSSMRA85C15H501X'}
        ]

        substitutor = Substitutor()
        result, mapping, reverse_key = substitutor.anonymize(text, detections)

        assert "RSSMRA85C15H501X" not in result
        # Should have a replacement
        assert len(result) > 4


class TestVisualRedactor:
    """Test VisualRedactor mode"""

    def test_visual_redactor_init(self):
        """Test VisualRedactor initialization"""
        visual_redactor = VisualRedactor()
        assert visual_redactor is not None

    def test_visual_redact_simple_detection(self):
        """Test visual redaction with simple detection"""
        text = "Email: test@example.com"
        detections = [
            {'entity_type': 'EMAIL', 'start': 7, 'end': 23, 'confidence': 0.9, 'text': 'test@example.com'}
        ]

        visual_redactor = VisualRedactor()
        result = visual_redactor.anonymize(text, detections)

        assert result != text
        assert "test@example.com" not in result
        assert "█" in result

    def test_visual_redact_uses_heavy_redaction(self):
        """Test that visual redaction uses heavy redaction (multiple blocks)"""
        text = "Email: test@example.com"
        detections = [
            {'entity_type': 'EMAIL', 'start': 7, 'end': 23, 'confidence': 0.9, 'text': 'test@example.com'}
        ]

        visual_redactor = VisualRedactor()
        result = visual_redactor.anonymize(text, detections)

        # Should have multiple block characters
        block_count = result.count("█")
        assert block_count >= 3  # Heavy redaction should use multiple blocks

    def test_visual_redact_empty_detections(self):
        """Test visual redaction with no detections"""
        text = "This is a normal text"
        detections = []

        visual_redactor = VisualRedactor()
        result = visual_redactor.anonymize(text, detections)

        # Text should remain unchanged
        assert result == text

    def test_visual_redact_multiple_detections(self):
        """Test visual redaction with multiple detections"""
        text = "Email: test@example.com, Phone: +39 339 1234567"
        detections = [
            {'entity_type': 'EMAIL', 'start': 7, 'end': 23, 'confidence': 0.9, 'text': 'test@example.com'},
            {'entity_type': 'PHONE', 'start': 32, 'end': 48, 'confidence': 0.9, 'text': '+39 339 1234567'}
        ]

        visual_redactor = VisualRedactor()
        result = visual_redactor.anonymize(text, detections)

        assert "test@example.com" not in result
        assert "+39 339 1234567" not in result
        assert result.count("█") > 5  # Multiple heavy redactions


class TestModesComparison:
    """Test comparison between different modes"""

    def test_redact_vs_visual_redact_different_output(self):
        """Test that REDACT and VISUAL_REDACT produce different outputs"""
        text = "Email: test@example.com"
        detections = [
            {'entity_type': 'EMAIL', 'start': 7, 'end': 23, 'confidence': 0.9, 'text': 'test@example.com'}
        ]

        redactor = Redactor()
        visual_redactor = VisualRedactor()

        result_redact = redactor.anonymize(text, detections)
        result_visual = visual_redactor.anonymize(text, detections)

        # Outputs should be different
        assert result_redact != result_visual

    def test_substitute_vs_redact_different_output(self):
        """Test that SUBSTITUTE and REDACT produce different outputs"""
        text = "Email: test@example.com"
        detections = [
            {'entity_type': 'EMAIL', 'start': 7, 'end': 23, 'confidence': 0.9, 'text': 'test@example.com'}
        ]

        redactor = Redactor()
        substitutor = Substitutor()

        result_redact = redactor.anonymize(text, detections)
        result_substitute, _, _ = substitutor.anonymize(text, detections)

        # Outputs should be different
        # SUBSTITUTE should have fake email, REDACT should have blocks
        assert result_redact != result_substitute
        assert "█" in result_redact
        assert "@" in result_substitute  # Substitute should keep email format
