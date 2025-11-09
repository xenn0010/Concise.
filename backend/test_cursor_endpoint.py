#!/usr/bin/env python3
"""
Test the OpenAI-compatible endpoint that Cursor will use.
"""
import requests
import json

API_KEY = "csk_live_fHE48ooBG-4UMlg59HI73fOk157nhL_lmYne-Y-9uJ0"
BASE_URL = "http://localhost:8000"

# Sample request similar to what Cursor sends
request_data = {
    "model": "gpt-4",
    "messages": [
        {
            "role": "system",
            "content": "You are a helpful coding assistant."
        },
        {
            "role": "user",
            "content": """I need to write a Python function that calculates the factorial of a number.
            The function should handle edge cases like negative numbers and zero.
            It should also be efficient for large numbers.
            Can you help me write this function with proper error handling?"""
        }
    ],
    "stream": False
}

print("🧪 Testing OpenAI Proxy Endpoint")
print("=" * 60)
print(f"Endpoint: {BASE_URL}/v1/chat/completions")
print(f"API Key: {API_KEY[:20]}...")
print()

try:
    print("📤 Sending request...")
    print(f"   Original prompt: {len(request_data['messages'][1]['content'])} chars")

    response = requests.post(
        f"{BASE_URL}/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        },
        json=request_data,
        timeout=30
    )

    print(f"   Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print()
        print("✅ SUCCESS!")
        print()
        print("📊 Compression Stats:")

        # Check if we have compression metadata
        if 'usage' in data:
            usage = data['usage']
            print(f"   Prompt tokens: {usage.get('prompt_tokens', 'N/A')}")
            print(f"   Completion tokens: {usage.get('completion_tokens', 'N/A')}")
            print(f"   Total tokens: {usage.get('total_tokens', 'N/A')}")

        # Check compression info if available
        if 'x_concise_compression' in data:
            comp = data['x_concise_compression']
            print()
            print(f"🗜️  Compression Details:")
            print(f"   Original tokens: {comp.get('original_tokens', 'N/A')}")
            print(f"   Compressed tokens: {comp.get('compressed_tokens', 'N/A')}")
            print(f"   Tokens saved: {comp.get('tokens_saved', 'N/A')}")
            print(f"   Compression ratio: {comp.get('compression_ratio', 'N/A'):.2f}x")
            print(f"   Cost saved: ${comp.get('cost_saved', 0):.4f}")

        print()
        print("💬 Response Preview:")
        if 'choices' in data and len(data['choices']) > 0:
            content = data['choices'][0]['message']['content']
            print(f"   {content[:200]}...")
        else:
            print("   (No content in response)")

    else:
        print()
        print("❌ ERROR!")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:500]}")

except requests.exceptions.Timeout:
    print()
    print("⏱️  Request timed out (>30s)")
    print("   This might be normal for first request (model loading)")
    print("   Try running again - subsequent requests should be faster")

except Exception as e:
    print()
    print(f"❌ Unexpected error: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 60)
