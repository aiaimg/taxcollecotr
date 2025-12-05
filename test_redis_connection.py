#!/usr/bin/env python
"""
Test script to verify Redis connection and configuration
"""
import os

import django

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "taxcollector_project.settings")
django.setup()

from django.conf import settings
from django.core.cache import cache

import redis


def test_redis_connection():
    """Test Redis connection for cache and Celery"""
    print("=" * 60)
    print("Testing Redis Configuration")
    print("=" * 60)

    # Test 1: Check Redis URLs
    print("\n1. Redis Configuration URLs:")
    print(f"   Celery URL: {settings.REDIS_URL}")
    print(f"   Cache URL: {settings.REDIS_CACHE_URL}")
    print(f"   Session URL: {settings.REDIS_SESSION_URL}")

    # Test 2: Test Redis connection directly
    print("\n2. Testing direct Redis connection:")
    try:
        redis_client = redis.from_url(settings.REDIS_CACHE_URL)
        redis_client.ping()
        print("   ✓ Redis connection successful")
    except Exception as e:
        print(f"   ✗ Redis connection failed: {e}")
        return False

    # Test 3: Test Django cache
    print("\n3. Testing Django cache (Redis):")
    try:
        # Set a test value
        cache.set("test_key", "test_value", 60)
        # Get the test value
        value = cache.get("test_key")
        if value == "test_value":
            print("   ✓ Cache set/get successful")
            cache.delete("test_key")
        else:
            print(f"   ✗ Cache get returned wrong value: {value}")
            return False
    except Exception as e:
        print(f"   ✗ Cache test failed: {e}")
        return False

    # Test 4: Check session backend
    print("\n4. Session Configuration:")
    print(f"   Session Engine: {settings.SESSION_ENGINE}")
    print(f"   Session Cache Alias: {settings.SESSION_CACHE_ALIAS}")
    if "cache" in settings.SESSION_ENGINE:
        print("   ✓ Sessions are configured to use cache (Redis)")
    else:
        print("   ⚠ Sessions are not using cache backend")

    # Test 5: Check Celery configuration
    print("\n5. Celery Configuration:")
    print(f"   Celery Broker URL: {settings.CELERY_BROKER_URL}")
    print(f"   Celery Result Backend: {settings.CELERY_RESULT_BACKEND}")

    # Test 6: Test cache backend info
    print("\n6. Cache Backend Info:")
    cache_backend = settings.CACHES["default"]["BACKEND"]
    cache_location = settings.CACHES["default"]["LOCATION"]
    print(f"   Cache Backend: {cache_backend}")
    print(f"   Cache Location: {cache_location}")
    print(f"   Key Prefix: {settings.CACHES['default'].get('KEY_PREFIX', 'None')}")

    print("\n" + "=" * 60)
    print("All tests passed! Redis is properly configured.")
    print("=" * 60)
    return True


if __name__ == "__main__":
    success = test_redis_connection()
    exit(0 if success else 1)
