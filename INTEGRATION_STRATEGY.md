# Concise - Integration & Pricing Strategy v2

## Two-Track Approach

### Track 1: MCP Server (For Coding Agents)
### Track 2: API/SDK (For General AI Apps)

---

## Track 1: MCP Server for Coding Agents

### What is MCP?

**Model Context Protocol** (Anthropic's standard)
- Standard way for AI apps to access external context
- Works with: Claude Code, Cursor, Windsurf, Cline, etc.
- Better than VSCode extension (model-agnostic, standardized)

### How Our MCP Server Works

**Installation:**
```bash
npm install -g @concise/mcp-server

# Configure in your AI tool
{
  "mcpServers": {
    "concise": {
      "command": "concise-mcp",
      "args": ["--api-key", "sk_live_..."]
    }
  }
}
```

**What It Does:**
1. Coding agent requests codebase context
2. Our MCP server intercepts
3. Compresses the context (50k tokens → 5k tokens)
4. Returns compressed context to coding agent
5. Agent uses compressed context (cheaper, faster)

**User Experience:**
```
Developer types in Cursor:
"Refactor the authentication module"

Behind the scenes:
→ Cursor requests full codebase context (100k tokens)
→ Concise MCP compresses to 10k tokens
→ Cursor gets compressed context
→ Developer sees same quality response
→ Costs 90% less
```

**MCP Tools We Provide:**

```typescript
// Our MCP server exposes these tools:

{
  "tools": [
    {
      "name": "compress_codebase",
      "description": "Compress entire codebase context",
      "inputSchema": {
        "type": "object",
        "properties": {
          "path": { "type": "string" },
          "compression_ratio": { "type": "number" }
        }
      }
    },
    {
      "name": "compress_context",
      "description": "Compress arbitrary text context",
      "inputSchema": {
        "type": "object",
        "properties": {
          "text": { "type": "string" },
          "strategy": { "type": "string" }
        }
      }
    },
    {
      "name": "get_savings",
      "description": "Get current savings stats",
      "inputSchema": {
        "type": "object",
        "properties": {}
      }
    }
  ]
}
```

**Why MCP is Perfect for Coding Agents:**

✅ **Universal:** Works with ANY MCP-compatible coding agent
✅ **Transparent:** Agent doesn't know context is compressed
✅ **Fast:** Local processing + API call
✅ **Trackable:** We see every compression in real-time
✅ **Sticky:** Once configured, always works

### MCP-Specific Features

**Smart Caching:**
```javascript
// If compressing same file multiple times
compress("src/auth.ts") // First time: compress + cache
compress("src/auth.ts") // Second time: instant return from cache
```

**File-Level Compression:**
```javascript
// Compress entire project intelligently
{
  "src/": {
    "strategy": "aggressive",  // Code can handle more compression
    "ratio": 0.1              // 10x compression
  },
  "docs/": {
    "strategy": "conservative", // Keep docs readable
    "ratio": 0.3               // 3x compression
  }
}
```

**Real-Time Stats:**
```bash
# Status bar in coding agent
💰 Concise: Saved $12.34 today | 234k tokens compressed
```

---

## Track 2: API/SDK (For General AI Apps)

### Standard REST API

**Endpoint:**
```
POST https://api.concise.ai/v1/compress
```

**Request:**
```json
{
  "text": "Long text here...",
  "strategy": "auto",
  "target_ratio": 0.1,
  "metadata": {
    "user_id": "optional",
    "project": "optional"
  }
}
```

**Response:**
```json
{
  "compressed_text": "Compressed version...",
  "original_tokens": 10000,
  "compressed_tokens": 1000,
  "compression_ratio": 10.0,
  "strategy_used": "llmlingua-2",
  "processing_time_ms": 45,
  "cost_saved_usd": 1.47,
  "usage_id": "comp_abc123"
}
```

### Python SDK

```python
import concise

concise.api_key = "sk_live_..."

# Basic compression
result = concise.compress("Long text...")

print(result.compressed_text)
print(f"Saved: ${result.cost_saved}")
```

### JavaScript/TypeScript SDK

```typescript
import Concise from 'concise-ai';

const concise = new Concise({ apiKey: 'sk_live_...' });

const result = await concise.compress({
  text: 'Long text...',
  strategy: 'auto'
});

console.log(result.compressedText);
console.log(`Saved: $${result.costSaved}`);
```

### LangChain Integration

```python
from langchain.llms import OpenAI
from concise.langchain import ConciseCompressor

llm = OpenAI()
compressed_llm = ConciseCompressor(llm)

# Automatic compression on all calls
response = compressed_llm("Long prompt...")
```

---

## Pricing Strategy v2: Hybrid Model

### Problem with Pure Subscription
- Small users overpay
- Large users underpay
- Hard to predict costs

### Problem with Pure Usage-Based
- Unpredictable bills
- Users scared to use it
- Low adoption

### Solution: Hybrid (Subscription + Usage)

---

## Pricing Tiers

### Free Tier
```
Cost: $0/month

Included:
- 500k tokens/month compressed
- Basic compression (LLMLingua)
- API + MCP server access
- Community support
- Rate limit: 10 req/min

Overage:
- $2 per 1M tokens (high rate to encourage upgrade)
```

**Target:** Hobbyists, testing, small projects

---

### Developer - $19/month

```
Subscription: $19/month

Included:
- 2M tokens/month
- All compression strategies
- API + MCP server
- Email support
- Rate limit: 100 req/min
- Basic analytics

Overage:
- $1 per 1M tokens
```

**Example:**
```
Month 1: Used 2M tokens → Pay $19
Month 2: Used 5M tokens → Pay $19 + (3M × $1) = $22
Month 3: Used 1M tokens → Pay $19
```

**Target:** Individual developers, small teams

---

### Professional - $79/month

```
Subscription: $79/month

Included:
- 10M tokens/month
- All strategies + auto-optimization
- API + MCP server
- Priority email support
- Rate limit: 1000 req/min
- Advanced analytics
- Team management (5 users)

Overage:
- $0.60 per 1M tokens
```

**Example:**
```
Month 1: Used 10M tokens → Pay $79
Month 2: Used 25M tokens → Pay $79 + (15M × $0.60) = $88
Month 3: Used 8M tokens → Pay $79
```

**Target:** Growing startups, small engineering teams

---

### Business - $299/month

```
Subscription: $299/month

Included:
- 50M tokens/month
- Everything in Professional +
- Custom compression models
- Dedicated support channel
- Rate limit: 5000 req/min
- Team management (20 users)
- SSO/SAML
- 99.9% SLA

Overage:
- $0.40 per 1M tokens
```

**Example:**
```
Month 1: Used 50M tokens → Pay $299
Month 2: Used 120M tokens → Pay $299 + (70M × $0.40) = $327
Month 3: Used 45M tokens → Pay $299
```

**Target:** Scale-ups, mid-size companies

---

### Enterprise - Custom

```
Subscription: Custom (typically $2k-10k/month)

Included:
- Custom token quota (e.g., 500M/month)
- Dedicated instances
- Custom SLA (99.99%)
- On-premise option
- Custom model training
- Unlimited users
- Dedicated CSM
- SOC2/HIPAA compliance

Overage:
- $0.20-$0.30 per 1M tokens (negotiated)
```

**Target:** Large enterprises, Fortune 500

---

## Per-Compression Pricing Breakdown

### How We Calculate Per-Compression Cost

**Base formula:**
```
cost_per_compression = (original_tokens / 1_000_000) × rate_per_million
```

**Examples:**

**Free tier user (overage rate: $2/1M):**
```
10k token compression = (10,000 / 1,000,000) × $2 = $0.02
100k tokens = $0.20
1M tokens = $2.00
```

**Professional user (overage rate: $0.60/1M):**
```
10k tokens = $0.006
100k tokens = $0.06
1M tokens = $0.60
```

**Enterprise user (negotiated: $0.25/1M):**
```
10k tokens = $0.0025
100k tokens = $0.025
1M tokens = $0.25
```

### Tracking & Billing

**Real-time tracking:**
```json
// Every compression creates a usage record
{
  "user_id": "user_123",
  "timestamp": "2025-11-06T10:30:00Z",
  "original_tokens": 8432,
  "tier": "professional",
  "included_quota": 10000000,
  "used_this_month": 7234567,
  "overage_rate": 0.60,
  "cost_this_call": 0.0000,  // Still within quota
  "remaining_quota": 2765433
}
```

**End of month billing:**
```
User: user_123
Tier: Professional ($79/month)

Usage this month:
━━━━━━━━━━━━━━━━━━━━━━━━━━
Included quota: 10M tokens
Actual usage:   23.4M tokens
Overage:        13.4M tokens

Charges:
Subscription:   $79.00
Overage:        13.4M × $0.60 = $8.04
━━━━━━━━━━━━━━━━━━━━━━━━━━
Total:          $87.04
```

**Dashboard shows:**
```
Current Usage This Month:
━━━━━━━━━━━━━━━━━━━━━━━━━━
[████████████░░░░░░] 23.4M / 10M (234%)

Estimated bill: $87.04
($79 subscription + $8.04 overage)

Projected end-of-month: $112.50
(based on current usage trend)

⚠️ Upgrade to Business tier to save $43/month
```

---

## Why This Hybrid Model Works

### For Users:

✅ **Predictable base cost:** Know minimum is $19/$79/$299
✅ **Fair overage:** Only pay for what you use above quota
✅ **No waste:** Don't pay for unused quota (unlike pure subscription)
✅ **No surprises:** Dashboard shows projected bill in real-time
✅ **Flexible:** Usage varies month-to-month? You only pay for peaks

### For Us:

✅ **Recurring revenue:** Predictable $X per user minimum
✅ **Scale revenue:** Heavy users pay more automatically
✅ **Lower churn:** No bill shock = happy customers
✅ **Upsell path:** "Upgrade to higher tier to reduce overage costs"
✅ **Simple pricing:** Easy to explain

---

## Pricing Strategy by Customer Type

### Individual Developer (Coding Agent User)

**Profile:**
- Uses Cursor/Claude Code
- ~5M tokens/month
- Price sensitive

**Best fit:** Developer tier ($19/month)
```
Base: $19
Overage: 3M × $1 = $3
Total: $22/month

Saves them ~$40/month on Cursor
ROI: 2x
```

### Startup (RAG Application)

**Profile:**
- Building AI chatbot
- ~30M tokens/month
- Growing fast

**Best fit:** Professional tier ($79/month)
```
Base: $79
Overage: 20M × $0.60 = $12
Total: $91/month

Saves them ~$3k/month on OpenAI
ROI: 33x
```

### Mid-Size Company (Multiple AI Products)

**Profile:**
- 10-person AI team
- ~200M tokens/month
- Compliance needs

**Best fit:** Business tier ($299/month)
```
Base: $299
Overage: 150M × $0.40 = $60
Total: $359/month

Saves them ~$25k/month on LLM costs
ROI: 70x
```

### Enterprise (Fortune 500)

**Profile:**
- 100+ developers using AI tools
- 2B+ tokens/month
- Requires SOC2, on-prem option

**Best fit:** Enterprise (custom)
```
Negotiated: $5k/month for 500M included
Overage: 1.5B × $0.25 = $375k
Total: $380k/month

Wait, that's broken. Let me recalculate...

Actually at enterprise scale:
Annual contract: $500k/year
Includes: 10B tokens/year (~833M/month)
Overage rate: $0.20/1M

If they use 2B/month = 24B/year:
Base: $500k
Overage: 14B × $0.20 = $2.8M

Hmm, that's too expensive. Better to do:
Annual contract: $2M/year (unlimited tokens)

They save ~$20M/year on LLM costs
ROI: 10x
```

---

## Pricing Comparison vs Alternatives

### vs DIY (LLMLingua open-source)

**DIY Cost:**
```
Engineer setup: 8 hours × $100/hr = $800
Monthly maintenance: 2 hours × $100/hr = $200/month
Server costs: $100/month
Total Year 1: $800 + ($300 × 12) = $4,400
```

**Concise Cost (Professional):**
```
Year 1: $79 × 12 + overage ~$100 = $1,048
Savings: $3,352 vs DIY
```

### vs OpenAI's Native Compression (if they build it)

**Advantages we have:**
- ✅ Model-agnostic (works with Claude, Gemini, etc.)
- ✅ Multiple strategies (they'd only have one)
- ✅ Already exists (first mover advantage)
- ✅ Independent (not locked to one provider)

**Pricing edge:**
- We can undercut them because we don't have LLM inference costs
- They'd probably bundle it into existing pricing
- We can offer better margins

---

## MCP-Specific Pricing Considerations

### Problem: MCP Usage is Different

**Coding agent pattern:**
- Hundreds of small compressions per day
- Lots of repeated content (same files)
- Caching is critical

**Traditional API pattern:**
- Fewer, larger compressions
- More diverse content
- Less caching opportunity

### Solution: MCP Caching Credits

**How it works:**
```
User compresses same file 10 times in a day:
- First compression: 10k tokens → charged
- Next 9 compressions: cached → FREE

Effective cost: 10k tokens (not 100k)
```

**Pricing impact:**
```
Without caching:
100 compressions × 10k tokens = 1M tokens = $0.60

With caching (80% hit rate):
20 compressions charged × 10k = 200k tokens = $0.12

Savings: 80% on compression costs
```

**We promote this:**
"MCP users typically save 80% vs API due to smart caching"

---

## Usage Tracking & Analytics

### What Users See (Dashboard)

**Overview:**
```
Current Period: Nov 1 - Nov 30, 2025
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💰 Total Saved This Month: $2,847.32

📊 Usage:
   Total compressed: 23.4M tokens
   Included quota:   10M tokens
   Overage:         13.4M tokens

💳 Billing:
   Subscription:    $79.00
   Overage:         $8.04
   ━━━━━━━━━━━━━━━━━━━━━━━━━━
   Current total:   $87.04

📈 Projection (if trend continues):
   End of month:    $112.50

💡 Recommendation:
   Upgrade to Business tier ($299/month)
   You'll save $45/month at your usage level
```

**Breakdown by Integration:**
```
Usage by Source:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MCP Server:     18.2M tokens (78%)
Python SDK:      3.1M tokens (13%)
LangChain:       2.1M tokens  (9%)

Top Projects:
1. cursor-workspace:  12.4M tokens
2. production-api:     5.3M tokens
3. dev-chatbot:        3.2M tokens
```

**Compression Stats:**
```
Performance:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Avg compression ratio:  11.2x
Avg quality score:      96.8%
Avg processing time:    42ms

Strategy breakdown:
- Conservative:  23% (slower but safer)
- Balanced:      68% (recommended)
- Aggressive:     9% (max savings)

Cache hit rate:  76% (MCP), 12% (API)
```

---

## Upsell Strategy

### Automated Upgrade Prompts

**When user hits 80% of quota:**
```
Email + Dashboard notification:

"You've used 8M of your 10M token quota this month.

At your current pace, you'll hit the limit in 6 days.

Upgrade to Professional for 5x more quota ($79/month)
or continue with overage charges ($1 per 1M tokens).

[Upgrade Now] [Set Usage Alert]
```

**When overage exceeds tier difference:**
```
Email:

"Hi [Name],

You paid $91 this month on the Professional tier
($79 + $12 overage).

If you upgraded to Business ($299/month), you'd
get 50M tokens included and only pay for actual usage.

Based on your last 3 months, you'd save $43/month.

[See Detailed Comparison]
```

**For MCP power users:**
```
Dashboard notification:

"💡 Tip: You're compressing the same files repeatedly.

Your cache hit rate is 82%, saving you $X/month.

Want to save even more? Upgrade to Business tier
for custom caching strategies.

[Learn More]
```

---

## Implementation Plan

### Phase 1: API + Basic Pricing (Week 1-2)

**Build:**
- REST API with compression
- Usage tracking (tokens per user)
- Simple billing (Stripe)
- Free + Professional tier only

**Launch:**
- Python SDK
- Basic dashboard
- Documentation

### Phase 2: MCP Server (Week 3-4)

**Build:**
- MCP server implementation
- File-level compression
- Smart caching
- Real-time stats

**Launch:**
- NPM package: `@concise/mcp-server`
- MCP-specific docs
- Cursor/Claude Code tutorials

### Phase 3: Advanced Features (Month 2)

**Build:**
- LangChain/LlamaIndex plugins
- JavaScript SDK
- Advanced analytics
- Team management

**Launch:**
- Developer + Business tiers
- Team features
- Upgrade prompts

### Phase 4: Enterprise (Month 3+)

**Build:**
- SSO/SAML
- SOC2 compliance
- Custom models
- Dedicated instances

**Launch:**
- Enterprise tier
- Sales process
- Customer success

---

## Pricing FAQs

**Q: What if I go over my quota?**
A: You're automatically charged the overage rate. No service interruption. You can set hard limits if you prefer.

**Q: Can I change tiers mid-month?**
A: Yes. You're charged pro-rata. Unused quota doesn't roll over.

**Q: What counts as a "token"?**
A: We count original (uncompressed) tokens. If you compress 10k tokens, we charge for 10k, not the compressed size.

**Q: Why charge for original tokens, not compressed?**
A: Because your savings are based on original tokens. We align pricing with value delivered.

**Q: Do cached compressions count toward quota?**
A: No. Cache hits are free. Only new compressions count.

**Q: Can I pay annually?**
A: Yes. 2 months free (pay for 10, get 12). Overage charges still monthly.

**Q: What if OpenAI drops their prices?**
A: You still save the same %. If they charge $0.10/1M instead of $0.15/1M, you still save ~80%.

---

## Summary: The Winning Formula

**Two Integrations:**
1. MCP Server → Coding agents (transparent, cached, sticky)
2. API/SDK → General AI apps (flexible, powerful)

**Hybrid Pricing:**
- Base subscription (predictable revenue)
- Usage-based overage (fair, scales with value)
- Per-compression tracking (transparent)

**Growth Path:**
- Free → Developer ($19) → Professional ($79) → Business ($299) → Enterprise (custom)
- Users upgrade as they see more value
- Clear ROI at every tier

**This works because:**
✅ Fair (pay for what you use)
✅ Predictable (base + overage)
✅ Scalable (from $0 to $millions)
✅ Simple (easy to understand)
✅ Aligned (we win when you save more)

---

**Does this pricing model make sense?**

Should we:
1. Start building the API + pricing system
2. Prototype the MCP server first
3. Refine pricing more before building

What's next?
