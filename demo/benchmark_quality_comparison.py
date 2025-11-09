"""
Quality Comparison Benchmark
Compares three approaches with REAL OpenAI API calls:
1. Baseline (no optimization)
2. LLMLingua compression only
3. LLMLingua + TALE (full optimization)

Shows actual output quality and cost differences.
"""
import asyncio
import httpx
from openai import OpenAI
import time
from datetime import datetime

# Colors
class Colors:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    END = '\033[0m'

# Configuration
CONCISE_API_URL = "http://localhost:8000"
CONCISE_API_KEY = "csk_live_o8PHSZvBOMPEaOdOi0kOHfm1c1-6K01STRE4ttUOJGU"
OPENAI_API_KEY = "YOUR_OPENAI_API_KEY_HERE"

# Test cases
TEST_CASES = [
    {
        "name": "Binary Search Explanation",
        "prompt": "Explain how binary search works with code examples and time complexity analysis.",
        "expected_quality": "Should include algorithm explanation, code, and complexity analysis"
    },
    {
        "name": "TCP vs UDP",
        "prompt": "What are the key differences between TCP and UDP protocols? When should you use each?",
        "expected_quality": "Should list differences and use cases"
    },
    {
        "name": "Hash Table Implementation",
        "prompt": "How does a hash table work internally? Explain collision resolution strategies.",
        "expected_quality": "Should explain mechanism and collision handling"
    }
]

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 100}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(100)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 100}{Colors.END}\n")

def print_section(text):
    print(f"\n{Colors.BOLD}{Colors.YELLOW}{text}{Colors.END}\n")

def calculate_cost(prompt_tokens, completion_tokens):
    """GPT-4 pricing"""
    return (prompt_tokens * 0.03 / 1000) + (completion_tokens * 0.06 / 1000)

async def compress_prompt(text):
    """Compress with LLMLingua"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{CONCISE_API_URL}/v1/compress",
            headers={"X-API-Key": CONCISE_API_KEY},
            json={"text": text, "level": "auto"},
            timeout=60.0
        )
        return response.json()

async def optimize_with_tale(text):
    """Optimize with TALE"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{CONCISE_API_URL}/v1/tale/optimize",
            headers={"X-API-Key": CONCISE_API_KEY},
            json={"prompt": text, "strategy": "fixed"},
            timeout=60.0
        )
        return response.json()

def call_openai(prompt, max_tokens=None, temperature=0.7):
    """Call OpenAI GPT-4"""
    client = OpenAI(api_key=OPENAI_API_KEY)

    start = time.time()
    completion = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        temperature=temperature
    )
    elapsed = time.time() - start

    return {
        "response": completion.choices[0].message.content,
        "prompt_tokens": completion.usage.prompt_tokens,
        "completion_tokens": completion.usage.completion_tokens,
        "total_tokens": completion.usage.total_tokens,
        "time_s": elapsed,
        "cost": calculate_cost(
            completion.usage.prompt_tokens,
            completion.usage.completion_tokens
        )
    }

async def run_quality_benchmark():
    """Run quality comparison benchmark"""

    print_header("CONCISE SDK - QUALITY COMPARISON BENCHMARK")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Model: GPT-4")
    print(f"Test Cases: {len(TEST_CASES)}")
    print()

    # Confirm with user
    print(f"{Colors.YELLOW}WARNING: This will make REAL OpenAI API calls and charge your account.{Colors.END}")
    print(f"{Colors.YELLOW}Each test case makes 3 API calls (baseline, compressed, full optimization).{Colors.END}")
    print(f"{Colors.YELLOW}Total calls: {len(TEST_CASES) * 3}{Colors.END}\n")

    response = input("Continue? (yes/no): ").strip().lower()
    if response != "yes":
        print("Benchmark cancelled.")
        return

    print()
    all_results = []

    for i, test_case in enumerate(TEST_CASES, 1):
        print_header(f"Test Case {i}/{len(TEST_CASES)}: {test_case['name']}")
        print(f"{Colors.BOLD}Original Prompt:{Colors.END}")
        print(f"  {test_case['prompt']}")
        print(f"\n{Colors.BOLD}Expected Quality:{Colors.END}")
        print(f"  {test_case['expected_quality']}")
        print()

        # Approach 1: Baseline (no optimization)
        print_section("APPROACH 1: Baseline (No Optimization)")
        print("Calling OpenAI with original prompt...")

        baseline = call_openai(test_case['prompt'])

        print(f"{Colors.GREEN}Response received!{Colors.END}")
        print(f"\n{Colors.BOLD}Baseline Output:{Colors.END}")
        print(f"{baseline['response'][:500]}..." if len(baseline['response']) > 500 else baseline['response'])
        print(f"\n{Colors.BOLD}Metrics:{Colors.END}")
        print(f"  Prompt tokens: {baseline['prompt_tokens']}")
        print(f"  Completion tokens: {baseline['completion_tokens']}")
        print(f"  Total tokens: {baseline['total_tokens']}")
        print(f"  Cost: ${baseline['cost']:.6f}")
        print(f"  Time: {baseline['time_s']:.1f}s")

        # Approach 2: LLMLingua compression only
        print_section("APPROACH 2: LLMLingua Compression Only")
        print("Compressing prompt with LLMLingua...")

        compressed = await compress_prompt(test_case['prompt'])
        compressed_text = compressed['compressed_text']

        print(f"{Colors.GREEN}Compression complete!{Colors.END}")
        print(f"\n{Colors.BOLD}Compressed Prompt:{Colors.END}")
        print(f"  {compressed_text}")
        print(f"\n{Colors.BOLD}Compression Stats:{Colors.END}")
        print(f"  Original tokens: {compressed['original_tokens']}")
        print(f"  Compressed tokens: {compressed['compressed_tokens']}")
        print(f"  Compression ratio: {compressed['compression_ratio']:.2f}")
        print(f"  Tokens saved: {compressed['tokens_saved']}")

        print("\nCalling OpenAI with compressed prompt...")
        compressed_result = call_openai(compressed_text)

        print(f"{Colors.GREEN}Response received!{Colors.END}")
        print(f"\n{Colors.BOLD}Compressed Output:{Colors.END}")
        print(f"{compressed_result['response'][:500]}..." if len(compressed_result['response']) > 500 else compressed_result['response'])
        print(f"\n{Colors.BOLD}Metrics:{Colors.END}")
        print(f"  Prompt tokens: {compressed_result['prompt_tokens']}")
        print(f"  Completion tokens: {compressed_result['completion_tokens']}")
        print(f"  Total tokens: {compressed_result['total_tokens']}")
        print(f"  Cost: ${compressed_result['cost']:.6f}")
        print(f"  Time: {compressed_result['time_s']:.1f}s")
        print(f"\n{Colors.BOLD}Savings vs Baseline:{Colors.END}")
        print(f"  Token savings: {baseline['total_tokens'] - compressed_result['total_tokens']} ({((baseline['total_tokens'] - compressed_result['total_tokens']) / baseline['total_tokens'] * 100):.1f}%)")
        print(f"  Cost savings: ${baseline['cost'] - compressed_result['cost']:.6f} ({((baseline['cost'] - compressed_result['cost']) / baseline['cost'] * 100):.1f}%)")

        # Approach 3: LLMLingua + TALE (full optimization)
        print_section("APPROACH 3: LLMLingua + TALE (Full Optimization)")
        print("Optimizing with TALE...")

        tale_optimized = await optimize_with_tale(compressed_text)
        optimized_prompt = tale_optimized['optimized_prompt']
        budget = tale_optimized['estimated_budget']

        print(f"{Colors.GREEN}TALE optimization complete!{Colors.END}")
        print(f"\n{Colors.BOLD}TALE-Optimized Prompt:{Colors.END}")
        print(f"  {optimized_prompt}")
        print(f"\n{Colors.BOLD}TALE Budget:{Colors.END}")
        print(f"  Estimated tokens: {budget}")
        print(f"  Strategy: {tale_optimized['budget_metadata']['strategy']}")
        print(f"  Reasoning: {tale_optimized['budget_metadata']['reasoning']}")

        print(f"\nCalling OpenAI with optimized prompt (max_tokens={budget})...")
        optimized_result = call_openai(optimized_prompt, max_tokens=budget)

        print(f"{Colors.GREEN}Response received!{Colors.END}")
        print(f"\n{Colors.BOLD}Optimized Output:{Colors.END}")
        print(f"{optimized_result['response'][:500]}..." if len(optimized_result['response']) > 500 else optimized_result['response'])
        print(f"\n{Colors.BOLD}Metrics:{Colors.END}")
        print(f"  Prompt tokens: {optimized_result['prompt_tokens']}")
        print(f"  Completion tokens: {optimized_result['completion_tokens']}")
        print(f"  Total tokens: {optimized_result['total_tokens']}")
        print(f"  Cost: ${optimized_result['cost']:.6f}")
        print(f"  Time: {optimized_result['time_s']:.1f}s")
        print(f"\n{Colors.BOLD}Savings vs Baseline:{Colors.END}")
        print(f"  Token savings: {baseline['total_tokens'] - optimized_result['total_tokens']} ({((baseline['total_tokens'] - optimized_result['total_tokens']) / baseline['total_tokens'] * 100):.1f}%)")
        print(f"  Cost savings: ${baseline['cost'] - optimized_result['cost']:.6f} ({((baseline['cost'] - optimized_result['cost']) / baseline['cost'] * 100):.1f}%)")

        # Compare all three
        print_section("COMPARISON SUMMARY")
        print(f"{Colors.BOLD}Approach               | Tokens | Cost      | vs Baseline{Colors.END}")
        print(f"1. Baseline            | {baseline['total_tokens']:6} | ${baseline['cost']:.6f} | -")
        print(f"2. Compression Only    | {compressed_result['total_tokens']:6} | ${compressed_result['cost']:.6f} | {((baseline['cost'] - compressed_result['cost']) / baseline['cost'] * 100):+.1f}%")
        print(f"3. Full Optimization   | {optimized_result['total_tokens']:6} | ${optimized_result['cost']:.6f} | {((baseline['cost'] - optimized_result['cost']) / baseline['cost'] * 100):+.1f}%")

        all_results.append({
            "test_name": test_case['name'],
            "baseline": baseline,
            "compressed": compressed_result,
            "optimized": optimized_result,
            "compression_data": compressed,
            "tale_data": tale_optimized
        })

        print()
        input(f"{Colors.YELLOW}Press Enter to continue to next test...{Colors.END}")

    # Final summary
    print_header("FINAL SUMMARY")

    total_baseline_cost = sum(r['baseline']['cost'] for r in all_results)
    total_compressed_cost = sum(r['compressed']['cost'] for r in all_results)
    total_optimized_cost = sum(r['optimized']['cost'] for r in all_results)

    total_baseline_tokens = sum(r['baseline']['total_tokens'] for r in all_results)
    total_compressed_tokens = sum(r['compressed']['total_tokens'] for r in all_results)
    total_optimized_tokens = sum(r['optimized']['total_tokens'] for r in all_results)

    print(f"{Colors.BOLD}Total Across {len(all_results)} Test Cases:{Colors.END}\n")
    print(f"{'Approach':<25} | {'Tokens':>8} | {'Cost':>12} | {'Savings':>10}")
    print("-" * 70)
    print(f"{'1. Baseline':<25} | {total_baseline_tokens:>8} | ${total_baseline_cost:>10.6f} | -")
    print(f"{'2. Compression Only':<25} | {total_compressed_tokens:>8} | ${total_compressed_cost:>10.6f} | {((total_baseline_cost - total_compressed_cost) / total_baseline_cost * 100):>9.1f}%")
    print(f"{'3. Full Optimization':<25} | {total_optimized_tokens:>8} | ${total_optimized_cost:>10.6f} | {((total_baseline_cost - total_optimized_cost) / total_baseline_cost * 100):>9.1f}%")

    print(f"\n{Colors.BOLD}Scaling Projections (1M calls/month):{Colors.END}\n")
    scaling = 1_000_000 / len(all_results)

    monthly_baseline = total_baseline_cost * scaling
    monthly_compressed = total_compressed_cost * scaling
    monthly_optimized = total_optimized_cost * scaling

    print(f"{'Approach':<25} | {'Monthly Cost':>15} | {'Yearly Cost':>15} | {'Savings':>15}")
    print("-" * 85)
    print(f"{'1. Baseline':<25} | ${monthly_baseline:>14,.2f} | ${monthly_baseline * 12:>14,.2f} | -")
    print(f"{'2. Compression Only':<25} | ${monthly_compressed:>14,.2f} | ${monthly_compressed * 12:>14,.2f} | ${(monthly_baseline - monthly_compressed) * 12:>14,.2f}")
    print(f"{'3. Full Optimization':<25} | ${monthly_optimized:>14,.2f} | ${monthly_optimized * 12:>14,.2f} | ${(monthly_baseline - monthly_optimized) * 12:>14,.2f}")

    print(f"\n{Colors.GREEN}Benchmark complete!{Colors.END}\n")

    return all_results

if __name__ == "__main__":
    asyncio.run(run_quality_benchmark())
