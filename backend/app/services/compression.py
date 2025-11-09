"""
Prompt compression service using LLMLingua and python-minifier
"""
import time
import re
from typing import Literal, Optional
from dataclasses import dataclass

import tiktoken
from llmlingua import PromptCompressor


@dataclass
class CompressionResult:
    """Result of prompt compression"""
    original_text: str
    compressed_text: str
    original_tokens: int
    compressed_tokens: int
    tokens_saved: int
    compression_ratio: float
    strategy: str
    compression_time_ms: float


class ConciseCompressor:
    """
    Intelligent prompt compressor that chooses between:
    - python-minifier for Python code
    - LLMLingua for natural language text
    """

    def __init__(
        self,
        model_name: str = "gpt-3.5-turbo",
        llm_lingua_model: str = "microsoft/llmlingua-2-xlm-roberta-large-meetingbank",
        device: str = "cpu"
    ):
        """
        Initialize compressor

        Args:
            model_name: OpenAI model name for token counting
            llm_lingua_model: LLMLingua model to use
            device: Device for LLMLingua ("cpu" or "cuda")
        """
        self.model_name = model_name
        self.tokenizer = tiktoken.encoding_for_model(model_name)

        # Initialize LLMLingua (lazy loaded to save memory)
        self._llm_compressor: Optional[PromptCompressor] = None
        self.llm_lingua_model = llm_lingua_model
        self.device = device

    @property
    def llm_compressor(self) -> PromptCompressor:
        """Lazy load LLMLingua compressor"""
        if self._llm_compressor is None:
            self._llm_compressor = PromptCompressor(
                model_name=self.llm_lingua_model,
                use_llmlingua2=True,
                device_map=self.device
            )
        return self._llm_compressor

    def count_tokens(self, text: str) -> int:
        """Count tokens in text using tiktoken"""
        return len(self.tokenizer.encode(text))

    def is_code(self, text: str) -> bool:
        """
        Detect if text is primarily Python code

        Heuristics:
        - Contains Python keywords
        - Has function/class definitions
        - Has imports
        - Has significant indentation
        """
        # Check for Python keywords
        keywords = [
            'def ', 'class ', 'import ', 'from ', 'return ', 'if ', 'else:',
            'elif ', 'for ', 'while ', 'try:', 'except ', 'with ', 'async ',
            'await ', 'yield ', 'lambda ', 'pass', 'raise ', 'assert '
        ]
        keyword_count = sum(1 for kw in keywords if kw in text)

        # Check for code patterns
        has_function = bool(re.search(r'\bdef\s+\w+\s*\(', text))
        has_class = bool(re.search(r'\bclass\s+\w+', text))
        has_import = bool(re.search(r'\b(import|from)\s+\w+', text))

        # Check for significant indentation (4+ spaces at start of lines)
        lines = text.split('\n')
        indented_lines = sum(1 for line in lines if line.startswith('    ') or line.startswith('\t'))
        indentation_ratio = indented_lines / max(len(lines), 1)

        # Decide if it's code
        is_likely_code = (
            keyword_count >= 3 or
            has_function or
            has_class or
            (has_import and keyword_count >= 1) or
            indentation_ratio > 0.3
        )

        return is_likely_code

    def compress_code(self, code: str) -> str:
        """
        Compress Python code using python-minifier

        Preserves functionality while removing:
        - Comments
        - Docstrings
        - Unnecessary whitespace
        - Long variable names (optional)
        """
        try:
            import python_minifier

            # Minify with safe defaults
            minified = python_minifier.minify(
                code,
                remove_annotations=False,  # Keep type hints for clarity
                remove_pass=True,
                remove_literal_statements=True,
                combine_imports=True,
                hoist_literals=True,
                rename_locals=False,  # Keep variable names for readability
                preserve_locals=None,
                rename_globals=False,
                preserve_globals=None,
                remove_object_base=True,
                convert_posargs_to_args=True,
                preserve_shebang=False,
                remove_asserts=False,
            )

            return minified

        except Exception as e:
            # If minification fails, return original
            # This can happen with syntax errors or edge cases
            return code

    def compress_text(
        self,
        text: str,
        target_ratio: float = 0.5,
        use_context_level: str = "medium"
    ) -> str:
        """
        Compress natural language text using LLMLingua-2 on jerry GPU

        Args:
            text: Text to compress
            target_ratio: Target compression ratio (0.0-1.0)
            use_context_level: How much context to preserve ("low", "medium", "high")

        Returns:
            Compressed text
        """
        try:
            # Try jerry GPU first (fast, ~315ms)
            from app.services.jerry_client import get_jerry_client

            jerry = get_jerry_client()

            # Check if jerry is available
            if jerry.health_check():
                result = jerry.compress_text(text, rate=target_ratio, timeout=120)

                if result.get('success'):
                    return result['compressed_text']
                # If jerry fails, fall through to CPU backup

        except Exception:
            # Jerry not available or failed, fall back to CPU
            pass

        try:
            # Fallback: Use local CPU compression (slower, ~500-2000ms)
            # Map context level to LLMLingua parameters
            context_params = {
                "low": {"rate": target_ratio, "use_sentence_level_filter": True},
                "medium": {"rate": target_ratio, "use_sentence_level_filter": False},
                "high": {"rate": min(target_ratio + 0.2, 0.9), "use_sentence_level_filter": False}
            }

            params = context_params.get(use_context_level, context_params["medium"])

            # Compress using LLMLingua on CPU
            result = self.llm_compressor.compress_prompt(
                text,
                rate=params["rate"],
                use_sentence_level_filter=params["use_sentence_level_filter"]
            )

            return result["compressed_prompt"]

        except Exception as e:
            # If all compression fails, return original
            return text

    def compress(
        self,
        text: str,
        level: Optional[Literal["auto", "aggressive", "balanced", "conservative"]] = "auto",
        internal_strategy: Optional[Literal["auto", "code", "text"]] = None
    ) -> CompressionResult:
        """
        Compress text using token compression

        Args:
            text: Text to compress
            level: Compression level (auto, aggressive, balanced, conservative)
            internal_strategy: Internal override for strategy detection

        Returns:
            CompressionResult with metrics
        """
        start_time = time.time()

        # Count original tokens
        original_tokens = self.count_tokens(text)

        # Map compression level to target ratio
        level_to_ratio = {
            "auto": 0.5,        # 50% compression
            "aggressive": 0.5,  # 50% compression
            "balanced": 0.7,    # 30% reduction
            "conservative": 0.8 # 20% reduction
        }
        target_ratio = level_to_ratio.get(level, 0.5)

        # Determine strategy (code vs text)
        if internal_strategy == "auto" or internal_strategy is None:
            detected_strategy = "code" if self.is_code(text) else "text"
        else:
            detected_strategy = internal_strategy

        # Compress based on strategy
        if detected_strategy == "code":
            # Code compression (python-minifier)
            compressed_text = self.compress_code(text)
            strategy_label = "token_compression_code"
        else:
            # Text compression (LLMLingua)
            compressed_text = self.compress_text(text, target_ratio=target_ratio)
            strategy_label = "token_compression_text"

        # Count compressed tokens
        compressed_tokens = self.count_tokens(compressed_text)

        # Calculate metrics
        tokens_saved = original_tokens - compressed_tokens
        compression_ratio = compressed_tokens / original_tokens if original_tokens > 0 else 1.0
        compression_time_ms = (time.time() - start_time) * 1000

        return CompressionResult(
            original_text=text,
            compressed_text=compressed_text,
            original_tokens=original_tokens,
            compressed_tokens=compressed_tokens,
            tokens_saved=tokens_saved,
            compression_ratio=compression_ratio,
            strategy=strategy_label,
            compression_time_ms=compression_time_ms
        )


# Global compressor instance (initialized on first use)
_compressor: Optional[ConciseCompressor] = None


def get_compressor() -> ConciseCompressor:
    """Get or create global compressor instance"""
    global _compressor
    if _compressor is None:
        _compressor = ConciseCompressor()
    return _compressor
