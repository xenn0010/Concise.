#!/usr/bin/env python3
"""
Test compression with 100 lines of actual code
"""
import requests
import json

API_KEY = "csk_live_1Gq6QI45LXuAHya_IDmdu1w9uebgE5COehJKSekQgE8"
BASE_URL = "http://localhost:8000"

# 100 lines of realistic Python code
code_sample = """
import os
import sys
import json
import logging
from typing import List, Dict, Optional, Union, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class UserProfile:
    \"\"\"Represents a user profile with authentication details\"\"\"
    user_id: str
    email: str
    username: str
    created_at: datetime
    last_login: Optional[datetime] = None
    is_active: bool = True
    roles: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        \"\"\"Convert user profile to dictionary\"\"\"
        return {
            'user_id': self.user_id,
            'email': self.email,
            'username': self.username,
            'created_at': self.created_at.isoformat(),
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'is_active': self.is_active,
            'roles': self.roles,
            'metadata': self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserProfile':
        \"\"\"Create user profile from dictionary\"\"\"
        return cls(
            user_id=data['user_id'],
            email=data['email'],
            username=data['username'],
            created_at=datetime.fromisoformat(data['created_at']),
            last_login=datetime.fromisoformat(data['last_login']) if data.get('last_login') else None,
            is_active=data.get('is_active', True),
            roles=data.get('roles', []),
            metadata=data.get('metadata', {})
        )

class AuthenticationManager:
    \"\"\"Manages user authentication and session handling\"\"\"

    def __init__(self, secret_key: str, session_timeout: int = 3600):
        self.secret_key = secret_key
        self.session_timeout = session_timeout
        self.active_sessions: Dict[str, UserProfile] = {}
        logger.info(f"AuthenticationManager initialized with timeout: {session_timeout}s")

    def create_session(self, user: UserProfile) -> str:
        \"\"\"Create a new session for the user\"\"\"
        import uuid
        session_id = str(uuid.uuid4())
        self.active_sessions[session_id] = user
        logger.info(f"Session created for user: {user.username}")
        return session_id

    def validate_session(self, session_id: str) -> Optional[UserProfile]:
        \"\"\"Validate a session and return user profile if valid\"\"\"
        user = self.active_sessions.get(session_id)
        if user is None:
            logger.warning(f"Invalid session attempt: {session_id}")
            return None

        # Check if session has expired
        if user.last_login:
            elapsed = datetime.now() - user.last_login
            if elapsed.total_seconds() > self.session_timeout:
                logger.warning(f"Session expired for user: {user.username}")
                del self.active_sessions[session_id]
                return None

        logger.debug(f"Session validated for user: {user.username}")
        return user

    def revoke_session(self, session_id: str) -> bool:
        \"\"\"Revoke a session\"\"\"
        if session_id in self.active_sessions:
            user = self.active_sessions[session_id]
            del self.active_sessions[session_id]
            logger.info(f"Session revoked for user: {user.username}")
            return True
        return False

    def cleanup_expired_sessions(self) -> int:
        \"\"\"Remove all expired sessions\"\"\"
        expired = []
        current_time = datetime.now()

        for session_id, user in self.active_sessions.items():
            if user.last_login:
                elapsed = current_time - user.last_login
                if elapsed.total_seconds() > self.session_timeout:
                    expired.append(session_id)

        for session_id in expired:
            del self.active_sessions[session_id]

        if expired:
            logger.info(f"Cleaned up {len(expired)} expired sessions")

        return len(expired)
"""

print("🧪 Testing Compression with 100 Lines of Code")
print("=" * 60)
print(f"Code sample: {len(code_sample)} characters")
print(f"Code lines: {len(code_sample.splitlines())} lines")
print()

# Test with different strategies
strategies = ["conservative", "balanced", "aggressive"]

for strategy in strategies:
    print(f"\n📊 Testing with '{strategy}' strategy:")
    print("-" * 60)

    try:
        response = requests.post(
            f"{BASE_URL}/v1/compress",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "text": code_sample,
                "strategy": strategy
            },
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()

            print(f"✅ SUCCESS")
            print(f"   Original tokens: {data['original_tokens']}")
            print(f"   Compressed tokens: {data['compressed_tokens']}")
            print(f"   Tokens saved: {data['tokens_saved']}")
            print(f"   Compression ratio: {data['compression_ratio']:.2f}x")
            print(f"   Cost saved: ${data['cost_saved_usd']:.4f}")
            print(f"   Compression time: {data['compression_time_ms']:.0f}ms")
            print(f"   Reduction: {(data['tokens_saved'] / data['original_tokens'] * 100):.1f}%")

            # Show a preview of compressed code
            compressed = data['compressed_text']
            print(f"\n   Compressed preview (first 200 chars):")
            print(f"   {compressed[:200]}...")

        else:
            print(f"❌ ERROR: {response.status_code}")
            print(f"   {response.text[:200]}")

    except Exception as e:
        print(f"❌ Exception: {e}")

print("\n" + "=" * 60)
print("Test complete!")
