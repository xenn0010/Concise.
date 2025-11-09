"""
Tests for the compression engine
"""

import pytest
from app.compressor import ConciseCompressor, CompressorConfig


@pytest.fixture
def compressor():
    """Create a compressor instance without Redis for testing"""
    return ConciseCompressor(redis_url=None)


def test_basic_compression(compressor):
    """Test basic text compression"""
    text = """
    Please help me understand how to implement authentication in my application.
    I need to know about JWT tokens, how they work, how to validate them,
    and how to handle token expiration. I would really appreciate a detailed
    explanation with code examples if possible. Thank you so much for your help!
    """

    result = compressor.compress(text, strategy="balanced", use_cache=False)

    # Verify result structure
    assert "compressed_text" in result
    assert "original_tokens" in result
    assert "compressed_tokens" in result
    assert "tokens_saved" in result
    assert "compression_ratio" in result

    # Verify compression happened
    assert result["compressed_tokens"] < result["original_tokens"]
    assert result["tokens_saved"] > 0
    assert result["compression_ratio"] > 1.0

    # Verify metadata
    assert result["strategy"] == "balanced"
    assert result["compression_time_ms"] > 0
    assert result["cost_saved_usd"] > 0


def test_compression_strategies(compressor):
    """Test different compression strategies"""
    text = "Please help me understand authentication. " * 50  # Repeat for longer text

    conservative = compressor.compress(text, strategy="conservative", use_cache=False)
    balanced = compressor.compress(text, strategy="balanced", use_cache=False)
    aggressive = compressor.compress(text, strategy="aggressive", use_cache=False)

    # Conservative should save least
    # Aggressive should save most
    assert conservative["compression_ratio"] < balanced["compression_ratio"]
    assert balanced["compression_ratio"] < aggressive["compression_ratio"]


def test_message_compression(compressor):
    """Test OpenAI message array compression"""
    messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant that helps with coding questions."
        },
        {
            "role": "user",
            "content": "What is 2+2?"
        }
    ]

    result = compressor.compress_messages(
        messages,
        strategy="balanced",
        compress_system=True,
        compress_user=False
    )

    # Verify structure
    assert "messages" in result
    assert len(result["messages"]) == 2

    # System message should be compressed
    assert len(result["messages"][0]["content"]) < len(messages[0]["content"])

    # User message should be unchanged
    assert result["messages"][1]["content"] == messages[1]["content"]

    # Verify metadata
    assert result["tokens_saved"] > 0


def test_stats_tracking(compressor):
    """Test that stats are tracked correctly"""
    initial_stats = compressor.get_stats()

    # Do a compression
    text = "Please help me with this task. " * 10
    compressor.compress(text, strategy="balanced", use_cache=False)

    # Check stats updated
    updated_stats = compressor.get_stats()
    assert updated_stats["total_requests"] == initial_stats["total_requests"] + 1
    assert updated_stats["cache_misses"] == initial_stats["cache_misses"] + 1


def test_empty_text_handling(compressor):
    """Test handling of edge cases"""
    # Empty text
    with pytest.raises(Exception):
        compressor.compress("", strategy="balanced")


def test_invalid_strategy(compressor):
    """Test invalid strategy defaults to balanced"""
    text = "Test text here."
    result = compressor.compress(text, strategy="invalid_strategy", use_cache=False)

    # Should default to balanced
    assert result["strategy"] == "balanced"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
