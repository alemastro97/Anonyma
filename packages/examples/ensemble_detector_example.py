#!/usr/bin/env python3
"""
Example: Ensemble Detector for Maximum Accuracy

Demonstrates how to use ensemble detection to combine:
- Presidio (rule-based + basic NER)
- Flair (deep learning NER)
- Custom patterns (regex)

With intelligent voting and confidence aggregation.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from anonyma_core.detectors.ensemble_detector import (
    EnsembleDetector,
    AdaptiveEnsembleDetector
)
from anonyma_core.detectors.custom_detector import CustomPatternDetector
from anonyma_core.modes import Redactor


def example_1_basic_ensemble():
    """Example 1: Basic ensemble with Presidio only"""
    print("=" * 70)
    print("EXAMPLE 1: Basic Ensemble (Presidio Only)")
    print("=" * 70)
    print()

    text = """
    Informazioni personali:
    Nome: Mario Rossi
    Email: mario.rossi@example.com
    Telefono: +39 339 1234567
    Codice Fiscale: RSSMRA85C15H501X
    Indirizzo: Via Roma 123, Milano
    """

    print("Original Text:")
    print("-" * 70)
    print(text)
    print()

    # Basic ensemble (Presidio only)
    detector = EnsembleDetector(
        use_presidio=True,
        use_flair=False,
        voting_strategy="any"
    )

    detections = detector.detect(text)

    print(f"Detections Found: {len(detections)}")
    print("-" * 70)
    for detection in detections:
        print(f"  • {detection['entity_type']}: '{detection['text']}'")
        print(f"    Confidence: {detection['confidence']:.2f}")
        print(f"    Votes: {detection['votes']}")
        print(f"    Detectors: {', '.join(detection['detectors'])}")
        print()


def example_2_ensemble_with_custom():
    """Example 2: Ensemble with custom patterns"""
    print("=" * 70)
    print("EXAMPLE 2: Ensemble with Custom Patterns")
    print("=" * 70)
    print()

    text = """
    Research Study Report

    Patient ID: PAT-2024-001
    Study Code: STUDY-XYZ-789
    Compound: COMP-ABC-123

    Participant: Dr. Mario Rossi
    Email: mario.rossi@hospital.it
    Internal ID: EMP-005678
    """

    print("Original Text:")
    print("-" * 70)
    print(text)
    print()

    # Create custom detector
    custom = CustomPatternDetector()
    custom.add_pattern("PATIENT_ID", r"PAT-\d{4}-\d{3}")
    custom.add_pattern("STUDY_CODE", r"STUDY-[A-Z]{3}-\d{3}")
    custom.add_pattern("COMPOUND_ID", r"COMP-[A-Z]{3}-\d{3}")
    custom.add_pattern("EMPLOYEE_ID", r"EMP-\d{6}")

    # Ensemble with custom patterns
    detector = EnsembleDetector(
        use_presidio=True,
        use_flair=False,
        use_custom=True,
        custom_patterns=custom,
        voting_strategy="any"
    )

    detections = detector.detect(text)

    print(f"Detections Found: {len(detections)}")
    print("-" * 70)
    for detection in detections:
        print(f"  • {detection['entity_type']}: '{detection['text']}'")
        print(f"    Confidence: {detection['confidence']:.2f}")
        print(f"    Votes: {detection['votes']}")
        print(f"    Detectors: {', '.join(detection['detectors'])}")
        print()


def example_3_voting_strategies():
    """Example 3: Different voting strategies"""
    print("=" * 70)
    print("EXAMPLE 3: Voting Strategies Comparison")
    print("=" * 70)
    print()

    text = "Mario Rossi (mario.rossi@email.com) abita a Milano."

    print("Original Text:")
    print("-" * 70)
    print(text)
    print()

    strategies = ["any", "majority", "unanimous", "weighted"]

    for strategy in strategies:
        print(f"\nStrategy: {strategy.upper()}")
        print("-" * 40)

        try:
            detector = EnsembleDetector(
                use_presidio=True,
                use_flair=False,
                voting_strategy=strategy,
                min_confidence=0.5
            )

            detections = detector.detect(text)

            print(f"Detections: {len(detections)}")
            for detection in detections:
                print(f"  • {detection['entity_type']}: '{detection['text']}'")
                print(f"    Confidence: {detection['confidence']:.2f}, Votes: {detection['votes']}")

        except Exception as e:
            print(f"Error: {e}")


def example_4_weighted_ensemble():
    """Example 4: Weighted ensemble with custom weights"""
    print("=" * 70)
    print("EXAMPLE 4: Weighted Ensemble")
    print("=" * 70)
    print()

    text = """
    Report medico:
    Paziente: Mario Rossi
    CF: RSSMRA85C15H501X
    Email: mario.rossi@ospedale.it
    Telefono: +39 339 1234567
    """

    print("Original Text:")
    print("-" * 70)
    print(text)
    print()

    # Create ensemble with custom weights
    detector = EnsembleDetector(
        use_presidio=True,
        use_flair=False,
        voting_strategy="weighted",
        min_confidence=0.6
    )

    # Adjust weights (if we had Flair, we'd give it higher weight)
    detector.set_detector_weight("PIIDetector", 1.0)

    detections = detector.detect(text)

    print(f"Detections Found: {len(detections)}")
    print("-" * 70)
    for detection in detections:
        print(f"  • {detection['entity_type']}: '{detection['text']}'")
        print(f"    Confidence: {detection['confidence']:.2f}")
        print()

    # Get detector stats
    print("\nDetector Statistics:")
    print("-" * 70)
    stats = detector.get_detector_stats(text)
    for detector_stat in stats["detectors"]:
        print(f"  • {detector_stat['name']}")
        print(f"    Detections: {detector_stat['detections']}")
        print(f"    Weight: {detector_stat['weight']}")
        print()


def example_5_adaptive_ensemble():
    """Example 5: Adaptive ensemble with feedback learning"""
    print("=" * 70)
    print("EXAMPLE 5: Adaptive Ensemble with Learning")
    print("=" * 70)
    print()

    text = """
    Cliente: Mario Rossi
    Email: mario.rossi@example.com
    Telefono: +39 339 1234567
    Codice: CUST-12345
    """

    print("Original Text:")
    print("-" * 70)
    print(text)
    print()

    # Create adaptive ensemble
    detector = AdaptiveEnsembleDetector(
        use_presidio=True,
        use_flair=False,
        voting_strategy="weighted"
    )

    # Run detection
    detections = detector.detect(text)

    print(f"Detections Found: {len(detections)}")
    print("-" * 70)
    for detection in detections:
        print(f"  • {detection['entity_type']}: '{detection['text']}'")
        print()

    # Simulate feedback
    print("\nSimulating Feedback:")
    print("-" * 70)
    print("Reporting correct detections (training the system)...")

    for detection in detections:
        # Simulate feedback (in real app, this would come from users)
        is_correct = detection['entity_type'] in ['PERSON', 'EMAIL_ADDRESS', 'PHONE_NUMBER']
        detector.report_feedback(detection, is_correct)
        print(f"  • {detection['text']}: {'✓ Correct' if is_correct else '✗ Incorrect'}")

    # Show performance stats
    print("\nPerformance Statistics:")
    print("-" * 70)
    stats = detector.get_performance_stats()
    for detector_name, stat in stats.items():
        print(f"  • {detector_name}")
        print(f"    Accuracy: {stat['accuracy']:.2%}")
        print(f"    Weight: {stat['weight']:.2f}")
        print(f"    Total Feedback: {stat['total']}")
        print()


def example_6_anonymization_workflow():
    """Example 6: Complete workflow with anonymization"""
    print("=" * 70)
    print("EXAMPLE 6: Complete Workflow")
    print("=" * 70)
    print()

    text = """
    DOCUMENTO RISERVATO

    Dipendente: Mario Rossi
    Codice: EMP-001234
    Email: mario.rossi@company.it
    Telefono: +39 339 1234567
    CF: RSSMRA85C15H501X
    Progetto: PRJ-ALPHA-2024
    """

    print("Original Text:")
    print("-" * 70)
    print(text)
    print()

    # Create custom patterns for company data
    custom = CustomPatternDetector()
    custom.add_pattern("EMPLOYEE_ID", r"EMP-\d{6}")
    custom.add_pattern("PROJECT_CODE", r"PRJ-[A-Z]{3,5}-\d{4}")

    # Create ensemble
    detector = EnsembleDetector(
        use_presidio=True,
        use_flair=False,
        use_custom=True,
        custom_patterns=custom,
        voting_strategy="weighted",
        min_confidence=0.5
    )

    # Detect
    detections = detector.detect(text)

    print(f"Detections Found: {len(detections)}")
    print("-" * 70)

    # Group by entity type
    by_type = {}
    for det in detections:
        entity_type = det['entity_type']
        if entity_type not in by_type:
            by_type[entity_type] = []
        by_type[entity_type].append(det['text'])

    for entity_type, entities in sorted(by_type.items()):
        print(f"  • {entity_type}: {len(entities)}")
        for entity in entities:
            print(f"    - {entity}")
    print()

    # Anonymize
    redactor = Redactor()
    anonymized = redactor.anonymize(text, detections)

    print("Anonymized Text:")
    print("-" * 70)
    print(anonymized)
    print()


def main():
    """Run all examples"""
    print()
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 20 + "ENSEMBLE DETECTOR EXAMPLES" + " " * 22 + "║")
    print("╚" + "=" * 68 + "╝")
    print()
    print("Demonstrating ensemble detection for maximum accuracy")
    print()

    try:
        example_1_basic_ensemble()
        input("Press Enter to continue to next example...\n")

        example_2_ensemble_with_custom()
        input("Press Enter to continue to next example...\n")

        example_3_voting_strategies()
        input("Press Enter to continue to next example...\n")

        example_4_weighted_ensemble()
        input("Press Enter to continue to next example...\n")

        example_5_adaptive_ensemble()
        input("Press Enter to continue to next example...\n")

        example_6_anonymization_workflow()

        print("=" * 70)
        print("ALL EXAMPLES COMPLETED!")
        print("=" * 70)
        print()
        print("Key Takeaways:")
        print("  ✓ Ensemble combines multiple detectors")
        print("  ✓ Voting strategies control strictness")
        print("  ✓ Weighted ensemble for confidence-based decisions")
        print("  ✓ Adaptive ensemble learns from feedback")
        print("  ✓ Custom patterns integrate seamlessly")
        print()

    except KeyboardInterrupt:
        print("\n\n⚠️  Examples interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
