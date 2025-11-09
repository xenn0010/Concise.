"""
REAL Benchmarks - No Mocks, Actual Measurements
Tests actual compression and OpenAI API calls
"""
import sys
import time
import asyncio
from datetime import datetime
import httpx
from openai import OpenAI

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(80)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 80}{Colors.END}\n")

def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}✗ {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.CYAN}→ {text}{Colors.END}")

def print_metric(label, value, unit=""):
    print(f"  {Colors.BOLD}{label}:{Colors.END} {Colors.GREEN}{value}{unit}{Colors.END}")

# Configuration
CONCISE_API_URL = "http://localhost:8000"
CONCISE_API_KEY = "csk_live_o8PHSZvBOMPEaOdOi0kOHfm1c1-6K01STRE4ttUOJGU"
OPENAI_API_KEY = "YOUR_OPENAI_API_KEY_HERE"

# Test prompts - diverse and realistic
TEST_PROMPTS = [
    {
        "name": "Code Explanation",
        "text": "Explain how binary search works with detailed code examples and time complexity analysis. Include edge cases and optimization techniques."
    },
    {
        "name": "Technical Question",
        "text": "What are the key differences between TCP and UDP protocols? Provide examples of when to use each one in real-world applications."
    },
    {
        "name": "Algorithm Request",
        "text": "Write a Python function to implement merge sort. Include detailed comments explaining each step and provide time and space complexity analysis."
    },
    {
        "name": "System Design",
        "text": "Describe the architecture of a scalable microservices-based e-commerce platform. Include database design, API gateway, and caching strategies."
    },
    {
        "name": "Data Structure Question",
        "text": "How does a hash table work internally? Explain collision resolution strategies like chaining and open addressing with concrete examples."
    }
]

async def test_compression(prompt_text, api_key):
    """Test actual compression with real API"""
    async with httpx.AsyncClient() as client:
        start = time.time()

        response = await client.post(
            f"{CONCISE_API_URL}/v1/compress",
            headers={"X-API-Key": api_key},
            json={"text": prompt_text, "level": "auto"},
            timeout=60.0
        )

        elapsed = time.time() - start

        if response.status_code != 200:
            raise Exception(f"Compression failed: {response.text}")

        data = response.json()
        return {
            "original_text": data["original_text"],
            "compressed_text": data["compressed_text"],
            "original_tokens": data["original_tokens"],
            "compressed_tokens": data["compressed_tokens"],
            "tokens_saved": data["tokens_saved"],
            "compression_ratio": data["compression_ratio"],
            "time_ms": elapsed * 1000
        }

async def test_tale_optimization(prompt_text, api_key):
    """Test TALE optimization with real API"""
    async with httpx.AsyncClient() as client:
        start = time.time()

        response = await client.post(
            f"{CONCISE_API_URL}/v1/tale/optimize",
            headers={"X-API-Key": api_key},
            json={"prompt": prompt_text, "strategy": "fixed"},
            timeout=60.0
        )

        elapsed = time.time() - start

        if response.status_code != 200:
            raise Exception(f"TALE failed: {response.text}")

        data = response.json()
        return {
            "original_prompt": data["original_prompt"],
            "optimized_prompt": data["optimized_prompt"],
            "estimated_budget": data["estimated_budget"],
            "time_ms": elapsed * 1000
        }

async def test_openai_call(prompt_text, openai_key, max_tokens=None):
    """Test actual OpenAI API call"""
    client = OpenAI(api_key=openai_key)

    start = time.time()

    completion = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt_text}],
        max_tokens=max_tokens
    )

    elapsed = time.time() - start

    return {
        "response": completion.choices[0].message.content,
        "prompt_tokens": completion.usage.prompt_tokens,
        "completion_tokens": completion.usage.completion_tokens,
        "total_tokens": completion.usage.total_tokens,
        "time_s": elapsed
    }

def calculate_cost(prompt_tokens, completion_tokens, model="gpt-4"):
    """Calculate actual OpenAI API cost"""
    if model == "gpt-4":
        input_price = 0.03 / 1000
        output_price = 0.06 / 1000
    else:  # gpt-3.5-turbo
        input_price = 0.0015 / 1000
        output_price = 0.002 / 1000

    return (prompt_tokens * input_price) + (completion_tokens * output_price)

async def run_full_benchmark(test_with_openai=False):
    """Run complete benchmark suite"""

    print_header("CONCISE SDK v1.1.0 - REAL BENCHMARKS")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Testing {len(TEST_PROMPTS)} prompts")
    print(f"OpenAI Integration: {'ENABLED' if test_with_openai else 'DISABLED (simulation only)'}")
    print()

    all_results = []

    for i, test_case in enumerate(TEST_PROMPTS, 1):
        print_header(f"Test {i}/{len(TEST_PROMPTS)}: {test_case['name']}")
        print_info(f"Prompt: {test_case['text'][:80]}...")
        print()

        try:
            # Step 1: Compress
            print_info("Step 1: Compressing with LLMLingua...")
            compress_result = await test_compression(test_case['text'], CONCISE_API_KEY)

            print_success("Compression complete!")
            print_metric("Original tokens", compress_result['original_tokens'])
            print_metric("Compressed tokens", compress_result['compressed_tokens'])
            print_metric("Tokens saved", compress_result['tokens_saved'])
            print_metric("Compression ratio", f"{compress_result['compression_ratio']:.2f}")
            print_metric("Time", f"{compress_result['time_ms']:.0f}", "ms")
            print_metric("Compressed text", f"\"{compress_result['compressed_text'][:100]}...\"")
            print()

            # Step 2: TALE optimization
            print_info("Step 2: Optimizing output with TALE...")
            tale_result = await test_tale_optimization(compress_result['compressed_text'], CONCISE_API_KEY)

            print_success("TALE optimization complete!")
            print_metric("Estimated output budget", tale_result['estimated_budget'], " tokens")
            print_metric("Time", f"{tale_result['time_ms']:.0f}", "ms")
            print()

            # Step 3: Calculate theoretical savings
            baseline_output = compress_result['original_tokens'] * 5  # Assume 5x output
            optimized_output = tale_result['estimated_budget']

            baseline_cost = calculate_cost(
                compress_result['original_tokens'],
                baseline_output
            )
            optimized_cost = calculate_cost(
                compress_result['compressed_tokens'],
                optimized_output
            )

            print_info("Cost Analysis (Theoretical):")
            print_metric("Baseline cost", f"${baseline_cost:.4f}")
            print_metric("Optimized cost", f"${optimized_cost:.4f}")
            print_metric("Savings", f"${baseline_cost - optimized_cost:.4f}", f" ({((baseline_cost - optimized_cost) / baseline_cost * 100):.1f}%)")
            print()

            # Step 4: Real OpenAI call (optional)
            real_baseline_cost = None
            real_optimized_cost = None
            real_savings = None

            if test_with_openai and OPENAI_API_KEY:
                try:
                    print_info("Step 3: Testing with REAL OpenAI API...")
                    print_info("  3a: Baseline call (no optimization)...")

                    baseline_openai = await test_openai_call(test_case['text'], OPENAI_API_KEY)
                    real_baseline_cost = calculate_cost(
                        baseline_openai['prompt_tokens'],
                        baseline_openai['completion_tokens']
                    )

                    print_success("Baseline call complete!")
                    print_metric("Prompt tokens", baseline_openai['prompt_tokens'])
                    print_metric("Completion tokens", baseline_openai['completion_tokens'])
                    print_metric("Total tokens", baseline_openai['total_tokens'])
                    print_metric("Cost", f"${real_baseline_cost:.4f}")
                    print_metric("Time", f"{baseline_openai['time_s']:.1f}", "s")
                    print()

                    print_info("  3b: Optimized call (with Concise)...")

                    optimized_openai = await test_openai_call(
                        tale_result['optimized_prompt'],
                        OPENAI_API_KEY,
                        max_tokens=tale_result['estimated_budget']
                    )
                    real_optimized_cost = calculate_cost(
                        optimized_openai['prompt_tokens'],
                        optimized_openai['completion_tokens']
                    )

                    print_success("Optimized call complete!")
                    print_metric("Prompt tokens", optimized_openai['prompt_tokens'])
                    print_metric("Completion tokens", optimized_openai['completion_tokens'])
                    print_metric("Total tokens", optimized_openai['total_tokens'])
                    print_metric("Cost", f"${real_optimized_cost:.4f}")
                    print_metric("Time", f"{optimized_openai['time_s']:.1f}", "s")
                    print()

                    real_savings = real_baseline_cost - real_optimized_cost
                    real_savings_pct = (real_savings / real_baseline_cost * 100)

                    print_success(f"REAL Savings: ${real_savings:.4f} ({real_savings_pct:.1f}%)")
                    print()

                except Exception as e:
                    print_error(f"OpenAI test failed: {e}")
                    print()

            all_results.append({
                "name": test_case['name'],
                "compression": compress_result,
                "tale": tale_result,
                "theoretical_baseline_cost": baseline_cost,
                "theoretical_optimized_cost": optimized_cost,
                "theoretical_savings": baseline_cost - optimized_cost,
                "real_baseline_cost": real_baseline_cost,
                "real_optimized_cost": real_optimized_cost,
                "real_savings": real_savings
            })

        except Exception as e:
            print_error(f"Test failed: {e}")
            import traceback
            traceback.print_exc()

    # Summary
    print_header("BENCHMARK SUMMARY")

    total_original_tokens = sum(r['compression']['original_tokens'] for r in all_results)
    total_compressed_tokens = sum(r['compression']['compressed_tokens'] for r in all_results)
    total_tokens_saved = total_original_tokens - total_compressed_tokens
    avg_compression_ratio = sum(r['compression']['compression_ratio'] for r in all_results) / len(all_results)

    total_theoretical_baseline = sum(r['theoretical_baseline_cost'] for r in all_results)
    total_theoretical_optimized = sum(r['theoretical_optimized_cost'] for r in all_results)
    total_theoretical_savings = total_theoretical_baseline - total_theoretical_optimized

    print(f"{Colors.BOLD}Compression Stats:{Colors.END}")
    print_metric("Total prompts tested", len(all_results))
    print_metric("Total original tokens", f"{total_original_tokens:,}")
    print_metric("Total compressed tokens", f"{total_compressed_tokens:,}")
    print_metric("Total tokens saved", f"{total_tokens_saved:,}")
    print_metric("Average compression ratio", f"{avg_compression_ratio:.2f}")
    print()

    print(f"{Colors.BOLD}Cost Analysis (Theoretical):{Colors.END}")
    print_metric("Total baseline cost", f"${total_theoretical_baseline:.4f}")
    print_metric("Total optimized cost", f"${total_theoretical_optimized:.4f}")
    print_metric("Total savings", f"${total_theoretical_savings:.4f}",
                 f" ({(total_theoretical_savings/total_theoretical_baseline*100):.1f}%)")
    print()

    if test_with_openai:
        real_results = [r for r in all_results if r['real_savings'] is not None]
        if real_results:
            total_real_baseline = sum(r['real_baseline_cost'] for r in real_results)
            total_real_optimized = sum(r['real_optimized_cost'] for r in real_results)
            total_real_savings = sum(r['real_savings'] for r in real_results)

            print(f"{Colors.BOLD}Cost Analysis (REAL OpenAI Calls):{Colors.END}")
            print_metric("Prompts with real calls", len(real_results))
            print_metric("Total baseline cost", f"${total_real_baseline:.4f}")
            print_metric("Total optimized cost", f"${total_real_optimized:.4f}")
            print_metric("Total REAL savings", f"${total_real_savings:.4f}",
                        f" ({(total_real_savings/total_real_baseline*100):.1f}%)")
            print()

    # Scaling projections
    print(f"{Colors.BOLD}Scaling Projections (1M calls/month):{Colors.END}")
    scaling_factor = 1_000_000 / len(all_results)
    monthly_baseline = total_theoretical_baseline * scaling_factor
    monthly_optimized = total_theoretical_optimized * scaling_factor
    monthly_savings = monthly_baseline - monthly_optimized

    print_metric("Baseline cost", f"${monthly_baseline:,.2f}", "/month")
    print_metric("Optimized cost", f"${monthly_optimized:,.2f}", "/month")
    print_metric("Monthly savings", f"${monthly_savings:,.2f}")
    print_metric("Yearly savings", f"${monthly_savings * 12:,.2f}")
    print()

    print_success(f"Benchmark complete! Tested {len(all_results)} prompts")

    return all_results

if __name__ == "__main__":
    print()
    print(f"{Colors.YELLOW}{'='*80}{Colors.END}")
    print(f"{Colors.YELLOW}REAL BENCHMARKS - Actual Measurements{Colors.END}")
    print(f"{Colors.YELLOW}{'='*80}{Colors.END}")
    print()

    # Ask user if they want to test with real OpenAI calls
    response = input("Run with REAL OpenAI API calls? This will cost money. (y/N): ").strip().lower()
    test_with_openai = response == 'y'

    if test_with_openai:
        print_info("Will execute REAL OpenAI API calls - this will charge your account!")
        confirm = input("Are you sure? (yes/no): ").strip().lower()
        if confirm != 'yes':
            test_with_openai = False
            print_info("Skipping real OpenAI calls, running theoretical benchmarks only")
    else:
        print_info("Running theoretical benchmarks only (no OpenAI charges)")

    print()

    # Run benchmarks
    results = asyncio.run(run_full_benchmark(test_with_openai=test_with_openai))

    print()
    print_header("BENCHMARK COMPLETE")
    print()
