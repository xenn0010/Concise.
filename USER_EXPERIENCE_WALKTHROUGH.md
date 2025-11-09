# Concise MCP - User Experience Walkthrough

## Scenario 1: Claude Code User

### Before Concise (Normal Claude Code Usage)

**User's workflow:**

```
1. User opens Claude Code
2. Types: "Refactor the authentication module to use async/await"
3. Claude Code requests context from codebase
```

**What happens behind the scenes:**

```
Claude Code → Reads entire auth module
            → Finds related files
            → Includes type definitions
            → Adds test files for context

Total context gathered: 50,000 tokens

Context sent to Anthropic API:
{
  "model": "claude-sonnet-4",
  "messages": [{
    "role": "user",
    "content": "[50,000 tokens of code context] + user's question"
  }]
}

Cost: 50,000 tokens × $0.003/1k = $0.15 per request
```

**User sees:**
- Response from Claude (works great)
- No visibility into token usage
- Bill at end of month: surprised by costs

---

### After Installing Concise MCP (First Time Setup)

**Installation (one time, 2 minutes):**

```bash
# Step 1: Install Concise MCP
npm install -g @concise/mcp-server

# Step 2: Get API key from concise.ai
# Sign up (free tier)
# Copy API key: sk_live_abc123...

# Step 3: Configure Claude Code
# Add to ~/.claude/config.json:
{
  "mcpServers": {
    "concise": {
      "command": "concise-mcp",
      "args": ["--api-key", "sk_live_abc123..."]
    }
  }
}

# Step 4: Restart Claude Code
# Done!
```

**User sees:**
- Small notification: "✓ Concise compression active"
- Everything else looks the same

---

### After Concise (Same Task)

**User's workflow (IDENTICAL):**

```
1. User opens Claude Code
2. Types: "Refactor the authentication module to use async/await"
3. Claude Code requests context from codebase
```

**What happens behind the scenes (NEW):**

```
Claude Code → Requests context (50,000 tokens)
            ↓
Concise MCP intercepts → "I'll compress this first"
            ↓
Sends to Concise API:
POST https://api.concise.ai/v1/compress
{
  "text": "[50,000 tokens of code]",
  "strategy": "auto"
}
            ↓
Concise compresses: 50,000 → 5,000 tokens (10x)
            ↓
Returns compressed context to Claude Code
            ↓
Claude Code sends to Anthropic:
{
  "model": "claude-sonnet-4",
  "messages": [{
    "role": "user",
    "content": "[5,000 compressed tokens] + user's question"
  }]
}

Cost: 5,000 tokens × $0.003/1k = $0.015 per request
Savings: $0.135 (90%)
```

**User sees:**
- Same great response from Claude
- Status bar update: "💰 Saved $0.13"
- Everything else identical

---

### Visual Comparison

**BEFORE (Without Concise):**

```
You: "Refactor authentication to async/await"
  ↓
Claude Code gathers context: 50k tokens
  ↓
Sends to Anthropic API: 50k tokens
  ↓
You get response
  ↓
Cost: $0.15
```

**AFTER (With Concise):**

```
You: "Refactor authentication to async/await"
  ↓
Claude Code gathers context: 50k tokens
  ↓
Concise compresses: 50k → 5k tokens (10x)
  ↓
Sends to Anthropic API: 5k tokens
  ↓
You get SAME response
  ↓
Cost: $0.015
Saved: $0.135 (90%)
```

---

### What the User Sees (Visual)

**Status Bar (Bottom Right):**

```
Before:
[Claude Code]  Ready

After:
[Claude Code]  Ready  |  💰 Concise: $2.47 saved today
```

**Click to expand:**

```
╔════════════════════════════════════════╗
║  Concise Compression Stats            ║
╠════════════════════════════════════════╣
║  Today:                                ║
║    Requests: 23                        ║
║    Tokens saved: 1.2M                  ║
║    Cost saved: $2.47                   ║
║    Avg compression: 11.3x              ║
║                                        ║
║  This Month:                           ║
║    Total saved: $47.82                 ║
║    Requests: 342                       ║
║                                        ║
║  [View Dashboard] [Settings]           ║
╚════════════════════════════════════════╝
```

---

### Real Example: Full Session

**User's afternoon coding session:**

```
12:00 PM - "Explain this authentication flow"
  Without Concise: 35k tokens → $0.105
  With Concise:     4k tokens → $0.012
  Saved: $0.093

12:15 PM - "Add error handling to login function"
  Without Concise: 28k tokens → $0.084
  With Concise:     3k tokens → $0.009
  Saved: $0.075

12:30 PM - "Write tests for the auth module"
  Without Concise: 45k tokens → $0.135
  With Concise:     5k tokens → $0.015
  Saved: $0.120

1:00 PM - "Debug why JWT token expires early"
  Without Concise: 52k tokens → $0.156
  With Concise:     6k tokens → $0.018
  Saved: $0.138

1:30 PM - "Refactor to use middleware pattern"
  Without Concise: 38k tokens → $0.114
  With Concise:     4k tokens → $0.012
  Saved: $0.102

───────────────────────────────────────
Total Session (5 requests):
  Without Concise: $0.594
  With Concise:    $0.066
  Saved:           $0.528 (89%)
```

**End of day notification:**

```
🎉 Great session! You saved $0.53 today with Concise

Over a month of similar usage, that's ~$15.90 saved
Your Concise plan: Free tier (no cost)

Net savings: $15.90/month
```

---

## Scenario 2: Cursor User

### Before Concise

**User's workflow:**

```
1. Open Cursor
2. Open large project (e.g., Next.js app)
3. Cmd+K: "Add authentication to this app"
4. Cursor Tab: auto-completion while coding
```

**What happens:**

```
Cursor → Indexes entire codebase
       → For EACH request, sends relevant context
       → Large codebases = huge context

Example session:
- Request 1: 80k tokens (include all routes)
- Request 2: 65k tokens (include components)
- Request 3: 70k tokens (include API layer)
- Request 4: 55k tokens (include auth related)

Daily usage: 20-50 requests
Monthly tokens: ~30M tokens
Cost at $0.003/1k: ~$90/month

Plus Cursor subscription: $20/month
Total: $110/month
```

---

### After Installing Concise

**Installation:**

```bash
# Same as Claude Code
npm install -g @concise/mcp-server

# Configure Cursor
# Add to Cursor settings:
{
  "mcpServers": {
    "concise": {
      "command": "concise-mcp",
      "args": ["--api-key", "sk_live_abc123..."]
    }
  }
}
```

**What changes:**

```
Cursor → Indexes entire codebase (same)
       → Prepares context (same)
       → Concise compresses before sending
       → Sends 10x less tokens

Example session:
- Request 1: 80k → 8k tokens (compressed)
- Request 2: 65k → 7k tokens (compressed)
- Request 3: 70k → 7k tokens (compressed)
- Request 4: 55k → 6k tokens (compressed)

Daily usage: 20-50 requests (same)
Monthly tokens: ~3M tokens (10x less)
Cost at $0.003/1k: ~$9/month

Plus Cursor: $20/month
Plus Concise: $19/month (Developer tier)
Total: $48/month

Savings: $62/month (56%)
```

---

### Visual Workflow

**BEFORE:**

```
You working in Cursor:
  ↓
[Cmd+K] "Add user profile page"
  ↓
Cursor analyzes codebase:
  - components/: 25k tokens
  - pages/: 20k tokens
  - api/: 15k tokens
  - utils/: 10k tokens
  Total: 70k tokens
  ↓
Sends to OpenAI: 70k tokens
  ↓
Cost: $0.21
```

**AFTER:**

```
You working in Cursor:
  ↓
[Cmd+K] "Add user profile page"
  ↓
Cursor analyzes codebase:
  - components/: 25k tokens
  - pages/: 20k tokens
  - api/: 15k tokens
  - utils/: 10k tokens
  Total: 70k tokens
  ↓
Concise compresses: 70k → 7k tokens
  ↓
Sends to OpenAI: 7k tokens
  ↓
Cost: $0.021
Saved: $0.189 (90%)
```

---

### Real Example: Building a Feature

**Task: "Build a user authentication system"**

**Session breakdown:**

```
Request 1: "Create login page"
  Context: All pages + components (80k tokens)
  Compressed: 8k tokens
  Saved: $0.216

Request 2: "Add API route for login"
  Context: All API routes + auth utils (65k tokens)
  Compressed: 7k tokens
  Saved: $0.174

Request 3: "Connect frontend to backend"
  Context: Pages + API + utils (75k tokens)
  Compressed: 8k tokens
  Saved: $0.201

Request 4: "Add JWT token handling"
  Context: Auth files + middleware (50k tokens)
  Compressed: 5k tokens
  Saved: $0.135

Request 5: "Write tests"
  Context: All auth code + test utils (60k tokens)
  Compressed: 6k tokens
  Saved: $0.162

Request 6-20: (auto-completion, small edits)
  Saved: ~$1.50

───────────────────────────────────────
Total Feature (20 requests):
  Without Concise: ~$3.00
  With Concise:    ~$0.30
  Saved:           ~$2.70 (90%)
```

---

## Key Differences: Claude Code vs Cursor

### Claude Code
- **Pattern:** Fewer, larger requests
- **Typical:** 10-20 requests/day
- **Context size:** 30-60k tokens each
- **Monthly savings:** $15-30

### Cursor
- **Pattern:** Many small + medium requests
- **Typical:** 30-50 requests/day
- **Context size:** 20-80k tokens each
- **Monthly savings:** $50-100

**Both benefit significantly from compression.**

---

## Behind The Scenes: How MCP Works

### The MCP Protocol

```
┌─────────────┐
│ Claude Code │
│  or Cursor  │
└──────┬──────┘
       │
       │ MCP Protocol
       │ "I need context for X"
       ↓
┌──────────────┐
│ Concise MCP  │
│   Server     │
└──────┬───────┘
       │
       │ 1. Receive context request
       │ 2. Read files/codebase
       │ 3. Compress via Concise API
       │ 4. Return compressed context
       │
       ↓
┌─────────────┐
│ Claude Code │
│  or Cursor  │
└──────┬──────┘
       │
       │ Send to LLM API
       │ (compressed context)
       ↓
┌─────────────┐
│  Anthropic  │
│  or OpenAI  │
└─────────────┘
```

### What Concise MCP Does

**Tools provided to Claude Code/Cursor:**

```json
{
  "tools": [
    {
      "name": "get_file_context",
      "description": "Get compressed file contents",
      "handler": "compress_and_return_file"
    },
    {
      "name": "get_directory_context",
      "description": "Get compressed directory tree",
      "handler": "compress_and_return_directory"
    },
    {
      "name": "search_codebase",
      "description": "Search and return compressed results",
      "handler": "search_and_compress"
    }
  ]
}
```

**When coding agent calls these tools:**
1. Concise MCP intercepts
2. Gathers the requested context
3. Sends to Concise API for compression
4. Caches result (same file = instant return)
5. Returns compressed context
6. Agent uses it like normal context

**Agent doesn't know it's compressed. It just works.**

---

## Smart Caching (The Secret Sauce)

### How It Saves Even More Money

**Scenario: Working on same file**

```
10:00 AM - Request: "Explain auth.js"
  → File not in cache
  → Compress: 5000 tokens → 500 tokens
  → Cost: $0.00025 (compression)
  → Cache for 1 hour

10:15 AM - Request: "Add error handling to auth.js"
  → File in cache! (same content)
  → Return cached compression instantly
  → Cost: $0 (cache hit)

10:30 AM - Request: "Refactor auth.js"
  → File in cache! (same content)
  → Return cached compression instantly
  → Cost: $0 (cache hit)

10:45 AM - User edits auth.js
  → File changed
  → Re-compress: 5100 tokens → 510 tokens
  → Cost: $0.00025
  → Update cache

11:00 AM - Request: "Test auth.js changes"
  → File in cache! (new version)
  → Return cached compression
  → Cost: $0
```

**Result:**
- 4 requests
- Only 2 compressions needed
- 50% cache hit rate
- Even MORE savings

**Typical cache hit rates:**
- Day 1: 30-40%
- After a week: 60-70%
- Established project: 80%+

---

## Configuration Options (Power User)

### User can customize:

```json
// ~/.concise/config.json
{
  "compression": {
    "strategy": "auto",        // or "conservative", "aggressive"
    "cache_duration": 3600,    // seconds
    "file_types": {
      ".js": "balanced",
      ".ts": "balanced",
      ".md": "aggressive",     // docs can handle more compression
      ".json": "conservative"  // config files need accuracy
    }
  },

  "performance": {
    "parallel_compression": true,
    "max_cache_size": "500MB"
  },

  "privacy": {
    "send_telemetry": true,
    "cache_locally": true
  }
}
```

---

## Pricing Impact (Real Numbers)

### Cursor User Example

**Heavy user profile:**
- Uses Cursor 5 days/week
- 40 requests/day
- Average 60k tokens/request

**Monthly usage:**
```
40 requests/day × 20 days = 800 requests
800 × 60k tokens = 48M tokens

Without Concise:
48M × $0.003/1k = $144/month in API costs
Plus Cursor: $20/month
Total: $164/month
```

**With Concise (10x compression):**
```
48M tokens → 4.8M compressed
4.8M × $0.003/1k = $14.40/month in API costs
Plus Cursor: $20/month
Plus Concise Developer: $19/month
Total: $53.40/month

Savings: $110.60/month (67%)
Annual savings: $1,327/year
```

**ROI on Concise subscription:**
Pays for itself 5.8x over

---

## The Magic Moment

**What users say:**

Before:
> "I love Cursor but the API costs are killing me.
> I'm spending $150/month on top of the subscription."

After installing Concise:
> "Holy shit. I've saved $87 this month.
> Concise costs $19 and saved me $87.
> That's $68 pure profit. Why isn't everyone using this?"

---

## Edge Cases & Smart Handling

### What if compression breaks something?

**Concise MCP has safeguards:**

```javascript
// Automatic quality detection
if (compression_ratio > 15x) {
  // Very aggressive, might lose context
  // Run test: does LLM still understand?

  test_prompt = compressed_context + "\nSummarize this code"
  test_response = llm.query(test_prompt)

  if (test_response.includes("unclear") ||
      test_response.includes("not enough context")) {
    // Compression too aggressive, reduce it
    retry_with_compression(10x)
  }
}
```

**Fallback modes:**
1. If API error → Use uncompressed (fail safe)
2. If quality low → Reduce compression automatically
3. If user reports issue → Disable for that file type

---

## Analytics Dashboard (What User Sees)

**Visit concise.ai/dashboard:**

```
╔══════════════════════════════════════════════════════╗
║  Concise Dashboard - November 2025                   ║
╠══════════════════════════════════════════════════════╣
║                                                      ║
║  💰 Total Saved This Month: $87.32                   ║
║                                                      ║
║  📊 Usage Stats:                                     ║
║    • Requests compressed: 847                        ║
║    • Tokens saved: 42.3M                             ║
║    • Avg compression: 11.2x                          ║
║    • Cache hit rate: 73%                             ║
║                                                      ║
║  📈 Trend:                                           ║
║    Week 1: $18.23                                    ║
║    Week 2: $21.47                                    ║
║    Week 3: $24.12                                    ║
║    Week 4: $23.50                                    ║
║                                                      ║
║  🎯 Top Projects:                                    ║
║    1. my-saas-app:      $42.18 saved                 ║
║    2. client-website:   $28.94 saved                 ║
║    3. side-project:     $16.20 saved                 ║
║                                                      ║
║  💳 Current Plan: Developer ($19/month)              ║
║    Tokens used: 2.1M / 2M included                   ║
║    Overage: 100k × $1/1M = $0.10                     ║
║    This month's bill: $19.10                         ║
║                                                      ║
║    💡 You're saving $68.22/month net                 ║
║       (ROI: 3.6x)                                    ║
║                                                      ║
╚══════════════════════════════════════════════════════╝

[View Detailed Stats] [Upgrade Plan] [Settings]
```

---

## Bottom Line: User Experience

### Installation:
- **Time:** 2 minutes
- **Difficulty:** Copy/paste 3 commands
- **Changes to workflow:** Zero

### Daily use:
- **What changes:** Nothing visible
- **What you notice:** Status bar showing savings
- **Impact:** 50-90% lower API costs

### Value:
- **Cursor user:** Save $50-150/month, pay $19
- **Claude Code user:** Save $15-50/month, pay $19 or free tier
- **Net benefit:** $0-130/month pure savings

### Why it works:
- ✅ Invisible (no workflow change)
- ✅ Automatic (no thinking required)
- ✅ Immediate value (save money today)
- ✅ Sticky (once installed, why remove it?)

---

**Does this make sense? Can you see why someone would use it?**
