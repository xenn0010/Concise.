# How Concise Works - Technical & Pricing Details

## How Integration Works (Developer Experience)

### Option 1: Direct API (Most Flexible)

**Step 1: Sign up & get API key**
```bash
# User goes to concise.ai/signup
# Gets API key: sk_live_abc123...
```

**Step 2: Install SDK**
```bash
pip install concise-ai
```

**Step 3: Use in code**
```python
import concise
from openai import OpenAI

# Initialize Concise
concise.api_key = "sk_live_abc123..."

# Compress your prompt
long_context = """
[10,000 tokens of documentation, code, or context]
"""

compressed = concise.compress(
    text=long_context,
    target_ratio=0.2  # Compress to 20% of original (5x compression)
)

# Use compressed text with any LLM
client = OpenAI()
response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "user", "content": compressed.text}
    ]
)

# Check savings
print(f"Original tokens: {compressed.original_tokens}")
print(f"Compressed tokens: {compressed.compressed_tokens}")
print(f"Saved: ${compressed.cost_saved}")
```

**What happens behind the scenes:**
1. Your code sends text to our API: `POST https://api.concise.ai/v1/compress`
2. Our server runs LLMLingua compression
3. Returns compressed text + metadata
4. You use compressed text with OpenAI/Anthropic/etc
5. We track usage and calculate savings

---

### Option 2: Drop-in Replacement (Easiest)

**Instead of this:**
```python
from openai import OpenAI

client = OpenAI(api_key="sk-...")
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": long_prompt}]
)
```

**Do this (2 lines changed):**
```python
from concise.openai import OpenAI  # ← Changed import

client = OpenAI(
    api_key="sk-...",
    concise_api_key="sk_live_abc123...",  # ← Added this
    auto_compress=True  # ← Added this
)

# Same code - compression happens automatically
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": long_prompt}]  # Auto-compressed!
)
```

**How it works:**
1. Our wrapper intercepts the call
2. Detects if prompt > threshold (e.g., 1000 tokens)
3. Compresses automatically
4. Sends to OpenAI
5. Returns response unchanged

**Advantage:** Zero code changes after setup

---

### Option 3: LangChain/LlamaIndex Plugin

**LangChain example:**
```python
from langchain.llms import OpenAI
from langchain.chains import RetrievalQA
from concise.langchain import ConciseCompressor

# Your existing RAG pipeline
llm = OpenAI()
qa = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)

# Add compression (1 line)
qa = ConciseCompressor(qa, compression_ratio=0.3)

# Use normally - compression happens automatically
result = qa.run("What is...?")
```

**How it works:**
- Plugin sits between retriever and LLM
- Compresses retrieved context before sending to LLM
- Tracks savings automatically

---

### Option 4: Coding Agents (VSCode Extension)

**Installation:**
```bash
# VSCode extension marketplace
# Search: "Concise for Copilot"
# Install → Enter API key
```

**How it works:**
1. Extension monitors your coding agent (Copilot/Cursor/Cody)
2. When agent requests codebase context, intercepts it
3. Compresses context (e.g., 50k tokens → 10k tokens)
4. Sends compressed context to coding agent
5. Shows savings in status bar: "💰 Saved $2.34 today"

**User experience:**
- Completely transparent
- Coding agent works exactly the same
- Just cheaper and faster

---

## How The Product Actually Works (Technical Deep Dive)

### Architecture

```
Developer's Code
      ↓
[Concise SDK/Wrapper]
      ↓
API Gateway (rate limiting, auth)
      ↓
Compression Service
      ↓
┌──────────────────┬──────────────────┬──────────────────┐
│   LLMLingua      │  InfiniRetri     │  Custom Models   │
│  (conservative)  │  (aggressive)    │  (optimized)     │
└──────────────────┴──────────────────┴──────────────────┘
      ↓
Cache Layer (Redis)
      ↓
Analytics/Usage Tracking (PostgreSQL)
      ↓
Return compressed text + metadata
```

### Compression Strategies (Auto-Selected)

**Strategy 1: Conservative (LLMLingua - default)**
- Compression ratio: 3-5x
- Quality loss: <2%
- Use case: Production apps, high accuracy needed
- Speed: Fast (100ms for 10k tokens)

**Strategy 2: Balanced (LLMLingua-2)**
- Compression ratio: 10-15x
- Quality loss: 3-5%
- Use case: RAG, Q&A, general use
- Speed: Very fast (30ms for 10k tokens)

**Strategy 3: Aggressive (InfiniRetri)**
- Compression ratio: 20-32x
- Quality loss: 5-10% (task-dependent)
- Use case: Summarization, where perfect accuracy not critical
- Speed: Slower (300ms for 10k tokens)

**Strategy 4: Custom (Enterprise only)**
- Fine-tuned on your data
- Optimized for your specific use case
- Highest compression with lowest quality loss

### How We Pick Strategy

**Auto mode (default):**
```python
compressed = concise.compress(
    text=long_text,
    strategy="auto"  # ← We analyze and pick best
)
```

**Our algorithm:**
1. Analyze text type (code? prose? structured data?)
2. Check user's quality tolerance (from settings)
3. Look at historical performance for similar texts
4. Pick optimal compression strategy
5. Cache decision for similar requests

**Manual override:**
```python
compressed = concise.compress(
    text=long_text,
    strategy="aggressive",  # User chooses
    target_ratio=0.05  # 20x compression
)
```

### Caching (Cost Optimization)

**Smart caching:**
- If you compress the same text twice, we return cached result
- Cache key: hash(text + strategy + ratio)
- TTL: 24 hours
- Saves you API calls, saves us compute

**Example:**
```python
# First call: compresses, takes 100ms, charges 1 credit
compressed1 = concise.compress(docs)

# Second call: cached, takes 5ms, FREE
compressed2 = concise.compress(docs)  # Same text
```

### Quality Monitoring

**We track:**
1. Compression ratio achieved
2. Processing time
3. User feedback (thumbs up/down)
4. A/B test results (when user has both compressed/uncompressed)

**Auto-adjustment:**
- If quality drops below threshold → reduce compression
- If user always uses aggressive → suggest it as default
- Continuous improvement loop

---

## Pricing Model (Detailed)

### Usage-Based Pricing (Primary Model)

**Free Tier:**
```
- 1M tokens/month compressed
- All compression strategies
- Basic analytics
- Community support
- Rate limit: 100 requests/minute
```

**Pro - $49/month:**
```
- 10M tokens/month included
- $0.50 per additional 1M tokens
- All strategies + auto-optimization
- Advanced analytics dashboard
- Email support
- Rate limit: 1000 req/min
- 99.9% SLA
```

**Team - $199/month:**
```
- 50M tokens/month included
- $0.40 per additional 1M tokens
- Everything in Pro +
- Team management (up to 10 users)
- Shared analytics
- Custom compression models
- Priority support
- Rate limit: 5000 req/min
```

**Enterprise - Custom (starts $2k/month):**
```
- Unlimited tokens OR custom volume
- $0.30 per 1M tokens (volume pricing)
- Everything in Team +
- Dedicated instance (optional)
- SOC2 compliance
- SSO/SAML
- Custom SLA (99.99%)
- Dedicated support
- On-premise option
- Custom model training
```

### Why This Pricing Works

**Calculation example (Pro user):**

User spends $10k/month on OpenAI:
- Typical prompt: 8k input tokens, 500 output tokens
- With 10x compression: 800 input, 500 output
- Savings per call: ~85% on input costs

**Math:**
```
Original cost:
  Input:  8,000 tokens × $0.00000015 = $0.0012
  Output:   500 tokens × $0.00000060 = $0.0003
  Total: $0.0015 per call

With Concise:
  Input:    800 tokens × $0.00000015 = $0.00012
  Output:   500 tokens × $0.00000060 = $0.0003
  Concise: ~100 tokens × $0.0000005  = $0.00005
  Total: $0.00047 per call

Savings: $0.001 per call (67% reduction)

If they make 100k calls/month:
  Before: $150
  After: $47 + $49 (Concise) = $96
  Total savings: $54/month

But for larger users:
  10M input tokens/month original cost: $1,500
  After compression: $150 + $49 = $199
  Savings: $1,301/month
```

**ROI is clear:** The more you use LLMs, the more you save

### Alternative: Savings-Based Pricing (Testing)

**"Pay 10% of what we save you"**

```
Month 1: You save $5,000 → Pay us $500
Month 2: You save $8,000 → Pay us $800
Month 3: You save $3,000 → Pay us $300
```

**Pros:**
- Perfect alignment of incentives
- Easy to justify ("it pays for itself")
- Scales with customer value

**Cons:**
- Requires access to customer's LLM bills (privacy concern)
- Complex tracking
- Unpredictable revenue for us

**Decision:** Start with usage-based, test savings-based with enterprise

---

## Token Accounting (How We Track)

### What We Track

**Per API call:**
```json
{
  "user_id": "user_123",
  "timestamp": "2025-11-06T10:30:00Z",
  "original_tokens": 8432,
  "compressed_tokens": 843,
  "compression_ratio": 10.0,
  "strategy_used": "llmlingua-2",
  "processing_time_ms": 45,
  "cost_saved_usd": 0.00126,
  "quality_score": 0.98
}
```

**Aggregated (shown in dashboard):**
- Total tokens compressed this month
- Total cost saved (estimated based on OpenAI pricing)
- Average compression ratio
- Most efficient strategy for your use case
- Breakdown by project/API key

### Dashboard Analytics

**User sees:**
```
This Month:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💰 Cost Saved:        $2,847.32
📊 Tokens Compressed: 18.4M / 50M
⚡ Avg Compression:   12.3x
🎯 Quality Score:     97.8%
⏱️  Avg Speed:        38ms

Top Strategies:
1. LLMLingua-2:  68% of requests
2. Conservative: 28%
3. Aggressive:    4%

Recommendations:
→ Your workload benefits from aggressive mode
  Switch to save an extra $400/month
```

### Billing Logic

**Free tier:**
- Track tokens compressed
- When hitting 1M → show upgrade prompt
- Can still use (rate limited) or hard stop (TBD)

**Paid tiers:**
- Track tokens against monthly quota
- Overage automatically billed at end of month
- Alert at 80%, 90%, 100% usage
- Option to set hard limits (prevent surprise bills)

**Enterprise:**
- Custom contract terms
- Annual prepay option (20% discount)
- Volume discounts kick in automatically

---

## Integration Examples (Real Code)

### Example 1: RAG Application

**Before Concise:**
```python
from langchain.vectorstores import Pinecone
from langchain.llms import OpenAI
from langchain.chains import RetrievalQA

# Retrieve context
retriever = Pinecone.from_existing_index("docs").as_retriever()
docs = retriever.get_relevant_documents("How do I...?")
context = "\n".join([doc.page_content for doc in docs])  # 15k tokens!

# Send to LLM
llm = OpenAI(model="gpt-4")
response = llm(f"Context: {context}\n\nQuestion: How do I...?")

# Cost: 15k input tokens = $0.00225 per query
```

**After Concise (3 lines changed):**
```python
from langchain.vectorstores import Pinecone
from langchain.llms import OpenAI
from langchain.chains import RetrievalQA
import concise  # ← Added

concise.api_key = "sk_live_..."  # ← Added

retriever = Pinecone.from_existing_index("docs").as_retriever()
docs = retriever.get_relevant_documents("How do I...?")
context = "\n".join([doc.page_content for doc in docs])  # 15k tokens

# Compress before sending
compressed_context = concise.compress(context).text  # ← Added (2k tokens!)

llm = OpenAI(model="gpt-4")
response = llm(f"Context: {compressed_context}\n\nQuestion: How do I...?")

# Cost: 2k input tokens = $0.0003 per query
# Savings: 87%
```

### Example 2: Chatbot with History

**Before:**
```python
conversation_history = [
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."},
    # ... 20 messages, 10k tokens total
]

response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=conversation_history + [{"role": "user", "content": "New question"}]
)
# Sending full 10k history every time = expensive
```

**After:**
```python
import concise

# Compress old messages, keep recent ones full
old_messages = conversation_history[:-3]  # All but last 3
recent_messages = conversation_history[-3:]  # Last 3

# Compress old context
old_context = "\n".join([f"{m['role']}: {m['content']}" for m in old_messages])
compressed = concise.compress(old_context).text

# Reconstruct
messages = [
    {"role": "system", "content": f"Previous conversation summary: {compressed}"}
] + recent_messages + [
    {"role": "user", "content": "New question"}
]

response = openai.ChatCompletion.create(model="gpt-4", messages=messages)
# Now sending 2k instead of 10k
```

### Example 3: Code Analysis

**Before:**
```python
# Analyzing a large codebase
codebase = read_directory("./src")  # 50k tokens of code

prompt = f"""
Analyze this codebase and find security vulnerabilities:

{codebase}

List all issues found.
"""

response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[{"role": "user", "content": prompt}]
)
# 50k tokens = hits context limit or very expensive
```

**After:**
```python
import concise

codebase = read_directory("./src")  # 50k tokens

# Compress codebase
compressed_code = concise.compress(
    text=codebase,
    strategy="conservative",  # Keep accuracy high for security
    target_ratio=0.2  # 5x compression → 10k tokens
).text

prompt = f"""
Analyze this codebase and find security vulnerabilities:

{compressed_code}

List all issues found.
"""

response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[{"role": "user", "content": prompt}]
)
# 10k tokens = fits in context, 80% cheaper
```

---

## Pricing Questions Answered

### Q: Why would I pay you instead of using LLMLingua directly?

**A: Time vs Money tradeoff**

**DIY with LLMLingua:**
- Initial setup: 4-8 hours
- Ongoing maintenance: 2 hours/month
- Your engineer's cost: $100/hour
- **Total: $600 setup + $200/month**

**Using Concise:**
- Setup: 5 minutes
- Maintenance: 0 hours
- **Cost: $49/month**

**Breakeven:** Month 1. You save $151/month in engineering time.

Plus you get:
- Auto-optimization (we improve compression over time)
- Analytics (see what you're saving)
- Support (we fix issues)
- Updates (new strategies automatically)

### Q: How do you calculate "cost saved"?

**A: Based on current OpenAI pricing**

```python
# Our calculation
original_cost = original_tokens * TOKEN_PRICE[model]["input"]
compressed_cost = compressed_tokens * TOKEN_PRICE[model]["input"]
concise_cost = original_tokens * 0.0000005  # Our processing fee
total_cost = compressed_cost + concise_cost
savings = original_cost - total_cost
```

**We show in dashboard:**
- "Based on GPT-4 pricing ($0.15/1M input tokens)"
- Update weekly if OpenAI changes prices
- Let enterprise customers input their actual costs

### Q: What if I use Claude/Gemini instead of OpenAI?

**A: Works the same, pricing adjusts**

- We support all major LLMs
- Dashboard lets you select your model
- Savings calculated based on that model's pricing
- Compression works regardless of target LLM

### Q: Do I pay for failed compressions?

**A: No, only successful compressions count toward quota**

If our API returns error:
- No tokens deducted
- No charge
- We eat the compute cost

### Q: What's the processing fee?

**A: Approximately $0.50 per 1M tokens compressed**

**Breakdown:**
- Our compute cost: $0.20/1M
- Infrastructure: $0.10/1M
- Margin: $0.20/1M

**Compared to savings:**
- You save: ~$100-$120/1M tokens (from LLM provider)
- You pay us: $0.50/1M
- **Net savings: $99.50-$119.50/1M tokens**

**ROI: ~200-240x**

---

## Next Questions?

Does this clarify:
- ✅ How developers integrate (4 options: direct API, wrapper, plugin, VSCode)
- ✅ How the compression actually works (strategies, caching, quality)
- ✅ How pricing works (usage-based, clear ROI)

**What else do you need to know?**

1. Technical implementation details?
2. Specific use case examples?
3. Pricing edge cases?
4. Competition comparison?

Let me know what to dive deeper on.
