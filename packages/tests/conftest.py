"""
Pytest configuration and shared fixtures for Anonyma tests.
"""

import pytest
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from anonyma_core import AnonymaEngine, AnonymizationMode
from anonyma_core.detectors.pii_detector import PIIDetector


@pytest.fixture
def sample_text_italian():
    """Sample Italian text with PII"""
    return """
    Il sig. Mario Rossi, nato il 15/03/1985, abita in Via Roma 123, Milano.
    Email: mario.rossi@email.com
    Telefono: +39 339 1234567
    Codice Fiscale: RSSMRA85C15H501X
    """


@pytest.fixture
def sample_text_english():
    """Sample English text with PII"""
    return """
    John Smith was born on 03/15/1985 and lives at 123 Main Street, New York.
    Email: john.smith@example.com
    Phone: +1 555-123-4567
    SSN: 123-45-6789
    """


@pytest.fixture
def sample_text_no_pii():
    """Sample text without PII"""
    return "This is a simple text without any personal information."


@pytest.fixture
def empty_text():
    """Empty text"""
    return ""


@pytest.fixture
def engine_basic():
    """Engine with basic detector (no Flair)"""
    return AnonymaEngine(use_flair=False)


@pytest.fixture
def basic_detector():
    """Basic PII detector instance"""
    return PIIDetector()


@pytest.fixture
def sample_detections():
    """Sample detection results"""
    return [
        {
            'entity_type': 'EMAIL',
            'start': 10,
            'end': 30,
            'confidence': 0.9,
            'text': 'test@example.com'
        },
        {
            'entity_type': 'PHONE',
            'start': 50,
            'end': 65,
            'confidence': 0.85,
            'text': '+39 339 1234567'
        }
    ]
