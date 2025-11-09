"""
Comprehensive system tests for Concise API
Tests database, models, configuration, and basic endpoints
"""
import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.config import get_settings
from app.database import Base, GUID
from app.models.user import User, UserTier
from app.models.api_key import APIKey
from app.models.usage import UsageRecord, UsageSummary

def test_configuration():
    """Test configuration loading"""
    print("\n🧪 Testing Configuration...")
    settings = get_settings()

    assert settings.APP_NAME == "Concise API"
    assert settings.VERSION == "1.0.0"
    assert settings.DATABASE_URL is not None
    assert settings.SECRET_KEY is not None

    print(f"✅ Config loaded: {settings.APP_NAME} v{settings.VERSION}")
    print(f"   Environment: {settings.ENVIRONMENT}")
    print(f"   Database: {settings.DATABASE_URL[:50]}...")
    return True


def test_database_connection():
    """Test database connection"""
    print("\n🧪 Testing Database Connection...")
    settings = get_settings()

    try:
        engine = create_engine(settings.DATABASE_URL)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            assert result.fetchone()[0] == 1
        print("✅ Database connection successful")
        return True, engine
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("\n💡 To fix this:")
        print("   Option 1: Install PostgreSQL locally")
        print("     sudo apt-get install postgresql")
        print("     sudo systemctl start postgresql")
        print("     sudo -u postgres createdb concise_dev")
        print("\n   Option 2: Use Docker")
        print("     docker run -d --name concise-postgres \\")
        print("       -e POSTGRES_PASSWORD=postgres \\")
        print("       -e POSTGRES_DB=concise_dev \\")
        print("       -p 5432:5432 postgres:15-alpine")
        return False, None


def test_models_creation(engine):
    """Test creating model instances"""
    print("\n🧪 Testing Models...")

    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    try:
        # Create tables
        Base.metadata.create_all(bind=engine)
        print("✅ Tables created successfully")

        # Test User model
        user = User(
            email="test@example.com",
            hashed_password="test_hash",
            full_name="Test User",
            tier=UserTier.FREE
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        assert user.id is not None
        assert user.rate_limit == 60  # FREE tier
        assert user.monthly_token_limit == 100_000
        print(f"✅ User model works: {user.email}")
        print(f"   Tier: {user.tier.value}, Rate limit: {user.rate_limit}/min")

        # Test APIKey model
        from app.utils.security import generate_api_key
        full_key, key_hash, key_prefix = generate_api_key()

        api_key = APIKey(
            user_id=user.id,
            key_hash=key_hash,
            key_prefix=key_prefix,
            name="Test Key"
        )
        db.add(api_key)
        db.commit()
        db.refresh(api_key)

        assert api_key.id is not None
        assert api_key.is_valid()
        print(f"✅ APIKey model works: {api_key.key_prefix}...")

        # Test UsageRecord model
        usage = UsageRecord(
            user_id=user.id,
            api_key_id=api_key.id,
            original_tokens=1000,
            compressed_tokens=500,
            tokens_saved=500,
            compression_ratio=0.5,
            strategy="minify",
            compression_time_ms=100.0
        )
        db.add(usage)
        db.commit()
        db.refresh(usage)

        assert usage.id is not None
        assert usage.tokens_saved == 500
        print(f"✅ UsageRecord model works: {usage.tokens_saved} tokens saved")

        # Test UsageSummary model
        summary = UsageSummary(
            user_id=user.id,
            period_start=datetime.utcnow(),
            period_end=datetime.utcnow(),
            total_requests=1,
            total_tokens_saved=500,
            tokens_limit=user.monthly_token_limit
        )
        db.add(summary)
        db.commit()
        db.refresh(summary)

        assert summary.id is not None
        assert summary.utilization_percent < 1  # Less than 1%
        print(f"✅ UsageSummary model works: {summary.utilization_percent:.2f}% used")

        # Cleanup
        db.query(UsageSummary).delete()
        db.query(UsageRecord).delete()
        db.query(APIKey).delete()
        db.query(User).delete()
        db.commit()

        return True

    except Exception as e:
        print(f"❌ Model test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


def test_guid_type():
    """Test GUID type compatibility"""
    print("\n🧪 Testing GUID Type...")
    import uuid
    from app.database import GUID

    guid = GUID()
    test_uuid = uuid.uuid4()

    # Test string conversion
    result = guid.process_bind_param(test_uuid, None)
    assert isinstance(result, str)

    # Test UUID parsing
    parsed = guid.process_result_value(str(test_uuid), None)
    assert isinstance(parsed, uuid.UUID)
    assert parsed == test_uuid

    print("✅ GUID type works for both SQLite and PostgreSQL")
    return True


def test_security_utils():
    """Test security utilities"""
    print("\n🧪 Testing Security Utils...")
    from app.utils.security import (
        hash_password,
        verify_password,
        generate_api_key,
        hash_api_key,
        create_access_token,
        verify_token
    )

    # Test password hashing
    password = "test_password_123"
    hashed = hash_password(password)
    assert verify_password(password, hashed)
    assert not verify_password("wrong_password", hashed)
    print("✅ Password hashing works")

    # Test API key generation
    full_key, key_hash, key_prefix = generate_api_key()
    assert full_key.startswith("csk_live_")
    assert len(key_prefix) == 12
    assert len(key_hash) == 64  # SHA-256 hash

    # Verify hash
    rehashed = hash_api_key(full_key)
    assert rehashed == key_hash
    print(f"✅ API key generation works: {key_prefix}...")

    # Test JWT tokens
    token = create_access_token({"sub": "test_user_id"})
    payload = verify_token(token)
    assert payload is not None
    assert payload["sub"] == "test_user_id"
    print("✅ JWT tokens work")

    return True


def test_api_endpoints():
    """Test API endpoints"""
    print("\n🧪 Testing API Endpoints...")

    try:
        import requests

        # Test health endpoint
        response = requests.get("http://localhost:8000/health", timeout=2)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health endpoint works: {data['status']}")
            return True
        else:
            print(f"⚠️  Health endpoint returned {response.status_code}")
            return False

    except requests.exceptions.ConnectionError:
        print("⚠️  Server not running. Start it with:")
        print("   uvicorn app.main:app --reload")
        return False
    except Exception as e:
        print(f"⚠️  API test skipped: {e}")
        return False


def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("🚀 Concise API - System Test Suite")
    print("=" * 60)

    results = []

    # Test 1: Configuration
    results.append(("Configuration", test_configuration()))

    # Test 2: Database Connection
    db_connected, engine = test_database_connection()
    results.append(("Database Connection", db_connected))

    if db_connected and engine:
        # Test 3: Models
        results.append(("Database Models", test_models_creation(engine)))
    else:
        print("\n⏭️  Skipping model tests (no database connection)")
        results.append(("Database Models", None))

    # Test 4: GUID Type
    results.append(("GUID Type", test_guid_type()))

    # Test 5: Security Utils
    results.append(("Security Utils", test_security_utils()))

    # Test 6: API Endpoints
    results.append(("API Endpoints", test_api_endpoints()))

    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)

    passed = sum(1 for _, result in results if result is True)
    failed = sum(1 for _, result in results if result is False)
    skipped = sum(1 for _, result in results if result is None)

    for name, result in results:
        if result is True:
            status = "✅ PASS"
        elif result is False:
            status = "❌ FAIL"
        else:
            status = "⏭️  SKIP"
        print(f"{status} - {name}")

    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed, {skipped} skipped")
    print("=" * 60)

    if failed > 0:
        print("\n❌ Some tests failed. Please fix the issues above.")
        return False
    elif db_connected:
        print("\n✅ All tests passed! System is ready.")
        return True
    else:
        print("\n⚠️  Tests passed but database not connected.")
        print("   Install PostgreSQL to complete setup.")
        return True


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
