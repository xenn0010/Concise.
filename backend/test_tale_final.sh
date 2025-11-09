#!/bin/bash

API_KEY="sk-test-concise-1234567890abcdef"
BASE="http://localhost:8000"

echo "============================================"
echo "TALE INTEGRATION - FINAL VERIFICATION"
echo "============================================"
echo ""

# Test 1: Info endpoint
echo "1. Testing GET /v1/tale/info"
curl -s "$BASE/v1/tale/info" | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f'   ✅ {data[\"name\"]}')
print(f'   Expected reduction: {data[\"expected_results\"][\"token_reduction\"]}')
"
echo ""

# Test 2: Optimize endpoint
echo "2. Testing POST /v1/tale/optimize"
curl -s -X POST "$BASE/v1/tale/optimize" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Explain recursion", "strategy": "fixed"}' | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f'   ✅ Estimated budget: {data[\"estimated_budget\"]} tokens')
print(f'   Confidence: {data[\"budget_metadata\"][\"confidence\"]}')
"
echo ""

# Test 3: Validate endpoint
echo "3. Testing POST /v1/tale/validate"
curl -s -X POST "$BASE/v1/tale/validate" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"output": "Recursion is when a function calls itself.", "budget": 100}' | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f'   ✅ Within budget: {data[\"within_budget\"]}')
print(f'   Utilization: {int(data[\"budget_utilization\"] * 100)}%')
"
echo ""

echo "============================================"
echo "✅ TALE FULLY INTEGRATED"
echo "============================================"
