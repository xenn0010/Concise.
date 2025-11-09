"""
Create a real test API key for the demo to use actual compression
"""
import sys
sys.path.insert(0, '/home/yab/Concise/backend')

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.user import User, UserTier
from app.models.api_key import APIKey
from app.utils.security import generate_api_key, hash_password
import time

print("=" * 70)
print("Setting up REAL API Key for Demo")
print("=" * 70)
print()

db = SessionLocal()

# Check if demo user exists
demo_email = "demo@concise.dev"
user = db.query(User).filter(User.email == demo_email).first()

if not user:
    print("Creating demo user...")
    user = User(
        email=demo_email,
        hashed_password=hash_password("demo-password-12345"),
        full_name="Demo User",
        tier=UserTier.PRO,  # Give PRO tier for unlimited tokens
        is_active=True,
        is_verified=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    print(f"✅ Demo user created: {user.email}")
else:
    print(f"✅ Demo user already exists: {user.email}")

# Delete old demo API keys
old_keys = db.query(APIKey).filter(
    APIKey.user_id == user.id,
    APIKey.name == "Demo API Key"
).all()

for old_key in old_keys:
    db.delete(old_key)
db.commit()

# Create new API key
print("\nGenerating new API key...")
full_key, key_hash, key_prefix = generate_api_key()

api_key = APIKey(
    user_id=user.id,
    key_hash=key_hash,
    key_prefix=key_prefix,
    name="Demo API Key"
)
db.add(api_key)
db.commit()
db.refresh(api_key)

print()
print("=" * 70)
print(" SUCCESS! Demo API Key Created")
print("=" * 70)
print()
print(f"API Key: {full_key}")
print()
print("Now update your .env file:")
print()
print(f"CONCISE_API_KEY={full_key}")
print()

# Update .env file automatically
env_path = "/home/yab/Concise/demo/.env"
try:
    with open(env_path, 'r') as f:
        lines = f.readlines()

    # Update or add CONCISE_API_KEY
    updated = False
    for i, line in enumerate(lines):
        if line.startswith('CONCISE_API_KEY='):
            lines[i] = f'CONCISE_API_KEY={full_key}\n'
            updated = True
            break

    if not updated:
        lines.append(f'CONCISE_API_KEY={full_key}\n')

    with open(env_path, 'w') as f:
        f.writelines(lines)

    print(f"✅ .env file updated automatically!")
    print()
except Exception as e:
    print(f"⚠️  Could not update .env file automatically: {e}")
    print("   Please update manually")
    print()

print("Now you can run the demo with REAL compression:")
print()
print("  cd /home/yab/Concise/demo")
print("  ./start_demo.sh")
print()
print("All compression and TALE optimization will use the REAL LLMLingua engine!")
print()

db.close()
