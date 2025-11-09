"""
Usage tracking and stats endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta

from app.database import get_db
from app.middleware.auth import get_current_api_key
from app.models.api_key import APIKey
from app.models.usage import UsageRecord
from app.models.user import User

router = APIRouter()


class UsageStats(BaseModel):
    """Usage statistics"""
    total_requests: int
    total_tokens_saved: int
    total_original_tokens: int
    total_compressed_tokens: int
    average_compression_ratio: float
    average_compression_time_ms: float
    by_strategy: dict


class UsageResponse(BaseModel):
    """Usage response"""
    stats: UsageStats
    recent_requests: list


@router.get(
    "/usage",
    response_model=UsageResponse,
    summary="Get usage statistics",
    description="Get usage stats for the current API key"
)
async def get_usage(
    api_key: APIKey = Depends(get_current_api_key),
    db: Session = Depends(get_db),
    days: int = 30
):
    """
    Get usage statistics

    Returns aggregated usage stats for the last N days.

    Example:
    ```bash
    curl http://localhost:8000/v1/usage?days=7 \\
      -H "X-API-Key: your-api-key"
    ```
    """
    try:
        # Get user
        user = db.query(User).filter(User.id == api_key.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Calculate date range
        since = datetime.utcnow() - timedelta(days=days)

        # Get all usage records for this user in the date range
        records = db.query(UsageRecord).filter(
            UsageRecord.user_id == user.id,
            UsageRecord.timestamp >= since
        ).all()

        if not records:
            return UsageResponse(
                stats=UsageStats(
                    total_requests=0,
                    total_tokens_saved=0,
                    total_original_tokens=0,
                    total_compressed_tokens=0,
                    average_compression_ratio=0.0,
                    average_compression_time_ms=0.0,
                    by_strategy={}
                ),
                recent_requests=[]
            )

        # Calculate stats
        total_requests = len(records)
        total_tokens_saved = sum(r.tokens_saved for r in records)
        total_original_tokens = sum(r.original_tokens for r in records)
        total_compressed_tokens = sum(r.compressed_tokens for r in records)
        average_compression_ratio = sum(r.compression_ratio for r in records) / total_requests
        average_compression_time_ms = sum(r.compression_time_ms for r in records) / total_requests

        # Group by strategy
        by_strategy = {}
        for record in records:
            strategy = record.strategy
            if strategy not in by_strategy:
                by_strategy[strategy] = {
                    "count": 0,
                    "tokens_saved": 0,
                    "average_ratio": 0.0
                }
            by_strategy[strategy]["count"] += 1
            by_strategy[strategy]["tokens_saved"] += record.tokens_saved
            by_strategy[strategy]["average_ratio"] += record.compression_ratio

        # Calculate averages for each strategy
        for strategy in by_strategy:
            count = by_strategy[strategy]["count"]
            by_strategy[strategy]["average_ratio"] /= count

        # Get recent requests
        recent = db.query(UsageRecord).filter(
            UsageRecord.user_id == user.id
        ).order_by(desc(UsageRecord.timestamp)).limit(10).all()

        recent_requests = [
            {
                "timestamp": r.timestamp.isoformat(),
                "original_tokens": r.original_tokens,
                "compressed_tokens": r.compressed_tokens,
                "tokens_saved": r.tokens_saved,
                "compression_ratio": r.compression_ratio,
                "strategy": r.strategy,
                "compression_time_ms": r.compression_time_ms
            }
            for r in recent
        ]

        return UsageResponse(
            stats=UsageStats(
                total_requests=total_requests,
                total_tokens_saved=total_tokens_saved,
                total_original_tokens=total_original_tokens,
                total_compressed_tokens=total_compressed_tokens,
                average_compression_ratio=average_compression_ratio,
                average_compression_time_ms=average_compression_time_ms,
                by_strategy=by_strategy
            ),
            recent_requests=recent_requests
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get usage: {str(e)}"
        )
