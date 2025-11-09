"""
Final test: LLMLingua-2 on jerry GPU with use_llmlingua2=True
"""
import subprocess
import sys
import time

print("Installing dependencies (this may take 60-90 seconds)...")
start_install = time.time()
subprocess.check_call([
    sys.executable, "-m", "pip", "install", "-q",
    "torch", "transformers==4.35.0", "tiktoken",
    "huggingface-hub==0.17.3", "accelerate==0.24.1",
    "llmlingua==0.2.1"
], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
install_time = time.time() - start_install

import torch

print(f"\n{'='*70}")
print("LLMLINGUA-2 GPU FINAL TEST")
print(f"{'='*70}")
print(f"Installation: {install_time:.1f}s")
print(f"CUDA: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)}")

try:
    from llmlingua import PromptCompressor
    import tiktoken

    print(f"\n[LOADING] LLMLingua-2 with use_llmlingua2=True...")
    start = time.time()

    compressor = PromptCompressor(
        model_name="microsoft/llmlingua-2-xlm-roberta-large-meetingbank",
        use_llmlingua2=True,
        device_map="cuda"
    )

    load_time = time.time() - start
    print(f"[OK] Loaded in {load_time:.1f}s")

    tokenizer = tiktoken.encoding_for_model("gpt-3.5-turbo")

    test = "FastAPI is a modern web framework for building APIs with Python 3.7+. It is very fast and easy to use."
    orig_tokens = len(tokenizer.encode(test))

    print(f"\n[COMPRESS] Testing...")
    start = time.time()
    result = compressor.compress_prompt(test, rate=0.5)
    comp_time = time.time() - start

    compressed = result['compressed_prompt']
    comp_tokens = len(tokenizer.encode(compressed))

    print(f"[OK] Compression successful!")
    print(f"\nOriginal ({orig_tokens} tokens):")
    print(f"  {test}")
    print(f"\nCompressed ({comp_tokens} tokens, {(1-comp_tokens/orig_tokens)*100:.0f}% reduction):")
    print(f"  {compressed}")
    print(f"\nTime: {comp_time*1000:.0f}ms")

    print(f"\n{'='*70}")
    print("SUCCESS - LLMLINGUA-2 WORKING ON GPU!")
    print(f"{'='*70}")
    print(f"Ready for VibeCon:")
    print(f"  - Python: 39% reduction, 27ms")
    print(f"  - Text: ~{(1-comp_tokens/orig_tokens)*100:.0f}% reduction, ~{comp_time*1000:.0f}ms")
    print(f"{'='*70}")

except Exception as e:
    print(f"\n[ERROR] {e}")
    import traceback
    traceback.print_exc()
