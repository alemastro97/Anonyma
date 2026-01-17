#!/usr/bin/env python3
"""
Generate API keys for Anonyma API.

Usage:
    python generate_api_key.py
    python generate_api_key.py --name "client-name" --rate-limit 1000
"""

import sys
import argparse
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from anonyma_api.auth import api_key_manager
from anonyma_api.config import settings


def main():
    parser = argparse.ArgumentParser(
        description="Generate API keys for Anonyma API"
    )
    parser.add_argument(
        "--name",
        type=str,
        default="default",
        help="Name/identifier for this API key"
    )
    parser.add_argument(
        "--rate-limit",
        type=int,
        default=None,
        help="Custom rate limit for this key (requests per window)"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all existing API keys"
    )

    args = parser.parse_args()

    print("=" * 70)
    print("Anonyma API - Key Management")
    print("=" * 70)
    print()

    if args.list:
        # List all keys
        keys = api_key_manager.list_keys()
        if not keys:
            print("No API keys found.")
        else:
            print(f"Total API keys: {len(keys)}")
            print()
            for key, info in keys.items():
                print(f"Key: {key}")
                print(f"  Name: {info.get('name', 'N/A')}")
                print(f"  Rate Limit: {info.get('rate_limit', 'default')} requests")
                print(f"  Created: {info.get('created_at', 'N/A')}")
                print()
    else:
        # Generate new key
        rate_limit = args.rate_limit or settings.rate_limit_requests

        print(f"Generating API key for: {args.name}")
        print(f"Rate limit: {rate_limit} requests per {settings.rate_limit_window}s")
        print()

        api_key = api_key_manager.generate_key(
            name=args.name,
            rate_limit=rate_limit
        )

        print("✓ API Key generated successfully!")
        print()
        print("=" * 70)
        print(f"API Key: {api_key}")
        print("=" * 70)
        print()
        print("Save this key securely! It cannot be retrieved later.")
        print()
        print("Usage example:")
        print(f'  curl -H "X-API-Key: {api_key}" http://localhost:8000/api/config')
        print()

        # Show configuration status
        print("Configuration Status:")
        print(f"  • Authentication: {'✓ Enabled' if settings.auth_enabled else '✗ Disabled'}")
        print(f"  • Rate Limiting: {'✓ Enabled' if settings.rate_limit_enabled else '✗ Disabled'}")
        print(f"  • Redis: {'✓ Enabled' if settings.redis_enabled else '✗ Disabled'}")
        print()

        if not settings.auth_enabled:
            print("⚠️  Warning: Authentication is disabled!")
            print("   Enable it by setting ANONYMA_AUTH_ENABLED=true")
            print()


if __name__ == "__main__":
    main()
