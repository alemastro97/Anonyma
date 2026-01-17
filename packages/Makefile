# Makefile for Anonyma Core
# Provides convenient commands for development tasks

.PHONY: help install test lint format type-check clean run-tests coverage

# Default target
help:
	@echo "Anonyma Core - Available Commands:"
	@echo ""
	@echo "  make install       - Install dependencies"
	@echo "  make install-dev   - Install dev dependencies"
	@echo "  make test          - Run tests"
	@echo "  make test-verbose  - Run tests with verbose output"
	@echo "  make coverage      - Run tests with coverage report"
	@echo "  make lint          - Run linters (ruff)"
	@echo "  make format        - Format code (black + isort)"
	@echo "  make format-check  - Check code formatting without changes"
	@echo "  make type-check    - Run type checking (mypy)"
	@echo "  make quality       - Run all quality checks (lint + type-check + format-check)"
	@echo "  make clean         - Clean temporary files"
	@echo "  make clean-all     - Clean everything including venv"
	@echo ""

# Installation
install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements.txt
	pip install -e ".[dev]"

# Testing
test:
	pytest

test-verbose:
	pytest -vv

coverage:
	pytest --cov=anonyma_core --cov-report=html --cov-report=term
	@echo "\nCoverage report generated in htmlcov/index.html"

# Linting
lint:
	ruff check anonyma_core tests

lint-fix:
	ruff check --fix anonyma_core tests

# Formatting
format:
	black anonyma_core tests examples
	isort anonyma_core tests examples

format-check:
	black --check anonyma_core tests examples
	isort --check-only anonyma_core tests examples

# Type checking
type-check:
	mypy anonyma_core

# Combined quality checks
quality: lint format-check type-check
	@echo "\n✅ All quality checks passed!"

# Run all checks before commit
pre-commit: format quality test
	@echo "\n✅ All pre-commit checks passed! Ready to commit."

# Cleaning
clean:
	rm -rf __pycache__
	rm -rf **/__pycache__
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf .ruff_cache
	rm -rf htmlcov
	rm -rf .coverage
	rm -rf *.egg-info
	rm -rf dist
	rm -rf build
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete

clean-all: clean
	rm -rf venv
	rm -rf .venv

# Quick test
quick-test:
	cd examples && python simple_test.py

# Full example test
example-test:
	cd examples && python quick_test.py
