"""
OpenAI-compatible proxy endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Header
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.auth import get_current_api_key
from app.schemas.proxy import ChatCompletionRequest, ChatCompletionResponse
from app.services.proxy import get_proxy_service
from app.models.api_key import APIKey
from app.models.usage import UsageRecord
from app.models.user import User
import time


router = APIRouter()


@router.post(
    "/chat/completions",
    response_model=ChatCompletionResponse,
    summary="Create chat completion",
    description="OpenAI-compatible chat completion endpoint with token compression"
)
async def create_chat_completion(
    request: ChatCompletionRequest,
    api_key: APIKey = Depends(get_current_api_key),
    db: Session = Depends(get_db)
):
    """
    Create a chat completion with optional token compression

    This endpoint is compatible with OpenAI's chat completion API.
    Simply replace your OpenAI base URL with Concise's URL to enable
    automatic token compression.

    Example:
    ```python
    from openai import OpenAI

    client = OpenAI(
        base_url="https://api.concise.dev/v1",
        api_key="your-concise-api-key"
    )

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Your long prompt here..."}],
        # Concise-specific parameters (optional)
        compression_enabled=True,  # Default: True
        compression_level="auto"   # auto, aggressive, balanced, conservative
    )
    ```
    """
    try:
        # Get user to check rate limits
        user = db.query(User).filter(User.id == api_key.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Check if user is active
        if not user.is_active:
            raise HTTPException(status_code=403, detail="User account is inactive")

        # Get proxy service
        proxy_service = get_proxy_service()

        # Handle streaming vs non-streaming
        if request.stream:
            # Return streaming response
            async def generate():
                async for chunk in proxy_service.create_chat_completion_stream(request):
                    yield chunk

            return StreamingResponse(
                generate(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "X-Accel-Buffering": "no"
                }
            )
        else:
            # Get non-streaming response
            start_time = time.time()
            response = await proxy_service.create_chat_completion(request)
            request_duration_ms = (time.time() - start_time) * 1000

            # Record usage
            usage_record = UsageRecord(
                user_id=user.id,
                api_key_id=api_key.id,
                original_tokens=response.compression_metadata.get("original_tokens", 0) if response.compression_metadata else response.usage.prompt_tokens,
                compressed_tokens=response.usage.prompt_tokens if response.usage else 0,
                tokens_saved=response.compression_metadata.get("tokens_saved", 0) if response.compression_metadata else 0,
                compression_ratio=response.compression_metadata.get("compression_ratio", 1.0) if response.compression_metadata else 1.0,
                strategy=response.compression_metadata.get("strategy", "none") if response.compression_metadata else "none",
                compression_time_ms=response.compression_metadata.get("compression_time_ms", 0) if response.compression_metadata else 0,
                request_metadata={
                    "model": request.model,
                    "request_duration_ms": request_duration_ms,
                    "stream": request.stream
                }
            )
            db.add(usage_record)
            db.commit()

            return response

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get(
    "/models",
    summary="List available models",
    description="List models available through Concise proxy"
)
async def list_models(
    api_key: APIKey = Depends(get_current_api_key)
):
    """
    List available models

    Returns OpenAI models that support compression through Concise
    """
    return {
        "object": "list",
        "data": [
            {
                "id": "gpt-4",
                "object": "model",
                "created": 1687882411,
                "owned_by": "openai",
                "permission": [],
                "root": "gpt-4",
                "parent": None,
            },
            {
                "id": "gpt-4-turbo-preview",
                "object": "model",
                "created": 1706037612,
                "owned_by": "openai",
                "permission": [],
                "root": "gpt-4-turbo-preview",
                "parent": None,
            },
            {
                "id": "gpt-3.5-turbo",
                "object": "model",
                "created": 1677610602,
                "owned_by": "openai",
                "permission": [],
                "root": "gpt-3.5-turbo",
                "parent": None,
            },
            {
                "id": "gpt-3.5-turbo-16k",
                "object": "model",
                "created": 1683758102,
                "owned_by": "openai",
                "permission": [],
                "root": "gpt-3.5-turbo-16k",
                "parent": None,
            }
        ]
    }
