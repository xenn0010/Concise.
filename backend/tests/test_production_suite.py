"""
Production-grade test suite for Concise SDK
Industry standard tests: Unit, Integration, E2E, Security, Performance
"""

import pytest
import time
import asyncio
import concurrent.futures
from typing import List, Dict, Any
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.hybrid_compressor import HybridCompressor
from app.smart_compressor import SmartCompressor
from app.compressor import ConciseCompressor
from app.services.tale_optimizer import TALEOptimizer, EstimationStrategy


class TestUnitCompression:
    """Unit tests for compression algorithms"""

    def test_simple_compressor_basic(self):
        """Test simple compressor with basic input"""
        comp = ConciseCompressor()
        text = "This is a test. This is only a test."
        result = comp.compress(text)

        assert result['compressed'] != ""
        assert result['original_tokens'] > 0
        assert result['compressed_tokens'] >= 0
        assert result['compression_ratio'] >= 1.0

    def test_smart_compressor_basic(self):
        """Test smart compressor with basic input"""
        comp = SmartCompressor()
        text = "def calculate_sum(numbers): return sum(numbers)"
        result = comp.compress(text)

        assert result['compressed'] != ""
        assert 'calculate_sum' in result['compressed'] or 'sum' in result['compressed']
        assert result['compression_ratio'] >= 1.0

    def test_hybrid_compressor_basic(self):
        """Test hybrid compressor with basic input"""
        comp = HybridCompressor()
        text = "Implement a function that calculates the factorial of a number"
        result = comp.compress(text, strategy='balanced')

        assert result['compressed'] != ""
        assert result['original_tokens'] > 0
        assert result['compression_ratio'] >= 1.0

    def test_empty_input_handling(self):
        """Test all compressors handle empty input gracefully"""
        compressors = [ConciseCompressor(), SmartCompressor(), HybridCompressor()]

        for comp in compressors:
            result = comp.compress("")
            assert result['compressed'] == ""
            assert result['original_tokens'] == 0
            assert result['compressed_tokens'] == 0

    def test_none_input_handling(self):
        """Test all compressors handle None input"""
        compressors = [ConciseCompressor(), SmartCompressor(), HybridCompressor()]

        for comp in compressors:
            with pytest.raises((ValueError, TypeError, AttributeError)):
                comp.compress(None)

    def test_special_characters(self):
        """Test compression with special characters"""
        comp = HybridCompressor()
        text = "Test with special chars: @#$%^&*(){}[]<>?/\\|"
        result = comp.compress(text)

        assert result['compressed'] != ""
        assert result['compressed_tokens'] >= 0

    def test_unicode_handling(self):
        """Test compression with unicode characters"""
        comp = HybridCompressor()
        texts = [
            "Hello 世界",  # Chinese
            "Привет мир",  # Russian
            "مرحبا بالعالم",  # Arabic
            "שלום עולם"  # Hebrew
        ]

        for text in texts:
            result = comp.compress(text)
            assert result['compressed'] != ""
            assert result['compressed_tokens'] >= 0

    def test_large_input_handling(self):
        """Test compression with very large input (50k tokens)"""
        comp = HybridCompressor()
        # Generate ~50k tokens worth of text
        text = "This is a long sentence that will be repeated many times. " * 2000

        result = comp.compress(text, strategy='aggressive')
        assert result['compressed'] != ""
        assert result['original_tokens'] > 10000  # Should be large
        assert result['compression_ratio'] > 1.0  # Should compress

    def test_compression_strategies(self):
        """Test all hybrid compressor strategies"""
        comp = HybridCompressor()
        text = "Implement a binary search algorithm in Python with proper error handling"

        strategies = ['aggressive', 'balanced', 'conservative']
        results = []

        for strategy in strategies:
            result = comp.compress(text, strategy=strategy)
            results.append(result)
            assert result['compressed'] != ""
            assert result['strategy'] == strategy

        # Aggressive should compress most
        assert results[0]['compression_ratio'] >= results[1]['compression_ratio']
        assert results[1]['compression_ratio'] >= results[2]['compression_ratio']


class TestIntegrationWorkflows:
    """Integration tests for complete workflows"""

    def test_compression_pipeline(self):
        """Test complete compression pipeline"""
        comp = HybridCompressor()

        # Step 1: Original prompt
        prompt = "Write a Python function to check if a string is a palindrome"

        # Step 2: Compress
        result = comp.compress(prompt, strategy='balanced')

        # Step 3: Verify
        assert result['compressed'] != ""
        assert result['original_tokens'] > 0
        assert 'compression_ratio' in result
        assert 'strategy' in result

    def test_tale_optimization_workflow(self):
        """Test TALE optimization workflow"""
        optimizer = TALEOptimizer()

        # Step 1: Optimize prompt
        prompt = "Explain how merge sort works"
        result = optimizer.optimize_prompt(
            prompt=prompt,
            strategy="fixed"
        )

        # Step 2: Verify structure
        assert 'optimized_prompt' in result
        assert 'estimated_budget' in result
        assert result['estimated_budget'] > 0
        assert prompt in result['optimized_prompt']

    def test_tale_validation_workflow(self):
        """Test TALE validation workflow"""
        optimizer = TALEOptimizer()

        # Validate output against budget
        output = "Merge sort is a divide-and-conquer algorithm that splits..."
        result = optimizer.validate_output(
            output=output,
            budget=100,
            tolerance=0.2
        )

        assert 'within_budget' in result
        assert 'actual_tokens' in result
        assert 'budget_utilization' in result
        assert result['actual_tokens'] > 0


class TestPerformance:
    """Performance and load tests"""

    def test_compression_speed(self):
        """Test compression completes within acceptable time"""
        comp = HybridCompressor()
        text = "Test performance of compression algorithm"

        start = time.time()
        result = comp.compress(text)
        duration = time.time() - start

        # Should complete in under 2 seconds for short text
        assert duration < 2.0
        assert result['compressed'] != ""

    def test_batch_compression_performance(self):
        """Test batch compression performance"""
        comp = HybridCompressor()
        texts = [
            f"Test prompt number {i} with various content"
            for i in range(100)
        ]

        start = time.time()
        results = [comp.compress(text) for text in texts]
        duration = time.time() - start

        # 100 compressions should complete in under 30 seconds
        assert duration < 30.0
        assert len(results) == 100
        assert all(r['compressed'] != "" for r in results)

    def test_concurrent_compression(self):
        """Test concurrent compression handling"""
        comp = HybridCompressor()
        text = "Test concurrent compression handling"

        def compress_task():
            return comp.compress(text)

        # Run 20 compressions concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(compress_task) for _ in range(20)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        assert len(results) == 20
        assert all(r['compressed'] != "" for r in results)


class TestErrorHandling:
    """Error handling and edge cases"""

    def test_invalid_strategy(self):
        """Test handling of invalid compression strategy"""
        comp = HybridCompressor()
        text = "Test invalid strategy"

        # Should default to 'balanced' or raise ValueError
        try:
            result = comp.compress(text, strategy='invalid_strategy')
            # If it doesn't raise, it should use a fallback
            assert result['strategy'] in ['aggressive', 'balanced', 'conservative']
        except (ValueError, KeyError):
            # Expected if strict validation
            pass

    def test_non_string_input(self):
        """Test handling of non-string input"""
        comp = HybridCompressor()

        invalid_inputs = [123, 45.67, ['list'], {'dict': 'value'}, True]

        for invalid_input in invalid_inputs:
            with pytest.raises((TypeError, AttributeError, ValueError)):
                comp.compress(invalid_input)

    def test_tale_invalid_budget(self):
        """Test TALE with invalid budget"""
        optimizer = TALEOptimizer()

        # Negative budget
        with pytest.raises((ValueError, AssertionError)):
            optimizer.optimize_prompt(
                prompt="Test",
                strategy="fixed",
                target_budget=-100
            )

    def test_tale_invalid_strategy(self):
        """Test TALE with invalid strategy"""
        optimizer = TALEOptimizer()

        # Invalid strategy should raise or fallback
        try:
            result = optimizer.optimize_prompt(
                prompt="Test",
                strategy="invalid_strategy"
            )
            # Should fallback to fixed
            assert result['budget_metadata']['strategy'] == 'fixed'
        except (ValueError, KeyError):
            pass


class TestDataIntegrity:
    """Data integrity and consistency tests"""

    def test_compression_deterministic(self):
        """Test that compression is deterministic"""
        comp = HybridCompressor()
        text = "Test deterministic compression behavior"

        result1 = comp.compress(text, strategy='balanced')
        result2 = comp.compress(text, strategy='balanced')

        # Results should be identical
        assert result1['compressed'] == result2['compressed']
        assert result1['compression_ratio'] == result2['compression_ratio']

    def test_token_count_accuracy(self):
        """Test that token counts are accurate"""
        comp = HybridCompressor()
        text = "Test token counting accuracy"

        result = comp.compress(text)

        # Token counts should be positive integers
        assert isinstance(result['original_tokens'], int)
        assert isinstance(result['compressed_tokens'], int)
        assert result['original_tokens'] > 0
        assert result['compressed_tokens'] > 0

        # Compressed should be <= original
        assert result['compressed_tokens'] <= result['original_tokens']

    def test_compression_ratio_calculation(self):
        """Test compression ratio calculation"""
        comp = HybridCompressor()
        text = "Test compression ratio calculation"

        result = comp.compress(text)

        expected_ratio = result['original_tokens'] / result['compressed_tokens']
        assert abs(result['compression_ratio'] - expected_ratio) < 0.01


class TestSecurityValidation:
    """Security-related tests"""

    def test_sql_injection_attempt(self):
        """Test that SQL injection attempts are handled safely"""
        comp = HybridCompressor()
        malicious_inputs = [
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
            "admin'--",
            "1; UPDATE users SET admin=1--"
        ]

        for malicious in malicious_inputs:
            result = comp.compress(malicious)
            # Should compress without executing anything
            assert result['compressed'] != ""
            assert result['original_tokens'] > 0

    def test_xss_attempt(self):
        """Test that XSS attempts are handled safely"""
        comp = HybridCompressor()
        xss_inputs = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')"
        ]

        for xss in xss_inputs:
            result = comp.compress(xss)
            # Should compress without executing
            assert result['compressed'] != ""

    def test_command_injection_attempt(self):
        """Test that command injection attempts are handled safely"""
        comp = HybridCompressor()
        command_injections = [
            "; ls -la",
            "$(rm -rf /)",
            "`whoami`",
            "| cat /etc/passwd"
        ]

        for cmd in command_injections:
            result = comp.compress(cmd)
            # Should compress without executing
            assert result['compressed'] != ""

    def test_path_traversal_attempt(self):
        """Test that path traversal attempts are handled safely"""
        comp = HybridCompressor()
        path_traversals = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32",
            "/etc/shadow"
        ]

        for path in path_traversals:
            result = comp.compress(path)
            # Should compress without accessing files
            assert result['compressed'] != ""


class TestBoundaryConditions:
    """Boundary condition tests"""

    def test_single_character_input(self):
        """Test compression with single character"""
        comp = HybridCompressor()
        result = comp.compress("a")

        assert result['compressed'] == "a" or result['compressed'] != ""
        assert result['original_tokens'] >= 1

    def test_single_word_input(self):
        """Test compression with single word"""
        comp = HybridCompressor()
        result = comp.compress("test")

        assert result['compressed'] != ""
        assert result['original_tokens'] >= 1

    def test_max_length_input(self):
        """Test compression with very long input"""
        comp = HybridCompressor()
        # Create 100k character string
        text = "x" * 100000

        result = comp.compress(text, strategy='aggressive')
        assert result['compressed'] != ""
        assert result['compression_ratio'] >= 1.0

    def test_whitespace_only(self):
        """Test compression with only whitespace"""
        comp = HybridCompressor()
        whitespace_inputs = ["   ", "\n\n\n", "\t\t\t", "  \n  \t  "]

        for ws in whitespace_inputs:
            result = comp.compress(ws)
            # Should handle gracefully
            assert isinstance(result, dict)


class TestRegressionPrevention:
    """Regression tests for known issues"""

    def test_empty_compression_bug(self):
        """Regression: Ensure compression never returns completely empty result"""
        comp = HybridCompressor()
        text = "Test " * 1000  # Repetitive text

        result = comp.compress(text, strategy='aggressive')

        # Should never compress to nothing
        assert result['compressed'] != ""
        assert result['compressed'].strip() != ""
        assert result['compressed_tokens'] > 0

    def test_division_by_zero_bug(self):
        """Regression: Ensure no division by zero in ratio calculation"""
        comp = HybridCompressor()

        # Even with problematic input, should never crash
        try:
            result = comp.compress("", strategy='balanced')
            if result['compressed_tokens'] == 0:
                # If empty, compression_ratio should be 1.0 or handled
                assert result['compression_ratio'] >= 1.0
        except Exception as e:
            # Should not be ZeroDivisionError
            assert not isinstance(e, ZeroDivisionError)


def run_production_tests():
    """Run all production tests and generate report"""
    print("=" * 80)
    print("CONCISE SDK - PRODUCTION TEST SUITE")
    print("=" * 80)
    print()

    # Run pytest with verbose output
    exit_code = pytest.main([
        __file__,
        '-v',
        '--tb=short',
        '--durations=10',
        '-x'  # Stop on first failure
    ])

    return exit_code


if __name__ == "__main__":
    exit_code = run_production_tests()
    sys.exit(exit_code)
