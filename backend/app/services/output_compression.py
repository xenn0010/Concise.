"""
Output Compression Service
Compress LLM completions to reduce output token costs
"""

import time
from typing import Dict, Any, Optional, Literal
import tiktoken

from app.services.compression import get_compressor


CompressionMethod = Literal["semantic", "token_extraction", "summarize", "none"]


class OutputCompressor:
    """
    Compress LLM outputs while maintaining quality

    Output tokens often cost 2-5x more than input tokens.
    This service compresses completions to reduce costs.
    """

    def __init__(self):
        self.compressor = get_compressor()
        self.tokenizer = tiktoken.encoding_for_model("gpt-3.5-turbo")

    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        return len(self.tokenizer.encode(text))

    def compress_output(
        self,
        output_text: str,
        method: CompressionMethod = "semantic",
        target_reduction: float = 0.4,
        min_length: int = 50
    ) -> Dict[str, Any]:
        """
        Compress LLM output

        Args:
            output_text: The LLM completion to compress
            method: Compression method to use
                - semantic: Use LLMLingua-2 (maintains meaning)
                - token_extraction: Remove filler words
                - summarize: Condense long outputs
                - none: No compression (passthrough)
            target_reduction: Target token reduction (0.4 = 40% reduction)
            min_length: Don't compress if output is shorter than this

        Returns:
            Dict with:
                - original_text: Original output
                - compressed_text: Compressed output
                - original_tokens: Token count before
                - compressed_tokens: Token count after
                - tokens_saved: How many tokens saved
                - reduction_pct: Percentage reduction
                - method: Method used
                - compression_time_ms: Time taken
        """
        start_time = time.time()

        original_tokens = self.count_tokens(output_text)

        # Skip compression for very short outputs
        if original_tokens < min_length:
            return {
                "original_text": output_text,
                "compressed_text": output_text,
                "original_tokens": original_tokens,
                "compressed_tokens": original_tokens,
                "tokens_saved": 0,
                "reduction_pct": 0.0,
                "method": "none",
                "compression_time_ms": 0.0,
                "skipped": True,
                "reason": "output_too_short"
            }

        # Apply compression method
        if method == "semantic":
            compressed_text = self._semantic_compression(output_text, target_reduction)
        elif method == "token_extraction":
            compressed_text = self._token_extraction(output_text, target_reduction)
        elif method == "summarize":
            compressed_text = self._summarize(output_text, target_reduction)
        else:  # none
            compressed_text = output_text

        compressed_tokens = self.count_tokens(compressed_text)
        tokens_saved = original_tokens - compressed_tokens
        reduction_pct = (tokens_saved / original_tokens * 100) if original_tokens > 0 else 0
        compression_time = (time.time() - start_time) * 1000

        return {
            "original_text": output_text,
            "compressed_text": compressed_text,
            "original_tokens": original_tokens,
            "compressed_tokens": compressed_tokens,
            "tokens_saved": tokens_saved,
            "reduction_pct": round(reduction_pct, 2),
            "method": method,
            "compression_time_ms": round(compression_time, 2),
            "skipped": False
        }

    def _semantic_compression(self, text: str, target_reduction: float) -> str:
        """
        Semantic compression using LLMLingua-2

        This is the highest quality method - uses our existing
        compression engine to preserve meaning while reducing tokens.
        """
        try:
            # Convert target_reduction to LLMLingua rate
            # target_reduction 0.4 = we want 40% reduction = 60% rate
            rate = 1.0 - target_reduction

            # Use our existing compressor
            result = self.compressor.compress(text, internal_strategy="text")
            return result.compressed_text

        except Exception:
            # Fallback to original if compression fails
            return text

    def _token_extraction(self, text: str, target_reduction: float) -> str:
        """
        Token extraction - remove filler words and condense

        Lighter weight than semantic compression, good for code.
        """
        # Simple implementation: remove common filler words
        filler_words = {
            "actually", "basically", "essentially", "literally",
            "really", "very", "quite", "rather", "somewhat",
            "just", "simply", "merely", "only",
            "I think", "I believe", "I would say", "In my opinion",
            "kind of", "sort of", "a bit", "a little"
        }

        words = text.split()
        filtered_words = []

        for word in words:
            # Keep word if it's not a filler word
            if word.lower() not in filler_words:
                filtered_words.append(word)

        # Rejoin
        compressed = " ".join(filtered_words)

        # Also condense multiple spaces
        while "  " in compressed:
            compressed = compressed.replace("  ", " ")

        return compressed.strip()

    def _summarize(self, text: str, target_reduction: float) -> str:
        """
        Summarization - for very long outputs

        This would ideally use a summarization model, but for now
        we use semantic compression with aggressive rate.
        """
        # For now, just use semantic compression with aggressive rate
        try:
            result = self.compressor.compress(text, level="aggressive")
            return result.compressed_text
        except Exception:
            return text


# Singleton instance
_output_compressor: Optional[OutputCompressor] = None


def get_output_compressor() -> OutputCompressor:
    """Get or create global output compressor instance"""
    global _output_compressor
    if _output_compressor is None:
        _output_compressor = OutputCompressor()
    return _output_compressor
