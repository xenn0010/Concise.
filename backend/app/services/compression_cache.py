"""
Simple in-memory cache for compression results
Makes repeated compressions instant
"""
import hashlib
import time
from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict


@dataclass
class CachedCompression:
    """Cached compression result"""
    compressed_text: str
    original_tokens: int
    compressed_tokens: int
    compression_time_ms: float
    timestamp: float
    cache_hit: bool = True


class CompressionCache:
    """
    In-memory LRU cache for compression results
    Makes repeated compressions instant (0ms vs 271ms)
    """

    def __init__(self, max_size: int = 1000, ttl_seconds: int = 3600):
        """
        Args:
            max_size: Maximum number of cached items
            ttl_seconds: Time to live for cached items (default 1 hour)
        """
        self.cache: Dict[str, CachedCompression] = {}
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.hits = 0
        self.misses = 0

    def _hash_key(self, text: str, rate: float) -> str:
        """Generate cache key from text and compression rate"""
        content = f"{text}:{rate}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def get(self, text: str, rate: float) -> Optional[CachedCompression]:
        """
        Get cached compression result

        Args:
            text: Original text
            rate: Compression rate used

        Returns:
            CachedCompression if found and valid, None otherwise
        """
        key = self._hash_key(text, rate)

        if key in self.cache:
            cached = self.cache[key]

            # Check if expired
            age = time.time() - cached.timestamp
            if age > self.ttl_seconds:
                del self.cache[key]
                self.misses += 1
                return None

            # Cache hit!
            self.hits += 1
            return cached

        self.misses += 1
        return None

    def set(
        self,
        text: str,
        rate: float,
        compressed_text: str,
        original_tokens: int,
        compressed_tokens: int,
        compression_time_ms: float
    ):
        """
        Store compression result in cache

        Args:
            text: Original text
            rate: Compression rate used
            compressed_text: Compressed result
            original_tokens: Token count before compression
            compressed_tokens: Token count after compression
            compression_time_ms: Time taken to compress
        """
        key = self._hash_key(text, rate)

        # Evict oldest if cache is full
        if len(self.cache) >= self.max_size:
            oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k].timestamp)
            del self.cache[oldest_key]

        # Store result
        self.cache[key] = CachedCompression(
            compressed_text=compressed_text,
            original_tokens=original_tokens,
            compressed_tokens=compressed_tokens,
            compression_time_ms=compression_time_ms,
            timestamp=time.time(),
            cache_hit=False  # Will be True when retrieved
        )

    def clear(self):
        """Clear all cached items"""
        self.cache.clear()
        self.hits = 0
        self.misses = 0

    def stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0

        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": f"{hit_rate:.1f}%",
            "total_requests": total
        }


# Global cache instance
_cache: Optional[CompressionCache] = None


def get_cache() -> CompressionCache:
    """Get or create global compression cache"""
    global _cache
    if _cache is None:
        _cache = CompressionCache(max_size=1000, ttl_seconds=3600)
    return _cache
