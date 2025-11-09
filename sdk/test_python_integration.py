"""
Python SDK Integration Tests
Tests real API calls against running backend
"""

import sys
sys.path.insert(0, '/home/yab/Concise/backend')

from concise import Concise, OpenAI
from concise.exceptions import AuthenticationError, APIError

# Load API key
with open('/tmp/concise_test_key.txt') as f:
    API_KEY = f.read().strip()

BASE_URL = "http://localhost:8000/v1"

print("=" * 70)
print("PYTHON SDK INTEGRATION TESTS")
print("=" * 70)

# Test 1: Health check
print("\n1. Testing health check...")
try:
    client = Concise(api_key=API_KEY, base_url=BASE_URL)
    health = client.health()
    print(f"   ✅ Health check successful")
    print(f"   - Status: {health['status']}")
    print(f"   - Version: {health['version']}")
except Exception as e:
    print(f"   ❌ Health check failed: {e}")

# Test 2: Compression - Python code
print("\n2. Testing Python code compression...")
try:
    code = """def fibonacci(n):
    '''Calculate fibonacci number'''
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
"""

    result = client.compress(code, level="auto")
    print(f"   ✅ Compression successful")
    print(f"   - Original: {result.original_tokens} tokens")
    print(f"   - Compressed: {result.compressed_tokens} tokens")
    print(f"   - Saved: {result.tokens_saved} tokens ({((1-result.compression_ratio)*100):.1f}%)")
    print(f"   - Strategy: {result.strategy}")
    print(f"   - Time: {result.compression_time_ms:.0f}ms")
    if result.cache_hit:
        print(f"   - Cache: HIT (instant!)")
except Exception as e:
    print(f"   ❌ Compression failed: {e}")
    import traceback
    traceback.print_exc()

# Test 3: Compression - Natural language
print("\n3. Testing natural language compression...")
try:
    text = "FastAPI is a modern, fast web framework for building APIs with Python 3.8+"

    result = client.compress(text, level="aggressive")
    print(f"   ✅ Compression successful")
    print(f"   - Original: {result.original_tokens} tokens")
    print(f"   - Compressed: {result.compressed_tokens} tokens")
    print(f"   - Saved: {result.tokens_saved} tokens ({((1-result.compression_ratio)*100):.1f}%)")
    print(f"   - Strategy: {result.strategy}")
    print(f"   - Time: {result.compression_time_ms:.0f}ms")
    if result.cache_hit:
        print(f"   - Cache: HIT")
except Exception as e:
    print(f"   ❌ Compression failed: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Repeat compression (cache test)
print("\n4. Testing cache (repeat compression)...")
try:
    result = client.compress(text, level="aggressive")
    if result.cache_hit:
        print(f"   ✅ Cache working! Response time: {result.compression_time_ms:.1f}ms")
    else:
        print(f"   ⚠️  Cache miss (expected hit)")
except Exception as e:
    print(f"   ❌ Cache test failed: {e}")

# Test 5: Different compression levels
print("\n5. Testing different compression levels...")
try:
    test_text = "The quick brown fox jumps over the lazy dog. This is a test sentence."

    for level in ["conservative", "balanced", "aggressive"]:
        result = client.compress(test_text, level=level)
        print(f"   - {level:15s}: {result.compressed_tokens:3d} tokens ({result.compression_ratio:.2f}x)")
except Exception as e:
    print(f"   ❌ Level testing failed: {e}")

# Test 6: Context manager
print("\n6. Testing context manager...")
try:
    with Concise(api_key=API_KEY, base_url=BASE_URL) as client:
        result = client.compress("Test text", level="auto")
        print(f"   ✅ Context manager works: {result.compressed_tokens} tokens")
except Exception as e:
    print(f"   ❌ Context manager failed: {e}")

# Test 7: Invalid API key
print("\n7. Testing invalid API key handling...")
try:
    bad_client = Concise(api_key="invalid-key", base_url=BASE_URL)
    result = bad_client.compress("test")
    print(f"   ❌ Should have raised AuthenticationError")
except AuthenticationError as e:
    print(f"   ✅ AuthenticationError raised correctly: {e}")
except Exception as e:
    print(f"   ⚠️  Different error: {e}")

print("\n" + "=" * 70)
print("INTEGRATION TESTS COMPLETE")
print("=" * 70)
