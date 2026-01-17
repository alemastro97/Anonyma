# Development Guide

This guide covers the development setup and workflow for Anonyma Core.

## Quick Start

```bash
# Install dependencies
make install-dev

# Run tests
make test

# Run all quality checks
make quality

# Format code
make format
```

## Setup

### 1. Install Dependencies

```bash
# Basic installation
pip install -r requirements.txt

# Development installation (includes testing and linting tools)
pip install -e ".[dev]"

# Or use make
make install-dev
```

### 2. Set up Pre-commit Hooks (Optional but Recommended)

Pre-commit hooks automatically run quality checks before each commit:

```bash
pip install pre-commit
pre-commit install
```

Now quality checks will run automatically on `git commit`.

## Development Workflow

### Running Tests

```bash
# Run all tests
make test
# or
pytest

# Run tests with verbose output
make test-verbose
# or
pytest -vv

# Run specific test file
pytest tests/unit/test_engine.py

# Run specific test
pytest tests/unit/test_engine.py::TestAnonymaEngineRedactMode::test_redact_mode_with_pii

# Run tests with coverage
make coverage
# Coverage report will be in htmlcov/index.html
```

### Code Quality

#### Formatting

```bash
# Format code automatically (black + isort)
make format

# Check formatting without changes
make format-check
```

#### Linting

```bash
# Run linter (ruff)
make lint

# Auto-fix linting issues
make lint-fix
```

#### Type Checking

```bash
# Run type checking (mypy)
make type-check
```

#### All Quality Checks

```bash
# Run all quality checks (lint + type-check + format-check)
make quality
```

### Before Committing

```bash
# Run all checks (format + quality + tests)
make pre-commit
```

This will:
1. Format your code
2. Run linters
3. Run type checking
4. Run all tests

If everything passes, you're ready to commit!

## Configuration

### Logging

Configure logging via environment variables or config files:

```bash
# Set log level
export ANONYMA_LOG_LEVEL=DEBUG

# Set device (cpu or cuda)
export ANONYMA_DEVICE=cuda

# Disable Flair
export ANONYMA_USE_FLAIR=false
```

Or edit `config/config.yaml` or `config/config.dev.yaml`.

### Configuration Files

- `config/config.yaml` - Base configuration
- `config/config.dev.yaml` - Development overrides
- `config/config.prod.yaml` - Production overrides

Load specific environment:

```python
from anonyma_core.config import load_config

config = load_config(environment="dev")
```

## Project Structure

```
packages/
├── anonyma_core/           # Core library
│   ├── __init__.py
│   ├── engine.py           # Main engine
│   ├── config.py           # Configuration system
│   ├── logging_config.py   # Logging setup
│   ├── detectors/          # PII detectors
│   └── modes/              # Anonymization modes
├── tests/                  # Test suite
│   ├── unit/               # Unit tests
│   ├── integration/        # Integration tests (TODO)
│   └── conftest.py         # Pytest fixtures
├── examples/               # Example scripts
├── config/                 # Configuration files
├── pyproject.toml          # Project configuration
├── pytest.ini              # Pytest configuration
├── Makefile                # Development commands
└── requirements.txt        # Dependencies
```

## Testing Guidelines

### Writing Tests

1. **Use fixtures** from `tests/conftest.py`
2. **Organize by feature** - one test file per module
3. **Use descriptive names** - `test_<what>_<condition>_<expected>`
4. **Test edge cases** - empty inputs, Unicode, very long texts
5. **Aim for >80% coverage**

Example test:

```python
def test_redact_mode_with_pii(engine_basic, sample_text_italian):
    """Test redaction of text with PII"""
    result = engine_basic.anonymize(sample_text_italian, AnonymizationMode.REDACT)

    assert isinstance(result, AnonymizationResult)
    assert result.anonymized_text != sample_text_italian
    assert "@" not in result.anonymized_text
```

### Test Categories

- **Unit tests** - Test individual functions/classes
- **Integration tests** - Test component interactions (TODO)
- **End-to-end tests** - Test full workflows (TODO)

## Code Style

### Formatting

- **Line length**: 100 characters
- **Formatter**: Black
- **Import sorting**: isort (black-compatible)

### Linting

- **Linter**: Ruff (fast Python linter)
- **Rules**: pycodestyle, pyflakes, flake8-bugbear, pyupgrade

### Type Hints

- Use type hints for public APIs
- Use `typing` module for complex types
- Run `mypy` to check types

Example:

```python
from typing import List, Dict, Any

def detect(self, text: str, language: str = 'it') -> List[Dict[str, Any]]:
    """Detect PII in text"""
    ...
```

## Common Tasks

### Adding a New Detector

1. Create file in `anonyma_core/detectors/`
2. Inherit from `BaseDetector` (or follow existing pattern)
3. Implement `detect()` method
4. Write tests in `tests/unit/test_detectors.py`
5. Add to engine initialization if needed

### Adding a New Anonymization Mode

1. Create file in `anonyma_core/modes/`
2. Implement `anonymize()` method
3. Add to `AnonymizationMode` enum in `modes/__init__.py`
4. Update engine to handle new mode
5. Write tests in `tests/unit/test_modes.py`

### Adding Configuration Options

1. Update config models in `anonyma_core/config.py`
2. Add to `config/config.yaml`
3. Add environment variable override if needed
4. Write tests in `tests/unit/test_config.py`
5. Update documentation

## Troubleshooting

### Tests Failing

```bash
# Run with verbose output
pytest -vv

# Run with debugger on failure
pytest --pdb

# Show print statements
pytest -s
```

### Import Errors

```bash
# Reinstall in development mode
pip install -e .

# Or add to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Flair Models Not Loading

```bash
# Download models manually
python scripts/download_models.py

# Or disable Flair for testing
export ANONYMA_USE_FLAIR=false
```

## Performance Tips

### Running Tests Faster

```bash
# Run tests in parallel
pytest -n auto

# Skip slow tests
pytest -m "not slow"

# Run only failed tests
pytest --lf
```

### Development Mode

For faster iteration, disable Flair:

```python
# In tests or development
engine = AnonymaEngine(use_flair=False)
```

## CI/CD (TODO)

Once GitHub Actions is set up, every push will:

1. Run linters
2. Run type checking
3. Run tests
4. Generate coverage report
5. Build documentation

## Documentation (TODO)

- API documentation with Sphinx/MkDocs
- User guide
- Architecture documentation

## Contributing

1. Create a feature branch
2. Make your changes
3. Run `make pre-commit` to ensure quality
4. Write/update tests
5. Update documentation if needed
6. Submit pull request

## Resources

- [pytest documentation](https://docs.pytest.org/)
- [Black formatter](https://black.readthedocs.io/)
- [Ruff linter](https://docs.astral.sh/ruff/)
- [mypy type checking](https://mypy.readthedocs.io/)
- [pre-commit hooks](https://pre-commit.com/)
