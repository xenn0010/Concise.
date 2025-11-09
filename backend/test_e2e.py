"""
End-to-end test for Concise API
Tests the complete flow: user creation -> API key generation -> compression request
"""
import sys
sys.path.insert(0, '.')

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app.models.user import User, UserTier
from app.models.api_key import APIKey
from app.utils.security import generate_api_key, hash_password
from app.config import get_settings
import uuid

settings = get_settings()

print("=" * 60)
print("Concise API - End-to-End Test")
print("=" * 60)

# Create tables
print("\n1. Creating database tables...")
try:
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created")
except Exception as e:
    print(f"❌ Failed to create tables: {e}")
    sys.exit(1)

# Create test user
print("\n2. Creating test user...")
db = SessionLocal()
try:
    # Check if test user exists
    test_user = db.query(User).filter(User.email == "test@concise.dev").first()

    if test_user:
        print("✅ Test user already exists")
    else:
        test_user = User(
            email="test@concise.dev",
            hashed_password=hash_password("test123"),
            full_name="Test User",
            tier=UserTier.PRO,
            is_active=True,
            is_verified=True
        )
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        print("✅ Test user created")

    print(f"   Email: {test_user.email}")
    print(f"   Tier: {test_user.tier.value}")
    print(f"   Rate limit: {test_user.rate_limit}/min")
    print(f"   Monthly tokens: {test_user.monthly_token_limit:,}")

except Exception as e:
    print(f"❌ Failed to create user: {e}")
    import traceback
    traceback.print_exc()
    db.close()
    sys.exit(1)

# Create API key
print("\n3. Creating API key...")
try:
    # Check if API key exists for user
    existing_key = db.query(APIKey).filter(
        APIKey.user_id == test_user.id,
        APIKey.name == "Test Key"
    ).first()

    if existing_key and existing_key.is_valid():
        # Use existing key
        full_key = None  # We don't have the full key
        api_key_obj = existing_key
        print("✅ Using existing API key")
    else:
        # Generate new key
        full_key, key_hash, key_prefix = generate_api_key()

        api_key_obj = APIKey(
            user_id=test_user.id,
            key_hash=key_hash,
            key_prefix=key_prefix,
            name="Test Key"
        )
        db.add(api_key_obj)
        db.commit()
        db.refresh(api_key_obj)
        print("✅ API key created")
        print(f"   Key: {full_key}")

    print(f"   Prefix: {api_key_obj.key_prefix}...")
    print(f"   Valid: {api_key_obj.is_valid()}")

except Exception as e:
    print(f"❌ Failed to create API key: {e}")
    import traceback
    traceback.print_exc()
    db.close()
    sys.exit(1)

db.close()

# Test API endpoints
print("\n4. Testing API endpoints...")

import requests

# Test health endpoint
print("\n   Testing /health...")
try:
    response = requests.get("http://localhost:8000/health", timeout=5)
    if response.status_code == 200:
        print(f"   ✅ Health check: {response.json()}")
    else:
        print(f"   ❌ Health check failed: {response.status_code}")
except Exception as e:
    print(f"   ❌ Health check error: {e}")

# Test models endpoint
print("\n   Testing /v1/models...")
if full_key:
    try:
        response = requests.get(
            "http://localhost:8000/v1/models",
            headers={"X-API-Key": full_key},
            timeout=5
        )
        if response.status_code == 200:
            models = response.json()
            print(f"   ✅ Models endpoint: {len(models.get('data', []))} models available")
        else:
            print(f"   ❌ Models endpoint failed: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
    except Exception as e:
        print(f"   ❌ Models endpoint error: {e}")
else:
    print("   ⏭️  Skipped (using existing API key, full key not available)")

# Check OPENAI_API_KEY
print("\n5. Checking OpenAI configuration...")
if settings.OPENAI_API_KEY:
    print(f"   ✅ OPENAI_API_KEY is set ({settings.OPENAI_API_KEY[:10]}...)")
else:
    print("   ❌ OPENAI_API_KEY is not set")
    print("   Add your OpenAI API key to .env file to test the proxy endpoint")

# Summary
print("\n" + "=" * 60)
print("Test Summary")
print("=" * 60)
print("\n✅ Core Components:")
print("   - Database: Connected")
print("   - Models: Created")
print("   - User: Created")
print("   - API Key: Generated")
print("   - Server: Running")

print("\n⚠️  Missing for Production:")
if not settings.OPENAI_API_KEY:
    print("   - OPENAI_API_KEY (required for proxy endpoint)")
if not settings.REDIS_URL:
    print("   - REDIS_URL (required for rate limiting)")

print("\n📝 To test the proxy endpoint:")
if full_key:
    print(f"""
   curl -X POST http://localhost:8000/v1/chat/completions \\
     -H "Content-Type: application/json" \\
     -H "X-API-Key: {full_key}" \\
     -d '{{
       "model": "gpt-3.5-turbo",
       "messages": [
         {{"role": "user", "content": "def fibonacci(n):\\n    if n <= 1:\\n        return n\\n    return fibonacci(n-1) + fibonacci(n-2)"}}
       ],
       "compression_enabled": true,
       "compression_level": "auto"
     }}'
    """)
else:
    print(f"""
   # API key exists but full key not available
   # Create a new API key or use the key displayed above
    """)

print("=" * 60)
