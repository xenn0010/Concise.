# Concise SDK - API Documentation

Complete API reference for the Concise SDK LLM cost reduction platform.

## Table of Contents

- [Authentication](#authentication)
- [Compression Endpoints](#compression-endpoints)
- [TALE Optimization](#tale-optimization)
- [Usage & Analytics](#usage--analytics)
- [Health & Monitoring](#health--monitoring)
- [Error Codes](#error-codes)
- [Rate Limits](#rate-limits)
- [Examples](#examples)

---

## Authentication

All API requests require authentication using an API key in the `Authorization` header.

### Header Format

```
Authorization: Bearer YOUR_API_KEY
```

### Demo API Key

For testing, a demo key is generated on startup. Check the server logs for:

```
🔑 Demo API Key: csk_live_...
```

---

## Compression Endpoints

### POST /v1/compress

Compress text directly to reduce token count.

**Request Body:**

```json
{
  "text": "Your text to compress here",
  "level": "auto"
}
```

**Parameters:**

- `text` (required): Text to compress
- `level` (optional): Compression level
  - `auto`: Automatic selection (default)
  - `aggressive`: Maximum compression (2-4x)
  - `balanced`: Balance quality/compression (1.5-2x)
  - `conservative`: Minimal compression (1.3-1.5x)

**Response:**

```json
{
  "original_text": "...",
  "compressed_text": "...",
  "original_tokens": 500,
  "compressed_tokens": 250,
  "tokens_saved": 250,
  "compression_ratio": 2.0,
  "strategy": "balanced",
  "compression_time_ms": 15.5
}
```

**Example:**

```bash
curl -X POST http://localhost:8000/v1/compress \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer csk_live_..." \
  -d '{
    "text": "Please write a Python function that implements a binary search algorithm with proper error handling and edge case validation",
    "level": "balanced"
  }'
```

**Response:**

```json
{
  "original_text": "Please write a Python function that implements a binary search algorithm with proper error handling and edge case validation",
  "compressed_text": "Write Python binary search function w/ error handling & edge cases",
  "original_tokens": 24,
  "compressed_tokens": 13,
  "tokens_saved": 11,
  "compression_ratio": 1.85,
  "strategy": "balanced",
  "compression_time_ms": 12.3
}
```

---

## TALE Optimization

TALE (Token-Budget-Aware LLM Reasoning) reduces output tokens by 60-70% while maintaining accuracy.

### POST /v1/tale/optimize

Optimize a prompt to guide LLM toward concise output.

**Request Body:**

```json
{
  "prompt": "Explain how merge sort works",
  "strategy": "fixed",
  "target_budget": null
}
```

**Parameters:**

- `prompt` (required): The prompt to optimize
- `strategy` (optional): Budget estimation strategy
  - `fixed`: Fast heuristic-based (default)
  - `zero_shot`: LLM-based estimation (requires OPENAI_API_KEY)
  - `adaptive`: User history-based
- `target_budget` (optional): Manual token budget (10-2000)

**Response:**

```json
{
  "optimized_prompt": "Let's think step by step and use less than 150 tokens:\n\nExplain how merge sort works\n\nRemember: Be concise, stay within 150 tokens.",
  "original_prompt": "Explain how merge sort works",
  "estimated_budget": 150,
  "budget_metadata": {
    "strategy": "fixed",
    "confidence": 0.7,
    "prompt_length": 28
  },
  "prompt_additions": {
    "prefix": "Let's think step by step and use less than 150 tokens:\n\n",
    "suffix": "\n\nRemember: Be concise, stay within 150 tokens."
  }
}
```

**Example:**

```bash
curl -X POST http://localhost:8000/v1/tale/optimize \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer csk_live_..." \
  -d '{
    "prompt": "Explain how merge sort works",
    "strategy": "fixed"
  }'
```

### POST /v1/tale/validate

Validate that LLM output stayed within budget.

**Request Body:**

```json
{
  "output": "Merge sort is a divide-and-conquer algorithm...",
  "budget": 150,
  "tolerance": 0.2
}
```

**Parameters:**

- `output` (required): LLM's output text
- `budget` (required): Token budget (10+)
- `tolerance` (optional): Budget tolerance (0.0-1.0, default: 0.2)
  - 0.2 = allow 20% over budget

**Response:**

```json
{
  "within_budget": true,
  "actual_tokens": 142,
  "budget_tokens": 150,
  "max_allowed_tokens": 180,
  "budget_utilization": 0.947,
  "tokens_saved": 8,
  "exceeded_by": 0
}
```

**Example:**

```bash
curl -X POST http://localhost:8000/v1/tale/validate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer csk_live_..." \
  -d '{
    "output": "Merge sort divides array in half recursively, sorts each half, then merges sorted halves. Time: O(n log n), Space: O(n). Stable, predictable performance.",
    "budget": 150,
    "tolerance": 0.2
  }'
```

### GET /v1/tale/info

Get information about TALE optimization framework.

**Response:**

```json
{
  "name": "TALE (Token-Budget-Aware LLM Reasoning)",
  "version": "1.0.0",
  "description": "Reduce output tokens by 60-70% while maintaining accuracy",
  "research_paper": "https://arxiv.org/abs/2412.18547",
  "conference": "ACL 2025 (Findings)",
  "expected_results": {
    "token_reduction": "60-70%",
    "accuracy_retention": "95%+",
    "cost_savings": "59% (on output tokens)"
  },
  "strategies": { ... },
  "compatible_models": [ ... ]
}
```

---

## Usage & Analytics

### GET /v1/usage/stats

Get usage statistics and savings.

**Query Parameters:**

- `start_date` (optional): Start date (ISO 8601)
- `end_date` (optional): End date (ISO 8601)

**Response:**

```json
{
  "total_requests": 1500,
  "total_tokens_saved": 125000,
  "total_compression_time_ms": 45000,
  "average_compression_ratio": 1.85,
  "cost_savings_usd": 3.75,
  "strategies_used": {
    "aggressive": 300,
    "balanced": 900,
    "conservative": 300
  }
}
```

---

## Health & Monitoring

### GET /health

Health check endpoint.

**Response:**

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "environment": "production"
}
```

### GET /

Root endpoint with API information.

**Response:**

```json
{
  "name": "Concise API",
  "version": "1.0.0",
  "docs": "/docs",
  "health": "/health"
}
```

### GET /docs

Interactive Swagger UI documentation.

### GET /redoc

Alternative ReDoc documentation.

---

## Error Codes

| Status Code | Meaning |
|-------------|---------|
| 200 | Success |
| 400 | Bad Request - Invalid parameters |
| 401 | Unauthorized - Invalid or missing API key |
| 404 | Not Found - Endpoint doesn't exist |
| 429 | Too Many Requests - Rate limit exceeded |
| 500 | Internal Server Error - Server error |

**Error Response Format:**

```json
{
  "error": "Error type",
  "detail": "Detailed error message"
}
```

**Example Error:**

```json
{
  "error": "Rate limit exceeded",
  "detail": "Max 100 requests per minute. Try again in 30 seconds."
}
```

---

## Rate Limits

**Default Limits:**

- Free Tier: 60 requests/minute
- Starter: 300 requests/minute
- Pro: 1000 requests/minute
- Enterprise: Custom limits

**Rate Limit Headers:**

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640000000
```

---

## Examples

### Full Pipeline Example

Complete workflow using both compression and TALE:

```python
import requests

API_KEY = "csk_live_..."
BASE_URL = "http://localhost:8000"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Step 1: Compress input prompt
compress_response = requests.post(
    f"{BASE_URL}/v1/compress",
    headers=headers,
    json={
        "text": "Please write a detailed Python function that implements a binary search algorithm with comprehensive error handling and edge case validation",
        "level": "balanced"
    }
)
compressed_prompt = compress_response.json()["compressed_text"]
print(f"Input compression: {compress_response.json()['compression_ratio']}x")

# Step 2: Optimize for output with TALE
tale_response = requests.post(
    f"{BASE_URL}/v1/tale/optimize",
    headers=headers,
    json={
        "prompt": compressed_prompt,
        "strategy": "fixed"
    }
)
optimized_prompt = tale_response.json()["optimized_prompt"]
budget = tale_response.json()["estimated_budget"]
print(f"Output budget: {budget} tokens")

# Step 3: Send to your LLM (e.g., OpenAI)
# llm_response = openai.ChatCompletion.create(
#     model="gpt-4",
#     messages=[{"role": "user", "content": optimized_prompt}]
# )
# output = llm_response.choices[0].message.content

# Step 4: Validate output
# validate_response = requests.post(
#     f"{BASE_URL}/v1/tale/validate",
#     headers=headers,
#     json={
#         "output": output,
#         "budget": budget,
#         "tolerance": 0.2
#     }
# )
# print(f"Within budget: {validate_response.json()['within_budget']}")
```

### cURL Examples

**Compress text:**

```bash
curl -X POST http://localhost:8000/v1/compress \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer csk_live_..." \
  -d '{"text": "Your long text here", "level": "balanced"}'
```

**Optimize with TALE:**

```bash
curl -X POST http://localhost:8000/v1/tale/optimize \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer csk_live_..." \
  -d '{"prompt": "Explain recursion", "strategy": "fixed"}'
```

**Check health:**

```bash
curl http://localhost:8000/health
```

### JavaScript/TypeScript Example

```typescript
const API_KEY = 'csk_live_...';
const BASE_URL = 'http://localhost:8000';

async function compressText(text: string, level: string = 'balanced') {
  const response = await fetch(`${BASE_URL}/v1/compress`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${API_KEY}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ text, level }),
  });

  return await response.json();
}

async function optimizePrompt(prompt: string, strategy: string = 'fixed') {
  const response = await fetch(`${BASE_URL}/v1/tale/optimize`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${API_KEY}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ prompt, strategy }),
  });

  return await response.json();
}

// Usage
const result = await compressText('Long prompt here');
console.log(`Saved ${result.tokens_saved} tokens`);
```

---

## Best Practices

1. **Input Compression**: Use `balanced` level for most cases
2. **Output Optimization**: Use TALE `fixed` strategy for speed, `zero_shot` for accuracy
3. **Error Handling**: Always handle 429 (rate limit) and 500 (server error) responses
4. **Caching**: Cache compression results for identical inputs
5. **Monitoring**: Track `tokens_saved` to measure ROI

---

## Support

- **Documentation**: https://docs.concise-sdk.com
- **GitHub**: https://github.com/yourusername/Concise
- **Issues**: https://github.com/yourusername/Concise/issues
- **Email**: support@concise-sdk.com

---

## License

MIT License - See LICENSE file for details
