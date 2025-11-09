# Concise Backend API

OpenAI proxy with automatic prompt compression using LLMLingua.

## Quick Start

### 1. Install Dependencies

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Set Up Environment Variables

```bash
cp .env.example .env
# Edit .env with your values
```

Required variables:
- `OPENAI_API_KEY` - Your OpenAI API key
- `SECRET_KEY` - Generate with: `openssl rand -hex 32`
- `REDIS_URL` - Optional, for caching (get free tier from Upstash)

### 3. Run Locally

```bash
uvicorn app.main:app --reload
```

Server starts at `http://localhost:8000`

### 4. Test the API

```bash
# Get demo API key from startup logs
# Look for: "🔑 Demo API Key: csk_live_..."

# Test compression
curl -X POST http://localhost:8000/v1/compress \
  -H "Authorization: Bearer YOUR_DEMO_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Please help me understand how to implement authentication in my application. I need to know about JWT tokens and how they work.",
    "strategy": "balanced"
  }'

# Test OpenAI proxy
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Authorization: Bearer YOUR_DEMO_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4",
    "messages": [
      {"role": "user", "content": "What is 2+2?"}
    ],
    "concise_compress": true,
    "concise_strategy": "balanced"
  }'
```

## API Endpoints

### `POST /v1/compress`
Compress text directly without sending to OpenAI.

**Request:**
```json
{
  "text": "Your long text here...",
  "strategy": "balanced",  // conservative, balanced, aggressive, extreme
  "use_cache": true
}
```

**Response:**
```json
{
  "compressed_text": "...",
  "original_tokens": 100,
  "compressed_tokens": 20,
  "tokens_saved": 80,
  "compression_ratio": 5.0,
  "cost_saved_usd": 0.0024,
  "strategy": "balanced",
  "compression_time_ms": 245.3,
  "cached": false
}
```

### `POST /v1/chat/completions`
OpenAI-compatible endpoint with automatic compression.

**Request:**
```json
{
  "model": "gpt-4",
  "messages": [
    {"role": "system", "content": "You are a helpful assistant..."},
    {"role": "user", "content": "Help me debug this code..."}
  ],
  "concise_compress": true,
  "concise_strategy": "balanced"
}
```

**Response:**
Standard OpenAI response with additional `concise` metadata:
```json
{
  "id": "...",
  "choices": [...],
  "concise": {
    "compressed": true,
    "tokens_saved": 450,
    "cost_saved_usd": 0.0135,
    "compression_ratio": 6.2,
    "strategy": "balanced",
    "processing_time_ms": 187.4
  }
}
```

### `GET /v1/stats`
Get your compression statistics.

**Response:**
```json
{
  "user_stats": {
    "total_requests": 42,
    "total_tokens_saved": 18500,
    "total_cost_saved_usd": 0.55,
    "cache_hit_rate": 78.5,
    "strategies_used": {
      "balanced": 35,
      "aggressive": 7
    }
  },
  "system_stats": {
    "total_requests": 156,
    "cache_hit_rate": 82.3,
    "avg_compression_time_ms": 203.4
  }
}
```

## Using with Cursor

1. Get your Concise API key from the dashboard
2. Open Cursor Settings
3. Go to "Models" → "OpenAI API Key"
4. Click "Override OpenAI Base URL"
5. Set to: `https://api.concise.dev` (or your Railway URL)
6. Set Authorization to: `Bearer YOUR_CONCISE_KEY`

Now all Cursor requests automatically compress! Check savings at `/v1/stats`

## Compression Strategies

| Strategy | Ratio | Speed | Quality | Use Case |
|----------|-------|-------|---------|----------|
| **conservative** | 3x | Fast | 98% | Production code |
| **balanced** | 5x | Medium | 95% | General use (default) |
| **aggressive** | 10x | Slower | 90% | Large contexts |
| **extreme** | 20x | Slowest | 85% | Massive documents |

## Performance

With caching enabled (recommended):
- Cache hit: <10ms overhead
- Cache miss: 200-500ms overhead
- Average (80% hit rate): ~100ms overhead

First request loads model (~3s), then stays in memory.

## Deployment

### Railway (Recommended - Free Tier)

1. Push code to GitHub
2. Create new project on Railway
3. Connect your GitHub repo
4. Add environment variables
5. Deploy!

Railway automatically:
- Detects Python and installs dependencies
- Runs the start command from `railway.json`
- Provides a public URL

### Manual Deployment

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export OPENAI_API_KEY=...
export SECRET_KEY=...
export REDIS_URL=...

# Run with gunicorn (production)
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## Architecture

```
┌─────────────┐
│   Cursor    │
│  (or IDE)   │
└──────┬──────┘
       │ POST /v1/chat/completions
       │ Authorization: Bearer CONCISE_KEY
       ▼
┌─────────────────────────────────┐
│     Concise API (FastAPI)       │
├─────────────────────────────────┤
│  1. Verify API key              │
│  2. Check rate limit            │
│  3. Compress messages           │
│     └─> LLMLingua (GPT-2)      │
│     └─> Redis cache             │
│  4. Forward to OpenAI           │
│  5. Track analytics             │
│  6. Return response + metadata  │
└──────┬──────────────────────────┘
       │ POST /v1/chat/completions
       │ Authorization: Bearer OPENAI_KEY
       ▼
┌─────────────┐
│   OpenAI    │
└─────────────┘
```

## Development

### Run tests
```bash
pytest tests/
```

### Format code
```bash
black app/
```

### Type checking
```bash
mypy app/
```

## Cost Analysis

Running on Railway free tier:
- 500 hours/month compute: ✅ Enough for 100-500 users
- Model size: 270MB (GPT-2 Small)
- Memory usage: ~500MB total
- Redis: Upstash free tier (10k commands/day)

**Total cost: $0/month until you exceed free tiers**

## Roadmap

- [x] Core compression engine
- [x] OpenAI proxy
- [x] API key auth
- [x] Redis caching
- [x] Analytics tracking
- [ ] PostgreSQL (replace in-memory storage)
- [ ] Web dashboard
- [ ] Stripe billing
- [ ] ONNX optimization
- [ ] GPU support (for paid tiers)
- [ ] MCP server for Claude Code

## License

MIT
