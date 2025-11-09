"""
Debug Compression - Deep Analysis
Investigates why LLMLingua compression is not working aggressively
"""
import sys
sys.path.insert(0, '/home/yab/Concise/backend')

from app.compressor import ConciseCompressor, CompressorConfig
from llmlingua import PromptCompressor
import json

print("=" * 80)
print("COMPRESSION DEBUG ANALYSIS")
print("=" * 80)
print()

# Test prompt
test_prompt = """You are a helpful customer support agent for TechCorp.

Our product is a cloud-based project management tool that helps teams collaborate on projects. It includes features like task management, file sharing, real-time chat, and analytics dashboards.

Common issues include:
- Login problems
- File upload errors
- Notification settings
- Billing questions
- Integration with third-party tools

Customer question: How do I reset my password?

Please provide a helpful, detailed response."""

print("TEST PROMPT:")
print(test_prompt)
print()
print("=" * 80)
print()

# Show current configuration
print("CURRENT COMPRESSOR CONFIGURATION:")
print()
for strategy_name, strategy_config in CompressorConfig.STRATEGIES.items():
    print(f"{strategy_name.upper()}:")
    print(f"  Target ratio: {strategy_config['ratio']}x")
    print(f"  Quality threshold: {strategy_config['quality_threshold']}")
    print(f"  Description: {strategy_config['description']}")
    print()

print("=" * 80)
print()

# Initialize compressor
print("Initializing compressor...")
compressor = ConciseCompressor()
print()

# Test each strategy
strategies = ["conservative", "balanced", "aggressive", "extreme"]

for strategy in strategies:
    print("=" * 80)
    print(f"TESTING STRATEGY: {strategy.upper()}")
    print("=" * 80)
    print()

    try:
        result = compressor.compress(test_prompt, strategy=strategy, use_cache=False)

        print(f"RESULTS:")
        print(f"  Original tokens:    {result['original_tokens']}")
        print(f"  Compressed tokens:  {result['compressed_tokens']}")
        print(f"  Compression ratio:  {result['compression_ratio']:.2f}x")
        print(f"  Tokens saved:       {result['tokens_saved']}")
        print(f"  Target ratio:       {CompressorConfig.STRATEGIES[strategy]['ratio']}x")
        print()

        print(f"COMPRESSED TEXT:")
        print(f"  {result['compressed_text']}")
        print()

        # Check if it met target
        target_ratio = CompressorConfig.STRATEGIES[strategy]['ratio']
        actual_ratio = result['compression_ratio']

        if actual_ratio < target_ratio * 0.8:  # Within 80% of target
            print(f"WARNING: Did not meet target ratio!")
            print(f"  Expected: {target_ratio}x")
            print(f"  Actual:   {actual_ratio:.2f}x")
            print(f"  Gap:      {target_ratio - actual_ratio:.2f}x")
        else:
            print(f"SUCCESS: Met target ratio")

        print()

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        print()

print("=" * 80)
print()

# Now let's test the raw LLMLingua library directly
print("TESTING RAW LLMLINGUA LIBRARY DIRECTLY")
print("(bypassing ConciseCompressor wrapper)")
print("=" * 80)
print()

print("Initializing raw PromptCompressor...")
raw_compressor = PromptCompressor(model_name="gpt2", device_map="cpu")
print("Done.")
print()

# Test with different rate parameters
compression_rates = [0.9, 0.7, 0.5, 0.3, 0.1]  # Higher = more aggressive

for rate in compression_rates:
    print("-" * 80)
    print(f"Testing with rate={rate} (lower = more compression)")
    print("-" * 80)

    try:
        compressed_result = raw_compressor.compress_prompt(
            test_prompt,
            rate=rate,
            force_tokens=[],  # No protected tokens
            drop_consecutive=True,  # More aggressive
            chunk_end_tokens=None
        )

        compressed_text = compressed_result['compressed_prompt']
        original_tokens = len(compressed_result.get('origin_tokens', []))
        compressed_tokens = len(compressed_result.get('compressed_tokens', []))

        if original_tokens > 0:
            actual_ratio = original_tokens / compressed_tokens if compressed_tokens > 0 else 1.0
        else:
            actual_ratio = 1.0

        print(f"Rate: {rate}")
        print(f"Original tokens: {original_tokens}")
        print(f"Compressed tokens: {compressed_tokens}")
        print(f"Ratio: {actual_ratio:.2f}x")
        print()
        print(f"Compressed text:")
        print(f"{compressed_text}")
        print()

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        print()

print("=" * 80)
print()

# Check the actual compress implementation
print("ANALYZING ConciseCompressor.compress() IMPLEMENTATION")
print("=" * 80)
print()

import inspect
compress_source = inspect.getsource(compressor.compress)
print("Source code:")
print(compress_source)
print()

print("=" * 80)
print("DIAGNOSIS COMPLETE")
print("=" * 80)
print()
print("Summary:")
print("- Checked all compression strategies")
print("- Tested raw LLMLingua with different rates")
print("- Analyzed implementation")
print()
print("Look for:")
print("1. Is the compression ratio matching the target?")
print("2. What rate parameter is being passed to LLMLingua?")
print("3. Are there any force_tokens protecting content?")
print("4. Is the model (gpt2) the right choice?")
