# Concise - Billing, Usage Tracking & Auto-Scaling Architecture

**Date:** 2025-11-06
**Goal:** Launch tonight with monetization ready

---

## Pricing Model Design

### Option 1: Token-Based Pricing (RECOMMENDED)
**How it works:** Charge per token saved

```
┌─────────────────────────────────────────────────────────┐
│                    PRICING TIERS                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  FREE (Starter)                                         │
│  ├─ 100,000 tokens saved/month                         │
│  ├─ 60 requests/minute                                  │
│  ├─ All compression strategies                          │
│  ├─ API access                                          │
│  └─ Community support                                   │
│                                                         │
│  PRO ($29/month)                                        │
│  ├─ 5M tokens saved/month                              │
│  ├─ 300 requests/minute                                 │
│  ├─ Priority support                                    │
│  ├─ Usage analytics dashboard                           │
│  └─ Overage: $0.01 per 1,000 tokens saved              │
│                                                         │
│  TEAM ($99/month)                                       │
│  ├─ 25M tokens saved/month                             │
│  ├─ 1,000 requests/minute                              │
│  ├─ Multiple team members                              │
│  ├─ Priority support + Slack channel                   │
│  ├─ Custom rate limits                                 │
│  └─ Overage: $0.008 per 1,000 tokens saved            │
│                                                         │
│  ENTERPRISE (Custom)                                    │
│  ├─ Unlimited tokens saved                             │
│  ├─ Custom rate limits                                 │
│  ├─ Dedicated infrastructure                           │
│  ├─ SLA guarantees (99.99%)                            │
│  ├─ On-premise deployment option                       │
│  ├─ Custom compression models                          │
│  ├─ White-label option                                 │
│  └─ Contact for pricing                                │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Why Token-Based Pricing?

**Pros:**
- ✅ Direct value correlation (you save tokens = you pay for savings)
- ✅ Usage-based (fair for all customer sizes)
- ✅ Scales naturally (heavy users pay more)
- ✅ Easy to track (we already count tokens)
- ✅ Competitive with OpenAI pricing

**Math:**
```
Example: Pro user compresses 500K input tokens/day
- Average compression: 60% (3M tokens saved/month)
- Pro plan: $29/month includes 5M saved tokens
- User is under limit ✅
- Value to user: ~$90/month (based on GPT-4 pricing)
- ROI: 3.1x
```

---

## Usage Tracking System

### Database Schema for Billing

```sql
-- Subscription plans
CREATE TABLE plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(50) NOT NULL,
    price_usd DECIMAL(10, 2) NOT NULL,
    tokens_included BIGINT NOT NULL,
    overage_rate_per_1k DECIMAL(10, 6),
    rate_limit_per_minute INTEGER NOT NULL,
    features JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW()
);

-- User subscriptions
CREATE TABLE subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    plan_id UUID REFERENCES plans(id),
    stripe_subscription_id VARCHAR(255),
    status VARCHAR(20) DEFAULT 'active',  -- active, canceled, past_due
    current_period_start TIMESTAMP NOT NULL,
    current_period_end TIMESTAMP NOT NULL,
    cancel_at_period_end BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Usage tracking (for billing)
CREATE TABLE usage_records (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    subscription_id UUID REFERENCES subscriptions(id),
    tokens_saved INTEGER NOT NULL,
    cost_saved_usd DECIMAL(10, 6),
    timestamp TIMESTAMP DEFAULT NOW(),

    -- Aggregation-friendly indexes
    year INTEGER GENERATED ALWAYS AS (EXTRACT(YEAR FROM timestamp)) STORED,
    month INTEGER GENERATED ALWAYS AS (EXTRACT(MONTH FROM timestamp)) STORED,
    day INTEGER GENERATED ALWAYS AS (EXTRACT(DAY FROM timestamp)) STORED
);

-- Pre-aggregated usage (for fast dashboard queries)
CREATE TABLE usage_summary (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    period_start TIMESTAMP NOT NULL,
    period_end TIMESTAMP NOT NULL,
    total_tokens_saved BIGINT NOT NULL,
    total_requests INTEGER NOT NULL,
    overage_tokens BIGINT DEFAULT 0,
    overage_cost_usd DECIMAL(10, 2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),

    UNIQUE(user_id, period_start)
);

-- Indexes for performance
CREATE INDEX idx_usage_records_user_timestamp ON usage_records(user_id, timestamp);
CREATE INDEX idx_usage_records_subscription ON usage_records(subscription_id);
CREATE INDEX idx_usage_records_month ON usage_records(user_id, year, month);
CREATE INDEX idx_usage_summary_user_period ON usage_summary(user_id, period_start);
```

---

## Tracking Implementation

### Every API Call Records Usage

```python
# In main.py - after compression
@app.post("/v1/compress")
async def compress(
    request: CompressRequest,
    api_key: APIKey = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    # Compress text
    result = compressor.compress(
        text=request.text,
        strategy=request.strategy
    )

    # Track usage for billing
    usage = UsageRecord(
        user_id=api_key.user_id,
        subscription_id=get_user_subscription(api_key.user_id),
        tokens_saved=result["tokens_saved"],
        cost_saved_usd=result["cost_saved_usd"],
        timestamp=datetime.utcnow()
    )
    db.add(usage)
    db.commit()

    # Check if user is over limit (async job)
    check_usage_limit.delay(api_key.user_id)

    return result
```

### Background Job: Aggregate Usage

```python
# Celery task - runs every hour
@celery.task
def aggregate_usage():
    """Aggregate hourly usage for all users"""
    db = SessionLocal()

    users = db.query(User).filter(User.is_active == True).all()

    for user in users:
        # Get current billing period
        subscription = get_active_subscription(user.id)
        if not subscription:
            continue

        period_start = subscription.current_period_start
        period_end = subscription.current_period_end

        # Calculate total usage
        total_tokens = db.query(
            func.sum(UsageRecord.tokens_saved)
        ).filter(
            UsageRecord.user_id == user.id,
            UsageRecord.timestamp >= period_start,
            UsageRecord.timestamp < period_end
        ).scalar() or 0

        total_requests = db.query(
            func.count(UsageRecord.id)
        ).filter(
            UsageRecord.user_id == user.id,
            UsageRecord.timestamp >= period_start,
            UsageRecord.timestamp < period_end
        ).scalar() or 0

        # Calculate overage
        plan = get_plan(subscription.plan_id)
        overage_tokens = max(0, total_tokens - plan.tokens_included)
        overage_cost = (overage_tokens / 1000) * plan.overage_rate_per_1k

        # Upsert summary
        summary = db.query(UsageSummary).filter(
            UsageSummary.user_id == user.id,
            UsageSummary.period_start == period_start
        ).first()

        if summary:
            summary.total_tokens_saved = total_tokens
            summary.total_requests = total_requests
            summary.overage_tokens = overage_tokens
            summary.overage_cost_usd = overage_cost
        else:
            summary = UsageSummary(
                user_id=user.id,
                period_start=period_start,
                period_end=period_end,
                total_tokens_saved=total_tokens,
                total_requests=total_requests,
                overage_tokens=overage_tokens,
                overage_cost_usd=overage_cost
            )
            db.add(summary)

        db.commit()

        # Send warning if approaching limit
        if total_tokens > plan.tokens_included * 0.8:
            send_usage_warning_email.delay(user.id, total_tokens, plan.tokens_included)
```

### Rate Limiting Based on Tier

```python
# Middleware for tier-based rate limiting
async def check_rate_limit(api_key: APIKey, db: Session):
    """Check rate limit based on user's subscription tier"""

    # Get user's plan
    subscription = get_active_subscription(api_key.user_id, db)
    if not subscription:
        # Free tier
        rate_limit = 60
    else:
        plan = get_plan(subscription.plan_id, db)
        rate_limit = plan.rate_limit_per_minute

    # Check Redis counter
    key = f"rate_limit:{api_key.user_id}:{datetime.utcnow().minute}"
    current = redis_client.get(key)

    if current and int(current) >= rate_limit:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Limit: {rate_limit}/minute. Upgrade your plan for higher limits."
        )

    # Increment counter
    pipe = redis_client.pipeline()
    pipe.incr(key)
    pipe.expire(key, 60)  # Expire after 1 minute
    pipe.execute()

    return api_key
```

---

## Stripe Integration

### Setup Stripe Products & Prices

```python
# Initialize Stripe (do this once)
import stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# Create products (one-time setup)
def create_stripe_products():
    # Pro Plan
    pro_product = stripe.Product.create(
        name="Concise Pro",
        description="5M tokens saved/month with overage billing"
    )

    pro_price = stripe.Price.create(
        product=pro_product.id,
        unit_amount=2900,  # $29.00 in cents
        currency="usd",
        recurring={"interval": "month"},
        metadata={"tokens_included": "5000000"}
    )

    # Team Plan
    team_product = stripe.Product.create(
        name="Concise Team",
        description="25M tokens saved/month for teams"
    )

    team_price = stripe.Price.create(
        product=team_product.id,
        unit_amount=9900,  # $99.00
        currency="usd",
        recurring={"interval": "month"},
        metadata={"tokens_included": "25000000"}
    )

    print(f"Pro Price ID: {pro_price.id}")
    print(f"Team Price ID: {team_price.id}")
```

### Subscription Creation

```python
@app.post("/v1/subscriptions/create")
async def create_subscription(
    plan: str,  # "pro" or "team"
    payment_method_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new Stripe subscription"""

    # Get Stripe customer or create
    if not user.stripe_customer_id:
        customer = stripe.Customer.create(
            email=user.email,
            payment_method=payment_method_id,
            invoice_settings={"default_payment_method": payment_method_id}
        )
        user.stripe_customer_id = customer.id
        db.commit()

    # Get price ID
    price_ids = {
        "pro": os.getenv("STRIPE_PRO_PRICE_ID"),
        "team": os.getenv("STRIPE_TEAM_PRICE_ID")
    }

    # Create subscription
    subscription = stripe.Subscription.create(
        customer=user.stripe_customer_id,
        items=[{"price": price_ids[plan]}],
        payment_behavior="default_incomplete",
        expand=["latest_invoice.payment_intent"]
    )

    # Save to database
    db_subscription = Subscription(
        user_id=user.id,
        plan_id=get_plan_by_name(plan).id,
        stripe_subscription_id=subscription.id,
        status=subscription.status,
        current_period_start=datetime.fromtimestamp(subscription.current_period_start),
        current_period_end=datetime.fromtimestamp(subscription.current_period_end)
    )
    db.add(db_subscription)
    db.commit()

    return {
        "subscription_id": subscription.id,
        "client_secret": subscription.latest_invoice.payment_intent.client_secret
    }
```

### Usage-Based Billing (Overage)

```python
# Celery task - runs at end of billing period
@celery.task
def bill_overage(subscription_id: str):
    """Bill user for overage at end of period"""
    db = SessionLocal()

    subscription = db.query(Subscription).filter(
        Subscription.stripe_subscription_id == subscription_id
    ).first()

    if not subscription:
        return

    # Get usage summary
    summary = db.query(UsageSummary).filter(
        UsageSummary.user_id == subscription.user_id,
        UsageSummary.period_start == subscription.current_period_start
    ).first()

    if not summary or summary.overage_cost_usd <= 0:
        return

    # Create Stripe invoice item for overage
    stripe.InvoiceItem.create(
        customer=subscription.user.stripe_customer_id,
        amount=int(summary.overage_cost_usd * 100),  # Convert to cents
        currency="usd",
        description=f"Overage: {summary.overage_tokens:,} tokens saved beyond plan limit"
    )

    print(f"Billed ${summary.overage_cost_usd} overage to {subscription.user.email}")
```

### Stripe Webhooks (Critical!)

```python
@app.post("/webhooks/stripe")
async def stripe_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """Handle Stripe events"""
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, os.getenv("STRIPE_WEBHOOK_SECRET")
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    # Handle different event types
    if event.type == "customer.subscription.created":
        # New subscription created
        handle_subscription_created(event.data.object, db)

    elif event.type == "customer.subscription.updated":
        # Subscription updated (e.g., plan change)
        handle_subscription_updated(event.data.object, db)

    elif event.type == "customer.subscription.deleted":
        # Subscription canceled
        handle_subscription_canceled(event.data.object, db)

    elif event.type == "invoice.payment_succeeded":
        # Payment successful
        handle_payment_success(event.data.object, db)

    elif event.type == "invoice.payment_failed":
        # Payment failed - suspend account
        handle_payment_failure(event.data.object, db)

    return {"status": "success"}
```

---

## Auto-Scaling Strategy

### Railway Auto-Scaling (Recommended for Launch)

```json
// railway.json
{
  "deploy": {
    "numReplicas": 2,  // Start with 2 instances
    "maxReplicas": 10,  // Scale up to 10
    "autoscaling": {
      "enabled": true,
      "minReplicas": 2,
      "maxReplicas": 10,
      "targetCPUUtilization": 70,
      "targetMemoryUtilization": 80
    },
    "healthcheckPath": "/health",
    "healthcheckInterval": 10,
    "healthcheckTimeout": 5
  }
}
```

**How it works:**
1. Start with 2 replicas (HA from day 1)
2. Railway monitors CPU & memory
3. When CPU > 70% → spin up new instance
4. When traffic drops → scale down
5. Load balancer distributes requests

**Cost:**
- 2 instances: $40/month
- 10 instances (peak): $200/month
- You only pay for what you use

### Enterprise: Dedicated Infrastructure

For enterprise customers, we deploy separate infrastructure:

```
┌────────────────────────────────────────────┐
│         ENTERPRISE CUSTOMER                │
├────────────────────────────────────────────┤
│                                            │
│  Dedicated Infrastructure:                 │
│  ├─ 3+ API servers (dedicated CPU/RAM)    │
│  ├─ Dedicated PostgreSQL instance         │
│  ├─ Dedicated Redis cluster                │
│  ├─ Custom rate limits (no throttling)    │
│  ├─ Private VPC (network isolation)       │
│  └─ SLA: 99.99% uptime                     │
│                                            │
│  Features:                                 │
│  ├─ Custom compression models              │
│  ├─ White-label branding                   │
│  ├─ On-premise deployment option           │
│  ├─ Dedicated support (Slack channel)     │
│  └─ Custom contract terms                  │
│                                            │
└────────────────────────────────────────────┘

Pricing: Starting at $2,000/month
```

**Implementation:**
```python
# Check if user is enterprise
if user.tier == "enterprise":
    # Route to dedicated infrastructure
    enterprise_url = user.enterprise_endpoint  # e.g., https://acme.concise.dev
    response = httpx.post(f"{enterprise_url}/v1/compress", json=request)
else:
    # Use shared infrastructure
    response = compressor.compress(request.text, request.strategy)
```

---

## Feature Gating by Tier

```python
# In compressor.py
def compress(
    self,
    text: str,
    strategy: str = "balanced",
    use_cache: bool = True,
    user_tier: str = "free"
) -> Dict:
    """Compress with tier-based features"""

    # Feature gating
    allowed_strategies = {
        "free": ["minify", "conservative"],
        "pro": ["minify", "conservative", "balanced"],
        "team": ["minify", "conservative", "balanced", "aggressive"],
        "enterprise": ["minify", "conservative", "balanced", "aggressive", "extreme"]
    }

    if strategy not in allowed_strategies.get(user_tier, []):
        raise HTTPException(
            status_code=403,
            detail=f"Strategy '{strategy}' requires {get_required_tier(strategy)} plan"
        )

    # Enterprise gets priority queue
    if user_tier == "enterprise":
        priority = "high"
    elif user_tier in ["team", "pro"]:
        priority = "normal"
    else:
        priority = "low"

    # Compress
    result = self._compress_with_priority(text, strategy, priority)

    return result
```

---

## Launch Checklist (Tonight)

### Must-Have (2-3 hours)
```
□ Add `subscriptions` table to database
□ Add `usage_records` table
□ Add `plans` table with seed data
□ Implement usage tracking (1 line per API call)
□ Add tier-based rate limiting
□ Create Stripe account
□ Set up Stripe products/prices
□ Add subscription creation endpoint
□ Add Stripe webhook handler
□ Test subscription flow end-to-end
□ Update .env with Stripe keys
□ Deploy to Railway
```

### Nice-to-Have (Add later)
```
□ Usage dashboard
□ Email notifications
□ Overage alerts
□ Analytics charts
□ Plan comparison page
□ Self-service upgrades
```

---

## Environment Variables Needed

```bash
# Stripe
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PRO_PRICE_ID=price_...
STRIPE_TEAM_PRICE_ID=price_...

# Database
DATABASE_URL=postgresql://...

# Redis
REDIS_URL=redis://...

# App
SECRET_KEY=...
ENVIRONMENT=production
```

---

## Pricing Page Copy

```markdown
# Simple, Usage-Based Pricing

Pay only for the tokens you save. No hidden fees.

## Free
Perfect for trying out Concise
- 100K tokens saved/month
- 60 requests/minute
- Code minification
- Conservative compression
- Community support

**$0/month**

## Pro
For developers building with AI
- 5M tokens saved/month
- 300 requests/minute
- All compression strategies
- Usage analytics
- Priority support
- Overage: $0.01/1K tokens

**$29/month**

## Team
For teams shipping AI products
- 25M tokens saved/month
- 1,000 requests/minute
- Team collaboration
- Advanced analytics
- Slack support
- Overage: $0.008/1K tokens

**$99/month**

## Enterprise
For companies at scale
- Unlimited tokens
- Dedicated infrastructure
- Custom models
- SLA guarantees
- On-premise option
- White-label

**Contact Sales**
```

---

## Next Steps

I can build this tonight in this order:

1. **Database schema** (15 min)
2. **Usage tracking** (30 min)
3. **Stripe setup** (45 min)
4. **Tier-based limits** (30 min)
5. **Deploy to Railway** (30 min)

Total: ~2.5 hours

Ready to start? Let's build the billing system first! 🚀
