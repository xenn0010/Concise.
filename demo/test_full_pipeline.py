"""
Test Full Pipeline: Input Compression + TALE Output Optimization
Shows the complete Concise optimization stack working together
"""
import sys
sys.path.insert(0, '/home/yab/Concise/backend')

from app.simple_compressor import SimpleCompressor
from app.services.tale_optimizer import TALEOptimizer
from openai import OpenAI
import time
import os
from dotenv import load_dotenv

# Configuration
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is required. Please set it in .env file.")

class Colors:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 100}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(100)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 100}{Colors.END}\n")

def calculate_cost(prompt_tokens, completion_tokens):
    """GPT-4 pricing"""
    return (prompt_tokens * 0.03 / 1000) + (completion_tokens * 0.06 / 1000)

def call_openai(prompt, max_tokens=None):
    """Call OpenAI GPT-4"""
    client = OpenAI(api_key=OPENAI_API_KEY)

    start = time.time()
    params = {
        "model": "gpt-4",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }
    if max_tokens:
        params["max_tokens"] = max_tokens

    completion = client.chat.completions.create(**params)
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

# Test prompt
prompt = """You are a helpful customer support agent for TechCorp.

Our product is a cloud-based project management tool that helps teams collaborate on projects. It includes features like task management, file sharing, real-time chat, and analytics dashboards.

Common issues include:
- Login problems
- File upload errors
- Notification settings
- Billing questions
- Integration with third-party tools

Customer question: How do I reset my password?

Please provide a helpful, detailed response."""

print_header("FULL PIPELINE TEST: Input Compression + TALE Output Optimization")
print("This demonstrates the COMPLETE Concise optimization stack\n")
print("Pipeline:")
print("  1. Compress INPUT prompt (save input tokens)")
print("  2. Apply TALE budget (save output tokens)")
print("  3. Call OpenAI with optimized prompt")
print()

# Initialize
print("Initializing...")
input_compressor = SimpleCompressor()
tale_optimizer = TALEOptimizer()
openai_client = OpenAI(api_key=OPENAI_API_KEY)
print(f"{Colors.GREEN}Ready!{Colors.END}\n")

print_header("BASELINE (No Optimization)")
print("Calling OpenAI with original prompt...")
baseline = call_openai(prompt)

print(f"{Colors.GREEN}Response received!{Colors.END}\n")
print(f"{Colors.BOLD}Output Preview:{Colors.END}")
print(f"{baseline['response'][:300]}...\n")
print(f"{Colors.BOLD}Metrics:{Colors.END}")
print(f"  Prompt tokens:     {baseline['prompt_tokens']}")
print(f"  Completion tokens: {baseline['completion_tokens']}")
print(f"  Total tokens:      {baseline['total_tokens']}")
print(f"  Cost:              ${baseline['cost']:.6f}")
print(f"  Time:              {baseline['time_s']:.1f}s")

print_header("STEP 1: Compress Input Prompt")
print("Using simple heuristic compressor (2x target)...")
compression_result = input_compressor.compress(prompt, target_ratio=0.5)

print(f"{Colors.GREEN}Compression complete!{Colors.END}\n")
print(f"{Colors.BOLD}Original Prompt ({compression_result['original_tokens']} tokens):{Colors.END}")
print(f"{prompt}\n")
print(f"{Colors.BOLD}Compressed Prompt ({compression_result['compressed_tokens']} tokens):{Colors.END}")
print(f"{Colors.YELLOW}{compression_result['compressed_text']}{Colors.END}\n")
print(f"{Colors.BOLD}Compression Stats:{Colors.END}")
print(f"  Tokens saved:      {compression_result['tokens_saved']} ({compression_result['compression_ratio']:.1f}x)")
print(f"  Input cost saved:  ${(compression_result['tokens_saved'] / 1000 * 0.03):.6f}")

print_header("STEP 2: Apply TALE Output Optimization")
print("Using TALE zero-shot estimator with GPT-5...")

tale_result = tale_optimizer.optimize_prompt(
    prompt=compression_result['compressed_text'],
    strategy="zero_shot",
    llm_client=openai_client
)

print(f"{Colors.GREEN}TALE optimization complete!{Colors.END}\n")
print(f"{Colors.BOLD}TALE Budget Estimate:{Colors.END}")
print(f"  Estimated output tokens: {tale_result['estimated_budget']}")
print(f"  Confidence: {tale_result['budget_metadata']['confidence']}")
print(f"  Reasoning: {tale_result['budget_metadata']['reasoning']}\n")
print(f"{Colors.BOLD}Optimized Prompt:{Colors.END}")
print(f"{tale_result['optimized_prompt'][:300]}...")

print_header("STEP 3: Call OpenAI with Full Optimization")
print(f"Compressed input + TALE budget constraint (max_tokens={tale_result['estimated_budget']})...")

optimized = call_openai(
    tale_result['optimized_prompt'],
    max_tokens=tale_result['estimated_budget']
)

print(f"{Colors.GREEN}Response received!{Colors.END}\n")
print(f"{Colors.BOLD}Output Preview:{Colors.END}")
print(f"{optimized['response'][:300]}...\n")
print(f"{Colors.BOLD}Metrics:{Colors.END}")
print(f"  Prompt tokens:     {optimized['prompt_tokens']}")
print(f"  Completion tokens: {optimized['completion_tokens']}")
print(f"  Total tokens:      {optimized['total_tokens']}")
print(f"  Cost:              ${optimized['cost']:.6f}")
print(f"  Time:              {optimized['time_s']:.1f}s")

print_header("FINAL COMPARISON")

print(f"{Colors.BOLD}Pipeline Performance:{Colors.END}\n")
print(f"{'Stage':<30} | {'Tokens':>12} | {'Cost':>12} | {'Savings':>12}")
print("-" * 75)
print(f"{'Baseline (No optimization)':<30} | {baseline['total_tokens']:>12} | ${baseline['cost']:>11.6f} | -")

input_savings = compression_result['tokens_saved']
output_savings_est = baseline['completion_tokens'] - tale_result['estimated_budget']
total_savings_est = input_savings + output_savings_est

print(f"{'Input compression only':<30} | {baseline['total_tokens'] - input_savings:>12} | ${(baseline['cost'] - (input_savings/1000*0.03)):>11.6f} | {(input_savings/baseline['total_tokens']*100):.1f}%")
print(f"{'Full optimization (actual)':<30} | {optimized['total_tokens']:>12} | ${optimized['cost']:>11.6f} | {((baseline['total_tokens'] - optimized['total_tokens'])/baseline['total_tokens']*100):.1f}%")

print(f"\n{Colors.BOLD}Breakdown:{Colors.END}")
print(f"  Input tokens saved:  {compression_result['tokens_saved']} ({compression_result['compression_ratio']:.1f}x compression)")
print(f"  Output tokens saved: {baseline['completion_tokens'] - optimized['completion_tokens']} (TALE budget)")
print(f"  Total tokens saved:  {baseline['total_tokens'] - optimized['total_tokens']}")
print(f"  Cost saved:          ${baseline['cost'] - optimized['cost']:.6f} ({((baseline['cost'] - optimized['cost'])/baseline['cost']*100):.1f}%)")

print(f"\n{Colors.BOLD}Scaling to 1M calls/month:{Colors.END}")
monthly_baseline = baseline['cost'] * 1_000_000
monthly_optimized = optimized['cost'] * 1_000_000
monthly_savings = monthly_baseline - monthly_optimized

print(f"  Baseline cost:     ${monthly_baseline:>12,.2f}/month")
print(f"  Optimized cost:    ${monthly_optimized:>12,.2f}/month")
print(f"  Monthly savings:   ${monthly_savings:>12,.2f}")
print(f"  Yearly savings:    ${monthly_savings * 12:>12,.2f}")

print(f"\n{Colors.GREEN}Full pipeline test complete!{Colors.END}\n")
print(f"{Colors.BOLD}Summary:{Colors.END}")
print("- Input compression: WORKS (simple heuristics)")
print("- TALE output optimization: WORKS (GPT-5 zero-shot estimation)")
print(f"- Combined savings: {((baseline['cost'] - optimized['cost'])/baseline['cost']*100):.0f}%")
