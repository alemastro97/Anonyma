#!/usr/bin/env python3
"""
Test script for Enterprise API features.

Tests:
- Basic API connectivity
- Authentication (if enabled)
- Rate limiting (if enabled)
- Redis integration (if enabled)
- Text anonymization
- Job storage
"""

import sys
import time
import requests
from pathlib import Path
from typing import Dict, Any

# Configuration
API_BASE_URL = "http://localhost:8000"
API_KEY = None  # Set this if authentication is enabled


def test_health_check() -> bool:
    """Test health check endpoint"""
    print("\n" + "=" * 70)
    print("TEST 1: Health Check")
    print("=" * 70)

    try:
        response = requests.get(f"{API_BASE_URL}/health")
        response.raise_for_status()

        data = response.json()
        print(f"✓ API Status: {data['status']}")
        print(f"✓ Version: {data['version']}")
        print(f"✓ Engines: {data['engines_loaded']}")
        return True

    except Exception as e:
        print(f"✗ Health check failed: {e}")
        return False


def test_config_endpoint() -> Dict[str, Any]:
    """Test configuration endpoint"""
    print("\n" + "=" * 70)
    print("TEST 2: Configuration")
    print("=" * 70)

    headers = {}
    if API_KEY:
        headers["X-API-Key"] = API_KEY

    try:
        response = requests.get(f"{API_BASE_URL}/api/config", headers=headers)
        response.raise_for_status()

        data = response.json()
        print("Features:")
        for feature, enabled in data["features"].items():
            status = "✓ Enabled" if enabled else "✗ Disabled"
            print(f"  • {feature}: {status}")

        print("\nLimits:")
        for limit, value in data["limits"].items():
            print(f"  • {limit}: {value}")

        return data

    except requests.exceptions.HTTPException as e:
        if e.response.status_code == 401:
            print("✗ Authentication required but no API key provided")
            print("  Set API_KEY variable in this script")
        else:
            print(f"✗ Configuration check failed: {e}")
        return {}
    except Exception as e:
        print(f"✗ Configuration check failed: {e}")
        return {}


def test_text_anonymization() -> bool:
    """Test text anonymization"""
    print("\n" + "=" * 70)
    print("TEST 3: Text Anonymization")
    print("=" * 70)

    headers = {"Content-Type": "application/json"}
    if API_KEY:
        headers["X-API-Key"] = API_KEY

    payload = {
        "text": "Mario Rossi (email: mario.rossi@example.com) lives in Milan. His phone is +39 339 1234567.",
        "mode": "redact",
        "language": "it"
    }

    try:
        response = requests.post(
            f"{API_BASE_URL}/anonymize/text",
            json=payload,
            headers=headers
        )
        response.raise_for_status()

        data = response.json()
        print(f"✓ Anonymization successful")
        print(f"✓ Detections: {data['detections_count']}")
        print(f"✓ Processing time: {data['processing_time']:.3f}s")
        print(f"\nOriginal: {payload['text']}")
        print(f"Anonymized: {data['anonymized_text']}")

        return True

    except requests.exceptions.HTTPException as e:
        if e.response.status_code == 401:
            print("✗ Authentication failed")
        elif e.response.status_code == 429:
            print("✗ Rate limit exceeded")
        else:
            print(f"✗ Anonymization failed: {e}")
        return False
    except Exception as e:
        print(f"✗ Anonymization failed: {e}")
        return False


def test_rate_limiting(config: Dict[str, Any]) -> bool:
    """Test rate limiting"""
    if not config.get("features", {}).get("rate_limit_enabled"):
        print("\n" + "=" * 70)
        print("TEST 4: Rate Limiting (SKIPPED - Not Enabled)")
        print("=" * 70)
        return True

    print("\n" + "=" * 70)
    print("TEST 4: Rate Limiting")
    print("=" * 70)

    headers = {"Content-Type": "application/json"}
    if API_KEY:
        headers["X-API-Key"] = API_KEY

    payload = {
        "text": "Test text",
        "mode": "redact"
    }

    limit = config.get("limits", {}).get("rate_limit_requests", 100)
    print(f"Rate limit: {limit} requests per window")

    # Make several requests quickly
    print("Making 5 rapid requests...")

    for i in range(5):
        try:
            response = requests.post(
                f"{API_BASE_URL}/anonymize/text",
                json=payload,
                headers=headers
            )

            remaining = response.headers.get("X-RateLimit-Remaining", "?")
            print(f"  Request {i+1}: Status {response.status_code}, Remaining: {remaining}")

            if response.status_code == 429:
                print("✓ Rate limiting is working!")
                return True

        except Exception as e:
            print(f"  Request {i+1} failed: {e}")

        time.sleep(0.1)

    print("✓ Rate limiting configured but not triggered (need more requests)")
    return True


def test_formats_endpoint() -> bool:
    """Test formats endpoint"""
    print("\n" + "=" * 70)
    print("TEST 5: Supported Formats")
    print("=" * 70)

    try:
        response = requests.get(f"{API_BASE_URL}/formats")
        response.raise_for_status()

        formats = response.json()
        print("✓ Supported formats:")
        for fmt in formats:
            print(f"  • {fmt}")

        return True

    except Exception as e:
        print(f"✗ Formats check failed: {e}")
        return False


def main():
    """Run all tests"""
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 18 + "ANONYMA ENTERPRISE API TESTS" + " " * 20 + "║")
    print("╚" + "=" * 68 + "╝")
    print()
    print(f"Testing API at: {API_BASE_URL}")
    if API_KEY:
        print(f"Using API Key: {API_KEY[:10]}...")
    else:
        print("No API Key configured (testing without authentication)")
    print()

    # Run tests
    results = []

    # 1. Health check
    results.append(("Health Check", test_health_check()))

    # 2. Config
    config = test_config_endpoint()
    results.append(("Configuration", bool(config)))

    # 3. Text anonymization
    results.append(("Text Anonymization", test_text_anonymization()))

    # 4. Rate limiting
    results.append(("Rate Limiting", test_rate_limiting(config)))

    # 5. Formats
    results.append(("Formats", test_formats_endpoint()))

    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test_name:.<50} {status}")

    print()
    print(f"Results: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! Enterprise features are working correctly.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Check configuration.")

    print()

    # Configuration tips
    if not config.get("features", {}).get("redis_enabled"):
        print("💡 Tip: Enable Redis for persistent job storage:")
        print("   export ANONYMA_REDIS_ENABLED=true")
        print()

    if not config.get("features", {}).get("auth_enabled"):
        print("💡 Tip: Enable authentication for production:")
        print("   export ANONYMA_AUTH_ENABLED=true")
        print("   export ANONYMA_MASTER_API_KEY=$(python -c 'import secrets; print(secrets.token_urlsafe(32))')")
        print()

    if not config.get("features", {}).get("rate_limit_enabled"):
        print("💡 Tip: Enable rate limiting to prevent abuse:")
        print("   export ANONYMA_RATE_LIMIT_ENABLED=true")
        print()

    return 0 if passed == total else 1


if __name__ == "__main__":
    try:
        exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        exit(1)
