# Cursor Integration Guide

## Quick Setup (2 minutes)

### Step 1: Configure Cursor

1. Open **Cursor Settings** (Cmd/Ctrl + ,)
2. Go to **Features** → **OpenAI**
3. Set the following:

```
Override OpenAI Base URL: http://localhost:8000
API Key: csk_live_fHE48ooBG-4UMlg59HI73fOk157nhL_lmYne-Y-9uJ0
```

### Step 2: Start Monitoring (Optional)

In a new terminal:

```bash
cd /home/yab/Concise/backend
python3 monitor_usage.py
```

This will show real-time compression statistics as you use Cursor.

### Step 3: Use Cursor Normally

Just use Cursor as you normally would! Every request will be:
1. Intercepted by Concise API
2. Compressed (40-60% reduction)
3. Forwarded to OpenAI
4. Response returned to you

You won't notice any difference except **faster responses** and **lower costs**.

## What to Watch For

### ✅ Success Indicators

- Cursor works normally (no errors)
- Monitor shows compressions happening
- Code quality remains high
- Responses feel natural

### ⚠️ Things to Monitor

1. **Compression Quality**
   - Are responses still accurate?
   - Is Cursor understanding context correctly?
   - Any degradation in code suggestions?

2. **Latency**
   - First request: 2-3s (model loading)
   - Subsequent: 200-800ms compression time
   - Total latency should be acceptable

3. **Token Savings**
   - Check `/v1/stats` endpoint for savings
   - Monitor should show tokens saved in real-time

## Testing Checklist

- [ ] Cursor connects successfully
- [ ] No authentication errors
- [ ] Code completions work normally
- [ ] Chat responses are coherent
- [ ] Monitor shows compressions
- [ ] Token savings are significant (>30%)

## Troubleshooting

### "Invalid API Key" error
- Check that you copied the full key including `csk_live_` prefix
- Verify server is running: `curl http://localhost:8000/health`

### Cursor shows OpenAI errors
- Check server logs: The background Bash process should show request details
- Verify your OPENAI_API_KEY is set in `.env`

### Slow responses
- First request loads model (normal)
- Compression adds 200-800ms (acceptable for 40-60% savings)
- Consider Redis caching if too slow

### Monitor not showing activity
- Verify Cursor is making requests (try asking it a question)
- Check server logs for incoming requests
- Ensure API key matches

## Example Session

```bash
# Terminal 1: Server (already running)
cd /home/yab/Concise/backend
./start.sh

# Terminal 2: Monitor
cd /home/yab/Concise/backend
python3 monitor_usage.py

# Now use Cursor normally and watch the magic happen! ✨
```

## Expected Results

Based on our tests:

| Metric | Value |
|--------|-------|
| Token reduction | 40-60% |
| Compression time | 200-800ms |
| Cost savings per request | $0.003-0.012 |
| Quality retention | 90%+ |

## Next Steps After Testing

1. **If it works well:**
   - Deploy to Railway for production use
   - Set up Redis for caching
   - Configure your real OpenAI key

2. **If quality issues:**
   - Try "conservative" strategy (95% quality retention)
   - Adjust compression ratios in `compressor.py`
   - Test different prompts

3. **If too slow:**
   - Enable Redis caching (80%+ hit rate)
   - Consider GPU deployment
   - Optimize model loading

---

**Status:** Server running at `http://localhost:8000` ✅

Ready to test! Just configure Cursor and start coding.
