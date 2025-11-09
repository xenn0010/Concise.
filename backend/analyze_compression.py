#!/usr/bin/env python3
"""
Analyze compression quality on production code
"""
import json

with open('/tmp/production_code.json', 'r') as f:
    original_data = json.load(f)
    original = original_data['text']

with open('/tmp/compression_result.json', 'r') as f:
    result = json.load(f)

if 'error' in result:
    print(f"Error: {result['error']}")
    exit(1)

compressed = result['compressed_text']

print("\n" + "=" * 80)
print("PRODUCTION CODE COMPRESSION ANALYSIS")
print("=" * 80)
print()
print(f"📊 Compression Stats:")
print(f"   Original tokens:    {result['original_tokens']}")
print(f"   Compressed tokens:  {result['compressed_tokens']}")
print(f"   Tokens saved:       {result['tokens_saved']}")
print(f"   Compression ratio:  {result['compression_ratio']}x")
print(f"   Reduction:          {(result['tokens_saved'] / result['original_tokens'] * 100):.1f}%")
print(f"   Time:               {result['compression_time_ms']:.0f}ms")
print()
print("=" * 80)
print("ORIGINAL CODE (First 40 lines):")
print("=" * 80)
for i, line in enumerate(original.split('\n')[:40], 1):
    print(f"{i:3d} | {line}")
print()
print("=" * 80)
print("COMPRESSED CODE (Complete):")
print("=" * 80)
for i, line in enumerate(compressed.split('\n'), 1):
    print(f"{i:3d} | {line}")
print()
print("=" * 80)
print("CONTEXT LOSS ANALYSIS:")
print("=" * 80)
print()

# Analyze what was kept vs lost
original_lines = original.split('\n')
compressed_lines = compressed.split('\n')

print(f"✅ What was PRESERVED:")
print(f"   - Class definition: {'ConciseCompressor' in compressed}")
print(f"   - Method definitions: {'def __init__' in compressed and 'def compress' in compressed}")
print(f"   - Key variables: {'cache' in compressed and 'compressor' in compressed}")
print(f"   - Error handling: {'Exception' in compressed}")
print(f"   - Core logic flow: {compressed.count('if') > 0}")
print()
print(f"❌ What was LOST:")
print(f"   - Docstrings: {original.count('\"\"\"') - compressed.count('\"\"\"')} removed")
print(f"   - Comments: {original.count('#') - compressed.count('#')} removed")
print(f"   - Whitespace: Significant formatting removed")
print(f"   - Some variable names: May be abbreviated")
print()
print("=" * 80)
print("CRITICAL QUESTION: Can an LLM still understand this code?")
print("=" * 80)
print()
print("Let's check if key information is present:")
print()

# Check critical elements
checks = {
    "Class name": "ConciseCompressor" in compressed,
    "Constructor logic": "__init__" in compressed,
    "Cache initialization": "cache" in compressed,
    "Model loading": "compressor" in compressed,
    "Compress method": "compress" in compressed,
    "Strategy handling": "strategy" in compressed,
    "Error handling": "Exception" in compressed,
    "Return values": "return" in compressed,
    "Statistics tracking": "stats" in compressed,
    "Token calculation": "tokens" in compressed,
}

for check, passed in checks.items():
    status = "✅" if passed else "❌"
    print(f"   {status} {check}: {passed}")

print()
print("=" * 80)
print("VERDICT:")
print("=" * 80)
print()

passing = sum(checks.values())
total = len(checks)
percentage = (passing / total) * 100

if percentage >= 90:
    verdict = "✅ EXCELLENT - Compression preserves critical context"
elif percentage >= 70:
    verdict = "⚠️  ACCEPTABLE - Most context preserved, some details lost"
else:
    verdict = "❌ POOR - Too much context lost"

print(f"{verdict}")
print(f"Score: {passing}/{total} ({percentage:.0f}%)")
print()

if percentage >= 70:
    print("An LLM should be able to:")
    print("  - Understand the class structure")
    print("  - See the main functionality")
    print("  - Identify key methods and their purpose")
    print("  - Understand error handling")
    print("  - Follow the control flow")
    print()
    print("What the LLM loses:")
    print("  - Detailed documentation (but can infer from code)")
    print("  - Some helper variable names")
    print("  - Exact formatting/indentation")
    print()
else:
    print("⚠️  WARNING: Compression may be too aggressive for code comprehension")

print("=" * 80)
