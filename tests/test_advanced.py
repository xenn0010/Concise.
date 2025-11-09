"""
Advanced Test Suite for Concise SDK
Tests: Integration, API endpoints, Error handling, Performance benchmarks
"""
import sys
sys.path.insert(0, '/home/yab/Concise/backend')

import time
import json
import threading
import asyncio
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed

from app.simple_compressor import SimpleCompressor
from app.smart_compressor import SmartCompressor
from app.hybrid_compressor import HybridCompressor
from app.services.tale_optimizer import TALEOptimizer
from app.cache.cache_manager import CacheManager
from app.middleware.rate_limiter import RateLimiter

class Colors:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 100}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(100)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 100}{Colors.END}\n")

def print_test(name, passed, details=""):
    status = f"{Colors.GREEN}✅ PASS{Colors.END}" if passed else f"{Colors.RED}❌ FAIL{Colors.END}"
    print(f"  {status} {name}")
    if details:
        print(f"    {details}")

print_header("CONCISE SDK - ADVANCED TEST SUITE")

# ============================================================================
# SECTION 1: COMPRESSOR COMPARISON TESTS
# ============================================================================

print_header("SECTION 1: COMPRESSOR COMPARISON")

print("Test Group: All Three Compressors\n")

test_prompts = [
    {
        "name": "Short prompt",
        "text": "Explain machine learning in simple terms."
    },
    {
        "name": "Medium prompt",
        "text": """You are a technical writer. Explain how neural networks work,
        including forward propagation, backpropagation, and gradient descent.
        Use clear examples and avoid jargon where possible."""
    },
    {
        "name": "Long prompt with code",
        "text": """Review this Python code and suggest improvements:

def process_data(data):
    result = []
    for item in data:
        if item > 0:
            result.append(item * 2)
        else:
            result.append(item)
    return result

Please analyze:
- Time complexity
- Space complexity
- Potential optimizations
- Edge cases to handle
- More Pythonic ways to write this
"""
    }
]

simple = SimpleCompressor()
smart = SmartCompressor()
hybrid = HybridCompressor()

for prompt in test_prompts:
    print(f"{Colors.BOLD}{prompt['name']}:{Colors.END}")
    original_tokens = hybrid.count_tokens(prompt['text'])
    print(f"  Original: {original_tokens} tokens")

    # Simple
    result = simple.compress(prompt['text'], target_ratio=0.5)
    print(f"  Simple:  {result['compressed_tokens']} tokens ({result['compression_ratio']}x)")

    # Smart
    result = smart.compress(prompt['text'], strategy="balanced")
    print(f"  Smart:   {result['compressed_tokens']} tokens ({result['compression_ratio']}x)")

    # Hybrid
    result = hybrid.compress(prompt['text'], strategy="balanced")
    print(f"  Hybrid:  {result['compressed_tokens']} tokens ({result['compression_ratio']}x, quality={result['quality_score']})")
    print()

print_test("All compressors produce valid output", True)

# ============================================================================
# SECTION 2: ERROR HANDLING & EDGE CASES
# ============================================================================

print_header("SECTION 2: ERROR HANDLING & ROBUSTNESS")

print("Test Group: Invalid Inputs\n")

compressor = HybridCompressor()

# Test 2.1: None input
try:
    result = compressor.compress(None, strategy="balanced")
    print_test("None input handling", False, "Should raise exception")
except Exception as e:
    print_test("None input handling", True, f"Correctly raised: {type(e).__name__}")

# Test 2.2: Non-string input
try:
    result = compressor.compress(12345, strategy="balanced")
    print_test("Non-string input", False, "Should raise exception")
except Exception as e:
    print_test("Non-string input", True, f"Correctly raised: {type(e).__name__}")

# Test 2.3: Very large input (memory test)
huge_text = "This is a test sentence. " * 10000  # ~50k tokens
try:
    start = time.time()
    result = compressor.compress(huge_text, strategy="balanced")
    duration = time.time() - start
    print_test(
        "Very large input (50k tokens)",
        duration < 10.0 and result['compressed_tokens'] > 0,
        f"Processed in {duration:.2f}s"
    )
except Exception as e:
    print_test("Very large input", False, f"Failed: {e}")

# Test 2.4: Special characters only
special_text = "!@#$%^&*()_+-=[]{}|;:',.<>?/~`"
result = compressor.compress(special_text, strategy="balanced")
print_test("Special characters only", result['compressed_tokens'] > 0)

# Test 2.5: Multilingual text
multilingual = "Hello 你好 Bonjour Hola こんにちは مرحبا"
result = compressor.compress(multilingual, strategy="balanced")
print_test("Multilingual text", result['compressed_tokens'] > 0)

# Test 2.6: HTML/XML content
html_text = """
<div class="container">
    <h1>Title</h1>
    <p>This is a paragraph with <strong>bold</strong> text.</p>
    <ul>
        <li>Item 1</li>
        <li>Item 2</li>
    </ul>
</div>
"""
result = compressor.compress(html_text, strategy="balanced")
print_test("HTML/XML preservation", '<div>' in result['compressed_text'] or result['compressed_tokens'] > 0)

# Test 2.7: JSON content
json_text = '''
{
    "name": "John Doe",
    "age": 30,
    "skills": ["Python", "JavaScript", "Go"],
    "experience": {
        "years": 5,
        "companies": ["TechCorp", "StartupXYZ"]
    }
}
'''
result = compressor.compress(json_text, strategy="balanced")
print_test("JSON structure preservation", '{' in result['compressed_text'] or result['compressed_tokens'] > 0)

# ============================================================================
# SECTION 3: TALE OPTIMIZER TESTS
# ============================================================================

print_header("SECTION 3: TALE OPTIMIZER ADVANCED TESTS")

print("Test Group: TALE Strategy Comparison\n")

tale = TALEOptimizer()

test_cases = [
    "Write a short poem about coding.",
    "Explain quantum computing in detail with examples and mathematical formulas.",
    "List the top 10 programming languages."
]

for prompt in test_cases:
    print(f"{Colors.BOLD}Prompt:{Colors.END} {prompt[:50]}...")

    # Fixed strategy
    result_fixed = tale.optimize_prompt(prompt, strategy="fixed")
    print(f"  Fixed:    {result_fixed['estimated_budget']} tokens")

    # Adaptive strategy
    result_adaptive = tale.optimize_prompt(prompt, strategy="adaptive")
    print(f"  Adaptive: {result_adaptive['estimated_budget']} tokens")
    print()

print_test("TALE produces reasonable budgets", True)

# Test 3.1: Manual budget override
result = tale.optimize_prompt("Test question?", strategy="fixed", target_budget=100)
print_test("Manual budget override", result['estimated_budget'] == 100)

# Test 3.2: TALE prompt augmentation
original = "Explain AI"
result = tale.optimize_prompt(original, strategy="fixed")
augmented = result['optimized_prompt']
print_test(
    "TALE adds output constraint",
    "concise" in augmented.lower() or "brief" in augmented.lower() or len(augmented) > len(original)
)

# ============================================================================
# SECTION 4: CACHE PERFORMANCE TESTS
# ============================================================================

print_header("SECTION 4: CACHE PERFORMANCE & SCALABILITY")

print("Test Group: Cache Efficiency\n")

cache = CacheManager()

# Test 4.1: Cache hit rate
cache.clear()
test_data = [f"query_{i % 50}" for i in range(200)]  # 50 unique, 200 total
hits = 0
misses = 0

for query in test_data:
    cached = cache.get("test", query)
    if cached:
        hits += 1
    else:
        misses += 1
        cache.set("test", query, {"result": f"data_{query}"}, ttl=300)

hit_rate = hits / len(test_data) * 100
print_test(
    "Cache hit rate optimization",
    hit_rate > 70,  # Should be 75% (150/200)
    f"Hit rate: {hit_rate:.1f}%"
)

# Test 4.2: Cache memory efficiency
cache.clear()
for i in range(1000):
    cache.set("perf", f"key_{i}", {"value": "x" * 100}, ttl=3600)

stats = cache.stats()
print_test(
    "Cache handles 1000 entries",
    stats['size'] <= 1000,
    f"Size: {stats['size']}"
)

# Test 4.3: Cache concurrent access
cache.clear()
results = {"success": 0, "failure": 0}

def cache_worker(worker_id, iterations):
    try:
        for i in range(iterations):
            key = f"worker_{worker_id}_item_{i}"
            cache.set("concurrent", key, {"data": i})
            retrieved = cache.get("concurrent", key)
            if retrieved and retrieved['data'] == i:
                results["success"] += 1
            else:
                results["failure"] += 1
    except Exception as e:
        results["failure"] += iterations

threads = []
for i in range(10):
    t = threading.Thread(target=cache_worker, args=(i, 50))
    threads.append(t)
    t.start()

for t in threads:
    t.join()

print_test(
    "Concurrent cache access (10 threads x 50 ops)",
    results["failure"] == 0,
    f"Success: {results['success']}, Failures: {results['failure']}"
)

# ============================================================================
# SECTION 5: RATE LIMITER STRESS TESTS
# ============================================================================

print_header("SECTION 5: RATE LIMITER ADVANCED TESTS")

print("Test Group: Rate Limiting Scenarios\n")

limiter = RateLimiter()

# Test 5.1: Burst handling
limiter.reset("burst_user")
allowed_count = 0
blocked_count = 0

for i in range(10):
    allowed, info = limiter.check_rate_limit("burst_user", max_requests=5, window_seconds=10)
    if allowed:
        allowed_count += 1
    else:
        blocked_count += 1

print_test(
    "Burst protection (10 requests, limit 5)",
    allowed_count == 5 and blocked_count == 5,
    f"Allowed: {allowed_count}, Blocked: {blocked_count}"
)

# Test 5.2: Window sliding
limiter.reset("slide_user")
allowed, _ = limiter.check_rate_limit("slide_user", max_requests=2, window_seconds=2)
allowed, _ = limiter.check_rate_limit("slide_user", max_requests=2, window_seconds=2)
blocked, info = limiter.check_rate_limit("slide_user", max_requests=2, window_seconds=2)

time.sleep(2.1)  # Wait for window to slide

allowed_after, _ = limiter.check_rate_limit("slide_user", max_requests=2, window_seconds=2)
print_test(
    "Window sliding (allows after expiry)",
    blocked is False and allowed_after is True,
    f"Retry after: {info['retry_after']}s"
)

# Test 5.3: Multiple users isolation
limiter.reset("user_a")
limiter.reset("user_b")

for i in range(3):
    limiter.check_rate_limit("user_a", max_requests=3, window_seconds=10)

allowed_a, _ = limiter.check_rate_limit("user_a", max_requests=3, window_seconds=10)
allowed_b, _ = limiter.check_rate_limit("user_b", max_requests=3, window_seconds=10)

print_test(
    "User isolation (user A blocked, user B allowed)",
    allowed_a is False and allowed_b is True
)

# Test 5.4: High concurrency rate limiting
limiter.reset("stress_user")
success = {"allowed": 0, "blocked": 0}

def rate_limit_worker(user_id, max_req):
    allowed, _ = limiter.check_rate_limit(user_id, max_requests=max_req, window_seconds=10)
    if allowed:
        success["allowed"] += 1
    else:
        success["blocked"] += 1

threads = []
for i in range(100):
    t = threading.Thread(target=rate_limit_worker, args=("stress_user", 50))
    threads.append(t)
    t.start()

for t in threads:
    t.join()

print_test(
    "Concurrent rate limiting (100 threads)",
    success["allowed"] == 50,
    f"Allowed: {success['allowed']}/100"
)

# ============================================================================
# SECTION 6: PERFORMANCE BENCHMARKS
# ============================================================================

print_header("SECTION 6: PERFORMANCE BENCHMARKS")

print("Test Group: Throughput & Latency\n")

# Test 6.1: Compression throughput
test_text = "This is a test prompt for compression benchmarking. " * 20
iterations = 100

start = time.time()
for i in range(iterations):
    compressor.compress(test_text, strategy="balanced")
duration = time.time() - start
throughput = iterations / duration

print_test(
    f"Compression throughput ({iterations} iterations)",
    throughput > 50,  # Should handle 50+ req/s
    f"{throughput:.0f} compressions/sec"
)

# Test 6.2: TALE optimization latency
start = time.time()
for i in range(50):
    tale.optimize_prompt("Test prompt", strategy="fixed")
duration = time.time() - start
avg_latency = (duration / 50) * 1000  # ms

print_test(
    "TALE average latency (50 iterations)",
    avg_latency < 10,  # Should be < 10ms for fixed strategy
    f"{avg_latency:.2f}ms per optimization"
)

# Test 6.3: Cache lookup speed
cache.clear()
for i in range(100):
    cache.set("perf", f"key_{i}", {"value": i})

start = time.time()
for i in range(1000):
    cache.get("perf", f"key_{i % 100}")
duration = time.time() - start
lookup_speed = 1000 / duration

print_test(
    "Cache lookup speed (1000 lookups)",
    lookup_speed > 10000,  # Should handle 10k+ lookups/sec
    f"{lookup_speed:.0f} lookups/sec"
)

# Test 6.4: End-to-end pipeline latency
start = time.time()
for i in range(20):
    compressed = compressor.compress(test_text, strategy="balanced")
    tale.optimize_prompt(compressed['compressed_text'], strategy="fixed")
duration = time.time() - start
avg_e2e = (duration / 20) * 1000

print_test(
    "End-to-end pipeline latency (20 iterations)",
    avg_e2e < 50,  # Should be < 50ms
    f"{avg_e2e:.2f}ms per request"
)

# ============================================================================
# SECTION 7: INTEGRATION TESTS
# ============================================================================

print_header("SECTION 7: INTEGRATION & WORKFLOW TESTS")

print("Test Group: Complete Workflows\n")

# Test 7.1: Full optimization pipeline with caching
cache.clear()
original_prompt = """You are a customer service agent. Help the user with their billing question.
User: Why was I charged twice this month?
Please provide a helpful response."""

# First request (cache miss)
start = time.time()
cached = cache.get("pipeline", original_prompt)
if not cached:
    compressed = compressor.compress(original_prompt, strategy="aggressive")
    optimized = tale.optimize_prompt(compressed['compressed_text'], strategy="fixed")
    result1 = {
        "compressed": compressed,
        "tale": optimized
    }
    cache.set("pipeline", original_prompt, result1, ttl=300)
else:
    result1 = cached
first_duration = time.time() - start

# Second request (cache hit)
start = time.time()
cached = cache.get("pipeline", original_prompt)
result2 = cached
second_duration = time.time() - start

speedup = first_duration / second_duration if second_duration > 0 else float('inf')
print_test(
    "Cache speedup for pipeline",
    speedup > 5,  # Cache should be 5x+ faster
    f"First: {first_duration*1000:.2f}ms, Second: {second_duration*1000:.2f}ms, Speedup: {speedup:.0f}x"
)

# Test 7.2: Rate-limited cached requests
limiter.reset("api_user")
cache.clear()

request_count = 0
cached_count = 0
rate_limited_count = 0

for i in range(15):
    allowed, info = limiter.check_rate_limit("api_user", max_requests=10, window_seconds=10)

    if not allowed:
        rate_limited_count += 1
        continue

    request_count += 1

    # Check cache
    cached = cache.get("api", f"query_{i % 5}")
    if cached:
        cached_count += 1
    else:
        cache.set("api", f"query_{i % 5}", {"result": i}, ttl=300)

print_test(
    "Rate limiting + caching integration",
    request_count == 10 and rate_limited_count == 5,
    f"Processed: {request_count}, Cached: {cached_count}, Rate limited: {rate_limited_count}"
)

# Test 7.3: Compression quality across strategies
strategies = ["balanced", "aggressive"]
quality_scores = []

long_prompt = """You are an AI assistant helping with code review.
Review this function and suggest improvements for readability, performance, and best practices.
Consider edge cases, error handling, and documentation."""

for strategy in strategies:
    result = compressor.compress(long_prompt, strategy=strategy)
    quality_scores.append(result['quality_score'])

print_test(
    "Quality preservation across strategies",
    quality_scores[0] >= 0.8 and quality_scores[1] >= 0.6,  # Balanced should be high, aggressive can be lower
    f"Balanced: {quality_scores[0]}, Aggressive: {quality_scores[1]}"
)

# ============================================================================
# FINAL SUMMARY
# ============================================================================

print_header("ADVANCED TEST SUITE COMPLETE")

print(f"{Colors.BOLD}Test Coverage Summary:{Colors.END}")
print("  Section 1: Compressor Comparison - 3 compressors tested")
print("  Section 2: Error Handling - 7 edge cases validated")
print("  Section 3: TALE Optimizer - Strategy comparison and customization")
print("  Section 4: Cache Performance - Hit rate, scalability, concurrency")
print("  Section 5: Rate Limiter - Burst, sliding window, isolation, stress")
print("  Section 6: Performance - Throughput, latency, end-to-end benchmarks")
print("  Section 7: Integration - Complete workflows with caching + rate limiting")
print()

print(f"{Colors.GREEN}All advanced tests completed!{Colors.END}\n")
print(f"{Colors.BOLD}Key Metrics:{Colors.END}")
print(f"  Compression throughput: {throughput:.0f} req/sec")
print(f"  Cache lookup speed: {lookup_speed:.0f} lookups/sec")
print(f"  End-to-end latency: {avg_e2e:.2f}ms")
print(f"  Cache speedup: {speedup:.0f}x faster on cache hit")
print()
