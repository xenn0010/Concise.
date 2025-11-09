#!/usr/bin/env python3
"""
Test to see how tokenization handles spaces
"""
from transformers import AutoTokenizer

# Load the same tokenizer our compressor uses
tokenizer = AutoTokenizer.from_pretrained("gpt2")

# Test strings
tests = [
    "hello",
    "hello world",
    "hello   world",  # Multiple spaces
    "   hello",       # Leading spaces
    "hello   ",       # Trailing spaces
]

print("=" * 60)
print("Tokenization Analysis - How Spaces Are Handled")
print("=" * 60)

for text in tests:
    tokens = tokenizer.encode(text)
    decoded_tokens = [tokenizer.decode([t]) for t in tokens]

    print(f"\nText: {repr(text)}")
    print(f"  Token count: {len(tokens)}")
    print(f"  Tokens: {decoded_tokens}")
    print(f"  Token IDs: {tokens}")

print("\n" + "=" * 60)
print("Key Findings:")
print("=" * 60)
print()
print("1. Spaces are PART of tokens, not separate tokens")
print("2. ' world' (with space) is ONE token, not two")
print("3. Multiple consecutive spaces may create extra tokens")
print("4. Leading/trailing spaces are tokenized")
print()
print("Example: 'hello world'")
tokens = tokenizer.encode("hello world")
print(f"  Tokens: {[tokenizer.decode([t]) for t in tokens]}")
print(f"  Count: {len(tokens)} tokens (not 3!)")
print()
print("So when we say '72 tokens', we're counting words+spaces")
print("as tokenized by GPT-2, not as separate entities.")
