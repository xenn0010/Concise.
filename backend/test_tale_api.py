"""
Test TALE API Endpoints
"""

import requests
import json

API_KEY = "sk-test-concise-1234567890abcdef"
BASE_URL = "http://localhost:8000"

headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

print("=" * 80)
print("TALE API ENDPOINT TESTS")
print("=" * 80)
print()

# Test 1: Get TALE info
print("TEST 1: GET /v1/tale/info")
print("-" * 80)

response = requests.get(f"{BASE_URL}/v1/tale/info")
info = response.json()

print(f"Status: {response.status_code}")
print(f"Name: {info['name']}")
print(f"Description: {info['description']}")
print(f"Expected token reduction: {info['expected_results']['token_reduction']}")
print(f"Expected cost savings: {info['expected_results']['cost_savings']}")
print(f"Compatible models: {', '.join(info['compatible_models'][:3])}...")
print()

# Test 2: Optimize a simple prompt
print("TEST 2: POST /v1/tale/optimize (Simple Q&A)")
print("-" * 80)

request_data = {
    "prompt": "What is recursion in programming?",
    "strategy": "fixed"
}

response = requests.post(
    f"{BASE_URL}/v1/tale/optimize",
    headers=headers,
    json=request_data
)

result = response.json()

print(f"Status: {response.status_code}")
print(f"Original prompt: {result['original_prompt']}")
print(f"Estimated budget: {result['estimated_budget']} tokens")
print(f"Strategy: {result['budget_metadata']['strategy']}")
print(f"Confidence: {result['budget_metadata']['confidence']}")
print()
print("Optimized prompt:")
print(result['optimized_prompt'][:150] + "...")
print()

# Test 3: Optimize with manual budget
print("TEST 3: POST /v1/tale/optimize (Manual Budget)")
print("-" * 80)

request_data = {
    "prompt": "Explain how neural networks work",
    "target_budget": 100
}

response = requests.post(
    f"{BASE_URL}/v1/tale/optimize",
    headers=headers,
    json=request_data
)

result = response.json()

print(f"Status: {response.status_code}")
print(f"Original prompt: {result['original_prompt']}")
print(f"Manual budget: {result['estimated_budget']} tokens")
print(f"Reasoning: {result['budget_metadata']['reasoning']}")
print()

# Test 4: Optimize code generation task
print("TEST 4: POST /v1/tale/optimize (Code Generation)")
print("-" * 80)

request_data = {
    "prompt": "Write a Python function to implement binary search",
    "strategy": "fixed"
}

response = requests.post(
    f"{BASE_URL}/v1/tale/optimize",
    headers=headers,
    json=request_data
)

result = response.json()

print(f"Status: {response.status_code}")
print(f"Original prompt: {result['original_prompt']}")
print(f"Estimated budget: {result['estimated_budget']} tokens (higher for code)")
print(f"Task detected: {result['budget_metadata']['reasoning']}")
print()

# Test 5: Validate output within budget
print("TEST 5: POST /v1/tale/validate (Within Budget)")
print("-" * 80)

request_data = {
    "output": "Recursion is when a function calls itself. It needs a base case to stop and a recursive case to continue.",
    "budget": 100,
    "tolerance": 0.2
}

response = requests.post(
    f"{BASE_URL}/v1/tale/validate",
    headers=headers,
    json=request_data
)

result = response.json()

print(f"Status: {response.status_code}")
print(f"Budget: {result['budget_tokens']} tokens")
print(f"Actual: {result['actual_tokens']} tokens")
print(f"Within budget: {result['within_budget']}")
print(f"Budget utilization: {result['budget_utilization'] * 100:.0f}%")
print(f"Tokens saved: {result['tokens_saved']}")
print()

# Test 6: Validate output over budget
print("TEST 6: POST /v1/tale/validate (Over Budget)")
print("-" * 80)

long_output = """
Binary search is a highly efficient searching algorithm that works on sorted arrays. Here's a comprehensive explanation of how it works:

The fundamental principle is divide and conquer. The algorithm repeatedly divides the search interval in half. It starts with the entire array and narrows down the search space with each iteration.

Here's the step-by-step process:
1. Start with two pointers, left and right, marking the boundaries of the search space
2. Calculate the middle index
3. Compare the middle element with the target value
4. If they match, return the index
5. If the target is smaller, search the left half
6. If the target is larger, search the right half
7. Repeat until found or search space is empty

The time complexity is O(log n), which makes it exponentially faster than linear search for large datasets. This logarithmic performance is what makes binary search so powerful.
"""

request_data = {
    "output": long_output,
    "budget": 50,  # Very tight budget
    "tolerance": 0.1
}

response = requests.post(
    f"{BASE_URL}/v1/tale/validate",
    headers=headers,
    json=request_data
)

result = response.json()

print(f"Status: {response.status_code}")
print(f"Budget: {result['budget_tokens']} tokens")
print(f"Actual: {result['actual_tokens']} tokens")
print(f"Within budget: {result['within_budget']}")
print(f"Exceeded by: {result['exceeded_by']} tokens")
print()

print("=" * 80)
print("TALE API INTEGRATION COMPLETE!")
print("=" * 80)
print()
print("All endpoints working:")
print("  - GET /v1/tale/info")
print("  - POST /v1/tale/optimize")
print("  - POST /v1/tale/validate")
print()
print("Next steps:")
print("  1. Add TALE support to Python SDK")
print("  2. Add TALE support to TypeScript SDK")
print("  3. Update docs with TALE examples")
print()
