"""
OpenAI proxy service with prompt compression
"""
import time
import uuid
from typing import AsyncIterator, Optional
import json

from openai import AsyncOpenAI
from openai.types.chat import ChatCompletion, ChatCompletionChunk

from app.config import get_settings
from app.schemas.proxy import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatMessage,
    ChatCompletionChoice,
    CompletionUsage
)
from app.services.compression import get_compressor, CompressionResult


class OpenAIProxyService:
    """
    Proxy service for OpenAI API with prompt compression

    Flow:
    1. Receive chat completion request
    2. Compress messages (if enabled)
    3. Forward to OpenAI
    4. Stream/return response
    5. Track usage metrics
    """

    def __init__(self):
        settings = get_settings()
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.compressor = get_compressor()

    def compress_messages(
        self,
        messages: list[ChatMessage],
        level: str = "auto"
    ) -> tuple[list[ChatMessage], list[CompressionResult]]:
        """
        Compress messages in the conversation using token compression

        Args:
            messages: List of chat messages
            level: Compression level (auto, aggressive, balanced, conservative)

        Returns:
            Tuple of (compressed_messages, compression_results)
        """
        compressed_messages = []
        compression_results = []

        for msg in messages:
            # Only compress user and system messages (not assistant responses)
            if msg.role in ["user", "system"] and msg.content:
                result = self.compressor.compress(
                    msg.content,
                    level=level
                )
                compression_results.append(result)

                # Create compressed message
                compressed_msg = ChatMessage(
                    role=msg.role,
                    content=result.compressed_text,
                    name=msg.name
                )
                compressed_messages.append(compressed_msg)
            else:
                # Don't compress assistant messages or empty content
                compressed_messages.append(msg)

        return compressed_messages, compression_results

    async def create_chat_completion(
        self,
        request: ChatCompletionRequest
    ) -> ChatCompletionResponse:
        """
        Create a chat completion with optional compression

        Args:
            request: Chat completion request

        Returns:
            Chat completion response
        """
        # Compress messages if enabled
        if request.compression_enabled:
            compressed_messages, compression_results = self.compress_messages(
                request.messages,
                level=request.compression_level
            )
        else:
            compressed_messages = request.messages
            compression_results = []

        # Prepare OpenAI request
        openai_request = {
            "model": request.model,
            "messages": [msg.model_dump(exclude_none=True) for msg in compressed_messages],
            "temperature": request.temperature,
            "top_p": request.top_p,
            "n": request.n,
            "stream": False,  # Non-streaming
            "max_tokens": request.max_tokens,
            "presence_penalty": request.presence_penalty,
            "frequency_penalty": request.frequency_penalty,
            "user": request.user,
        }

        # Add optional parameters
        if request.stop:
            openai_request["stop"] = request.stop
        if request.logit_bias:
            openai_request["logit_bias"] = request.logit_bias
        if request.functions:
            openai_request["functions"] = [f.model_dump(exclude_none=True) for f in request.functions]
        if request.function_call:
            openai_request["function_call"] = request.function_call

        # Call OpenAI API
        response: ChatCompletion = await self.client.chat.completions.create(**openai_request)

        # Calculate compression metadata
        compression_metadata = None
        if compression_results:
            total_original = sum(r.original_tokens for r in compression_results)
            total_compressed = sum(r.compressed_tokens for r in compression_results)
            total_saved = total_original - total_compressed

            compression_metadata = {
                "enabled": True,
                "level": request.compression_level,
                "original_tokens": total_original,
                "compressed_tokens": total_compressed,
                "tokens_saved": total_saved,
                "compression_ratio": total_compressed / total_original if total_original > 0 else 1.0,
                "compression_time_ms": sum(r.compression_time_ms for r in compression_results)
            }

        # Build response
        return ChatCompletionResponse(
            id=response.id,
            created=response.created,
            model=response.model,
            choices=[
                ChatCompletionChoice(
                    index=choice.index,
                    message=ChatMessage(
                        role=choice.message.role,
                        content=choice.message.content or "",
                        function_call=choice.message.function_call
                    ),
                    finish_reason=choice.finish_reason
                )
                for choice in response.choices
            ],
            usage=CompletionUsage(
                prompt_tokens=response.usage.prompt_tokens,
                completion_tokens=response.usage.completion_tokens,
                total_tokens=response.usage.total_tokens,
                original_prompt_tokens=compression_metadata["original_tokens"] if compression_metadata else None,
                compressed_prompt_tokens=compression_metadata["compressed_tokens"] if compression_metadata else None,
                tokens_saved=compression_metadata["tokens_saved"] if compression_metadata else None,
                compression_ratio=compression_metadata["compression_ratio"] if compression_metadata else None
            ) if response.usage else None,
            compression_metadata=compression_metadata
        )

    async def create_chat_completion_stream(
        self,
        request: ChatCompletionRequest
    ) -> AsyncIterator[str]:
        """
        Create a streaming chat completion with optional compression

        Args:
            request: Chat completion request

        Yields:
            Server-sent event strings in OpenAI format
        """
        # Compress messages if enabled
        if request.compression_enabled:
            compressed_messages, compression_results = self.compress_messages(
                request.messages,
                level=request.compression_level
            )
        else:
            compressed_messages = request.messages
            compression_results = []

        # Prepare OpenAI request
        openai_request = {
            "model": request.model,
            "messages": [msg.model_dump(exclude_none=True) for msg in compressed_messages],
            "temperature": request.temperature,
            "top_p": request.top_p,
            "n": request.n,
            "stream": True,  # Enable streaming
            "max_tokens": request.max_tokens,
            "presence_penalty": request.presence_penalty,
            "frequency_penalty": request.frequency_penalty,
            "user": request.user,
        }

        # Add optional parameters
        if request.stop:
            openai_request["stop"] = request.stop
        if request.logit_bias:
            openai_request["logit_bias"] = request.logit_bias
        if request.functions:
            openai_request["functions"] = [f.model_dump(exclude_none=True) for f in request.functions]
        if request.function_call:
            openai_request["function_call"] = request.function_call

        # Stream from OpenAI
        stream = await self.client.chat.completions.create(**openai_request)

        # Send compression metadata as first chunk (custom extension)
        if compression_results:
            total_original = sum(r.original_tokens for r in compression_results)
            total_compressed = sum(r.compressed_tokens for r in compression_results)
            total_saved = total_original - total_compressed

            metadata_chunk = {
                "id": f"chatcmpl-{uuid.uuid4().hex[:24]}",
                "object": "chat.completion.chunk",
                "created": int(time.time()),
                "model": request.model,
                "choices": [],
                "compression_metadata": {
                    "enabled": True,
                    "strategy": request.compression_strategy,
                    "original_tokens": total_original,
                    "compressed_tokens": total_compressed,
                    "tokens_saved": total_saved,
                    "compression_ratio": total_compressed / total_original if total_original > 0 else 1.0,
                    "compression_time_ms": sum(r.compression_time_ms for r in compression_results)
                }
            }
            yield f"data: {json.dumps(metadata_chunk)}\n\n"

        # Forward chunks from OpenAI
        async for chunk in stream:
            chunk_dict = chunk.model_dump()
            yield f"data: {json.dumps(chunk_dict)}\n\n"

        # Send final [DONE] message
        yield "data: [DONE]\n\n"


# Global proxy service instance
_proxy_service: Optional[OpenAIProxyService] = None


def get_proxy_service() -> OpenAIProxyService:
    """Get or create global proxy service instance"""
    global _proxy_service
    if _proxy_service is None:
        _proxy_service = OpenAIProxyService()
    return _proxy_service
