"""
Rate Limiter Middleware
Supports Redis and in-memory sliding window rate limiting
"""
import time
import threading
from typing import Dict, List, Tuple, Optional
from collections import deque
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False


class SlidingWindowRateLimiter:
    """
    In-memory sliding window rate limiter
    More accurate than fixed window, handles bursts better
    """

    def __init__(self):
        # {identifier: deque of timestamps}
        self.windows: Dict[str, deque] = {}
        self.lock = threading.Lock()

    def is_allowed(
        self,
        identifier: str,
        max_requests: int,
        window_seconds: int
    ) -> Tuple[bool, Dict[str, int]]:
        """
        Check if request is allowed

        Returns: (allowed: bool, info: dict)
        """
        with self.lock:
            now = time.time()
            window_start = now - window_seconds

            # Initialize or get existing window
            if identifier not in self.windows:
                self.windows[identifier] = deque()

            window = self.windows[identifier]

            # Remove expired timestamps
            while window and window[0] < window_start:
                window.popleft()

            # Check limit
            current_count = len(window)
            allowed = current_count < max_requests

            if allowed:
                # Add current request
                window.append(now)

            # Calculate retry after
            if not allowed and window:
                oldest_request = window[0]
                retry_after = int(window_seconds - (now - oldest_request)) + 1
            else:
                retry_after = 0

            info = {
                'limit': max_requests,
                'remaining': max(0, max_requests - current_count - (1 if allowed else 0)),
                'reset': int(now + window_seconds),
                'retry_after': retry_after
            }

            return allowed, info

    def reset(self, identifier: str):
        """Reset rate limit for identifier"""
        with self.lock:
            if identifier in self.windows:
                del self.windows[identifier]

    def cleanup_old_windows(self, max_age_seconds: int = 3600):
        """Clean up old windows to prevent memory leak"""
        with self.lock:
            now = time.time()
            to_delete = []

            for identifier, window in self.windows.items():
                if window and (now - window[-1]) > max_age_seconds:
                    to_delete.append(identifier)

            for identifier in to_delete:
                del self.windows[identifier]


class RedisRateLimiter:
    """Redis-based rate limiter using sorted sets"""

    def __init__(self, redis_client):
        self.redis = redis_client

    def is_allowed(
        self,
        identifier: str,
        max_requests: int,
        window_seconds: int
    ) -> Tuple[bool, Dict[str, int]]:
        """Check if request is allowed using Redis"""
        now = time.time()
        window_start = now - window_seconds
        key = f"ratelimit:{identifier}"

        try:
            pipe = self.redis.pipeline()

            # Remove old entries
            pipe.zremrangebyscore(key, 0, window_start)

            # Count current requests
            pipe.zcard(key)

            # Add current request (optimistically)
            pipe.zadd(key, {str(now): now})

            # Set expiry
            pipe.expire(key, window_seconds + 60)

            # Execute pipeline
            _, current_count, _, _ = pipe.execute()

            # Check if allowed (before adding current)
            allowed = current_count < max_requests

            if not allowed:
                # Remove the request we just added
                self.redis.zrem(key, str(now))

                # Get oldest request for retry-after
                oldest = self.redis.zrange(key, 0, 0, withscores=True)
                if oldest:
                    oldest_time = oldest[0][1]
                    retry_after = int(window_seconds - (now - oldest_time)) + 1
                else:
                    retry_after = window_seconds
            else:
                retry_after = 0

            info = {
                'limit': max_requests,
                'remaining': max(0, max_requests - current_count - (1 if allowed else 0)),
                'reset': int(now + window_seconds),
                'retry_after': retry_after
            }

            return allowed, info

        except Exception as e:
            print(f"Redis rate limit error: {e}, allowing request")
            # Fail open on errors
            return True, {
                'limit': max_requests,
                'remaining': max_requests,
                'reset': int(now + window_seconds),
                'retry_after': 0
            }

    def reset(self, identifier: str):
        """Reset rate limit"""
        try:
            self.redis.delete(f"ratelimit:{identifier}")
        except Exception as e:
            print(f"Redis reset error: {e}")


class RateLimiter:
    """
    Unified rate limiter supporting Redis and in-memory backends
    """

    def __init__(self, redis_url: Optional[str] = None):
        self.use_redis = False
        self.backend = None

        # Try Redis first
        if redis_url and REDIS_AVAILABLE:
            try:
                redis_client = redis.from_url(
                    redis_url,
                    decode_responses=True,
                    socket_connect_timeout=2
                )
                redis_client.ping()
                self.backend = RedisRateLimiter(redis_client)
                self.use_redis = True
                print("✅ Rate limiter using Redis")
            except Exception as e:
                print(f"⚠️  Redis rate limiter failed: {e}")

        # Fallback to in-memory
        if not self.use_redis:
            self.backend = SlidingWindowRateLimiter()
            print("💾 Rate limiter using in-memory sliding window")

    def check_rate_limit(
        self,
        identifier: str,
        max_requests: int = 100,
        window_seconds: int = 60
    ) -> Tuple[bool, Dict[str, int]]:
        """
        Check if request is within rate limit

        Args:
            identifier: Unique identifier (API key, IP, user ID)
            max_requests: Max requests allowed in window
            window_seconds: Time window in seconds

        Returns:
            (allowed, info) where info contains limit details
        """
        return self.backend.is_allowed(identifier, max_requests, window_seconds)

    def reset(self, identifier: str):
        """Reset rate limit for identifier"""
        self.backend.reset(identifier)


# Global rate limiter
_rate_limiter: Optional[RateLimiter] = None


def get_rate_limiter(redis_url: Optional[str] = None) -> RateLimiter:
    """Get or create global rate limiter"""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RateLimiter(redis_url)
    return _rate_limiter


# FastAPI middleware
async def rate_limit_middleware(request: Request, call_next):
    """
    FastAPI middleware for rate limiting
    """
    # Skip rate limiting for health checks and docs
    if request.url.path in ["/health", "/docs", "/openapi.json"]:
        return await call_next(request)

    # Get identifier (API key or IP)
    api_key = request.headers.get("X-API-Key")
    identifier = api_key if api_key else request.client.host

    # Get rate limits from environment or use defaults
    import os
    max_requests = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
    window_seconds = int(os.getenv("RATE_LIMIT_WINDOW", "60"))

    # Check rate limit
    limiter = get_rate_limiter()
    allowed, info = limiter.check_rate_limit(identifier, max_requests, window_seconds)

    if not allowed:
        # Rate limited
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "error": "Rate limit exceeded",
                "message": f"Too many requests. Maximum {max_requests} requests per {window_seconds} seconds.",
                "limit": info['limit'],
                "retry_after": info['retry_after']
            },
            headers={
                "X-RateLimit-Limit": str(info['limit']),
                "X-RateLimit-Remaining": str(info['remaining']),
                "X-RateLimit-Reset": str(info['reset']),
                "Retry-After": str(info['retry_after'])
            }
        )

    # Request allowed, add rate limit headers
    response = await call_next(request)
    response.headers["X-RateLimit-Limit"] = str(info['limit'])
    response.headers["X-RateLimit-Remaining"] = str(info['remaining'])
    response.headers["X-RateLimit-Reset"] = str(info['reset'])

    return response


# Test
if __name__ == "__main__":
    print("Testing Rate Limiter...\n")

    limiter = RateLimiter()

    print("Test 1: Allow requests within limit")
    for i in range(5):
        allowed, info = limiter.check_rate_limit("test_user", max_requests=5, window_seconds=10)
        print(f"  Request {i+1}: {'✅ Allowed' if allowed else '❌ Blocked'} - Remaining: {info['remaining']}")

    print("\nTest 2: Block when limit exceeded")
    allowed, info = limiter.check_rate_limit("test_user", max_requests=5, window_seconds=10)
    print(f"  Request 6: {'✅ Allowed' if allowed else '❌ Blocked'} - Retry after: {info['retry_after']}s")

    print("\nTest 3: Reset and allow again")
    limiter.reset("test_user")
    allowed, info = limiter.check_rate_limit("test_user", max_requests=5, window_seconds=10)
    print(f"  After reset: {'✅ Allowed' if allowed else '❌ Blocked'} - Remaining: {info['remaining']}")

    print("\n✅ Rate limiter test complete")
