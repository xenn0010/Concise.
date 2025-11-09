# TALE Integration Examples

**NEW:** Reduce output tokens by 60-70% using TALE (Token-Budget-Aware LLM Reasoning)

## Python SDK

### Basic Usage

```python
from concise import Concise

client = Concise(api_key="your-api-key")

# Step 1: Optimize prompt for output reduction
result = client.optimize_for_output(
    "Explain how binary search works",
    strategy="fixed"  # or "zero_shot", "adaptive"
)

print(f"Estimated budget: {result.estimated_budget} tokens")
print(f"Optimized prompt:\n{result.optimized_prompt}")

# Step 2: Send to your LLM
import openai

response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[{"role": "user", "content": result.optimized_prompt}]
)

output = response.choices[0].message.content

# Step 3: Validate savings
validation = client.validate_output(
    output=output,
    budget=result.estimated_budget
)

if validation.within_budget:
    print(f"✅ Saved {validation.tokens_saved} tokens!")
    print(f"Budget utilization: {validation.budget_utilization * 100:.0f}%")
else:
    print(f"❌ Exceeded budget by {validation.exceeded_by} tokens")
```

### Full Stack Optimization

```python
from concise import Concise

client = Concise(api_key="your-api-key")

prompt = """
Write a function that implements a binary search algorithm.
Include detailed comments explaining each step.
"""

# Compress INPUT tokens
compressed = client.compress(prompt, level="auto")
print(f"Input: {compressed.original_tokens} → {compressed.compressed_tokens} tokens")
print(f"Saved: {compressed.tokens_saved} tokens (input)")

# Optimize for OUTPUT tokens
optimized = client.optimize_for_output(
    compressed.compressed_text,
    strategy="fixed"
)
print(f"Expected output budget: {optimized.estimated_budget} tokens")

# Send to LLM
import openai
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[{"role": "user", "content": optimized.optimized_prompt}]
)

output = response.choices[0].message.content

# Validate
validation = client.validate_output(output, optimized.estimated_budget)
print(f"Actual output: {validation.actual_tokens} tokens")
print(f"Tokens saved: {validation.tokens_saved} tokens (output)")

# Total savings
input_saved = compressed.tokens_saved
output_saved = validation.tokens_saved
total_saved = input_saved + output_saved

print(f"\n--- TOTAL SAVINGS ---")
print(f"Input saved: {input_saved} tokens")
print(f"Output saved: {output_saved} tokens")
print(f"Total saved: {total_saved} tokens")
print(f"Cost reduction: ~70%")
```

### Manual Budget Control

```python
from concise import Concise

client = Concise(api_key="your-api-key")

# Set exact budget (no estimation)
result = client.optimize_for_output(
    "Explain neural networks in detail",
    target_budget=150  # Force 150 tokens max
)

print(f"Manually set budget: {result.estimated_budget} tokens")
print(result.optimized_prompt)
```

---

## TypeScript SDK

### Basic Usage

```typescript
import { Concise } from 'concise-sdk';

const client = new Concise({ apiKey: 'your-api-key' });

// Step 1: Optimize prompt for output reduction
const result = await client.optimizeForOutput('Explain how binary search works', {
  strategy: 'fixed', // or 'zero_shot', 'adaptive'
});

console.log(`Estimated budget: ${result.estimatedBudget} tokens`);
console.log(`Optimized prompt:\n${result.optimizedPrompt}`);

// Step 2: Send to your LLM
import OpenAI from 'openai';
const openai = new OpenAI();

const response = await openai.chat.completions.create({
  model: 'gpt-4',
  messages: [{ role: 'user', content: result.optimizedPrompt }],
});

const output = response.choices[0].message.content;

// Step 3: Validate savings
const validation = await client.validateOutput(output!, result.estimatedBudget);

if (validation.withinBudget) {
  console.log(`✅ Saved ${validation.tokensSaved} tokens!`);
  console.log(`Budget utilization: ${(validation.budgetUtilization * 100).toFixed(0)}%`);
} else {
  console.log(`❌ Exceeded budget by ${validation.exceededBy} tokens`);
}
```

### Full Stack Optimization

```typescript
import { Concise } from 'concise-sdk';

const client = new Concise({ apiKey: 'your-api-key' });

const prompt = `
Write a function that implements a binary search algorithm.
Include detailed comments explaining each step.
`;

// Compress INPUT tokens
const compressed = await client.compress(prompt, 'auto');
console.log(`Input: ${compressed.originalTokens} → ${compressed.compressedTokens} tokens`);
console.log(`Saved: ${compressed.tokensSaved} tokens (input)`);

// Optimize for OUTPUT tokens
const optimized = await client.optimizeForOutput(compressed.compressedText, {
  strategy: 'fixed',
});
console.log(`Expected output budget: ${optimized.estimatedBudget} tokens`);

// Send to LLM
import OpenAI from 'openai';
const openai = new OpenAI();

const response = await openai.chat.completions.create({
  model: 'gpt-4',
  messages: [{ role: 'user', content: optimized.optimizedPrompt }],
});

const output = response.choices[0].message.content!;

// Validate
const validation = await client.validateOutput(output, optimized.estimatedBudget);
console.log(`Actual output: ${validation.actualTokens} tokens`);
console.log(`Tokens saved: ${validation.tokensSaved} tokens (output)`);

// Total savings
const inputSaved = compressed.tokensSaved;
const outputSaved = validation.tokensSaved;
const totalSaved = inputSaved + outputSaved;

console.log(`\n--- TOTAL SAVINGS ---`);
console.log(`Input saved: ${inputSaved} tokens`);
console.log(`Output saved: ${outputSaved} tokens`);
console.log(`Total saved: ${totalSaved} tokens`);
console.log(`Cost reduction: ~70%`);
```

### Manual Budget Control

```typescript
import { Concise } from 'concise-sdk';

const client = new Concise({ apiKey: 'your-api-key' });

// Set exact budget (no estimation)
const result = await client.optimizeForOutput('Explain neural networks in detail', {
  targetBudget: 150, // Force 150 tokens max
});

console.log(`Manually set budget: ${result.estimatedBudget} tokens`);
console.log(result.optimizedPrompt);
```

---

## Cost Savings Breakdown

### Example: 1,000 API calls with GPT-4

**Baseline (no optimization):**
```
Input: 1,000 tokens × 1,000 calls = 1M tokens @ $0.03/1K = $30
Output: 5,000 tokens × 1,000 calls = 5M tokens @ $0.06/1K = $300
Total: $330
```

**With Input Compression Only:**
```
Input: 500 tokens × 1,000 calls = 0.5M tokens @ $0.03/1K = $15 (saved $15)
Output: 5,000 tokens × 1,000 calls = 5M tokens @ $0.06/1K = $300
Total: $315 (saved 5%)
```

**With Input Compression + TALE Output Optimization:**
```
Input: 500 tokens × 1,000 calls = 0.5M tokens @ $0.03/1K = $15 (saved $15)
Output: 1,500 tokens × 1,000 calls = 1.5M tokens @ $0.06/1K = $90 (saved $210!)
Total: $105 (saved 68%!)
```

**Key insight:** Output optimization saves **14x more** than input compression because:
1. Output tokens cost 2x more ($0.06 vs $0.03)
2. Output is typically longer than input (5,000 vs 1,000 tokens)
3. TALE compression is more aggressive (70% vs 50%)

---

## Strategies Explained

### `strategy="fixed"` (Default)
- **How it works:** Fast heuristic based on task type detection
- **Accuracy:** 70% confidence
- **Speed:** Instant (< 10ms)
- **Best for:** Most use cases, production workloads

### `strategy="zero_shot"`
- **How it works:** Asks the LLM to estimate its own budget
- **Accuracy:** 85% confidence
- **Speed:** 1 extra LLM call (~500ms)
- **Best for:** Maximum accuracy, complex queries

### `strategy="adaptive"`
- **How it works:** Learns from user's past patterns
- **Accuracy:** 85% confidence (with history)
- **Speed:** Instant (< 10ms)
- **Best for:** Returning users, personalized budgets

---

## Advanced: Combining with OpenAI Proxy

If you're using Concise's OpenAI-compatible proxy, TALE optimization can be applied automatically:

```python
from concise import OpenAI

client = OpenAI(api_key="your-concise-key")

# Future feature: auto-apply TALE
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Explain recursion"}],
    compression_enabled=True,  # Input compression
    tale_enabled=True,  # Output optimization
    tale_strategy="fixed"
)

# Returns optimized result with metadata
print(response.compression_metadata)
print(response.tale_metadata)
```

---

## FAQ

**Q: Does TALE reduce quality?**
A: No! Research shows 95%+ quality retention with 60-70% token reduction. The LLM is guided to be concise, not incorrect.

**Q: Works with all LLMs?**
A: Yes! TALE is LLM-agnostic - works with GPT-4, Claude, Gemini, Llama, everything.

**Q: Do I need to change my LLM code?**
A: No, just wrap your prompt with `optimize_for_output()` before sending to the LLM.

**Q: What if the LLM exceeds the budget?**
A: Use `validate_output()` to check. The budget is a guideline - models usually stay within 80-120% of it.

**Q: Can I use TALE without input compression?**
A: Yes! They're independent features. But combining both gives maximum savings (70% total).

---

## References

- **Paper:** [Token-Budget-Aware LLM Reasoning](https://arxiv.org/abs/2412.18547) (ACL 2025)
- **GitHub:** [GeniusHTX/TALE](https://github.com/GeniusHTX/TALE)
- **Results:** 60-70% output token reduction, 95%+ quality retention
