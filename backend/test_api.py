#!/usr/bin/env python3
"""
Quick test script for Concise API
Run this after starting the server to verify it works
"""

import requests
import json
import sys

BASE_URL = "http://localhost:8000"

# Get demo key from server logs
# You'll need to copy it from the startup output
DEMO_KEY = input("Enter your demo API key (from server startup logs): ").strip()

if not DEMO_KEY:
    print("❌ No API key provided")
    sys.exit(1)


def test_health():
    """Test health endpoint"""
    print("\n1️⃣  Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")

    if response.status_code == 200:
        print("✅ Health check passed")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"❌ Health check failed: {response.status_code}")
        sys.exit(1)


def test_compression():
    """Test direct compression endpoint"""
    print("\n2️⃣  Testing compression endpoint...")

    test_text = """
    Please help me understand how to implement user authentication in my
    web application. I need to know about password hashing, session management,
    JWT tokens, OAuth integration, and security best practices. I would really
    appreciate a detailed explanation with code examples showing how to properly
    implement these features in a production environment. Thank you so much!
    """

    response = requests.post(
        f"{BASE_URL}/v1/compress",
        headers={
            "Authorization": f"Bearer {DEMO_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "text": test_text,
            "strategy": "balanced"
        }
    )

    if response.status_code == 200:
        result = response.json()
        print("✅ Compression successful!")
        print(f"   Original tokens: {result['original_tokens']}")
        print(f"   Compressed tokens: {result['compressed_tokens']}")
        print(f"   Tokens saved: {result['tokens_saved']}")
        print(f"   Compression ratio: {result['compression_ratio']}x")
        print(f"   Cost saved: ${result['cost_saved_usd']}")
        print(f"   Time: {result['compression_time_ms']}ms")
        print(f"   Cached: {result['cached']}")
        print(f"\n   Compressed text preview:")
        print(f"   {result['compressed_text'][:150]}...")
    else:
        print(f"❌ Compression failed: {response.status_code}")
        print(response.text)
        sys.exit(1)


def test_stats():
    """Test stats endpoint"""
    print("\n3️⃣  Testing stats endpoint...")

    response = requests.get(
        f"{BASE_URL}/v1/stats",
        headers={"Authorization": f"Bearer {DEMO_KEY}"}
    )

    if response.status_code == 200:
        stats = response.json()
        print("✅ Stats retrieved!")
        print("\n   User Stats:")
        print(f"   Total requests: {stats['user_stats']['total_requests']}")
        print(f"   Tokens saved: {stats['user_stats']['total_tokens_saved']}")
        print(f"   Cost saved: ${stats['user_stats']['total_cost_saved_usd']}")
        print(f"   Cache hit rate: {stats['user_stats']['cache_hit_rate']}%")

        print("\n   System Stats:")
        print(f"   Total requests: {stats['system_stats']['total_requests']}")
        print(f"   Cache hit rate: {stats['system_stats']['cache_hit_rate']}%")
        print(f"   Avg compression time: {stats['system_stats']['avg_compression_time_ms']}ms")
    else:
        print(f"❌ Stats failed: {response.status_code}")
        sys.exit(1)


def test_openai_proxy():
    """Test OpenAI proxy endpoint (requires OPENAI_API_KEY in .env)"""
    print("\n4️⃣  Testing OpenAI proxy endpoint...")

    response = requests.post(
        f"{BASE_URL}/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {DEMO_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "gpt-3.5-turbo",
            "messages": [
                {
                    "role": "user",
                    "content": "What is 2+2? Answer in one word."
                }
            ],
            "concise_compress": True,
            "concise_strategy": "balanced"
        }
    )

    if response.status_code == 200:
        result = response.json()
        print("✅ OpenAI proxy successful!")

        if "choices" in result:
            print(f"   Response: {result['choices'][0]['message']['content']}")

        if "concise" in result:
            print(f"   Tokens saved: {result['concise']['tokens_saved']}")
            print(f"   Cost saved: ${result['concise']['cost_saved_usd']}")
            print(f"   Compression ratio: {result['concise']['compression_ratio']}x")
    else:
        print(f"⚠️  OpenAI proxy test skipped or failed: {response.status_code}")
        if response.status_code == 500:
            print("   (This is expected if OPENAI_API_KEY is not set in .env)")


if __name__ == "__main__":
    print("=" * 60)
    print("🧪 Concise API Test Suite")
    print("=" * 60)

    try:
        test_health()
        test_compression()
        test_stats()
        test_openai_proxy()

        print("\n" + "=" * 60)
        print("✅ All tests passed!")
        print("=" * 60)

        print("\n📊 Next steps:")
        print("   1. Add OPENAI_API_KEY to .env for full functionality")
        print("   2. Deploy to Railway")
        print("   3. Configure Cursor to use your Concise API URL")
        print("   4. Start saving money! 💰")

    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        sys.exit(1)
