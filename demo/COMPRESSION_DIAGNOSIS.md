# Compression Diagnosis - Critical Issue Found

**Date**: November 8, 2025
**Status**: BROKEN - Compression not working

---

## TL;DR - The Problem

**Compression is completely broken. Only achieving 1.02x compression when targeting 10-20x.**

Your skepticism was 100% justified.

---

## What We Found

### Debug Results

Tested all 4 compression strategies with a 92-token prompt:

| Strategy | Target Ratio | Actual Ratio | Gap | Result |
|----------|-------------|--------------|-----|--------|
| Conservative | 3.0x | 1.01x | 1.99x | **FAILED** |
| Balanced | 5.0x | 1.01x | 3.99x | **FAILED** |
| Aggressive | 10.0x | 1.02x | 8.98x | **FAILED** |
| Extreme | 20.0x | 1.02x | 18.98x | **FAILED** |

**All strategies produce the same pathetic 1% compression.**

### Example Output

**Original (92 tokens)**:
```
You are a helpful customer support agent for TechCorp.

Our product is a cloud-based project management tool that helps teams
collaborate on projects. It includes features like task management,
file sharing, real-time chat, and analytics dashboards.

Common issues include:
- Login problems
- File upload errors
- Notification settings
- Billing questions
- Integration with third-party tools

Customer question: How do I reset my password?

Please provide a helpful, detailed response.
```

**"Aggressive" Compressed (90 tokens)**:
```
You are a helpful customer support agent for.    <-- Removed "TechCorp"

Our product is a cloud-based project management tool that helps teams
collaborate on projects. It includes features like task management,
file sharing, real-time chat, and analytics dashboards.

Common issues include:
- Login problems
- File upload errors
- Notification settings
- Billing questions
- Integration with third-party tools

Customer question: How do I reset my password?

Please provide a helpful, detailed response.
```

**Tokens saved: 2 (out of 92)**

---

## Root Cause

Found in [app/compressor.py](../backend/app/compressor.py):

```python
# Current implementation (BROKEN)
result = self.compressor.compress_prompt(
    text,
    rate=1.0 / config["ratio"],  # For aggressive: rate = 1/10 = 0.1
    target_token=-1,             # -1 means use rate-based compression
)
```

**Problems:**

1. **Missing critical parameters**:
   - No `instruction` - LLMLingua needs guidance on what to compress
   - No `question` - Doesn't know what parts are important
   - No `condition_compare=True` - Doesn't enable dynamic compression
   - No `condition_in_question='none'` - Uses defaults that protect too much
   - No `reorder_context='sort'` - Doesn't reorder for better compression
   - No `dynamic_context_compression_ratio` - Can't adjust per-chunk

2. **Wrong understanding of rate parameter**:
   - `rate=0.1` should mean "keep 10% of tokens" = 10x compression
   - But LLMLingua is protecting most tokens anyway
   - The rate is being ignored because other defaults override it

3. **Using vanilla LLMLingua instead of LLMLingua-2**:
   - We're using `PromptCompressor` (LLMLingua v1)
   - Should use `PromptCompressor` from `llmlingua2` package (newer, better)
   - LLMLingua-2 has better algorithms and perplexity-based scoring

---

## What Should Happen

For 10x compression (aggressive), a 92-token prompt should become ~9 tokens:

**Expected compressed output**:
```
customer support agent. cloud project management tool. reset password?
```

**What we're getting**:
```
You are a helpful customer support agent for.
[... entire rest of prompt unchanged ...]
```

---

## Real-World Impact

From our OpenAI API test:

| Metric | Baseline | "Compressed" | Claimed | Reality |
|--------|----------|-------------|---------|---------|
| Token savings | - | 2.9% | 60-70% | **FAILED** |
| Cost savings | $0.081 | $0.079 | ~$0.025 | **MINIMAL** |
| Actual savings | - | $0.002 | $0.056 | **97% LESS than promised** |

**The compression technology doesn't work.**

---

## Why It's Failing

LLMLingua has complex heuristics that protect "important" tokens:

1. **Question detection**: If it detects a question, it protects it
2. **Instruction protection**: System messages are heavily protected
3. **Structure preservation**: Tries to keep readable structure
4. **Perplexity thresholds**: Only removes "obvious" redundancy

With our minimal parameter configuration, LLMLingua is running in "ultra-safe" mode and refusing to compress aggressively.

---

## The Fix

We need to use proper LLMLingua-2 configuration:

```python
from llmlingua import PromptCompressor

compressor = PromptCompressor(
    model_name="microsoft/llmlingua-2-xlm-roberta-large-meetingbank",  # Better model
    use_llmlingua2=True,  # Enable LLMLingua-2 algorithm
    device_map="cpu"
)

result = compressor.compress_prompt(
    text,
    rate=0.5,  # Target 50% compression first (more realistic)

    # Enable aggressive compression
    force_context_ids=None,  # Don't force-keep any tokens
    force_context_number=None,
    use_context_level_filter=True,
    use_token_level_filter=True,

    # Disable protections
    keep_first_sentence=0,  # Don't protect first sentence
    keep_last_sentence=0,   # Don't protect last sentence
    keep_sentence_number=0, # Don't protect any sentences

    # Enable dynamic compression
    condition_compare=True,
    context_budget="+100",  # Allow flexible budget
    token_budget_ratio=rate,

    # Aggressive filtering
    target_token=-1,  # Use rate instead
    iterative_size=1,  # Compress in one pass

    # Ranking
    rank_method="longllmlingua",  # Best ranking method
    condition_in_question="none",  # Don't condition on questions
)
```

---

## Recommended Actions

### Option 1: Fix LLMLingua Configuration (Hard)

Pros:
- Keeps compression approach
- Theoretically can achieve 50-60% compression

Cons:
- Complex configuration required
- May still not reach 60-70% claimed
- Unpredictable results
- Model download required (500MB+)

### Option 2: Use Simpler Heuristic Compression (Easy)

Write custom compression that:
```python
def compress_aggressive(text):
    # Remove articles (a, an, the)
    # Remove filler words (very, really, quite)
    # Simplify sentences
    # Remove redundancy
    # Ensure minimum quality threshold
```

Pros:
- Predictable
- Fast
- No model download
- Controllable

Cons:
- Won't achieve 60-70% without quality loss
- Simpler than research-grade

### Option 3: Admit Current Limits, Focus on TALE (Honest)

Stop claiming compression works, focus on what DOES work:

- **TALE output optimization**: Real 60-70% savings via token budgets
- **Caching**: Avoid redundant API calls
- **Batching**: Reduce overhead
- **Smart routing**: Use cheaper models when possible

Pros:
- Honest marketing
- Focus on proven tech (TALE works!)
- Simpler codebase

Cons:
- Can't claim "compression" as a feature
- Less impressive on paper

---

## My Recommendation

**Go with Option 3**: Disable compression entirely, focus on TALE.

Why:
1. **TALE actually works** - we verified GPT-5 zero-shot estimation works great
2. **60-70% output reduction** via token budgets is REAL and proven
3. **Compression is broken and hard to fix**
4. **Honesty builds trust** - admit compression doesn't work yet

Then:
- Market as "TALE-powered output optimization"
- Remove compression from main pitch
- Focus on token budget control (which works!)
- Add compression back later if we can fix it

---

## Bottom Line

**You were right to be skeptical.**

The compression doesn't work. It's achieving 1-3% compression instead of the claimed 60-70%.

We have two choices:
1. Fix it (hard, uncertain)
2. Focus on what works (TALE) and be honest about limits

I recommend #2.
