"""
Basic compression example
"""

from concise import Concise

client = Concise(api_key="your-api-key")

text = "FastAPI is a modern, fast web framework for building APIs with Python 3.8+"

result = client.compress(text, level="auto")

print(f"Original: {result.original_tokens} tokens")
print(f"Compressed: {result.compressed_tokens} tokens")
print(f"Saved: {result.tokens_saved} tokens ({(1-result.compression_ratio)*100:.1f}%)")
print(f"Time: {result.compression_time_ms:.0f}ms")
print(f"\nOriginal text:\n{result.original_text}")
print(f"\nCompressed text:\n{result.compressed_text}")
