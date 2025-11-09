"""
API Key authentication and management
"""

import secrets
from typing import Optional
from datetime import datetime, timedelta

from fastapi import HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel


class APIKey(BaseModel):
    """API Key model"""
    key: str
    user_id: str
    name: str
    created_at: datetime
    last_used: Optional[datetime] = None
    is_active: bool = True
    rate_limit: int = 60  # requests per minute
    tier: str = "free"  # free, starter, pro, team


class APIKeyManager:
    """
    Manage API keys with in-memory storage.

    Note: API keys are ephemeral and reset on application restart.
    For persistent storage, integrate with the PostgreSQL database models.
    """

    def __init__(self):
        self.keys: dict[str, APIKey] = {}

        # Create a demo key for testing
        demo_key = self.generate_key(
            user_id="demo",
            name="Demo Key",
            tier="pro"
        )
        print(f"🔑 Demo API Key: {demo_key}")

    def generate_key(
        self,
        user_id: str,
        name: str = "Default",
        tier: str = "free"
    ) -> str:
        """Generate a new API key"""
        # Format: csk_live_... (concise secret key)
        key = f"csk_live_{secrets.token_urlsafe(32)}"

        api_key = APIKey(
            key=key,
            user_id=user_id,
            name=name,
            created_at=datetime.utcnow(),
            tier=tier
        )

        self.keys[key] = api_key
        return key

    def validate_key(self, key: str) -> Optional[APIKey]:
        """Validate an API key and return key info"""
        api_key = self.keys.get(key)

        if not api_key:
            return None

        if not api_key.is_active:
            return None

        # Update last used timestamp
        api_key.last_used = datetime.utcnow()

        return api_key

    def revoke_key(self, key: str) -> bool:
        """Revoke an API key"""
        api_key = self.keys.get(key)
        if api_key:
            api_key.is_active = False
            return True
        return False

    def get_user_keys(self, user_id: str) -> list[APIKey]:
        """Get all keys for a user"""
        return [
            key for key in self.keys.values()
            if key.user_id == user_id
        ]


# Singleton instance
_key_manager: Optional[APIKeyManager] = None

def get_key_manager() -> APIKeyManager:
    """Get or create the key manager singleton"""
    global _key_manager
    if _key_manager is None:
        _key_manager = APIKeyManager()
    return _key_manager


# FastAPI security scheme
security = HTTPBearer(
    scheme_name="API Key",
    description="Provide your API key in the Authorization header as 'Bearer YOUR_KEY'"
)


async def verify_api_key(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> APIKey:
    """
    FastAPI dependency to verify API key from Authorization header

    Usage:
        @app.get("/protected")
        async def protected_route(api_key: APIKey = Depends(verify_api_key)):
            return {"user_id": api_key.user_id}
    """
    key = credentials.credentials
    key_manager = get_key_manager()

    api_key = key_manager.validate_key(key)

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired API key",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return api_key


class RateLimiter:
    """Simple in-memory rate limiter"""

    def __init__(self):
        # user_id -> list of request timestamps
        self.requests: dict[str, list[datetime]] = {}

    def check_rate_limit(
        self,
        user_id: str,
        limit: int = 60,
        window_seconds: int = 60
    ) -> bool:
        """
        Check if user is within rate limit

        Args:
            user_id: User identifier
            limit: Max requests per window
            window_seconds: Time window in seconds

        Returns:
            True if within limit, False if exceeded
        """
        now = datetime.utcnow()
        window_start = now - timedelta(seconds=window_seconds)

        # Get user's request history
        if user_id not in self.requests:
            self.requests[user_id] = []

        # Remove old requests outside the window
        self.requests[user_id] = [
            ts for ts in self.requests[user_id]
            if ts > window_start
        ]

        # Check limit
        if len(self.requests[user_id]) >= limit:
            return False

        # Add current request
        self.requests[user_id].append(now)
        return True


# Singleton rate limiter
_rate_limiter: Optional[RateLimiter] = None

def get_rate_limiter() -> RateLimiter:
    """Get or create the rate limiter singleton"""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RateLimiter()
    return _rate_limiter


async def check_rate_limit(
    api_key: APIKey = Security(verify_api_key)
) -> APIKey:
    """
    FastAPI dependency to check rate limits

    Usage:
        @app.get("/limited")
        async def limited_route(api_key: APIKey = Depends(check_rate_limit)):
            return {"status": "ok"}
    """
    limiter = get_rate_limiter()

    if not limiter.check_rate_limit(api_key.user_id, api_key.rate_limit):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Max {api_key.rate_limit} requests per minute.",
        )

    return api_key
