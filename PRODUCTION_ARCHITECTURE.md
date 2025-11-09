# Concise API - Production-Ready Architecture

**Created:** 2025-11-06
**Status:** Architecture Design Document
**Target:** Production deployment supporting 1000+ users

---

## Current State Assessment

### What We Have (MVP)
```
✅ FastAPI application (347 lines)
✅ LLMLingua compression engine
✅ In-memory authentication (demo keys)
✅ In-memory analytics
✅ Redis cache support (configured but optional)
✅ Basic error handling
✅ Health check endpoint
✅ Rate limiting (basic)
```

### What's Missing for Production
```
❌ Persistent database (PostgreSQL)
❌ Proper authentication & user management
❌ Background job processing
❌ Comprehensive monitoring
❌ Structured logging
❌ API versioning
❌ Load balancing
❌ Auto-scaling
❌ Backup & disaster recovery
❌ Security hardening
❌ Performance optimization
❌ CI/CD pipeline
```

---

## Production Architecture Overview

### High-Level System Design

```
┌─────────────────────────────────────────────────────────────────┐
│                       CLIENT LAYER                               │
│  (Cursor, Web Dashboard, Mobile Apps, CLI Tools)                │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     │ HTTPS (TLS 1.3)
                     │
┌────────────────────▼────────────────────────────────────────────┐
│                     EDGE LAYER                                   │
│  ┌──────────────────────────────────────────────────────┐       │
│  │  Cloudflare / AWS CloudFront                         │       │
│  │  - DDoS Protection                                   │       │
│  │  - WAF (Web Application Firewall)                    │       │
│  │  - Rate Limiting (Global)                            │       │
│  │  - SSL/TLS Termination                               │       │
│  │  - CDN for static assets                             │       │
│  └──────────────────────────────────────────────────────┘       │
└────────────────────┬────────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────────┐
│                  LOAD BALANCER                                   │
│  ┌──────────────────────────────────────────────────────┐       │
│  │  NGINX / Railway Load Balancer                       │       │
│  │  - Request routing                                   │       │
│  │  - Health checks                                     │       │
│  │  - SSL termination (if not at edge)                 │       │
│  │  - Request buffering                                 │       │
│  └──────────────────────────────────────────────────────┘       │
└────────────────────┬────────────────────────────────────────────┘
                     │
      ┌──────────────┼──────────────┐
      │              │              │
      ▼              ▼              ▼
┌──────────┐  ┌──────────┐  ┌──────────┐
│  API     │  │  API     │  │  API     │
│  Server  │  │  Server  │  │  Server  │
│  (Pod 1) │  │  (Pod 2) │  │  (Pod 3) │
└────┬─────┘  └────┬─────┘  └────┬─────┘
     │             │             │
     └─────────────┼─────────────┘
                   │
       ┌───────────┼───────────┬────────────┬─────────────┐
       │           │           │            │             │
       ▼           ▼           ▼            ▼             ▼
┌──────────┐ ┌──────────┐ ┌─────────┐ ┌─────────┐ ┌──────────┐
│PostgreSQL│ │  Redis   │ │  Queue  │ │  S3     │ │Monitoring│
│(Primary) │ │  Cluster │ │(Celery) │ │(Models) │ │ Stack    │
└──────────┘ └──────────┘ └─────────┘ └─────────┘ └──────────┘
     │
     ▼
┌──────────┐
│PostgreSQL│
│(Replica) │
└──────────┘
```

---

## Tech Stack Recommendations

### 1. API Layer

**Current: FastAPI** ✅
- Keep FastAPI (excellent choice)
- Add: API versioning (v1, v2)
- Add: OpenAPI spec generation
- Add: Request validation with Pydantic v2

**Additions:**
```python
# API versioning
/v1/compress
/v1/chat/completions
/v2/compress  # Future: new features

# Dependencies
fastapi==0.104.1
pydantic==2.5.0
uvicorn[standard]==0.24.0
```

---

### 2. Database Layer

**Recommended: PostgreSQL 15+**

**Why PostgreSQL:**
- ✅ ACID compliance
- ✅ JSON support (for metadata)
- ✅ Full-text search
- ✅ Excellent performance
- ✅ Managed services available (Railway, Supabase, AWS RDS)

**Schema Design:**
```sql
-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    tier VARCHAR(20) DEFAULT 'free',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- API Keys table
CREATE TABLE api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    key_hash VARCHAR(255) UNIQUE NOT NULL,
    key_prefix VARCHAR(20) NOT NULL,
    name VARCHAR(100),
    last_used_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP,
    rate_limit_per_minute INTEGER DEFAULT 60
);

-- Compression logs (for analytics)
CREATE TABLE compression_logs (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    api_key_id UUID REFERENCES api_keys(id),
    original_tokens INTEGER NOT NULL,
    compressed_tokens INTEGER NOT NULL,
    tokens_saved INTEGER NOT NULL,
    compression_ratio FLOAT NOT NULL,
    strategy VARCHAR(20) NOT NULL,
    compression_time_ms FLOAT NOT NULL,
    cached BOOLEAN DEFAULT false,
    cost_saved_usd DECIMAL(10, 6),
    created_at TIMESTAMP DEFAULT NOW(),
    metadata JSONB
);

-- Create indexes for performance
CREATE INDEX idx_compression_logs_user_id ON compression_logs(user_id);
CREATE INDEX idx_compression_logs_created_at ON compression_logs(created_at);
CREATE INDEX idx_api_keys_user_id ON api_keys(user_id);
CREATE INDEX idx_api_keys_key_hash ON api_keys(key_hash);
```

**ORM: SQLAlchemy 2.0 + Alembic**
```python
# For migrations and type-safe queries
sqlalchemy==2.0.23
alembic==1.12.1
asyncpg==0.29.0  # Async PostgreSQL driver
```

---

### 3. Caching Layer

**Current: Redis** ✅

**Production Setup:**
- **Redis Cluster** (3+ nodes for HA)
- **Managed Service:** Upstash, Railway Redis, AWS ElastiCache
- **Configuration:**
  ```
  maxmemory: 2GB
  maxmemory-policy: allkeys-lru
  persistence: AOF + RDB snapshots
  ```

**Usage:**
- Cache compressed results (24hr TTL)
- Session storage
- Rate limiting counters
- Request deduplication

**Library:**
```python
redis[hiredis]==5.0.1  # Async support
```

---

### 4. Background Jobs

**Add: Celery + Redis**

**Use Cases:**
- Async compression for large texts
- Batch processing
- Analytics aggregation
- Email notifications
- Model warm-up

**Setup:**
```python
celery==5.3.4
flower==2.0.1  # Monitoring UI

# Tasks
@celery.task
def compress_async(text, strategy, user_id):
    result = compressor.compress(text, strategy)
    log_to_database(user_id, result)
    return result
```

---

### 5. Model Storage & Loading

**Recommended: S3 + Local Cache**

**Strategy:**
```
1. Store models in S3/R2 (Cloudflare R2 is cheaper)
2. Download to local cache on startup
3. Use persistent volume for model storage
4. Implement model versioning
```

**Benefits:**
- Faster pod startup (download once)
- Model versioning
- Easy rollback
- Share models across instances

---

### 6. Authentication & Authorization

**Current: Simple bearer tokens** ⚠️

**Production: OAuth2 + JWT**

**Libraries:**
```python
python-jose[cryptography]==3.3.0  # JWT
passlib[bcrypt]==1.7.4            # Password hashing
authlib==1.2.1                    # OAuth2 flows
```

**Authentication Flow:**
```
1. User signs up → Store in PostgreSQL
2. User logs in → Issue JWT access token (15min)
3. Refresh token stored in Redis (30 days)
4. API calls use Bearer token
5. Token validation via middleware
```

**API Key Management:**
```python
# Generate secure API keys
prefix = "csk_live_"  # Customer Secret Key
key = secrets.token_urlsafe(32)
full_key = f"{prefix}{key}"

# Store hash, not plain key
key_hash = bcrypt.hashpw(full_key.encode(), salt)
```

---

### 7. Rate Limiting

**Multi-Layer Approach:**

**Layer 1: Edge (Cloudflare)**
- 100 req/sec per IP
- DDoS protection

**Layer 2: Application (slowapi)**
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/v1/compress")
@limiter.limit("60/minute")
async def compress(...):
    ...
```

**Layer 3: User Tier-Based (Redis)**
```python
# In middleware
async def check_rate_limit(api_key: str):
    user_tier = get_user_tier(api_key)
    limits = {
        "free": 60,      # 60 req/min
        "starter": 300,  # 300 req/min
        "pro": 1000,     # 1000 req/min
        "team": 5000     # 5000 req/min
    }
    # Check Redis counter
    ...
```

---

### 8. Monitoring & Observability

**Recommended Stack:**

**Option A: Self-Hosted (Open Source)**
```
Prometheus (metrics)
   ↓
Grafana (dashboards)
   ↓
Loki (logs)
   ↓
Tempo (traces)
```

**Option B: Managed Services**
```
Railway Observability (built-in)
   or
Datadog / New Relic / Grafana Cloud
```

**Metrics to Track:**
```python
# Application metrics
- Request count (by endpoint, status)
- Response time (p50, p95, p99)
- Compression ratio (avg, by strategy)
- Cache hit rate
- Token savings (total, per user)
- Error rate

# Infrastructure metrics
- CPU usage
- Memory usage
- Disk I/O
- Network I/O
- PostgreSQL connections
- Redis memory

# Business metrics
- Active users (DAU, MAU)
- Compressions per user
- Revenue (MRR, ARR)
- Churn rate
```

**Implementation:**
```python
from prometheus_client import Counter, Histogram

compression_counter = Counter(
    'compressions_total',
    'Total compressions',
    ['strategy', 'cached']
)

compression_duration = Histogram(
    'compression_duration_seconds',
    'Compression duration'
)
```

---

### 9. Logging

**Structured Logging with Context**

```python
import structlog

logger = structlog.get_logger()

logger.info(
    "compression_completed",
    user_id=user_id,
    strategy=strategy,
    original_tokens=original_tokens,
    compressed_tokens=compressed_tokens,
    duration_ms=duration_ms,
    cached=cached
)
```

**Log Aggregation:**
- **Development:** File logs
- **Production:** CloudWatch, Loki, or Datadog

**Log Levels:**
```
ERROR: System errors, exceptions
WARN: Rate limits, cache misses, slow queries
INFO: API calls, compression events
DEBUG: Detailed debugging (dev only)
```

---

### 10. Error Tracking

**Recommended: Sentry**

```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    integrations=[FastApiIntegration()],
    traces_sample_rate=0.1,
    profiles_sample_rate=0.1
)
```

**Benefits:**
- Error grouping
- Stack traces
- User context
- Performance monitoring
- Release tracking

---

### 11. Security

**Essential Security Measures:**

**A. HTTPS Everywhere**
```
- TLS 1.3
- HSTS headers
- Certificate management (Let's Encrypt)
```

**B. API Security**
```python
# CORS
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://concise.dev"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Security headers
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*.concise.dev", "localhost"]
)
```

**C. Input Validation**
```python
# Max request size
app.add_middleware(
    RequestSizeLimitMiddleware,
    max_size=1_000_000  # 1MB max
)

# Request timeout
@app.middleware("http")
async def timeout_middleware(request, call_next):
    try:
        return await asyncio.wait_for(
            call_next(request),
            timeout=30.0
        )
    except asyncio.TimeoutError:
        return JSONResponse(
            status_code=504,
            content={"error": "Request timeout"}
        )
```

**D. Secrets Management**
```bash
# Use environment variables
# Never commit secrets
# Use secrets manager (Railway, AWS Secrets Manager)

DATABASE_URL=postgresql://...
REDIS_URL=redis://...
SECRET_KEY=$(openssl rand -hex 32)
SENTRY_DSN=https://...
```

---

### 12. Deployment & Infrastructure

**Recommended: Railway (Current Choice) ✅**

**Why Railway:**
- ✅ Zero-config PostgreSQL
- ✅ Redis included
- ✅ Auto-scaling
- ✅ GitHub integration (CI/CD)
- ✅ Environment management
- ✅ Monitoring built-in
- ✅ $5-50/month for MVP

**Alternative: AWS ECS/EKS**
```
Pros: Full control, enterprise features
Cons: Complex, expensive ($100+/month)
```

**Deployment Strategy:**
```yaml
# railway.json
{
  "build": {
    "builder": "NIXPACKS",
    "buildCommand": "pip install -r requirements.txt"
  },
  "deploy": {
    "startCommand": "uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 4",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10,
    "healthcheckPath": "/health",
    "healthcheckTimeout": 300
  }
}
```

---

### 13. Scaling Strategy

**Vertical Scaling (First 1000 users)**
```
CPU: 2 cores → 4 cores
RAM: 2GB → 4GB
Workers: 4 → 8
Cost: $20/month → $50/month
```

**Horizontal Scaling (1000+ users)**
```
Instances: 1 → 3+
Load balancer: ✅
Auto-scaling: CPU > 70%
Database: Read replicas
Redis: Cluster mode
Cost: $50/month → $200/month
```

---

## Production Deployment Checklist

### Phase 1: Database & Persistence
- [ ] Set up PostgreSQL (Railway or Supabase)
- [ ] Create database schema
- [ ] Implement SQLAlchemy models
- [ ] Set up Alembic migrations
- [ ] Migrate in-memory auth to PostgreSQL
- [ ] Migrate analytics to PostgreSQL
- [ ] Set up database backups (daily)

### Phase 2: Caching & Performance
- [ ] Deploy Redis cluster (Upstash or Railway)
- [ ] Implement connection pooling
- [ ] Add request deduplication
- [ ] Optimize database queries (indexes)
- [ ] Implement background jobs (Celery)
- [ ] Add model caching (S3 → local)

### Phase 3: Authentication & Security
- [ ] Implement proper user registration
- [ ] Add OAuth2 JWT authentication
- [ ] Implement API key management UI
- [ ] Add rate limiting (multi-layer)
- [ ] Set up HTTPS/TLS
- [ ] Add security headers
- [ ] Implement input validation
- [ ] Set up secrets management

### Phase 4: Monitoring & Observability
- [ ] Set up Prometheus metrics
- [ ] Create Grafana dashboards
- [ ] Implement structured logging
- [ ] Add error tracking (Sentry)
- [ ] Set up alerts (Slack/Email)
- [ ] Add health checks
- [ ] Implement request tracing

### Phase 5: Testing & CI/CD
- [ ] Write unit tests (pytest)
- [ ] Write integration tests
- [ ] Add load testing (Locust)
- [ ] Set up GitHub Actions CI/CD
- [ ] Implement staging environment
- [ ] Add automated deployments
- [ ] Set up rollback procedures

### Phase 6: Launch Preparation
- [ ] Load testing (1000 concurrent users)
- [ ] Security audit
- [ ] Documentation update
- [ ] Pricing page
- [ ] Terms of Service
- [ ] Privacy Policy
- [ ] Status page (status.concise.dev)
- [ ] Support email/chat

---

## Cost Breakdown (Production)

### Minimal Production ($50-100/month)
```
Railway Starter: $20/month
  - 2 vCPU, 4GB RAM
  - PostgreSQL 10GB
  - Redis 512MB

Upstash Redis: $0/month (free tier)
Cloudflare: $0/month (free tier)
Sentry: $0/month (free tier)
Domain: $12/year

Total: ~$30-50/month (supports 100-500 users)
```

### Growth Stage ($200-500/month)
```
Railway Pro: $50-150/month
  - Auto-scaling
  - 4 vCPU, 8GB RAM
  - PostgreSQL 50GB
  - Redis 2GB

Cloudflare Pro: $20/month (advanced DDoS)
Sentry Team: $26/month
Datadog: $0-100/month (based on usage)
S3 Storage: $5/month (model storage)

Total: $200-500/month (supports 1,000-5,000 users)
```

### Enterprise ($1,000+/month)
```
AWS ECS/EKS: $500+/month
RDS PostgreSQL: $200+/month
ElastiCache Redis: $100+/month
CloudFront: $50+/month
Monitoring (Datadog): $200+/month

Total: $1,000-3,000/month (supports 10,000+ users)
```

---

## Performance Targets

### Response Times
```
p50: < 500ms
p95: < 2s
p99: < 5s
```

### Availability
```
Uptime: 99.9% (8.76 hours downtime/year)
Error rate: < 0.1%
```

### Throughput
```
100 requests/second/instance
With 3 instances: 300 req/sec = 25.9M req/month
```

---

## Recommended Implementation Order

1. **Week 1-2: Database Migration**
   - PostgreSQL setup
   - Schema creation
   - SQLAlchemy integration
   - Data migration

2. **Week 3: Authentication**
   - User registration/login
   - JWT implementation
   - API key management

3. **Week 4: Monitoring**
   - Prometheus setup
   - Grafana dashboards
   - Sentry integration

4. **Week 5-6: Performance**
   - Redis clustering
   - Background jobs
   - Caching optimization

5. **Week 7-8: Testing & Launch**
   - Load testing
   - Security audit
   - Staging deployment
   - Production launch

---

## References

- FastAPI Best Practices: https://fastapi.tiangolo.com/deployment/
- PostgreSQL Performance: https://wiki.postgresql.org/wiki/Performance_Optimization
- Redis Cluster: https://redis.io/docs/management/scaling/
- Prometheus FastAPI: https://github.com/trallnag/prometheus-fastapi-instrumentator
- Railway Deployment: https://docs.railway.app/

---

**Next Steps:** Review this architecture and decide:
1. Start with Phase 1 (Database Migration)?
2. Deploy current MVP to Railway first, then iterate?
3. Build dashboard frontend in parallel?

Your call! 🚀
