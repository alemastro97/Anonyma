#!/usr/bin/env python3
"""
Example: Custom Pattern Detection for Any Sensitive Data

Demonstrates how to detect and anonymize ANY type of sensitive information,
not just standard PII. Examples include:
- Chemical compound names
- Internal IDs and codes
- Drug research codes
- Proprietary identifiers
- Domain-specific patterns

This shows that Anonyma is not limited to emails, names, etc., but can
handle ANY pattern you define!
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from anonyma_core.detectors.custom_detector import (
    CustomPatternDetector,
    CustomPattern,
    CompoundPatternDetector,
    InternalIDDetector,
)
from anonyma_core.modes.redactor import Redactor


def example_1_chemical_compounds():
    """Example 1: Detecting chemical compound identifiers"""
    print("=" * 70)
    print("EXAMPLE 1: Chemical Compound Detection")
    print("=" * 70)
    print()

    # Sample text with compound names
    text = """
    Research Report - Q1 2024

    Study on Compound-XYZ-123 showed promising results.
    The drug DRG-A4F7B2 was tested on 50 subjects.
    CAS Number 50-00-0 (formaldehyde) was used as control.

    Compound-ABC-456 demonstrated 85% efficacy.
    Further testing of DRG-M9K3L1 is recommended.
    """

    print("Original Text:")
    print("-" * 70)
    print(text)
    print()

    # Create detector with compound patterns
    detector = CompoundPatternDetector()

    # Detect
    detections = detector.detect(text)

    print(f"Detections Found: {len(detections)}")
    print("-" * 70)
    for detection in detections:
        print(f"  • {detection['entity_type']}: '{detection['text']}' (confidence: {detection['confidence']})")
    print()

    # Anonymize
    redactor = Redactor()
    anonymized = redactor.anonymize(text, detections)

    print("Anonymized Text:")
    print("-" * 70)
    print(anonymized)
    print()


def example_2_internal_ids():
    """Example 2: Detecting internal company identifiers"""
    print("=" * 70)
    print("EXAMPLE 2: Internal ID Detection")
    print("=" * 70)
    print()

    # Sample text with internal IDs
    text = """
    Project Status Update

    Project PRJ-ALPHA-2024 is on schedule.
    Team lead: Employee EMP-001234
    Budget: Document DOC-20240115001

    Contract CTR-US123456 signed by EMP-005678.
    Next milestone: PRJ-BETA-2024 kickoff.
    """

    print("Original Text:")
    print("-" * 70)
    print(text)
    print()

    # Create detector with internal ID patterns
    detector = InternalIDDetector()

    # Detect
    detections = detector.detect(text)

    print(f"Detections Found: {len(detections)}")
    print("-" * 70)
    for detection in detections:
        print(f"  • {detection['entity_type']}: '{detection['text']}' (confidence: {detection['confidence']})")
    print()

    # Anonymize
    redactor = Redactor()
    anonymized = redactor.anonymize(text, detections)

    print("Anonymized Text:")
    print("-" * 70)
    print(anonymized)
    print()


def example_3_custom_patterns():
    """Example 3: Adding your own custom patterns"""
    print("=" * 70)
    print("EXAMPLE 3: Custom Pattern Definition")
    print("=" * 70)
    print()

    # Sample text with custom identifiers
    text = """
    Lab Report - Experiment XP-2024-001

    Sample ID: SAMPLE-A1B2C3
    Batch number: BATCH-20240117-001
    Machine: INSTRUMENT-MS-07

    Results stored in file: DATA-XP2024-A1B2.csv
    Analyzed by: USER-12345
    """

    print("Original Text:")
    print("-" * 70)
    print(text)
    print()

    # Create custom detector
    detector = CustomPatternDetector()

    # Add custom patterns
    print("Adding custom patterns...")
    print("-" * 70)

    detector.add_pattern(
        name="EXPERIMENT_ID",
        pattern=r"XP-\d{4}-\d{3}",
        confidence=0.95,
        description="Experiment identifier",
    )

    detector.add_pattern(
        name="SAMPLE_ID",
        pattern=r"SAMPLE-[A-Z0-9]{6}",
        confidence=0.95,
        description="Sample identifier",
    )

    detector.add_pattern(
        name="BATCH_NUMBER",
        pattern=r"BATCH-\d{8}-\d{3}",
        confidence=0.95,
        description="Batch number",
    )

    detector.add_pattern(
        name="INSTRUMENT_ID",
        pattern=r"INSTRUMENT-[A-Z]{2}-\d{2}",
        confidence=0.95,
        description="Instrument identifier",
    )

    detector.add_pattern(
        name="DATA_FILE",
        pattern=r"DATA-[A-Z0-9]+-[A-Z0-9]+\.csv",
        confidence=0.90,
        description="Data file name",
    )

    detector.add_pattern(
        name="USER_ID",
        pattern=r"USER-\d{5}",
        confidence=0.95,
        description="User identifier",
    )

    print(f"Added {len(detector.list_patterns())} custom patterns:")
    for pattern_name in detector.list_patterns():
        pattern = detector.get_pattern(pattern_name)
        print(f"  • {pattern_name}: {pattern.description}")
    print()

    # Detect
    detections = detector.detect(text)

    print(f"Detections Found: {len(detections)}")
    print("-" * 70)
    for detection in detections:
        print(f"  • {detection['entity_type']}: '{detection['text']}'")
    print()

    # Anonymize
    redactor = Redactor()
    anonymized = redactor.anonymize(text, detections)

    print("Anonymized Text:")
    print("-" * 70)
    print(anonymized)
    print()


def example_4_with_validation():
    """Example 4: Custom patterns with validation functions"""
    print("=" * 70)
    print("EXAMPLE 4: Custom Patterns with Validation")
    print("=" * 70)
    print()

    # Sample text
    text = """
    Order Summary

    Order ID: ORD-12345 (valid)
    Order ID: ORD-99999 (invalid - test order)
    Order ID: ORD-54321 (valid)

    Product codes: PROD-001, PROD-002, PROD-999
    """

    print("Original Text:")
    print("-" * 70)
    print(text)
    print()

    # Create detector
    detector = CustomPatternDetector()

    # Validation function: only anonymize orders < 90000
    def validate_order(text):
        """Only match real orders (ID < 90000)"""
        order_num = int(text.split("-")[1])
        return order_num < 90000

    # Add pattern with validation
    detector.add_pattern(
        name="ORDER_ID",
        pattern=r"ORD-\d{5}",
        confidence=0.95,
        description="Order ID (validated)",
        validate=validate_order,
    )

    # Simple pattern without validation
    detector.add_pattern(
        name="PRODUCT_CODE", pattern=r"PROD-\d{3}", confidence=0.90, description="Product code"
    )

    print("Patterns with validation:")
    print("-" * 70)
    print("  • ORDER_ID: Only matches orders with ID < 90000")
    print("  • PRODUCT_CODE: Matches all product codes")
    print()

    # Detect
    detections = detector.detect(text)

    print(f"Detections Found: {len(detections)}")
    print("-" * 70)
    for detection in detections:
        print(f"  • {detection['entity_type']}: '{detection['text']}'")
    print()

    print("Notice: ORD-99999 was NOT detected due to validation function!")
    print()

    # Anonymize
    redactor = Redactor()
    anonymized = redactor.anonymize(text, detections)

    print("Anonymized Text:")
    print("-" * 70)
    print(anonymized)
    print()


def example_5_image_with_custom_patterns():
    """Example 5: Using custom patterns with images (conceptual)"""
    print("=" * 70)
    print("EXAMPLE 5: Custom Patterns for Image Processing")
    print("=" * 70)
    print()

    print("Scenario: You have an image of a document containing:")
    print("  • Drug research codes (DRC-XXXX)")
    print("  • Compound names (Compound-XXX-123)")
    print("  • Internal protocol IDs (PROTO-2024-XXX)")
    print()

    print("How it works:")
    print("-" * 70)
    print("1. Use OCR to extract text from image")
    print("2. Define custom patterns for your specific data")
    print("3. Detect patterns in extracted text")
    print("4. Map detections back to image coordinates")
    print("5. Draw black boxes over sensitive regions")
    print()

    # Example code
    print("Code Example:")
    print("-" * 70)
    print("""
from anonyma_core import AnonymaEngine
from anonyma_core.documents import DocumentPipeline, ImageDocument
from anonyma_core.detectors.custom_detector import CustomPatternDetector

# Create custom detector
custom_detector = CustomPatternDetector()
custom_detector.add_pattern(
    name="DRUG_RESEARCH_CODE",
    pattern=r"DRC-[A-Z0-9]{4}",
    confidence=0.95
)

# Initialize engine with custom detector
engine = AnonymaEngine(use_flair=False)
# Add custom detector to engine (future feature)

# Process image
pipeline = DocumentPipeline(engine)
result = pipeline.process(
    file_path=Path("research_document.png"),
    mode=AnonymizationMode.REDACT,
    output_path=Path("anonymized.png")
)

# Result: Image with black boxes over DRC codes!
    """)
    print()


def main():
    """Run all examples"""
    print()
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "CUSTOM PATTERN DETECTION EXAMPLES" + " " * 20 + "║")
    print("╚" + "=" * 68 + "╝")
    print()
    print("This demonstrates Anonyma's flexibility to detect and anonymize")
    print("ANY type of sensitive data, not just standard PII!")
    print()

    try:
        example_1_chemical_compounds()
        input("Press Enter to continue to next example...\n")

        example_2_internal_ids()
        input("Press Enter to continue to next example...\n")

        example_3_custom_patterns()
        input("Press Enter to continue to next example...\n")

        example_4_with_validation()
        input("Press Enter to continue to next example...\n")

        example_5_image_with_custom_patterns()

        print("=" * 70)
        print("ALL EXAMPLES COMPLETED!")
        print("=" * 70)
        print()
        print("Key Takeaways:")
        print("  ✓ You can detect ANY pattern with regex")
        print("  ✓ Add validation functions for complex logic")
        print("  ✓ Combine with standard PII detection")
        print("  ✓ Works with documents and images")
        print("  ✓ Not limited to emails, names, phone numbers!")
        print()

    except KeyboardInterrupt:
        print("\n\n⚠️  Examples interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
