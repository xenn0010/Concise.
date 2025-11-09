#!/bin/bash

API_KEY="csk_live_ZT6qVvmFTEEE7ZvZrwcfMJ3e3UHzFuLY0lmGk8tQjQ4"

echo ""
echo "========================================================================"
echo "PRODUCTION CODE COMPRESSION: STRATEGY COMPARISON"
echo "========================================================================"
echo ""

# Test conservative
echo "Testing CONSERVATIVE strategy (3x compression, 95% quality)..."
curl -s -X POST http://localhost:8000/v1/compress \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d @/tmp/production_code_conservative.json > /tmp/result_conservative.json

if [ -f /tmp/result_conservative.json ]; then
    python3 << 'PYTHON'
import json

with open('/tmp/result_conservative.json') as f:
    data = json.load(f)

if 'error' in data:
    print(f"❌ Error: {data['error']['message']}")
else:
    print(f"\n✅ CONSERVATIVE Strategy Results:")
    print(f"   Original:    {data['original_tokens']} tokens")
    print(f"   Compressed:  {data['compressed_tokens']} tokens")
    print(f"   Saved:       {data['tokens_saved']} ({data['tokens_saved']/data['original_tokens']*100:.1f}% reduction)")
    print(f"   Ratio:       {data['compression_ratio']}x")
    print(f"   Time:        {data['compression_time_ms']:.0f}ms")
    print()
    print(f"First 30 lines of compressed code:")
    for i, line in enumerate(data['compressed_text'].split('\n')[:30], 1):
        print(f"   {i:2d} | {line[:70]}")
PYTHON
fi

echo ""
echo "------------------------------------------------------------------------"
echo ""

# Test balanced (we already have this result)
echo "Comparing with BALANCED strategy (5x compression, 90% quality)..."
python3 << 'PYTHON'
import json

with open('/tmp/compression_result.json') as f:
    data = json.load(f)

if 'error' in data:
    print(f"❌ Error: {data['error']['message']}")
else:
    print(f"\n⚡ BALANCED Strategy Results:")
    print(f"   Original:    {data['original_tokens']} tokens")
    print(f"   Compressed:  {data['compressed_tokens']} tokens")
    print(f"   Saved:       {data['tokens_saved']} ({data['tokens_saved']/data['original_tokens']*100:.1f}% reduction)")
    print(f"   Ratio:       {data['compression_ratio']}x")
    print(f"   Time:        {data['compression_time_ms']:.0f}ms")
    print()
    print(f"First 30 lines of compressed code:")
    for i, line in enumerate(data['compressed_text'].split('\n')[:30], 1):
        print(f"   {i:2d} | {line[:70]}")
PYTHON

echo ""
echo "========================================================================"
echo "VERDICT:"
echo "========================================================================"
echo ""

python3 << 'PYTHON'
import json

with open('/tmp/result_conservative.json') as f:
    conservative = json.load(f)

with open('/tmp/compression_result.json') as f:
    balanced = json.load(f)

if 'error' not in conservative and 'error' not in balanced:
    print("📊 Comparison:")
    print()
    print("                    Conservative    Balanced")
    print("   -----------------------------------------------")
    print(f"   Compression:     {conservative['compression_ratio']}x            {balanced['compression_ratio']}x")
    print(f"   Tokens saved:    {conservative['tokens_saved']}            {balanced['tokens_saved']}")
    print(f"   % reduction:     {conservative['tokens_saved']/conservative['original_tokens']*100:.1f}%           {balanced['tokens_saved']/balanced['original_tokens']*100:.1f}%")
    print()

    # Check readability
    cons_code = conservative['compressed_text']
    bal_code = balanced['compressed_text']

    print("🔍 Code Quality Assessment:")
    print()
    print("   Conservative:")
    has_class = "class ConciseCompressor:" in cons_code
    has_methods = "def __init__" in cons_code and "def compress" in cons_code
    has_indent = cons_code.count('    ') > 10
    print(f"      Class definition:  {'✅' if has_class else '❌'}")
    print(f"      Method signatures: {'✅' if has_methods else '❌'}")
    print(f"      Indentation:       {'✅' if has_indent else '❌'}")

    cons_score = sum([has_class, has_methods, has_indent])

    print()
    print("   Balanced:")
    has_class = "class ConciseCompressor:" in bal_code
    has_methods = "def __init__" in bal_code and "def compress" in bal_code
    has_indent = bal_code.count('    ') > 10
    print(f"      Class definition:  {'✅' if has_class else '❌'}")
    print(f"      Method signatures: {'✅' if has_methods else '❌'}")
    print(f"      Indentation:       {'✅' if has_indent else '❌'}")

    bal_score = sum([has_class, has_methods, has_indent])

    print()
    print("=" * 72)
    print("📌 RECOMMENDATION:")
    print("=" * 72)
    print()
    if cons_score >= 2:
        print("✅ Use CONSERVATIVE for production code context")
        print("   - Preserves code structure")
        print("   - LLM can understand and modify code")
        print(f"   - Still saves {conservative['tokens_saved']/conservative['original_tokens']*100:.0f}% of tokens")
    else:
        print("⚠️  Both strategies lose too much context")
        print("   - Consider sending uncompressed code")
        print("   - Or use compression only for documentation/comments")

    print()
    if bal_score < 2:
        print("❌ AVOID BALANCED for production code")
        print("   - Too much information loss")
        print("   - Code structure becomes unclear")
        print("   - LLM will struggle to understand context")

    print()
    print("=" * 72)
PYTHON

echo ""
