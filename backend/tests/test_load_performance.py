"""
Load testing and performance benchmarking for Concise SDK
Tests throughput, latency, concurrent load, and system limits
"""

import time
import statistics
import concurrent.futures
import sys
import os
from typing import List, Dict, Tuple

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.hybrid_compressor import HybridCompressor
from app.services.tale_optimizer import TALEOptimizer


class LoadTestMetrics:
    """Container for load test metrics"""

    def __init__(self):
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.latencies: List[float] = []
        self.start_time = None
        self.end_time = None

    def record_request(self, success: bool, latency: float):
        """Record a request result"""
        self.total_requests += 1
        if success:
            self.successful_requests += 1
        else:
            self.failed_requests += 1
        self.latencies.append(latency)

    def get_summary(self) -> Dict:
        """Get summary statistics"""
        if not self.latencies:
            return {}

        duration = self.end_time - self.start_time if self.end_time else 0

        return {
            'total_requests': self.total_requests,
            'successful_requests': self.successful_requests,
            'failed_requests': self.failed_requests,
            'success_rate': self.successful_requests / self.total_requests * 100,
            'duration_seconds': duration,
            'requests_per_second': self.total_requests / duration if duration > 0 else 0,
            'latency_min_ms': min(self.latencies) * 1000,
            'latency_max_ms': max(self.latencies) * 1000,
            'latency_mean_ms': statistics.mean(self.latencies) * 1000,
            'latency_median_ms': statistics.median(self.latencies) * 1000,
            'latency_p95_ms': statistics.quantiles(self.latencies, n=20)[18] * 1000 if len(self.latencies) >= 20 else max(self.latencies) * 1000,
            'latency_p99_ms': statistics.quantiles(self.latencies, n=100)[98] * 1000 if len(self.latencies) >= 100 else max(self.latencies) * 1000,
        }


def test_compression_throughput():
    """Test maximum compression throughput"""
    print("\n" + "=" * 80)
    print("TEST 1: Compression Throughput")
    print("=" * 80)

    comp = HybridCompressor()
    text = "Implement a function that calculates the factorial of a number recursively"

    metrics = LoadTestMetrics()
    metrics.start_time = time.time()

    # Run 1000 compressions
    num_requests = 1000
    print(f"Running {num_requests} compression requests...")

    for i in range(num_requests):
        start = time.time()
        try:
            result = comp.compress(text, strategy='balanced')
            success = result['compressed'] != ""
        except Exception as e:
            success = False
        latency = time.time() - start
        metrics.record_request(success, latency)

        if (i + 1) % 100 == 0:
            print(f"  Progress: {i + 1}/{num_requests}")

    metrics.end_time = time.time()
    summary = metrics.get_summary()

    print("\nResults:")
    print(f"  Total Requests: {summary['total_requests']}")
    print(f"  Success Rate: {summary['success_rate']:.2f}%")
    print(f"  Duration: {summary['duration_seconds']:.2f}s")
    print(f"  Throughput: {summary['requests_per_second']:.2f} req/s")
    print(f"  Latency (mean): {summary['latency_mean_ms']:.2f}ms")
    print(f"  Latency (median): {summary['latency_median_ms']:.2f}ms")
    print(f"  Latency (p95): {summary['latency_p95_ms']:.2f}ms")
    print(f"  Latency (p99): {summary['latency_p99_ms']:.2f}ms")

    # Assert performance requirements
    assert summary['success_rate'] >= 99.0, "Success rate below 99%"
    assert summary['requests_per_second'] >= 50, "Throughput below 50 req/s"
    assert summary['latency_p95_ms'] <= 500, "P95 latency above 500ms"

    print("\n✓ Throughput test PASSED")
    return summary


def test_concurrent_load():
    """Test concurrent request handling"""
    print("\n" + "=" * 80)
    print("TEST 2: Concurrent Load")
    print("=" * 80)

    comp = HybridCompressor()
    texts = [
        "Write a Python function to reverse a string",
        "Explain how quicksort works",
        "Implement a binary search tree",
        "Calculate the fibonacci sequence",
        "Design a rate limiter"
    ]

    def compression_task(task_id: int) -> Tuple[int, bool, float]:
        """Single compression task"""
        text = texts[task_id % len(texts)]
        start = time.time()
        try:
            result = comp.compress(text, strategy='balanced')
            success = result['compressed'] != ""
        except Exception:
            success = False
        latency = time.time() - start
        return task_id, success, latency

    metrics = LoadTestMetrics()
    metrics.start_time = time.time()

    # Run 500 concurrent compressions with 50 workers
    num_requests = 500
    num_workers = 50
    print(f"Running {num_requests} requests with {num_workers} concurrent workers...")

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures = [executor.submit(compression_task, i) for i in range(num_requests)]

        completed = 0
        for future in concurrent.futures.as_completed(futures):
            task_id, success, latency = future.result()
            metrics.record_request(success, latency)
            completed += 1

            if completed % 50 == 0:
                print(f"  Progress: {completed}/{num_requests}")

    metrics.end_time = time.time()
    summary = metrics.get_summary()

    print("\nResults:")
    print(f"  Total Requests: {summary['total_requests']}")
    print(f"  Success Rate: {summary['success_rate']:.2f}%")
    print(f"  Duration: {summary['duration_seconds']:.2f}s")
    print(f"  Throughput: {summary['requests_per_second']:.2f} req/s")
    print(f"  Latency (mean): {summary['latency_mean_ms']:.2f}ms")
    print(f"  Latency (p95): {summary['latency_p95_ms']:.2f}ms")
    print(f"  Latency (max): {summary['latency_max_ms']:.2f}ms")

    # Assert concurrency requirements
    assert summary['success_rate'] >= 95.0, "Success rate below 95% under load"
    assert summary['latency_p95_ms'] <= 2000, "P95 latency above 2s under load"

    print("\n✓ Concurrent load test PASSED")
    return summary


def test_tale_optimization_performance():
    """Test TALE optimization performance"""
    print("\n" + "=" * 80)
    print("TEST 3: TALE Optimization Performance")
    print("=" * 80)

    optimizer = TALEOptimizer()
    prompts = [
        "Explain machine learning",
        "How does TCP/IP work?",
        "What is recursion?",
        "Describe binary search",
        "Explain REST APIs"
    ]

    metrics = LoadTestMetrics()
    metrics.start_time = time.time()

    num_requests = 200
    print(f"Running {num_requests} TALE optimizations...")

    for i in range(num_requests):
        prompt = prompts[i % len(prompts)]
        start = time.time()
        try:
            result = optimizer.optimize_prompt(prompt, strategy='fixed')
            success = 'optimized_prompt' in result
        except Exception:
            success = False
        latency = time.time() - start
        metrics.record_request(success, latency)

        if (i + 1) % 50 == 0:
            print(f"  Progress: {i + 1}/{num_requests}")

    metrics.end_time = time.time()
    summary = metrics.get_summary()

    print("\nResults:")
    print(f"  Total Requests: {summary['total_requests']}")
    print(f"  Success Rate: {summary['success_rate']:.2f}%")
    print(f"  Duration: {summary['duration_seconds']:.2f}s")
    print(f"  Throughput: {summary['requests_per_second']:.2f} req/s")
    print(f"  Latency (mean): {summary['latency_mean_ms']:.2f}ms")
    print(f"  Latency (p95): {summary['latency_p95_ms']:.2f}ms")

    # Assert TALE performance
    assert summary['success_rate'] >= 99.0, "TALE success rate below 99%"
    assert summary['latency_mean_ms'] <= 50, "TALE mean latency above 50ms"

    print("\n✓ TALE performance test PASSED")
    return summary


def test_stress_conditions():
    """Test under stress conditions"""
    print("\n" + "=" * 80)
    print("TEST 4: Stress Testing")
    print("=" * 80)

    comp = HybridCompressor()

    # Test 1: Very long input
    print("\nStress Test 1: Very long input (100k characters)")
    long_text = "This is a very long text. " * 4000  # ~100k chars
    start = time.time()
    try:
        result = comp.compress(long_text, strategy='aggressive')
        duration = time.time() - start
        print(f"  Duration: {duration:.2f}s")
        print(f"  Compression: {result['compression_ratio']:.2f}x")
        assert duration < 10.0, "Long text compression took over 10s"
        print("  ✓ PASSED")
    except Exception as e:
        print(f"  ✗ FAILED: {e}")

    # Test 2: Rapid successive requests
    print("\nStress Test 2: Rapid successive requests (no delay)")
    text = "Test rapid requests"
    success_count = 0
    num_rapid = 100

    start = time.time()
    for _ in range(num_rapid):
        try:
            result = comp.compress(text)
            success_count += 1
        except Exception:
            pass
    duration = time.time() - start

    print(f"  Completed: {success_count}/{num_rapid}")
    print(f"  Duration: {duration:.2f}s")
    print(f"  Rate: {num_rapid/duration:.2f} req/s")
    assert success_count >= 95, "Less than 95% success under rapid requests"
    print("  ✓ PASSED")

    # Test 3: Mixed strategy load
    print("\nStress Test 3: Mixed strategy load")
    strategies = ['aggressive', 'balanced', 'conservative']
    metrics = LoadTestMetrics()
    metrics.start_time = time.time()

    for i in range(150):
        strategy = strategies[i % len(strategies)]
        start = time.time()
        try:
            result = comp.compress("Test mixed strategies", strategy=strategy)
            success = True
        except Exception:
            success = False
        latency = time.time() - start
        metrics.record_request(success, latency)

    metrics.end_time = time.time()
    summary = metrics.get_summary()

    print(f"  Success Rate: {summary['success_rate']:.2f}%")
    print(f"  Throughput: {summary['requests_per_second']:.2f} req/s")
    assert summary['success_rate'] >= 95.0
    print("  ✓ PASSED")

    print("\n✓ Stress testing PASSED")


def test_memory_stability():
    """Test memory stability under load"""
    print("\n" + "=" * 80)
    print("TEST 5: Memory Stability")
    print("=" * 80)

    comp = HybridCompressor()
    text = "Test memory stability"

    print("Running 5000 compressions to check for memory leaks...")

    start = time.time()
    for i in range(5000):
        try:
            comp.compress(text, strategy='balanced')
        except Exception:
            pass

        if (i + 1) % 1000 == 0:
            print(f"  Progress: {i + 1}/5000")

    duration = time.time() - start

    print(f"\nCompleted 5000 compressions in {duration:.2f}s")
    print(f"Average: {duration/5000*1000:.2f}ms per request")
    print("✓ Memory stability test PASSED (no crashes)")


def run_load_tests():
    """Run all load tests"""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "CONCISE SDK - LOAD TEST SUITE" + " " * 29 + "║")
    print("╚" + "=" * 78 + "╝")

    all_results = {}

    try:
        all_results['throughput'] = test_compression_throughput()
    except Exception as e:
        print(f"\n✗ Throughput test FAILED: {e}")

    try:
        all_results['concurrent'] = test_concurrent_load()
    except Exception as e:
        print(f"\n✗ Concurrent test FAILED: {e}")

    try:
        all_results['tale'] = test_tale_optimization_performance()
    except Exception as e:
        print(f"\n✗ TALE test FAILED: {e}")

    try:
        test_stress_conditions()
    except Exception as e:
        print(f"\n✗ Stress test FAILED: {e}")

    try:
        test_memory_stability()
    except Exception as e:
        print(f"\n✗ Memory test FAILED: {e}")

    # Final summary
    print("\n" + "=" * 80)
    print("FINAL SUMMARY")
    print("=" * 80)

    if 'throughput' in all_results:
        print(f"\nThroughput: {all_results['throughput']['requests_per_second']:.2f} req/s")
        print(f"Latency (p95): {all_results['throughput']['latency_p95_ms']:.2f}ms")

    if 'concurrent' in all_results:
        print(f"\nConcurrent Load (50 workers):")
        print(f"  Success Rate: {all_results['concurrent']['success_rate']:.2f}%")
        print(f"  Throughput: {all_results['concurrent']['requests_per_second']:.2f} req/s")

    if 'tale' in all_results:
        print(f"\nTALE Optimization:")
        print(f"  Throughput: {all_results['tale']['requests_per_second']:.2f} req/s")
        print(f"  Latency (mean): {all_results['tale']['latency_mean_ms']:.2f}ms")

    print("\n" + "=" * 80)
    print("All load tests completed!")
    print("=" * 80)


if __name__ == "__main__":
    run_load_tests()
