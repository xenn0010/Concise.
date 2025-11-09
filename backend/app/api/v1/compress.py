"""
Direct compression endpoint for testing
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Literal, Optional

from app.database import get_db
from app.middleware.auth import get_current_api_key
from app.models.api_key import APIKey
from app.models.usage import UsageRecord
from app.models.user import User
from app.services.compression import get_compressor

router = APIRouter()


class CompressionRequest(BaseModel):
    """Request body for compression endpoint"""
    text: str
    level: Optional[Literal["auto", "aggressive", "balanced", "conservative"]] = "auto"


class CompressionResponse(BaseModel):
    """Response from compression endpoint"""
    original_text: str
    compressed_text: str
    original_tokens: int
    compressed_tokens: int
    tokens_saved: int
    compression_ratio: float
    strategy: str
    compression_time_ms: float


@router.post(
    "/compress",
    response_model=CompressionResponse,
    summary="Compress text directly",
    description="Test endpoint for token compression without OpenAI proxy"
)
async def compress_text(
    request: CompressionRequest,
    api_key: APIKey = Depends(get_current_api_key),
    db: Session = Depends(get_db)
):
    """
    Compress text directly for testing

    This endpoint allows you to test the compression service without
    going through the OpenAI proxy. Perfect for testing and debugging.

    Example:
    ```bash
    curl -X POST http://localhost:8000/v1/compress \\
      -H "Content-Type: application/json" \\
      -H "X-API-Key: your-api-key" \\
      -d '{
        "text": "def fibonacci(n):\\n    if n <= 1:\\n        return n\\n    return fibonacci(n-1) + fibonacci(n-2)",
        "level": "auto"
      }'
    ```
    """
    try:
        # Get user
        user = db.query(User).filter(User.id == api_key.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Compress
        compressor = get_compressor()
        result = compressor.compress(request.text, level=request.level)

        # Record usage
        usage_record = UsageRecord(
            user_id=user.id,
            api_key_id=api_key.id,
            original_tokens=result.original_tokens,
            compressed_tokens=result.compressed_tokens,
            tokens_saved=result.tokens_saved,
            compression_ratio=result.compression_ratio,
            strategy=result.strategy,
            compression_time_ms=result.compression_time_ms,
            request_metadata={
                "endpoint": "/v1/compress",
                "level": request.level
            }
        )
        db.add(usage_record)
        db.commit()

        return CompressionResponse(
            original_text=result.original_text,
            compressed_text=result.compressed_text,
            original_tokens=result.original_tokens,
            compressed_tokens=result.compressed_tokens,
            tokens_saved=result.tokens_saved,
            compression_ratio=result.compression_ratio,
            strategy=result.strategy,
            compression_time_ms=result.compression_time_ms
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Compression failed: {str(e)}"
        )
