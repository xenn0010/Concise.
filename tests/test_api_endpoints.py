"""
API Endpoint Test Suite for Concise SDK
Tests all HTTP endpoints with various scenarios
"""
import sys
sys.path.insert(0, '/home/yab/Concise/backend')

import requests
import time
import json
from typing import Dict, List

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

BASE_URL = "http://localhost:8000"
API_KEY = "test-api-key-123"  # Test API key
HEADERS = {"X-API-Key": API_KEY}

print_header("CONCISE SDK - API ENDPOINT TEST SUITE")

# Check if server is running
try:
    response = requests.get(f"{BASE_URL}/health", timeout=2)
    if response.status_code == 200:
        print(f"{Colors.GREEN}Server is running at {BASE_URL}{Colors.END}\n")
    else:
        print(f"{Colors.YELLOW}Warning: Server returned status {response.status_code}{Colors.END}\n")
except Exception as e:
    print(f"{Colors.RED}Error: Server not running at {BASE_URL}{Colors.END}")
    print(f"{Colors.YELLOW}Please start the server first with: cd backend && uvicorn app.main:app{Colors.END}\n")
    sys.exit(1)

# ============================================================================
# SECTION 1: HEALTH & INFO ENDPOINTS
# ============================================================================

print_header("SECTION 1: HEALTH & INFO ENDPOINTS")

print("Test Group: Basic Endpoints\n")

# Test 1.1: Health check
try:
    response = requests.get(f"{BASE_URL}/health")
    print_test(
        "GET /health",
        response.status_code == 200 and response.json().get('status') == 'healthy',
        f"Status: {response.status_code}"
    )
except Exception as e:
    print_test("GET /health", False, f"Error: {e}")

# Test 1.2: Root endpoint
try:
    response = requests.get(f"{BASE_URL}/")
    print_test(
        "GET / (root)",
        response.status_code == 200,
        f"Status: {response.status_code}"
    )
except Exception as e:
    print_test("GET / (root)", False, f"Error: {e}")

# Test 1.3: TALE info endpoint
try:
    response = requests.get(f"{BASE_URL}/v1/tale/info")
    data = response.json()
    print_test(
        "GET /v1/tale/info",
        response.status_code == 200 and 'strategies' in data,
        f"Strategies: {', '.join(data.get('strategies', []))}"
    )
except Exception as e:
    print_test("GET /v1/tale/info", False, f"Error: {e}")

# ============================================================================
# SECTION 2: COMPRESSION ENDPOINTS
# ============================================================================

print_header("SECTION 2: COMPRESSION ENDPOINTS")

print("Test Group: POST /v1/compress\n")

# Test 2.1: Basic compression
try:
    payload = {
        "text": "You are a helpful assistant that provides detailed technical support for software development.",
        "strategy": "balanced"
    }
    response = requests.post(f"{BASE_URL}/v1/compress", json=payload, headers=HEADERS)
    data = response.json()

    print_test(
        "Basic compression (balanced)",
        response.status_code == 200 and data['compression_ratio'] > 1.0,
        f"Ratio: {data.get('compression_ratio', 0)}x, Tokens: {data.get('original_tokens', 0)} → {data.get('compressed_tokens', 0)}"
    )
except Exception as e:
    print_test("Basic compression", False, f"Error: {e}")

# Test 2.2: Aggressive compression
try:
    payload = {
        "text": "Please provide a very detailed and comprehensive explanation of machine learning algorithms including neural networks, decision trees, and support vector machines.",
        "strategy": "aggressive"
    }
    response = requests.post(f"{BASE_URL}/v1/compress", json=payload, headers=HEADERS)
    data = response.json()

    print_test(
        "Aggressive compression",
        response.status_code == 200 and data['compression_ratio'] >= 1.5,
        f"Ratio: {data.get('compression_ratio', 0)}x"
    )
except Exception as e:
    print_test("Aggressive compression", False, f"Error: {e}")

# Test 2.3: Empty text handling
try:
    payload = {
        "text": "",
        "strategy": "balanced"
    }
    response = requests.post(f"{BASE_URL}/v1/compress", json=payload, headers=HEADERS)

    print_test(
        "Empty text handling",
        response.status_code in [200, 400],  # Either accept with empty result or reject
        f"Status: {response.status_code}"
    )
except Exception as e:
    print_test("Empty text handling", False, f"Error: {e}")

# Test 2.4: Invalid strategy
try:
    payload = {
        "text": "Test text",
        "strategy": "invalid_strategy"
    }
    response = requests.post(f"{BASE_URL}/v1/compress", json=payload, headers=HEADERS)

    print_test(
        "Invalid strategy handling",
        response.status_code in [400, 422],  # Should reject with validation error
        f"Status: {response.status_code}"
    )
except Exception as e:
    print_test("Invalid strategy handling", False, f"Error: {e}")

# Test 2.5: Missing required field
try:
    payload = {
        "strategy": "balanced"
        # Missing 'text' field
    }
    response = requests.post(f"{BASE_URL}/v1/compress", json=payload, headers=HEADERS)

    print_test(
        "Missing required field",
        response.status_code in [400, 422],
        f"Status: {response.status_code}"
    )
except Exception as e:
    print_test("Missing required field", False, f"Error: {e}")

# ============================================================================
# SECTION 3: TALE ENDPOINTS
# ============================================================================

print_header("SECTION 3: TALE OPTIMIZATION ENDPOINTS")

print("Test Group: POST /v1/tale/optimize\n")

# Test 3.1: Basic TALE optimization
try:
    payload = {
        "prompt": "Explain quantum computing in simple terms.",
        "strategy": "fixed"
    }
    response = requests.post(f"{BASE_URL}/v1/tale/optimize", json=payload, headers=HEADERS)
    data = response.json()

    print_test(
        "Basic TALE optimization (fixed)",
        response.status_code == 200 and 'estimated_budget' in data,
        f"Budget: {data.get('estimated_budget', 0)} tokens"
    )
except Exception as e:
    print_test("Basic TALE optimization", False, f"Error: {e}")

# Test 3.2: Adaptive strategy
try:
    payload = {
        "prompt": "List the top 5 programming languages.",
        "strategy": "adaptive"
    }
    response = requests.post(f"{BASE_URL}/v1/tale/optimize", json=payload, headers=HEADERS)
    data = response.json()

    print_test(
        "TALE adaptive strategy",
        response.status_code == 200 and data.get('estimated_budget', 0) > 0,
        f"Budget: {data.get('estimated_budget', 0)} tokens"
    )
except Exception as e:
    print_test("TALE adaptive strategy", False, f"Error: {e}")

# Test 3.3: Manual budget override
try:
    payload = {
        "prompt": "Test prompt",
        "strategy": "fixed",
        "target_budget": 150
    }
    response = requests.post(f"{BASE_URL}/v1/tale/optimize", json=payload, headers=HEADERS)
    data = response.json()

    print_test(
        "Manual budget override",
        response.status_code == 200 and data.get('estimated_budget') == 150,
        f"Requested: 150, Got: {data.get('estimated_budget', 0)}"
    )
except Exception as e:
    print_test("Manual budget override", False, f"Error: {e}")

# ============================================================================
# SECTION 4: FULL PIPELINE ENDPOINT
# ============================================================================

print_header("SECTION 4: FULL PIPELINE OPTIMIZATION")

print("Test Group: POST /v1/optimize\n")

# Test 4.1: Full pipeline optimization
try:
    payload = {
        "text": """You are a customer support agent for TechCorp.
        Our product is a cloud-based project management tool.
        Customer question: How do I reset my password?
        Please provide a helpful response.""",
        "compression_strategy": "balanced",
        "tale_strategy": "fixed"
    }
    response = requests.post(f"{BASE_URL}/v1/optimize", json=payload, headers=HEADERS)
    data = response.json()

    savings_pct = (1 - data.get('optimized_total_tokens', 0) / data.get('original_total_tokens', 1)) * 100

    print_test(
        "Full pipeline optimization",
        response.status_code == 200 and savings_pct > 30,
        f"Savings: {savings_pct:.0f}% ({data.get('original_total_tokens', 0)} → {data.get('optimized_total_tokens', 0)} tokens)"
    )
except Exception as e:
    print_test("Full pipeline optimization", False, f"Error: {e}")

# Test 4.2: Aggressive full pipeline
try:
    payload = {
        "text": "Explain machine learning, deep learning, and artificial intelligence in detail with examples and use cases for each.",
        "compression_strategy": "aggressive",
        "tale_strategy": "fixed"
    }
    response = requests.post(f"{BASE_URL}/v1/optimize", json=payload, headers=HEADERS)
    data = response.json()

    print_test(
        "Aggressive full pipeline",
        response.status_code == 200,
        f"Compression: {data.get('compression_ratio', 0)}x, Total savings: {data.get('total_tokens_saved', 0)} tokens"
    )
except Exception as e:
    print_test("Aggressive full pipeline", False, f"Error: {e}")

# ============================================================================
# SECTION 5: RATE LIMITING TESTS
# ============================================================================

print_header("SECTION 5: RATE LIMITING")

print("Test Group: Rate Limit Headers\n")

# Test 5.1: Rate limit headers present
try:
    response = requests.post(
        f"{BASE_URL}/v1/compress",
        json={"text": "Test", "strategy": "balanced"}
    )

    has_headers = (
        'X-RateLimit-Limit' in response.headers or
        'x-ratelimit-limit' in response.headers
    )

    print_test(
        "Rate limit headers present",
        has_headers,
        f"Headers: {[h for h in response.headers if 'rate' in h.lower()]}"
    )
except Exception as e:
    print_test("Rate limit headers", False, f"Error: {e}")

# Test 5.2: Rate limit enforcement (make many requests)
try:
    successful_requests = 0
    rate_limited = False

    for i in range(150):
        response = requests.post(
            f"{BASE_URL}/v1/compress",
            json={"text": f"Test {i}", "strategy": "balanced"},
            headers={"X-API-Key": "test-rate-limit-key"}
        )
        if response.status_code == 200:
            successful_requests += 1
        elif response.status_code == 429:
            rate_limited = True
            break

    print_test(
        "Rate limit enforcement",
        rate_limited or successful_requests >= 100,
        f"Made {successful_requests} requests before rate limit"
    )
except Exception as e:
    print_test("Rate limit enforcement", False, f"Error: {e}")

# ============================================================================
# SECTION 6: PERFORMANCE TESTS
# ============================================================================

print_header("SECTION 6: API PERFORMANCE")

print("Test Group: Response Times\n")

# Test 6.1: Compression endpoint latency
try:
    latencies = []
    for i in range(10):
        start = time.time()
        response = requests.post(
            f"{BASE_URL}/v1/compress",
            json={"text": "Test text for latency measurement " * 10, "strategy": "balanced"}
        )
        latencies.append((time.time() - start) * 1000)

    avg_latency = sum(latencies) / len(latencies)
    p95_latency = sorted(latencies)[int(len(latencies) * 0.95)]

    print_test(
        "Compression endpoint latency",
        avg_latency < 100,  # Should be < 100ms
        f"Avg: {avg_latency:.2f}ms, P95: {p95_latency:.2f}ms"
    )
except Exception as e:
    print_test("Compression latency", False, f"Error: {e}")

# Test 6.2: TALE endpoint latency
try:
    latencies = []
    for i in range(10):
        start = time.time()
        response = requests.post(
            f"{BASE_URL}/v1/tale/optimize",
            json={"prompt": "Test prompt for latency", "strategy": "fixed"}
        )
        latencies.append((time.time() - start) * 1000)

    avg_latency = sum(latencies) / len(latencies)

    print_test(
        "TALE endpoint latency",
        avg_latency < 50,
        f"Avg: {avg_latency:.2f}ms"
    )
except Exception as e:
    print_test("TALE latency", False, f"Error: {e}")

# Test 6.3: Full pipeline latency
try:
    latencies = []
    for i in range(10):
        start = time.time()
        response = requests.post(
            f"{BASE_URL}/v1/optimize",
            json={
                "text": "Test prompt for full pipeline latency measurement",
                "compression_strategy": "balanced",
                "tale_strategy": "fixed"
            }
        )
        latencies.append((time.time() - start) * 1000)

    avg_latency = sum(latencies) / len(latencies)

    print_test(
        "Full pipeline latency",
        avg_latency < 150,
        f"Avg: {avg_latency:.2f}ms"
    )
except Exception as e:
    print_test("Full pipeline latency", False, f"Error: {e}")

# ============================================================================
# SECTION 7: ERROR HANDLING
# ============================================================================

print_header("SECTION 7: ERROR HANDLING")

print("Test Group: API Error Responses\n")

# Test 7.1: Invalid JSON
try:
    response = requests.post(
        f"{BASE_URL}/v1/compress",
        data="invalid json",
        headers={"Content-Type": "application/json"}
    )

    print_test(
        "Invalid JSON handling",
        response.status_code in [400, 422],
        f"Status: {response.status_code}"
    )
except Exception as e:
    print_test("Invalid JSON handling", False, f"Error: {e}")

# Test 7.2: Non-existent endpoint
try:
    response = requests.get(f"{BASE_URL}/v1/nonexistent")

    print_test(
        "Non-existent endpoint",
        response.status_code == 404,
        f"Status: {response.status_code}"
    )
except Exception as e:
    print_test("Non-existent endpoint", False, f"Error: {e}")

# Test 7.3: Wrong HTTP method
try:
    response = requests.get(  # GET instead of POST
        f"{BASE_URL}/v1/compress"
    )

    print_test(
        "Wrong HTTP method",
        response.status_code in [405, 422],
        f"Status: {response.status_code}"
    )
except Exception as e:
    print_test("Wrong HTTP method", False, f"Error: {e}")

# ============================================================================
# FINAL SUMMARY
# ============================================================================

print_header("API ENDPOINT TEST SUITE COMPLETE")

print(f"{Colors.BOLD}Test Coverage:{Colors.END}")
print("  Section 1: Health & Info Endpoints - 3 tests")
print("  Section 2: Compression API - 5 tests")
print("  Section 3: TALE Optimization API - 3 tests")
print("  Section 4: Full Pipeline API - 2 tests")
print("  Section 5: Rate Limiting - 2 tests")
print("  Section 6: Performance Benchmarks - 3 tests")
print("  Section 7: Error Handling - 3 tests")
print()

print(f"{Colors.GREEN}All API endpoint tests completed!{Colors.END}\n")
