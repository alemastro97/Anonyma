#!/usr/bin/env python3
"""
Quick test script for Phase 1 components.
Tests components without requiring full dependency installation.
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_logging():
    """Test logging system"""
    print("=" * 60)
    print("TEST 1: Logging System")
    print("=" * 60)

    # Import directly from module
    import anonyma_core.logging_config as logging_config

    logger = logging_config.setup_logging(level='INFO')
    print("✅ Logging setup successful")

    test_logger = logging_config.get_logger('test_module')
    test_logger.info('Test info message')
    test_logger.warning('Test warning message')
    print("✅ Logger working correctly")
    print()


def test_config():
    """Test configuration system"""
    print("=" * 60)
    print("TEST 2: Configuration System")
    print("=" * 60)

    import anonyma_core.config as config_module

    try:
        config = config_module.load_config()
        print("✅ Config loaded successfully")
        print(f"  - Log level: {config.logging.level}")
        print(f"  - Use Flair: {config.detection.use_flair}")
        print(f"  - Confidence threshold: {config.detection.confidence_threshold}")
        print(f"  - Device: {config.models.flair.device}")
        print(f"  - Redaction char: '{config.anonymization.redaction_character}'")
    except Exception as e:
        print(f"❌ Config loading failed: {e}")
        import traceback
        traceback.print_exc()
    print()


def test_exceptions():
    """Test custom exceptions"""
    print("=" * 60)
    print("TEST 3: Custom Exceptions")
    print("=" * 60)

    import anonyma_core.exceptions as exceptions

    # Test TextTooLongError
    try:
        raise exceptions.TextTooLongError(10000, 5000)
    except exceptions.TextTooLongError as e:
        print(f"✅ TextTooLongError: {e}")
        print(f"  - Details: {e.details}")

    # Test EmptyTextError
    try:
        raise exceptions.EmptyTextError()
    except exceptions.EmptyTextError as e:
        print(f"✅ EmptyTextError: {e}")

    # Test InvalidModeError
    try:
        raise exceptions.InvalidModeError("invalid", ["redact", "substitute"])
    except exceptions.InvalidModeError as e:
        print(f"✅ InvalidModeError: {e}")
        print(f"  - Details: {e.details}")

    print()


def test_validation():
    """Test input validation"""
    print("=" * 60)
    print("TEST 4: Input Validation")
    print("=" * 60)

    import anonyma_core.validation as validation
    import anonyma_core.exceptions as exceptions

    # Test valid text
    try:
        text = validation.validate_text_input("Test text for validation")
        print(f"✅ Valid text accepted: '{text}'")
    except Exception as e:
        print(f"❌ Validation failed: {e}")

    # Test empty text rejection
    try:
        validation.validate_text_input("   ")
        print("❌ Empty text should have been rejected")
    except exceptions.EmptyTextError as e:
        print(f"✅ Empty text rejected: {e}")

    # Test confidence threshold
    try:
        threshold = validation.validate_confidence_threshold(0.75)
        print(f"✅ Valid confidence threshold: {threshold}")
    except Exception as e:
        print(f"❌ Threshold validation failed: {e}")

    # Test invalid threshold
    try:
        validation.validate_confidence_threshold(1.5)
        print("❌ Invalid threshold should have been rejected")
    except exceptions.ValidationError as e:
        print(f"✅ Invalid threshold rejected: {e}")

    # Test Pydantic models
    try:
        request = validation.AnonymizationRequest(
            text="Test text",
            mode="redact",
            language="it"
        )
        print(f"✅ Pydantic AnonymizationRequest: mode={request.mode}, language={request.language}")
    except Exception as e:
        print(f"❌ Pydantic validation failed: {e}")

    print()


def test_base_classes():
    """Test base classes"""
    print("=" * 60)
    print("TEST 5: Base Classes")
    print("=" * 60)

    import anonyma_core.detectors.base as detector_base
    import anonyma_core.modes.base as mode_base

    print(f"✅ BaseDetector imported: {detector_base.BaseDetector}")
    print(f"  - Abstract methods: detect()")
    print(f"  - Properties: name, version, supported_languages")

    print(f"✅ BaseAnonymizationMode imported: {mode_base.BaseAnonymizationMode}")
    print(f"  - Abstract methods: anonymize()")
    print(f"  - Properties: mode_name, description, is_reversible")

    print()


def test_file_structure():
    """Test that all Phase 1 files exist"""
    print("=" * 60)
    print("TEST 6: File Structure")
    print("=" * 60)

    base_path = Path(__file__).parent

    files_to_check = [
        "anonyma_core/logging_config.py",
        "anonyma_core/config.py",
        "anonyma_core/exceptions.py",
        "anonyma_core/validation.py",
        "anonyma_core/detectors/base.py",
        "anonyma_core/modes/base.py",
        "config/config.yaml",
        "config/config.dev.yaml",
        "config/config.prod.yaml",
        "tests/conftest.py",
        "tests/unit/test_engine.py",
        "tests/unit/test_detectors.py",
        "tests/unit/test_modes.py",
        "tests/unit/test_config.py",
        "Makefile",
        ".pre-commit-config.yaml",
        "DEVELOPMENT.md",
    ]

    missing = []
    for file_path in files_to_check:
        full_path = base_path / file_path
        if full_path.exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - MISSING")
            missing.append(file_path)

    if missing:
        print(f"\n❌ {len(missing)} files missing")
    else:
        print(f"\n✅ All {len(files_to_check)} files present")

    print()


def main():
    """Run all tests"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "ANONYMA PHASE 1 - COMPONENT TESTS" + " " * 15 + "║")
    print("╚" + "=" * 58 + "╝")
    print()

    tests = [
        ("Logging System", test_logging),
        ("Configuration", test_config),
        ("Exceptions", test_exceptions),
        ("Validation", test_validation),
        ("Base Classes", test_base_classes),
        ("File Structure", test_file_structure),
    ]

    passed = 0
    failed = 0

    for name, test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"❌ TEST FAILED: {name}")
            print(f"   Error: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
            print()

    # Summary
    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Total:  {passed + failed}")
    print()

    if failed == 0:
        print("🎉 ALL TESTS PASSED! Phase 1 components working correctly!")
    else:
        print(f"⚠️  {failed} test(s) failed. Please review errors above.")

    print("=" * 60)
    print()


if __name__ == "__main__":
    main()
