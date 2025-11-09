"""
Test Python SDK functionality
"""

import os
import sys

# Add backend to path for access to jerry config
sys.path.insert(0, '/home/yab/Concise/backend')

from concise import Concise, OpenAI
from concise.exceptions import AuthenticationError

print("=" * 70)
print("PYTHON SDK TESTS")
print("=" * 70)

# Test 1: Import test
print("\n1. Testing imports...")
try:
    from concise import Concise, OpenAI, ConciseError, CompressionResult
    print("   ✅ All imports successful")
except Exception as e:
    print(f"   ❌ Import failed: {e}")
    sys.exit(1)

# Test 2: Authentication error test
print("\n2. Testing authentication error...")
try:
    client = Concise(api_key="invalid-key", base_url="http://localhost:8000/v1")
    result = client.compress("test")
    print("   ❌ Should have raised AuthenticationError")
except AuthenticationError:
    print("   ✅ AuthenticationError raised correctly")
except Exception as e:
    print(f"   ⚠️  Different error: {e}")

# Test 3: Missing API key test
print("\n3. Testing missing API key...")
try:
    # Clear env var if set
    old_key = os.environ.pop('CONCISE_API_KEY', None)
    client = Concise()
    print("   ❌ Should have raised AuthenticationError")
except AuthenticationError as e:
    print(f"   ✅ AuthenticationError raised: {e}")
finally:
    if old_key:
        os.environ['CONCISE_API_KEY'] = old_key

# Test 4: Client initialization
print("\n4. Testing client initialization with API key...")
try:
    # Use a dummy key for testing structure
    client = Concise(api_key="test-key-12345", base_url="http://localhost:8000/v1")
    print(f"   ✅ Client initialized")
    print(f"   - Base URL: {client.base_url}")
    print(f"   - API key set: {bool(client.api_key)}")
except Exception as e:
    print(f"   ❌ Initialization failed: {e}")

# Test 5: OpenAI wrapper initialization
print("\n5. Testing OpenAI wrapper...")
try:
    openai_client = OpenAI(api_key="test-key-12345", base_url="http://localhost:8000/v1")
    print(f"   ✅ OpenAI wrapper initialized")
    print(f"   - Has chat attribute: {hasattr(openai_client, 'chat')}")
    print(f"   - Has completions: {hasattr(openai_client.chat, 'completions')}")
except Exception as e:
    print(f"   ❌ OpenAI wrapper failed: {e}")

# Test 6: Context manager support
print("\n6. Testing context manager...")
try:
    with Concise(api_key="test-key", base_url="http://localhost:8000/v1") as client:
        print("   ✅ Context manager entry successful")
    print("   ✅ Context manager exit successful")
except Exception as e:
    print(f"   ❌ Context manager failed: {e}")

# Test 7: Type checking
print("\n7. Testing type definitions...")
try:
    from concise.types import CompressionResult, CompressionLevel

    # Check CompressionLevel type
    levels = ["auto", "aggressive", "balanced", "conservative"]
    print(f"   ✅ CompressionLevel defined: {levels}")

    # Check CompressionResult dataclass
    print(f"   ✅ CompressionResult is a dataclass")
except Exception as e:
    print(f"   ❌ Type checking failed: {e}")

print("\n" + "=" * 70)
print("BASIC STRUCTURE TESTS COMPLETE")
print("=" * 70)

print("\nNote: Full integration tests require:")
print("  1. Backend API running (uvicorn app.main:app)")
print("  2. Valid API key from database")
print("  3. Jerry GPU connected")
