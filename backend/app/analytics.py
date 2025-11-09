"""
Analytics and usage tracking
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import defaultdict
from pydantic import BaseModel


class CompressionEvent(BaseModel):
    """Single compression event"""
    timestamp: datetime
    user_id: str
    tokens_saved: int
    cost_saved_usd: float
    strategy: str
    cached: bool


class UserStats(BaseModel):
    """User-level statistics"""
    user_id: str
    total_requests: int
    total_tokens_saved: int
    total_cost_saved_usd: float
    cache_hit_rate: float
    strategies_used: Dict[str, int]
    first_request: Optional[datetime] = None
    last_request: Optional[datetime] = None


class Analytics:
    """Analytics tracking for compression events"""

    def __init__(self):
        # In-memory storage (move to DB in Phase 2)
        self.events: List[CompressionEvent] = []
        self.user_stats: Dict[str, Dict] = defaultdict(lambda: {
            "total_requests": 0,
            "total_tokens_saved": 0,
            "total_cost_saved_usd": 0.0,
            "cache_hits": 0,
            "cache_misses": 0,
            "strategies": defaultdict(int),
            "first_request": None,
            "last_request": None
        })

    def track_compression(
        self,
        user_id: str,
        tokens_saved: int,
        cost_saved: float,
        strategy: str,
        cached: bool = False
    ) -> None:
        """Track a compression event"""

        # Create event
        event = CompressionEvent(
            timestamp=datetime.utcnow(),
            user_id=user_id,
            tokens_saved=tokens_saved,
            cost_saved_usd=cost_saved,
            strategy=strategy,
            cached=cached
        )
        self.events.append(event)

        # Update user stats
        stats = self.user_stats[user_id]
        stats["total_requests"] += 1
        stats["total_tokens_saved"] += tokens_saved
        stats["total_cost_saved_usd"] += cost_saved
        stats["strategies"][strategy] += 1

        if cached:
            stats["cache_hits"] += 1
        else:
            stats["cache_misses"] += 1

        if stats["first_request"] is None:
            stats["first_request"] = event.timestamp
        stats["last_request"] = event.timestamp

    def get_user_stats(self, user_id: str) -> Dict:
        """Get statistics for a specific user"""
        if user_id not in self.user_stats:
            return {
                "total_requests": 0,
                "total_tokens_saved": 0,
                "total_cost_saved_usd": 0.0,
                "cache_hit_rate": 0.0,
                "strategies_used": {},
                "first_request": None,
                "last_request": None
            }

        stats = self.user_stats[user_id]
        total_requests = stats["total_requests"]
        cache_hit_rate = (
            (stats["cache_hits"] / total_requests * 100)
            if total_requests > 0 else 0.0
        )

        return {
            "total_requests": total_requests,
            "total_tokens_saved": stats["total_tokens_saved"],
            "total_cost_saved_usd": round(stats["total_cost_saved_usd"], 2),
            "cache_hit_rate": round(cache_hit_rate, 2),
            "strategies_used": dict(stats["strategies"]),
            "first_request": stats["first_request"],
            "last_request": stats["last_request"]
        }

    def get_user_timeline(
        self,
        user_id: str,
        days: int = 7
    ) -> List[Dict]:
        """Get daily timeline of user's compressions"""
        cutoff = datetime.utcnow() - timedelta(days=days)

        # Filter events for this user
        user_events = [
            e for e in self.events
            if e.user_id == user_id and e.timestamp > cutoff
        ]

        # Group by day
        daily_stats = defaultdict(lambda: {
            "requests": 0,
            "tokens_saved": 0,
            "cost_saved_usd": 0.0
        })

        for event in user_events:
            day = event.timestamp.date()
            daily_stats[day]["requests"] += 1
            daily_stats[day]["tokens_saved"] += event.tokens_saved
            daily_stats[day]["cost_saved_usd"] += event.cost_saved_usd

        # Convert to sorted list
        timeline = []
        for day in sorted(daily_stats.keys()):
            stats = daily_stats[day]
            timeline.append({
                "date": day.isoformat(),
                "requests": stats["requests"],
                "tokens_saved": stats["tokens_saved"],
                "cost_saved_usd": round(stats["cost_saved_usd"], 2)
            })

        return timeline

    def get_global_stats(self) -> Dict:
        """Get system-wide statistics"""
        total_users = len(self.user_stats)
        total_requests = sum(s["total_requests"] for s in self.user_stats.values())
        total_tokens_saved = sum(s["total_tokens_saved"] for s in self.user_stats.values())
        total_cost_saved = sum(s["total_cost_saved_usd"] for s in self.user_stats.values())

        # Calculate overall cache hit rate
        total_hits = sum(s["cache_hits"] for s in self.user_stats.values())
        total_misses = sum(s["cache_misses"] for s in self.user_stats.values())
        cache_hit_rate = (
            (total_hits / (total_hits + total_misses) * 100)
            if (total_hits + total_misses) > 0 else 0.0
        )

        # Most popular strategy
        all_strategies = defaultdict(int)
        for stats in self.user_stats.values():
            for strategy, count in stats["strategies"].items():
                all_strategies[strategy] += count

        most_popular_strategy = (
            max(all_strategies.items(), key=lambda x: x[1])[0]
            if all_strategies else None
        )

        return {
            "total_users": total_users,
            "total_requests": total_requests,
            "total_tokens_saved": total_tokens_saved,
            "total_cost_saved_usd": round(total_cost_saved, 2),
            "cache_hit_rate": round(cache_hit_rate, 2),
            "most_popular_strategy": most_popular_strategy,
            "strategies_breakdown": dict(all_strategies)
        }


# Singleton instance
_analytics: Optional[Analytics] = None

def get_analytics() -> Analytics:
    """Get or create the analytics singleton"""
    global _analytics
    if _analytics is None:
        _analytics = Analytics()
    return _analytics
