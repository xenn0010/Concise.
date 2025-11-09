import asyncio
import sys
import httpx
from datetime import datetime

DEMO_API_URL = "http://localhost:3000"
CONCISE_API_URL = "http://localhost:8000"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(60)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.END}\n")

def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}✗ {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.YELLOW}→ {text}{Colors.END}")

async def test_backend_health():
    print_info("Testing Concise backend health...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{CONCISE_API_URL}/health", timeout=5.0)
            if response.status_code == 200:
                print_success("Concise backend is healthy")
                return True
            else:
                print_error(f"Backend returned status {response.status_code}")
                return False
    except Exception as e:
        print_error(f"Backend health check failed: {e}")
        return False

async def test_demo_health():
    print_info("Testing demo API health...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{DEMO_API_URL}/api/health", timeout=5.0)
            data = response.json()
            print_success(f"Demo API is {data['status']}")
            print_info(f"  Backend connected: {data['backend_connected']}")
            print_info(f"  OpenAI configured: {data['openai_configured']}")
            return True
    except Exception as e:
        print_error(f"Demo health check failed: {e}")
        return False

async def test_compression():
    print_info("Testing compression endpoint...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{DEMO_API_URL}/api/compress",
                json={
                    "text": "Explain how binary search works with detailed code examples and time complexity analysis",
                    "level": "auto"
                },
                timeout=30.0
            )
            data = response.json()
            print_success("Compression successful")
            print_info(f"  Original tokens: {data['original_tokens']}")
            print_info(f"  Compressed tokens: {data['compressed_tokens']}")
            print_info(f"  Tokens saved: {data['tokens_saved']}")
            print_info(f"  Compression ratio: {data['compression_ratio']:.2f}")
            print_info(f"  Time: {data['compression_time_ms']:.0f}ms")
            return True
    except Exception as e:
        print_error(f"Compression test failed: {e}")
        return False

async def test_tale_optimization():
    print_info("Testing TALE optimization endpoint...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{DEMO_API_URL}/api/tale/optimize",
                json={
                    "prompt": "Explain how binary search works",
                    "strategy": "fixed"
                },
                timeout=30.0
            )
            data = response.json()
            print_success("TALE optimization successful")
            print_info(f"  Estimated budget: {data['estimated_budget']} tokens")
            print_info(f"  Strategy: {data['budget_metadata']['strategy']}")
            print_info(f"  Confidence: {data['budget_metadata']['confidence'] * 100:.0f}%")
            print_info(f"  Time: {data['optimization_time_ms']:.0f}ms")
            return True
    except Exception as e:
        print_error(f"TALE test failed: {e}")
        return False

async def test_full_optimization():
    print_info("Testing full optimization pipeline...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{DEMO_API_URL}/api/full-optimization",
                json={
                    "prompt": "Write a Python function to implement quicksort with detailed comments",
                    "model": "gpt-4",
                    "compression_level": "auto",
                    "tale_strategy": "fixed",
                    "execute_llm": False
                },
                timeout=60.0
            )
            data = response.json()
            print_success("Full optimization successful")

            print(f"\n{Colors.BOLD}Compression Step:{Colors.END}")
            print_info(f"  Original tokens: {data['compression_step']['original_tokens']}")
            print_info(f"  Compressed tokens: {data['compression_step']['compressed_tokens']}")
            print_info(f"  Saved: {data['compression_step']['tokens_saved']} tokens")
            print_info(f"  Time: {data['compression_step']['time_ms']:.0f}ms")

            print(f"\n{Colors.BOLD}TALE Step:{Colors.END}")
            print_info(f"  Baseline output: {data['tale_step']['baseline_estimated_output']} tokens")
            print_info(f"  Optimized budget: {data['tale_step']['estimated_output_budget']} tokens")
            print_info(f"  Saved: {data['tale_step']['output_tokens_saved']} tokens")
            print_info(f"  Time: {data['tale_step']['time_ms']:.0f}ms")

            print(f"\n{Colors.BOLD}Cost Analysis:{Colors.END}")
            print_info(f"  Baseline cost: ${data['cost_analysis']['baseline']['total_cost']:.4f}")
            print_info(f"  Optimized cost: ${data['cost_analysis']['optimized']['total_cost']:.4f}")
            print_info(f"  {Colors.GREEN}Saved: ${data['cost_analysis']['savings']['cost_saved']:.4f} ({data['cost_analysis']['savings']['savings_percentage']:.1f}%){Colors.END}")

            return True
    except Exception as e:
        print_error(f"Full optimization test failed: {e}")
        return False

async def test_benchmark():
    print_info("Testing benchmark suite...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{DEMO_API_URL}/api/benchmark",
                json={
                    "prompts": [
                        "Explain recursion with examples",
                        "What is object-oriented programming?",
                        "How does a hash table work?"
                    ],
                    "model": "gpt-4"
                },
                timeout=120.0
            )
            data = response.json()
            print_success("Benchmark completed")
            print_info(f"  Total prompts: {data['summary']['total_prompts']}")
            print_info(f"  Avg compression: {data['summary']['avg_compression_ratio']:.2f}")
            print_info(f"  Avg savings: {data['summary']['avg_cost_savings_percentage']:.1f}%")
            print_info(f"  Total saved: ${data['summary']['total_cost_saved_usd']:.4f}")
            print_info(f"  Avg time: {data['summary']['avg_processing_time_ms']:.0f}ms")
            return True
    except Exception as e:
        print_error(f"Benchmark test failed: {e}")
        return False

async def run_comprehensive_benchmark():
    print_header("COMPREHENSIVE PERFORMANCE BENCHMARK")

    test_prompts = [
        "Explain how binary search works with code examples",
        "What are the SOLID principles in software engineering?",
        "Describe the difference between TCP and UDP",
        "How does gradient descent work in machine learning?",
        "Write a function to reverse a linked list in Python",
        "Explain the concept of closures in JavaScript",
        "What is database normalization and why is it important?",
        "Describe how REST APIs work",
        "What are design patterns? Give examples.",
        "Explain Big O notation with examples"
    ]

    results = []
    total_baseline_cost = 0
    total_optimized_cost = 0
    total_tokens_saved = 0

    print(f"Testing {len(test_prompts)} prompts...\n")

    async with httpx.AsyncClient() as client:
        for i, prompt in enumerate(test_prompts, 1):
            print(f"[{i}/{len(test_prompts)}] {prompt[:50]}...")
            try:
                response = await client.post(
                    f"{DEMO_API_URL}/api/full-optimization",
                    json={
                        "prompt": prompt,
                        "model": "gpt-4",
                        "compression_level": "auto",
                        "tale_strategy": "fixed",
                        "execute_llm": False
                    },
                    timeout=60.0
                )
                data = response.json()

                baseline_cost = data['cost_analysis']['baseline']['total_cost']
                optimized_cost = data['cost_analysis']['optimized']['total_cost']
                tokens_saved = data['cost_analysis']['savings']['total_tokens_saved']

                total_baseline_cost += baseline_cost
                total_optimized_cost += optimized_cost
                total_tokens_saved += tokens_saved

                results.append({
                    'prompt': prompt,
                    'savings_pct': data['cost_analysis']['savings']['savings_percentage'],
                    'cost_saved': data['cost_analysis']['savings']['cost_saved'],
                    'tokens_saved': tokens_saved
                })

                print_success(f"  {data['cost_analysis']['savings']['savings_percentage']:.1f}% savings, ${data['cost_analysis']['savings']['cost_saved']:.4f} saved")

            except Exception as e:
                print_error(f"  Failed: {e}")

    print_header("BENCHMARK RESULTS SUMMARY")

    avg_savings_pct = ((total_baseline_cost - total_optimized_cost) / total_baseline_cost) * 100

    print(f"{Colors.BOLD}Total Prompts:{Colors.END} {len(test_prompts)}")
    print(f"{Colors.BOLD}Baseline Cost:{Colors.END} ${total_baseline_cost:.4f}")
    print(f"{Colors.BOLD}Optimized Cost:{Colors.END} ${total_optimized_cost:.4f}")
    print(f"{Colors.BOLD}{Colors.GREEN}Total Saved:{Colors.END} ${total_baseline_cost - total_optimized_cost:.4f} ({avg_savings_pct:.1f}%){Colors.END}")
    print(f"{Colors.BOLD}Total Tokens Saved:{Colors.END} {total_tokens_saved:,}")

    print(f"\n{Colors.BOLD}At scale (1M API calls/month):{Colors.END}")
    monthly_baseline = total_baseline_cost * (1_000_000 / len(test_prompts))
    monthly_optimized = total_optimized_cost * (1_000_000 / len(test_prompts))
    monthly_savings = monthly_baseline - monthly_optimized
    print(f"  Baseline: ${monthly_baseline:,.2f}/month")
    print(f"  Optimized: ${monthly_optimized:,.2f}/month")
    print(f"  {Colors.GREEN}Monthly Savings: ${monthly_savings:,.2f}{Colors.END}")
    print(f"  {Colors.GREEN}Yearly Savings: ${monthly_savings * 12:,.2f}{Colors.END}")

async def main():
    print_header(f"CONCISE SDK v1.1.0 - DEMO TEST SUITE")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    tests = [
        ("Backend Health", test_backend_health),
        ("Demo API Health", test_demo_health),
        ("Compression", test_compression),
        ("TALE Optimization", test_tale_optimization),
        ("Full Optimization", test_full_optimization),
        ("Benchmark Suite", test_benchmark),
    ]

    results = []

    for test_name, test_func in tests:
        print_header(test_name)
        try:
            success = await test_func()
            results.append((test_name, success))
        except Exception as e:
            print_error(f"Test crashed: {e}")
            results.append((test_name, False))

    await run_comprehensive_benchmark()

    print_header("TEST RESULTS SUMMARY")

    passed = sum(1 for _, success in results if success)
    total = len(results)

    for test_name, success in results:
        if success:
            print_success(f"{test_name}")
        else:
            print_error(f"{test_name}")

    print(f"\n{Colors.BOLD}Total: {passed}/{total} tests passed{Colors.END}")

    if passed == total:
        print(f"\n{Colors.GREEN}{Colors.BOLD}ALL TESTS PASSED! System is production-ready.{Colors.END}")
        return 0
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}Some tests failed. Please review.{Colors.END}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
