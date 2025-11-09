"""
Cache Manager with Redis + In-Memory Fallback
Supports both Redis (production) and in-memory (development/testing)
"""
import hashlib
import json
import time
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import threading

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False


class InMemoryCache:
    """
    Thread-safe in-memory cache with TTL support
    Fallback when Redis is not available
    """

    def __init__(self, max_size: int = 10000):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.max_size = max_size
        self.lock = threading.Lock()

    def get(self, key: str) -> Optional[str]:
        """Get value from cache"""
        with self.lock:
            if key in self.cache:
                entry = self.cache[key]
                # Check if expired
                if entry['expires_at'] > time.time():
                    entry['hits'] += 1
                    entry['last_accessed'] = time.time()
                    return entry['value']
                else:
                    # Expired, remove
                    del self.cache[key]
            return None

    def set(self, key: str, value: str, ttl: int = 3600):
        """Set value in cache with TTL (seconds)"""
        with self.lock:
            # Evict if cache is full
            if len(self.cache) >= self.max_size:
                self._evict_lru()

            self.cache[key] = {
                'value': value,
                'expires_at': time.time() + ttl,
                'created_at': time.time(),
                'last_accessed': time.time(),
                'hits': 0
            }

    def delete(self, key: str):
        """Delete key from cache"""
        with self.lock:
            if key in self.cache:
                del self.cache[key]

    def clear(self):
        """Clear all cache"""
        with self.lock:
            self.cache.clear()

    def _evict_lru(self):
        """Evict least recently used entry"""
        if not self.cache:
            return

        # Find LRU entry
        lru_key = min(
            self.cache.keys(),
            key=lambda k: self.cache[k]['last_accessed']
        )
        del self.cache[lru_key]

    def stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self.lock:
            total_hits = sum(entry['hits'] for entry in self.cache.values())
            return {
                'type': 'in_memory',
                'size': len(self.cache),
                'max_size': self.max_size,
                'total_hits': total_hits,
                'avg_hits_per_key': total_hits / len(self.cache) if self.cache else 0
            }


class CacheManager:
    """
    Unified cache interface supporting Redis and in-memory fallback
    """

    def __init__(self, redis_url: Optional[str] = None):
        self.redis_client = None
        self.use_redis = False

        # Try to connect to Redis
        if redis_url and REDIS_AVAILABLE:
            try:
                self.redis_client = redis.from_url(
                    redis_url,
                    decode_responses=True,
                    socket_connect_timeout=2
                )
                self.redis_client.ping()
                self.use_redis = True
                print(f"✅ Connected to Redis: {redis_url}")
            except Exception as e:
                print(f"⚠️  Redis connection failed: {e}")
                print("   Falling back to in-memory cache")

        # Fallback to in-memory cache
        if not self.use_redis:
            self.memory_cache = InMemoryCache()
            print("💾 Using in-memory cache (development mode)")

    def _make_key(self, prefix: str, data: str) -> str:
        """Generate cache key"""
        hash_val = hashlib.sha256(data.encode()).hexdigest()[:16]
        return f"{prefix}:{hash_val}"

    def get(self, prefix: str, data: str) -> Optional[Dict]:
        """Get cached value"""
        key = self._make_key(prefix, data)

        try:
            if self.use_redis:
                cached = self.redis_client.get(key)
                if cached:
                    return json.loads(cached)
            else:
                cached = self.memory_cache.get(key)
                if cached:
                    return json.loads(cached)
        except Exception as e:
            print(f"Cache get error: {e}")

        return None

    def set(self, prefix: str, data: str, value: Dict, ttl: int = 3600):
        """Set cached value with TTL"""
        key = self._make_key(prefix, data)

        try:
            json_value = json.dumps(value)

            if self.use_redis:
                self.redis_client.setex(key, ttl, json_value)
            else:
                self.memory_cache.set(key, json_value, ttl)
        except Exception as e:
            print(f"Cache set error: {e}")

    def delete(self, prefix: str, data: str):
        """Delete cached value"""
        key = self._make_key(prefix, data)

        try:
            if self.use_redis:
                self.redis_client.delete(key)
            else:
                self.memory_cache.delete(key)
        except Exception as e:
            print(f"Cache delete error: {e}")

    def clear(self, prefix: Optional[str] = None):
        """Clear cache (optionally by prefix)"""
        try:
            if self.use_redis:
                if prefix:
                    # Delete keys matching prefix
                    pattern = f"{prefix}:*"
                    keys = self.redis_client.keys(pattern)
                    if keys:
                        self.redis_client.delete(*keys)
                else:
                    self.redis_client.flushdb()
            else:
                self.memory_cache.clear()
        except Exception as e:
            print(f"Cache clear error: {e}")

    def stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        try:
            if self.use_redis:
                info = self.redis_client.info('stats')
                return {
                    'type': 'redis',
                    'connected': True,
                    'keyspace_hits': info.get('keyspace_hits', 0),
                    'keyspace_misses': info.get('keyspace_misses', 0),
                    'hit_rate': self._calculate_hit_rate(info)
                }
            else:
                return self.memory_cache.stats()
        except Exception as e:
            return {'type': 'unknown', 'error': str(e)}

    def _calculate_hit_rate(self, info: Dict) -> float:
        """Calculate cache hit rate"""
        hits = info.get('keyspace_hits', 0)
        misses = info.get('keyspace_misses', 0)
        total = hits + misses
        return (hits / total * 100) if total > 0 else 0.0


# Global cache instance
_cache_manager: Optional[CacheManager] = None


def get_cache_manager(redis_url: Optional[str] = None) -> CacheManager:
    """Get or create global cache manager"""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager(redis_url)
    return _cache_manager


# Test
if __name__ == "__main__":
    print("Testing Cache Manager...\n")

    # Test in-memory cache
    cache = CacheManager()

    print("1. Set value")
    cache.set("test", "hello", {"result": "world"}, ttl=5)

    print("2. Get value")
    result = cache.get("test", "hello")
    print(f"   Result: {result}")

    print("3. Get non-existent")
    result = cache.get("test", "missing")
    print(f"   Result: {result}")

    print("4. Cache stats")
    stats = cache.stats()
    print(f"   Stats: {stats}")

    print("\n5. Test expiration")
    cache.set("test", "expire", {"data": "soon"}, ttl=1)
    print(f"   Immediate: {cache.get('test', 'expire')}")
    time.sleep(2)
    print(f"   After 2s: {cache.get('test', 'expire')}")

    print("\n✅ Cache manager test complete")
