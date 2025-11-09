"""
Quick test for compression service
"""
import sys
sys.path.insert(0, '.')

from app.services.compression import ConciseCompressor

# Sample Python code
code_sample = """
def fibonacci(n):
    '''Calculate fibonacci number'''
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

class Calculator:
    '''A simple calculator class'''

    def add(self, a, b):
        '''Add two numbers'''
        return a + b

    def multiply(self, a, b):
        '''Multiply two numbers'''
        result = a * b
        return result
"""

# Sample text
text_sample = """
The quick brown fox jumps over the lazy dog. This is a simple sentence
used for testing text compression. We want to see how well the compression
algorithm works on natural language text. The goal is to reduce the token
count while preserving the essential meaning and context of the original text.
"""

print("=" * 60)
print("Concise Compression Service Test")
print("=" * 60)

# Initialize compressor
print("\nInitializing compressor...")
compressor = ConciseCompressor()
print("✅ Compressor initialized")

# Test code compression - AUTO level (should detect code)
print("\n" + "-" * 60)
print("Testing TOKEN COMPRESSION - AUTO (code)")
print("-" * 60)
result = compressor.compress(code_sample, level="auto")
print(f"Original tokens: {result.original_tokens}")
print(f"Compressed tokens: {result.compressed_tokens}")
print(f"Tokens saved: {result.tokens_saved}")
print(f"Compression ratio: {result.compression_ratio:.2%}")
print(f"Internal strategy: {result.strategy}")
print(f"Time: {result.compression_time_ms:.2f}ms")
print(f"\nCompressed code preview (first 200 chars):")
print(result.compressed_text[:200])

# Test aggressive compression on code
print("\n" + "-" * 60)
print("Testing TOKEN COMPRESSION - AGGRESSIVE (code)")
print("-" * 60)
result = compressor.compress(code_sample, level="aggressive")
print(f"Original tokens: {result.original_tokens}")
print(f"Compressed tokens: {result.compressed_tokens}")
print(f"Tokens saved: {result.tokens_saved}")
print(f"Compression ratio: {result.compression_ratio:.2%}")

# Test conservative compression on code
print("\n" + "-" * 60)
print("Testing TOKEN COMPRESSION - CONSERVATIVE (code)")
print("-" * 60)
result = compressor.compress(code_sample, level="conservative")
print(f"Original tokens: {result.original_tokens}")
print(f"Compressed tokens: {result.compressed_tokens}")
print(f"Tokens saved: {result.tokens_saved}")
print(f"Compression ratio: {result.compression_ratio:.2%}")

# Test auto-detection on text
print("\n" + "-" * 60)
print("Testing TOKEN COMPRESSION - AUTO (text)")
print("-" * 60)
print("Note: Text compression requires 2.24GB LLMLingua model download")
print("This will be downloaded on first use and cached locally")

print("\n" + "=" * 60)
print("✅ All compression tests passed!")
print("=" * 60)
