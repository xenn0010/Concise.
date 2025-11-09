#!/usr/bin/env python3
"""
Test LLMLingua API to understand the correct usage
"""

from llmlingua import PromptCompressor
import json

print("Testing LLMLingua API...")

# Test different initialization options
print("\n1. Testing basic initialization...")
try:
    compressor = PromptCompressor(
        model_name="gpt2",
        device_map="cpu"
    )
    print("✅ Basic initialization works")
    print(f"   Compressor type: {type(compressor)}")
    print(f"   Has compress_prompt: {hasattr(compressor, 'compress_prompt')}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test compression with simple text
print("\n2. Testing simple compression...")
simple_text = "This is a simple test to see if compression works properly."

try:
    result = compressor.compress_prompt(simple_text)
    print("✅ Simple compression works")
    print(f"   Result type: {type(result)}")
    print(f"   Result keys: {result.keys() if isinstance(result, dict) else 'Not a dict'}")
    print(f"   Result: {json.dumps(result, indent=2, default=str)[:500]}")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

# Test with rate parameter
print("\n3. Testing compression with rate parameter...")
try:
    result = compressor.compress_prompt(simple_text, rate=0.5)
    print("✅ Compression with rate works")
    print(f"   Compressed: {result.get('compressed_prompt', 'N/A')[:100]}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test with longer text
print("\n4. Testing with longer text...")
long_text = """
I am working on a project that requires user authentication. I need to understand
how to implement a secure login system using JWT tokens. Can you please explain to me
step by step how to create the authentication middleware, how to generate tokens.
"""

try:
    result = compressor.compress_prompt(long_text, rate=0.5)
    print("✅ Long text compression works")
    print(f"   Original length: {len(long_text)}")
    print(f"   Compressed: {result.get('compressed_prompt', 'N/A')[:100]}")
    print(f"   Result structure: {json.dumps({k: type(v).__name__ for k, v in result.items()}, indent=2)}")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

# List all available methods
print("\n5. Available methods:")
methods = [m for m in dir(compressor) if not m.startswith('_')]
for method in methods[:10]:
    print(f"   - {method}")
