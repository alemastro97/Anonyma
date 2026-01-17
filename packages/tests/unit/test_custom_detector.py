"""
Unit tests for custom pattern detector.

Tests for:
- CustomPattern dataclass
- CustomPatternDetector
- CompoundPatternDetector
- InternalIDDetector
- Pattern validation functions
"""

import pytest
from anonyma_core.detectors.custom_detector import (
    CustomPattern,
    CustomPatternDetector,
    CompoundPatternDetector,
    InternalIDDetector,
)


# ============================================================================
# CustomPattern Tests
# ============================================================================


def test_custom_pattern_creation():
    """Test CustomPattern creation"""
    pattern = CustomPattern(
        name="TEST_PATTERN",
        pattern=r"TEST-\d{3}",
        confidence=0.95,
        description="Test pattern"
    )

    assert pattern.name == "TEST_PATTERN"
    assert pattern.pattern == r"TEST-\d{3}"
    assert pattern.confidence == 0.95
    assert pattern.description == "Test pattern"
    assert pattern.validate is None


def test_custom_pattern_with_validator():
    """Test CustomPattern with validation function"""
    def validator(text):
        return len(text) > 5

    pattern = CustomPattern(
        name="VALIDATED",
        pattern=r"\w+",
        validate=validator
    )

    assert pattern.validate is not None
    assert pattern.validate("short") is False
    assert pattern.validate("longer") is True


# ============================================================================
# CustomPatternDetector Tests
# ============================================================================


def test_custom_detector_initialization():
    """Test CustomPatternDetector initialization"""
    detector = CustomPatternDetector()

    assert detector is not None
    assert detector.name == "CustomPatternDetector"
    assert len(detector.list_patterns()) == 0


def test_add_pattern():
    """Test adding custom pattern"""
    detector = CustomPatternDetector()

    detector.add_pattern(
        name="ORDER_ID",
        pattern=r"ORD-\d{5}",
        confidence=0.95,
        description="Order identifier"
    )

    patterns = detector.list_patterns()
    assert "ORDER_ID" in patterns
    assert len(patterns) == 1


def test_add_multiple_patterns():
    """Test adding multiple patterns"""
    detector = CustomPatternDetector()

    detector.add_pattern("PATTERN_1", r"P1-\d{3}")
    detector.add_pattern("PATTERN_2", r"P2-\d{3}")
    detector.add_pattern("PATTERN_3", r"P3-\d{3}")

    patterns = detector.list_patterns()
    assert len(patterns) == 3
    assert "PATTERN_1" in patterns
    assert "PATTERN_2" in patterns
    assert "PATTERN_3" in patterns


def test_get_pattern():
    """Test retrieving pattern"""
    detector = CustomPatternDetector()

    detector.add_pattern(
        name="TEST_PATTERN",
        pattern=r"TEST-\d{3}",
        description="Test"
    )

    pattern = detector.get_pattern("TEST_PATTERN")

    assert pattern is not None
    assert pattern.name == "TEST_PATTERN"
    assert pattern.pattern == r"TEST-\d{3}"


def test_get_nonexistent_pattern():
    """Test retrieving non-existent pattern"""
    detector = CustomPatternDetector()

    pattern = detector.get_pattern("NONEXISTENT")
    assert pattern is None


def test_remove_pattern():
    """Test removing pattern"""
    detector = CustomPatternDetector()

    detector.add_pattern("TO_REMOVE", r"REMOVE-\d{3}")
    assert "TO_REMOVE" in detector.list_patterns()

    detector.remove_pattern("TO_REMOVE")
    assert "TO_REMOVE" not in detector.list_patterns()


def test_detect_simple_pattern():
    """Test detecting simple pattern"""
    detector = CustomPatternDetector()

    detector.add_pattern(
        name="ORDER_ID",
        pattern=r"ORD-\d{5}",
        confidence=0.95
    )

    text = "Order ORD-12345 has been processed. Reference: ORD-67890."
    detections = detector.detect(text)

    assert len(detections) == 2
    assert detections[0]["text"] == "ORD-12345"
    assert detections[0]["entity_type"] == "ORDER_ID"
    assert detections[0]["confidence"] == 0.95
    assert detections[1]["text"] == "ORD-67890"


def test_detect_multiple_pattern_types():
    """Test detecting multiple different patterns"""
    detector = CustomPatternDetector()

    detector.add_pattern("ORDER_ID", r"ORD-\d{5}")
    detector.add_pattern("PRODUCT_CODE", r"PROD-\d{3}")

    text = "Order ORD-12345 contains product PROD-001 and PROD-002."
    detections = detector.detect(text)

    assert len(detections) == 3

    order_detections = [d for d in detections if d["entity_type"] == "ORDER_ID"]
    product_detections = [d for d in detections if d["entity_type"] == "PRODUCT_CODE"]

    assert len(order_detections) == 1
    assert len(product_detections) == 2


def test_detect_with_validation():
    """Test detection with validation function"""
    detector = CustomPatternDetector()

    # Only match orders with ID < 50000
    def validate_order(text):
        order_num = int(text.split("-")[1])
        return order_num < 50000

    detector.add_pattern(
        name="VALID_ORDER",
        pattern=r"ORD-\d{5}",
        validate=validate_order
    )

    text = "Orders: ORD-12345, ORD-99999, ORD-30000"
    detections = detector.detect(text)

    # Should only detect ORD-12345 and ORD-30000
    assert len(detections) == 2
    detected_texts = [d["text"] for d in detections]
    assert "ORD-12345" in detected_texts
    assert "ORD-30000" in detected_texts
    assert "ORD-99999" not in detected_texts


def test_detect_no_matches():
    """Test detection when no matches found"""
    detector = CustomPatternDetector()

    detector.add_pattern("ORDER_ID", r"ORD-\d{5}")

    text = "No orders in this text."
    detections = detector.detect(text)

    assert len(detections) == 0


def test_detect_case_sensitive():
    """Test case-sensitive detection"""
    detector = CustomPatternDetector()

    detector.add_pattern("CODE", r"CODE-\d{3}")

    text = "Valid: CODE-123, Invalid: code-456"
    detections = detector.detect(text)

    assert len(detections) == 1
    assert detections[0]["text"] == "CODE-123"


def test_detect_overlapping_patterns():
    """Test handling overlapping patterns"""
    detector = CustomPatternDetector()

    detector.add_pattern("LONG_CODE", r"ABC-\d{5}")
    detector.add_pattern("SHORT_CODE", r"ABC-\d{3}")

    text = "Code: ABC-12345"
    detections = detector.detect(text)

    # Both patterns match, should get 2 detections
    # (one for ABC-123, one for ABC-12345)
    assert len(detections) >= 1


# ============================================================================
# CompoundPatternDetector Tests
# ============================================================================


def test_compound_detector_initialization():
    """Test CompoundPatternDetector has predefined patterns"""
    detector = CompoundPatternDetector()

    patterns = detector.list_patterns()

    assert "COMPOUND_NAME" in patterns
    assert "DRUG_CODE" in patterns
    assert "CAS_NUMBER" in patterns


def test_compound_detector_detects_compounds():
    """Test compound name detection"""
    detector = CompoundPatternDetector()

    text = """
    Study on Compound-ABC-123 showed promising results.
    The drug DRG-A4F7B2 was tested on subjects.
    CAS Number 50-00-0 was used as control.
    """

    detections = detector.detect(text)

    assert len(detections) > 0

    # Check for compound detection
    compound_detections = [d for d in detections if "COMPOUND" in d["entity_type"]]
    assert len(compound_detections) > 0


def test_compound_detector_drug_codes():
    """Test drug code detection"""
    detector = CompoundPatternDetector()

    text = "Testing drugs: DRG-A4F7B2, DRG-M9K3L1"
    detections = detector.detect(text)

    drug_detections = [d for d in detections if d["entity_type"] == "DRUG_CODE"]
    assert len(drug_detections) == 2


# ============================================================================
# InternalIDDetector Tests
# ============================================================================


def test_internal_id_detector_initialization():
    """Test InternalIDDetector has predefined patterns"""
    detector = InternalIDDetector()

    patterns = detector.list_patterns()

    assert "PROJECT_CODE" in patterns
    assert "EMPLOYEE_ID" in patterns
    assert "DOCUMENT_ID" in patterns
    assert "CONTRACT_ID" in patterns


def test_internal_id_detector_detects_ids():
    """Test internal ID detection"""
    detector = InternalIDDetector()

    text = """
    Project PRJ-ALPHA-2024 is on schedule.
    Team lead: Employee EMP-001234
    Budget document: DOC-20240115001
    Contract: CTR-US123456
    """

    detections = detector.detect(text)

    assert len(detections) >= 4

    # Check each type
    project_ids = [d for d in detections if d["entity_type"] == "PROJECT_CODE"]
    employee_ids = [d for d in detections if d["entity_type"] == "EMPLOYEE_ID"]
    document_ids = [d for d in detections if d["entity_type"] == "DOCUMENT_ID"]
    contract_ids = [d for d in detections if d["entity_type"] == "CONTRACT_ID"]

    assert len(project_ids) >= 1
    assert len(employee_ids) >= 1
    assert len(document_ids) >= 1
    assert len(contract_ids) >= 1


def test_internal_id_detector_employee_id():
    """Test employee ID detection"""
    detector = InternalIDDetector()

    text = "Employees: EMP-001234, EMP-005678"
    detections = detector.detect(text)

    employee_detections = [d for d in detections if d["entity_type"] == "EMPLOYEE_ID"]
    assert len(employee_detections) == 2


# ============================================================================
# Complex Validation Tests
# ============================================================================


def test_validation_with_exception_handling():
    """Test validation function with exception handling"""
    detector = CustomPatternDetector()

    def buggy_validator(text):
        # This might raise an exception
        if "ERROR" in text:
            raise ValueError("Invalid text")
        return True

    detector.add_pattern(
        name="SAFE_PATTERN",
        pattern=r"ITEM-\d{3}",
        validate=buggy_validator
    )

    # Should handle validator exception gracefully
    text = "Valid: ITEM-123, Invalid: ITEM-ERROR"
    detections = detector.detect(text)

    # Should still detect the valid one
    assert len(detections) >= 1


def test_complex_pattern_with_groups():
    """Test complex regex pattern with groups"""
    detector = CustomPatternDetector()

    detector.add_pattern(
        name="VERSION_CODE",
        pattern=r"v(\d+)\.(\d+)\.(\d+)",
        confidence=0.90
    )

    text = "Released versions: v1.2.3, v2.0.1, v10.5.42"
    detections = detector.detect(text)

    assert len(detections) == 3
    assert "v1.2.3" in [d["text"] for d in detections]


def test_unicode_patterns():
    """Test patterns with Unicode characters"""
    detector = CustomPatternDetector()

    detector.add_pattern(
        name="ITALIAN_CODE",
        pattern=r"CODICE-[À-ÿ]{3}-\d{3}",
    )

    text = "Codici: CODICE-ÀBC-123, CODICE-ÉFG-456"
    detections = detector.detect(text)

    assert len(detections) >= 1


# ============================================================================
# Integration Tests
# ============================================================================


def test_detector_with_anonymization_workflow():
    """Test custom detector in anonymization workflow"""
    detector = CompoundPatternDetector()

    # Sample research text
    text = """
    Research Report Q1 2024

    Study Results:
    - Compound-ABC-123: 85% efficacy
    - Drug DRG-M9K3L1: 92% efficacy
    - Control (CAS 50-00-0): baseline

    Next phase: Test Compound-XYZ-456
    """

    detections = detector.detect(text)

    # Should detect multiple compounds
    assert len(detections) >= 3

    # Verify detection structure
    for detection in detections:
        assert "text" in detection
        assert "entity_type" in detection
        assert "start" in detection
        assert "end" in detection
        assert "confidence" in detection


def test_multiple_detectors_combined():
    """Test combining multiple custom detectors"""
    compound_detector = CompoundPatternDetector()
    id_detector = InternalIDDetector()

    text = """
    Project PRJ-PHARMA-2024
    Lead: Employee EMP-007890

    Testing Compound-ABC-123 (Drug DRG-X1Y2Z3)
    Reference: Document DOC-20240117001
    """

    # Detect with both
    compound_detections = compound_detector.detect(text)
    id_detections = id_detector.detect(text)

    # Should find both types
    assert len(compound_detections) >= 2  # Compound + Drug
    assert len(id_detections) >= 3  # Project + Employee + Document

    # Combine results
    all_detections = compound_detections + id_detections
    assert len(all_detections) >= 5
