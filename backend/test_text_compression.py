"""
Test text compression effectiveness for AI agent use cases
"""
import requests
import json

API_KEY = "csk_live_x3xPv7y5L3FbUBM_1gebMM8vlibydeXSsmvYPez56ak"
BASE_URL = "http://localhost:8000"

def test_compression(text, name):
    """Test compression and print results"""
    print(f"\n{'='*70}")
    print(f"TEST: {name}")
    print(f"{'='*70}")
    print(f"Original text preview: {text[:200]}...")

    response = requests.post(
        f"{BASE_URL}/v1/compress",
        headers={
            "Content-Type": "application/json",
            "X-API-Key": API_KEY
        },
        json={
            "text": text,
            "level": "auto"
        }
    )

    if response.status_code == 200:
        result = response.json()
        print(f"\n✅ Compression Results:")
        print(f"   Original tokens:    {result['original_tokens']}")
        print(f"   Compressed tokens:  {result['compressed_tokens']}")
        print(f"   Tokens saved:       {result['tokens_saved']}")
        print(f"   Compression ratio:  {result['compression_ratio']*100:.1f}%")
        print(f"   Strategy:           {result['strategy']}")
        print(f"   Processing time:    {result['compression_time_ms']:.2f}ms")

        # Calculate cost savings
        gpt4_cost_per_1k = 0.01
        tokens_saved = result['tokens_saved']
        cost_saved = (tokens_saved / 1000) * gpt4_cost_per_1k
        print(f"\n💰 Cost Savings (GPT-4):")
        print(f"   Per request:        ${cost_saved:.6f}")
        print(f"   Per 1K requests:    ${cost_saved * 1000:.2f}")
        print(f"   Per 100K requests:  ${cost_saved * 100000:.2f}")

        print(f"\n📄 Compressed preview: {result['compressed_text'][:200]}...")
    else:
        print(f"❌ Error: {response.status_code}")
        print(f"   {response.text}")

# Test 1: Short system prompt (50-100 tokens)
short_system_prompt = """You are a helpful AI assistant. Answer questions clearly and concisely. Provide examples when helpful."""

# Test 2: Medium system prompt (200-300 tokens)
medium_system_prompt = """You are a helpful AI assistant specialized in software development. Your primary goal is to help developers write better code, debug issues, and understand complex systems. When answering questions, you should always provide clear explanations with relevant examples. Make sure to consider edge cases and potential security vulnerabilities in your recommendations. If you are uncertain about something, it is better to admit that you do not know rather than providing incorrect information. You have access to a wide range of programming languages including Python, JavaScript, TypeScript, Java, C++, Go, Rust, and many others."""

# Test 3: Large RAG context (500+ tokens)
large_rag_context = """
# API Documentation for Payment Processing Service

## Overview
The Payment Processing Service is a RESTful API that allows you to process credit card payments, manage subscriptions, handle refunds, and track transaction history. This service is PCI DSS compliant and supports multiple payment methods including credit cards, debit cards, and digital wallets.

## Authentication
All API requests must be authenticated using an API key. Include your API key in the Authorization header of each request. API keys can be obtained from the developer dashboard at https://dashboard.example.com. Keep your API keys secure and never share them publicly. If you believe your API key has been compromised, revoke it immediately and generate a new one.

## Rate Limiting
The API enforces rate limits to ensure fair usage and system stability. The default rate limit is 100 requests per minute for standard accounts and 1000 requests per minute for premium accounts. If you exceed the rate limit, you will receive a 429 Too Many Requests response. The response headers will include information about your current rate limit status.

## Payment Processing
To process a payment, send a POST request to /v1/payments with the following parameters:
- amount: The payment amount in cents (required)
- currency: Three-letter currency code (required, default: USD)
- payment_method: Payment method details including card number, expiration date, and CVV (required)
- customer_id: The unique identifier for the customer (optional but recommended)
- description: A description of the payment (optional)
- metadata: Additional metadata as key-value pairs (optional)

The API will return a payment object with a unique payment ID, status, and other relevant information. Payment processing typically completes within 2-3 seconds. If the payment fails, the response will include an error code and message explaining the reason for failure.

## Error Handling
The API uses standard HTTP status codes to indicate success or failure. Common error codes include:
- 400 Bad Request: The request was invalid or missing required parameters
- 401 Unauthorized: Authentication failed or API key is invalid
- 403 Forbidden: The API key does not have permission to perform this action
- 404 Not Found: The requested resource does not exist
- 429 Too Many Requests: Rate limit exceeded
- 500 Internal Server Error: An unexpected error occurred on the server

All error responses include a JSON body with an error code, message, and additional details to help you troubleshoot the issue.
"""

# Test 4: Conversation history (300+ tokens)
conversation_history = """
User: I'm having trouble connecting to my database. I keep getting a "Connection refused" error.