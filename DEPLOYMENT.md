# Deployment Guide - Railway

Deploy Concise to production in 15 minutes for $0.

---

## Prerequisites

- [x] Working local setup (see QUICKSTART.md)
- [ ] GitHub account
- [ ] Railway account (free - sign up at railway.app)
- [ ] OpenAI API key
- [ ] Upstash Redis (optional, free tier)

---

## Step 1: Prepare Repository (3 minutes)

### Initialize Git (if not already)

```bash
cd /home/yab/Concise

git init
git add .
git commit -m "Initial commit - Concise compression API"
```

### Create GitHub Repository

1. Go to github.com
2. Click "New repository"
3. Name: `concise-api`
4. Make it **Private** (your API keys will be in env vars)
5. Don't initialize with README (we have one)
6. Click "Create repository"

### Push to GitHub

```bash
# Add remote
git remote add origin https://github.com/YOUR_USERNAME/concise-api.git

# Push
git branch -M main
git push -u origin main
```

---

## Step 2: Set Up Railway (5 minutes)

### Create Railway Account

1. Go to [railway.app](https://railway.app)
2. Click "Login"
3. Sign in with GitHub
4. Authorize Railway

### Create New Project

1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Choose your `concise-api` repository
4. Railway will detect it's a Python app

### Configure Build

Railway auto-detects everything from:
- `requirements.txt` - dependencies
- `railway.json` - build config
- `Procfile` - start command

No manual configuration needed!

---

## Step 3: Add Environment Variables (3 minutes)

In your Railway project:

1. Click on your service
2. Go to "Variables" tab
3. Click "New Variable"

### Required Variables

```bash
OPENAI_API_KEY=sk-your-real-openai-key-here
SECRET_KEY=generate-new-one-with-openssl-rand-hex-32
ENVIRONMENT=production
DEBUG=false
```

### Optional but Recommended

```bash
# Upstash Redis (free tier)
REDIS_URL=redis://default:password@host.upstash.io:6379

# Sentry error tracking (optional)
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project

# Rate limiting
RATE_LIMIT_PER_MINUTE=60
```

### Get Free Redis from Upstash

1. Go to [upstash.com](https://upstash.com)
2. Sign up (free)
3. Click "Create Database"
4. Choose "Global" for best performance
5. Click "Create"
6. Copy the "Connection String" (Redis URL)
7. Paste into Railway `REDIS_URL` variable

---

## Step 4: Deploy (2 minutes)

Railway automatically deploys when you add variables.

Watch the build logs:
```
Building...
Installing dependencies...
Starting server...
✅ Deployed successfully
```

### Get Your URL

1. Go to "Settings" tab
2. Scroll to "Domains"
3. Click "Generate Domain"
4. You'll get: `your-app.up.railway.app`

**This is your production API URL!**

---

## Step 5: Test Production Deployment (2 minutes)

### Test Health Check

```bash
curl https://your-app.up.railway.app/health
```

Should return:
```json
{
  "status": "healthy",
  "services": {
    "compressor": "ready",
    "cache": true,
    "openai": true
  }
}
```

### Get Demo API Key

Check Railway logs (in Dashboard):
```
🔑 Demo API Key: csk_live_xxxxxxxxxxxxx
```

**Copy this key!**

### Test Compression

```bash
curl -X POST https://your-app.up.railway.app/v1/compress \
  -H "Authorization: Bearer YOUR_DEMO_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Please help me understand how to implement authentication with JWT tokens in my application.",
    "strategy": "balanced"
  }'
```

Should return compression results.

---

## Step 6: Configure Cursor for Production (1 minute)

1. Open Cursor Settings
2. Go to "Models" → "OpenAI"
3. Override OpenAI Base URL
4. Set to: `https://your-app.up.railway.app`
5. Authorization: `Bearer YOUR_DEMO_KEY`

**Done! You're now using production compression.**

Try asking Cursor a question, then check stats:

```bash
curl https://your-app.up.railway.app/v1/stats \
  -H "Authorization: Bearer YOUR_DEMO_KEY"
```

---

## Monitoring Your Deployment

### Railway Dashboard

- **Metrics:** CPU, Memory, Network usage
- **Logs:** Real-time server logs
- **Deployments:** History of all deploys

### Check Server Status

```bash
# Health check
curl https://your-app.up.railway.app/health

# Stats
curl https://your-app.up.railway.app/v1/stats \
  -H "Authorization: Bearer YOUR_DEMO_KEY"
```

### View Logs

In Railway:
1. Click your service
2. Go to "Deployments"
3. Click latest deployment
4. See real-time logs

---

## Cost Monitoring

### Railway Free Tier Limits

```
✅ $5 credit per month
✅ 500 execution hours
✅ 512 MB memory
✅ 1 GB disk
```

**This supports:**
- 100-500 free tier users
- ~10,000 compressions/day
- 80% cache hit rate
- 24/7 uptime

### When You'll Need to Pay

**Scenario 1: Free tier runs out**
- Traffic exceeds $5/month in compute
- Solution: Upgrade to Hobby plan ($5/month)

**Scenario 2: Need more resources**
- 100+ active users
- High compression volume
- Solution: Upgrade to Pro plan ($20/month)

**But by then you should have revenue!**

If 50 users pay $29/month = $1,450 MRR
Minus $20 Railway = $1,430 profit 💰

---

## Custom Domain (Optional - $10/year)

### Buy Domain

1. Go to Namecheap, Cloudflare, or any registrar
2. Buy domain: `concise.dev` (~$12/year)

### Configure DNS

In Railway:
1. Go to "Settings" → "Domains"
2. Click "Custom Domain"
3. Enter: `api.concise.dev`
4. Railway gives you CNAME record

In your DNS provider:
```
Type: CNAME
Name: api
Value: your-app.up.railway.app
```

Wait 5-10 minutes for DNS propagation.

### Update Cursor

Change base URL to: `https://api.concise.dev`

**Now you have a professional API!**

---

## Security Checklist

Before going live with real users:

- [ ] Remove demo API key (or set to expire)
- [ ] Move to PostgreSQL for API key storage (Phase 2)
- [ ] Add rate limiting per IP (not just per key)
- [ ] Set up Sentry for error tracking
- [ ] Enable CORS restrictions (not allow all origins)
- [ ] Add request size limits
- [ ] Set up automated backups
- [ ] Create monitoring alerts
- [ ] Add SSL/TLS (Railway does this automatically)

---

## Scaling Strategy

### Free Tier → Hobby ($5/mo)
**When:** 500+ active users

**Changes:**
- Same infrastructure
- Just more compute credits

### Hobby → Pro ($20/mo)
**When:** 1,000+ active users or high volume

**Changes:**
- More memory (up to 8GB)
- Better CPU priority
- More reliable

### Pro → Custom
**When:** 10,000+ users or enterprise clients

**Changes:**
- Dedicated infrastructure
- Multiple regions
- SLA guarantees
- Custom pricing

---

## Updating Your Deployment

### Push Updates

```bash
# Make changes locally
# Test: ./start.sh

# Commit and push
git add .
git commit -m "Improve compression speed"
git push origin main
```

Railway **automatically redeploys** on every push to main!

### Rollback if Needed

In Railway:
1. Go to "Deployments"
2. Find previous working deployment
3. Click "..." → "Rollback"

---

## Database Migration (When You're Ready)

Currently using in-memory storage (data lost on restart).

### When to Migrate

- You have 10+ paying customers
- You need persistent API keys
- You want historical analytics

### Add PostgreSQL (Still Free on Railway)

1. In Railway project, click "New"
2. Select "Database" → "PostgreSQL"
3. Railway provisions free Postgres
4. Get connection string
5. Update code to use PostgreSQL

See `docs/database-migration.md` for full guide.

---

## Troubleshooting

### Deployment Failed

**Check logs:**
- Missing environment variables?
- Python version wrong?
- Dependency installation failed?

**Fix:**
```bash
# Ensure requirements.txt is correct
# Ensure runtime.txt has: python-3.11.6
# Push fix, Railway auto-redeploys
```

### Out of Memory

**Symptoms:**
- 502 errors
- Slow responses
- Crashes in logs

**Quick fix:**
```bash
# In Railway settings
# Increase memory limit
# Or optimize: Use ONNX quantized model
```

### High Latency

**Check:**
1. Cache enabled? (REDIS_URL set?)
2. Cache hit rate? (Should be 70-80%)
3. Model optimized? (Use ONNX in Phase 2)

**Fix:**
```bash
# Enable Redis caching
# Add REDIS_URL to Railway variables
# Redeploy
```

### SSL Certificate Issues

Railway handles SSL automatically. If issues:
1. Check domain DNS is correct
2. Wait 10-15 min for propagation
3. Contact Railway support (excellent response time)

---

## Success Metrics

### Week 1 Goals

- [x] Deployed to Railway
- [ ] 10 test users using it
- [ ] 1,000+ compressions performed
- [ ] Average compression ratio: 5x+
- [ ] Cache hit rate: 60%+
- [ ] Uptime: 99%+

### Month 1 Goals

- [ ] 100 free tier users
- [ ] 10 paying customers ($290 MRR)
- [ ] 100,000+ compressions
- [ ] Average latency: <200ms
- [ ] Cache hit rate: 80%+
- [ ] $50+ saved per user/month

### Month 3 Goals

- [ ] 500 users
- [ ] 50 paying customers ($1,450 MRR)
- [ ] 1M+ compressions
- [ ] Dashboard launched
- [ ] Stripe integration live
- [ ] First $10k month

---

## Next Steps

1. **Monitor for 1 week**
   - Watch logs
   - Track usage
   - Gather feedback

2. **Build dashboard** (Week 2)
   - Next.js frontend
   - User signup
   - Usage visualization

3. **Add billing** (Week 3)
   - Stripe integration
   - Subscription plans
   - Usage limits

4. **Optimize** (Week 4)
   - ONNX model
   - Better caching
   - Faster responses

5. **Launch** (Week 5)
   - Twitter announcement
   - Hacker News post
   - Get first customers

---

## Support

**Railway Issues:**
- Railway Discord: discord.gg/railway
- Railway Docs: docs.railway.app

**Concise Issues:**
- Check server logs in Railway
- Test health endpoint
- Review environment variables

---

**You're now live in production! 🚀**

Monitor your stats:
```bash
watch -n 5 "curl -s https://your-app.up.railway.app/v1/stats \
  -H 'Authorization: Bearer YOUR_KEY' | jq"
```

Start saving money and making money! 💰
