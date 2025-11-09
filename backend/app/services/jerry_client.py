"""
Jerry GPU Client for LLMLingua-2 Compression
Integrates jerry GPU into FastAPI backend
"""
import requests
import json
from typing import Optional, Dict, Any
from pathlib import Path
import os


class JerryGPUClient:
    """Client to communicate with jerry GPU for LLMLingua-2 compression"""

    def __init__(self):
        """Initialize jerry client with saved config"""
        self.url, self.token = self._load_config()

        if not self.url or not self.token:
            raise ValueError(
                "Jerry not configured. Run 'jerry connect <url> <token>' first"
            )

    def _load_config(self) -> tuple[Optional[str], Optional[str]]:
        """Load jerry configuration from config file or environment"""
        # Try environment variables first
        url = os.environ.get('JERRY_URL') or os.environ.get('COLAB_URL')
        token = os.environ.get('JERRY_TOKEN') or os.environ.get('COLAB_TOKEN')

        # Fall back to config file
        if not url or not token:
            config_file = Path.home() / '.jerry_config.json'
            if config_file.exists():
                try:
                    with open(config_file) as f:
                        config = json.load(f)
                        url = config.get('url')
                        token = config.get('token')
                except Exception:
                    pass

        return url, token

    def health_check(self) -> bool:
        """Check if jerry server is reachable"""
        try:
            response = requests.get(f'{self.url}/health', timeout=5)
            response.raise_for_status()
            data = response.json()
            return data.get('gpu_available', False)
        except Exception:
            return False

    def compress_text(
        self,
        text: str,
        rate: float = 0.5,
        timeout: int = 120,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Compress text using LLMLingua-2 on jerry GPU (with caching)

        Args:
            text: Text to compress
            rate: Compression rate (0.0-1.0, lower = more compression)
            timeout: Request timeout in seconds
            use_cache: Whether to use cache (default: True for instant repeated requests)

        Returns:
            Dict with:
                - success: bool
                - compressed_text: str (if successful)
                - error: str (if failed)
                - compression_time_ms: float
                - original_tokens: int
                - compressed_tokens: int
                - cache_hit: bool (True if from cache)
        """
        # Check cache first
        if use_cache:
            from app.services.compression_cache import get_cache
            cache = get_cache()
            cached = cache.get(text, rate)

            if cached:
                # Cache hit - instant response!
                return {
                    'success': True,
                    'compressed_text': cached.compressed_text,
                    'original_tokens': cached.original_tokens,
                    'compressed_tokens': cached.compressed_tokens,
                    'compression_time_ms': 0.0,  # Instant!
                    'reduction_pct': (1 - cached.compressed_tokens/cached.original_tokens) * 100 if cached.original_tokens > 0 else 0,
                    'cache_hit': True
                }

        # Python code to run on jerry GPU
        compression_code = f'''
import sys
import time
import json

# Install dependencies (cached after first run)
import subprocess
subprocess.run([sys.executable, "-m", "pip", "install", "-q",
    "transformers==4.35.0", "tiktoken", "llmlingua==0.2.1",
    "huggingface-hub==0.17.3", "accelerate==0.24.1"],
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

import torch
from llmlingua import PromptCompressor
import tiktoken

try:
    # Initialize compressor
    compressor = PromptCompressor(
        model_name="microsoft/llmlingua-2-xlm-roberta-large-meetingbank",
        use_llmlingua2=True,
        device_map="cuda"
    )

    tokenizer = tiktoken.encoding_for_model("gpt-3.5-turbo")

    # Input text (properly escaped)
    text = {json.dumps(text)}

    # Count original tokens
    orig_tokens = len(tokenizer.encode(text))

    # Compress
    start = time.time()
    result = compressor.compress_prompt(text, rate={rate})
    comp_time = (time.time() - start) * 1000

    compressed = result['compressed_prompt']
    comp_tokens = len(tokenizer.encode(compressed))

    # Output JSON result
    output = {{
        "success": True,
        "compressed_text": compressed,
        "original_tokens": orig_tokens,
        "compressed_tokens": comp_tokens,
        "compression_time_ms": comp_time,
        "reduction_pct": (1 - comp_tokens/orig_tokens) * 100 if orig_tokens > 0 else 0
    }}

    print("JERRY_RESULT_START")
    print(json.dumps(output))
    print("JERRY_RESULT_END")

except Exception as e:
    error_output = {{
        "success": False,
        "error": str(e)
    }}
    print("JERRY_RESULT_START")
    print(json.dumps(error_output))
    print("JERRY_RESULT_END")
'''

        try:
            # Send request to jerry
            headers = {
                'Authorization': f'Bearer {self.token}',
                'Content-Type': 'application/json'
            }

            response = requests.post(
                f'{self.url}/execute-cuda',
                headers=headers,
                json={'code': compression_code, 'language': 'py'},
                timeout=timeout
            )

            response.raise_for_status()
            result = response.json()

            # Extract result from stdout
            if result.get('success') and result.get('stdout'):
                stdout = result['stdout']

                # Parse JSON output between markers
                if 'JERRY_RESULT_START' in stdout and 'JERRY_RESULT_END' in stdout:
                    start_idx = stdout.index('JERRY_RESULT_START') + len('JERRY_RESULT_START')
                    end_idx = stdout.index('JERRY_RESULT_END')
                    json_str = stdout[start_idx:end_idx].strip()

                    compression_result = json.loads(json_str)
                    compression_result['cache_hit'] = False

                    # Store in cache for future requests
                    if use_cache and compression_result.get('success'):
                        from app.services.compression_cache import get_cache
                        cache = get_cache()
                        cache.set(
                            text=text,
                            rate=rate,
                            compressed_text=compression_result['compressed_text'],
                            original_tokens=compression_result['original_tokens'],
                            compressed_tokens=compression_result['compressed_tokens'],
                            compression_time_ms=compression_result['compression_time_ms']
                        )

                    return compression_result

            # If we get here, something went wrong
            return {
                'success': False,
                'error': result.get('stderr', 'Unknown error')
            }

        except requests.exceptions.Timeout:
            return {
                'success': False,
                'error': f'Request timed out after {timeout}s'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }


# Singleton instance
_jerry_client: Optional[JerryGPUClient] = None


def get_jerry_client() -> JerryGPUClient:
    """Get or create jerry GPU client singleton"""
    global _jerry_client
    if _jerry_client is None:
        _jerry_client = JerryGPUClient()
    return _jerry_client
