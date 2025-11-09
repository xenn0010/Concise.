"""
Optimized LLMLingua compression engine with caching
"""

import hashlib
import json
import time
from typing import Dict, List, Optional
from functools import lru_cache

from llmlingua import PromptCompressor
import redis


class CompressorConfig:
    """Configuration for the compression engine"""

    # Model settings
    MODEL_NAME = "gpt2"  # Start with GPT-2 Small (270MB)
    DEVICE = "cpu"  # Free tier uses CPU

    # Compression strategies
    STRATEGIES = {
        "conservative": {
            "ratio": 3.0,
            "quality_threshold": 0.95,
            "description": "Light compression, highest quality"
        },
        "balanced": {
            "ratio": 5.0,
            "quality_threshold": 0.90,
            "description": "Good trade-off between compression and quality"
        },
        "aggressive": {
            "ratio": 10.0,
            "quality_threshold": 0.85,
            "description": "Maximum compression, acceptable quality"
        },
        "extreme": {
            "ratio": 20.0,
            "quality_threshold": 0.75,
            "description": "Extreme compression for large contexts"
        }
    }

    # Cache settings
    CACHE_TTL = 86400  # 24 hours
    CACHE_ENABLED = True


class CompressionCache:
    """Redis-based caching layer for compressed prompts"""

    def __init__(self, redis_url: Optional[str] = None):
        self.enabled = redis_url is not None and CompressorConfig.CACHE_ENABLED
        self.client = None

        if self.enabled:
            try:
                self.client = redis.from_url(redis_url, decode_responses=True)
                self.client.ping()
                print("✅ Redis cache connected")
            except Exception as e:
                print(f"⚠️  Redis cache disabled: {e}")
                self.enabled = False

    def _make_key(self, text: str, strategy: str) -> str:
        """Generate cache key from text and strategy"""
        content = f"{text}:{strategy}".encode('utf-8')
        return f"compress:{hashlib.sha256(content).hexdigest()}"

    def get(self, text: str, strategy: str) -> Optional[Dict]:
        """Get cached compression result"""
        if not self.enabled:
            return None

        try:
            key = self._make_key(text, strategy)
            cached = self.client.get(key)
            if cached:
                return json.loads(cached)
        except Exception as e:
            print(f"Cache get error: {e}")

        return None

    def set(self, text: str, strategy: str, result: Dict) -> None:
        """Cache compression result"""
        if not self.enabled:
            return

        try:
            key = self._make_key(text, strategy)
            self.client.setex(
                key,
                CompressorConfig.CACHE_TTL,
                json.dumps(result)
            )
        except Exception as e:
            print(f"Cache set error: {e}")

    def get_stats(self) -> Dict:
        """Get cache statistics"""
        if not self.enabled:
            return {"enabled": False}

        try:
            info = self.client.info("stats")
            return {
                "enabled": True,
                "hits": info.get("keyspace_hits", 0),
                "misses": info.get("keyspace_misses", 0),
                "hit_rate": self._calculate_hit_rate(info)
            }
        except Exception as e:
            return {"enabled": True, "error": str(e)}

    def _calculate_hit_rate(self, info: Dict) -> float:
        """Calculate cache hit rate percentage"""
        hits = info.get("keyspace_hits", 0)
        misses = info.get("keyspace_misses", 0)
        total = hits + misses
        return (hits / total * 100) if total > 0 else 0.0


class ConciseCompressor:
    """Main compression engine with optimization and caching"""

    def __init__(self, redis_url: Optional[str] = None):
        print("🔧 Initializing Concise Compressor...")

        # Initialize cache
        self.cache = CompressionCache(redis_url)

        # Load model (this happens once, stays in memory)
        print(f"📦 Loading {CompressorConfig.MODEL_NAME} model...")
        start_time = time.time()

        self.compressor = PromptCompressor(
            model_name=CompressorConfig.MODEL_NAME,
            device_map=CompressorConfig.DEVICE
        )

        load_time = time.time() - start_time
        print(f"✅ Model loaded in {load_time:.2f}s")

        # Statistics
        self.stats = {
            "total_requests": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "total_tokens_saved": 0,
            "total_compression_time": 0.0
        }

    def compress(
        self,
        text: str,
        strategy: str = "balanced",
        use_cache: bool = True
    ) -> Dict:
        """
        Compress text using specified strategy

        Args:
            text: Text to compress
            strategy: One of 'conservative', 'balanced', 'aggressive', 'extreme'
            use_cache: Whether to use caching

        Returns:
            Dict with compression results and metadata
        """
        self.stats["total_requests"] += 1

        # Validate strategy
        if strategy not in CompressorConfig.STRATEGIES:
            strategy = "balanced"

        # Check cache first
        if use_cache:
            cached_result = self.cache.get(text, strategy)
            if cached_result:
                self.stats["cache_hits"] += 1
                cached_result["cached"] = True
                cached_result["compression_time_ms"] = 0
                return cached_result

        # Cache miss - do compression
        self.stats["cache_misses"] += 1

        start_time = time.time()
        config = CompressorConfig.STRATEGIES[strategy]

        try:
            # Run LLMLingua compression with aggressive parameters
            # Rate calculation: for 5x compression, rate=0.2 (keep 20% of tokens)
            compression_rate = 1.0 / config["ratio"]

            result = self.compressor.compress_prompt(
                text,

                # Compression target
                rate=compression_rate,
                target_token=-1,  # Use rate-based compression instead of target

                # Enable all compression levels
                use_sentence_level_filter=True,  # Enable sentence filtering
                use_context_level_filter=True,   # Enable context filtering
                use_token_level_filter=True,      # Enable token filtering (most aggressive)

                # Aggressive compression settings
                force_tokens=[],  # Don't force-keep any specific tokens
                drop_consecutive=True,  # Drop consecutive similar tokens

                # Sentence preservation (disable for aggressive compression)
                keep_first_sentence=0,  # Don't protect first sentence
                keep_last_sentence=0,   # Don't protect last sentence
                keep_sentence_number=0, # Don't protect any specific sentences

                # Reduce iteration size for more aggressive per-chunk compression
                iterative_size=50,  # Smaller chunks = more aggressive

                # Budget controls
                context_budget="+0",  # No extra budget
                token_budget_ratio=compression_rate,  # Match target rate
            )

            compression_time = (time.time() - start_time) * 1000  # ms
            self.stats["total_compression_time"] += compression_time

            # Calculate metrics
            # LLMLingua returns token counts as integers, not lists
            original_tokens = result.get("origin_tokens", len(text.split()))
            if isinstance(original_tokens, list):
                original_tokens = len(original_tokens)

            compressed_tokens = result.get("compressed_tokens", len(result["compressed_prompt"].split()))
            if isinstance(compressed_tokens, list):
                compressed_tokens = len(compressed_tokens)

            tokens_saved = original_tokens - compressed_tokens
            actual_ratio = original_tokens / compressed_tokens if compressed_tokens > 0 else 0

            # Calculate cost savings (assuming GPT-4 pricing)
            # Input: $0.03 per 1K tokens
            cost_saved = (tokens_saved / 1000) * 0.03

            self.stats["total_tokens_saved"] += tokens_saved

            # Prepare result
            result_dict = {
                "compressed_text": result["compressed_prompt"],
                "original_tokens": original_tokens,
                "compressed_tokens": compressed_tokens,
                "tokens_saved": tokens_saved,
                "compression_ratio": round(actual_ratio, 2),
                "target_ratio": config["ratio"],
                "cost_saved_usd": round(cost_saved, 4),
                "strategy": strategy,
                "compression_time_ms": round(compression_time, 2),
                "cached": False
            }

            # Cache the result
            if use_cache:
                self.cache.set(text, strategy, result_dict)

            return result_dict

        except Exception as e:
            raise Exception(f"Compression failed: {str(e)}")

    def compress_messages(
        self,
        messages: List[Dict],
        strategy: str = "balanced",
        compress_system: bool = True,
        compress_user: bool = False
    ) -> Dict:
        """
        Compress OpenAI-style message array

        Args:
            messages: List of message dicts with 'role' and 'content'
            strategy: Compression strategy
            compress_system: Whether to compress system messages
            compress_user: Whether to compress user messages (usually keep as-is)

        Returns:
            Dict with compressed messages and metadata
        """
        compressed_messages = []
        total_saved = 0
        total_original = 0
        total_compressed = 0

        for msg in messages:
            role = msg.get("role", "")
            content = msg.get("content", "")

            # Decide whether to compress this message
            should_compress = (
                (role == "system" and compress_system) or
                (role == "user" and compress_user) or
                (role == "assistant" and False)  # Never compress assistant messages
            )

            if should_compress and len(content) > 100:  # Only compress if worth it
                result = self.compress(content, strategy=strategy)
                compressed_messages.append({
                    "role": role,
                    "content": result["compressed_text"]
                })
                total_saved += result["tokens_saved"]
                total_original += result["original_tokens"]
                total_compressed += result["compressed_tokens"]
            else:
                # Keep original
                compressed_messages.append(msg)
                token_count = len(content.split())
                total_original += token_count
                total_compressed += token_count

        ratio = total_original / total_compressed if total_compressed > 0 else 1.0
        cost_saved = (total_saved / 1000) * 0.03

        return {
            "messages": compressed_messages,
            "original_tokens": total_original,
            "compressed_tokens": total_compressed,
            "tokens_saved": total_saved,
            "compression_ratio": round(ratio, 2),
            "cost_saved_usd": round(cost_saved, 4),
            "strategy": strategy
        }

    def get_stats(self) -> Dict:
        """Get compression statistics"""
        avg_time = (
            self.stats["total_compression_time"] / self.stats["cache_misses"]
            if self.stats["cache_misses"] > 0 else 0
        )

        hit_rate = (
            (self.stats["cache_hits"] / self.stats["total_requests"] * 100)
            if self.stats["total_requests"] > 0 else 0
        )

        total_cost_saved = (self.stats["total_tokens_saved"] / 1000) * 0.03

        return {
            "total_requests": self.stats["total_requests"],
            "cache_hits": self.stats["cache_hits"],
            "cache_misses": self.stats["cache_misses"],
            "cache_hit_rate": round(hit_rate, 2),
            "total_tokens_saved": self.stats["total_tokens_saved"],
            "total_cost_saved_usd": round(total_cost_saved, 2),
            "avg_compression_time_ms": round(avg_time, 2),
            "cache_stats": self.cache.get_stats()
        }


# Singleton instance (load model once)
_compressor_instance: Optional[ConciseCompressor] = None

def get_compressor(redis_url: Optional[str] = None) -> ConciseCompressor:
    """Get or create the singleton compressor instance"""
    global _compressor_instance

    if _compressor_instance is None:
        _compressor_instance = ConciseCompressor(redis_url)

    return _compressor_instance
