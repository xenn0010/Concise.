"""
Pydantic schemas for OpenAI proxy endpoints
Matches OpenAI Chat Completion API format
"""
from typing import Optional, List, Dict, Any, Literal, Union
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """A single chat message"""
    role: Literal["system", "user", "assistant", "function"]
    content: str
    name: Optional[str] = None
    function_call: Optional[Dict[str, Any]] = None


class FunctionDefinition(BaseModel):
    """Function definition for function calling"""
    name: str
    description: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None


class ChatCompletionRequest(BaseModel):
    """
    Request body for /v1/chat/completions endpoint
    Matches OpenAI API format with Concise-specific extensions
    """
    # Required
    model: str
    messages: List[ChatMessage]

    # Optional OpenAI parameters
    temperature: Optional[float] = Field(default=1.0, ge=0, le=2)
    top_p: Optional[float] = Field(default=1.0, ge=0, le=1)
    n: Optional[int] = Field(default=1, ge=1)
    stream: Optional[bool] = False
    stop: Optional[Union[str, List[str]]] = None
    max_tokens: Optional[int] = None
    presence_penalty: Optional[float] = Field(default=0, ge=-2, le=2)
    frequency_penalty: Optional[float] = Field(default=0, ge=-2, le=2)
    logit_bias: Optional[Dict[str, float]] = None
    user: Optional[str] = None
    functions: Optional[List[FunctionDefinition]] = None
    function_call: Optional[Union[str, Dict[str, str]]] = None

    # Concise-specific parameters
    compression_enabled: Optional[bool] = Field(
        default=True,
        description="Enable token compression"
    )
    compression_level: Optional[Literal["auto", "aggressive", "balanced", "conservative"]] = Field(
        default="auto",
        description="Compression level: auto (recommended), aggressive (50% reduction), balanced (30% reduction), conservative (20% reduction)"
    )


class CompletionUsage(BaseModel):
    """Token usage statistics"""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

    # Concise-specific fields
    original_prompt_tokens: Optional[int] = None
    compressed_prompt_tokens: Optional[int] = None
    tokens_saved: Optional[int] = None
    compression_ratio: Optional[float] = None


class ChatCompletionChoice(BaseModel):
    """A single completion choice"""
    index: int
    message: ChatMessage
    finish_reason: Optional[str] = None


class ChatCompletionResponse(BaseModel):
    """Response from /v1/chat/completions endpoint"""
    id: str
    object: Literal["chat.completion"] = "chat.completion"
    created: int
    model: str
    choices: List[ChatCompletionChoice]
    usage: Optional[CompletionUsage] = None

    # Concise-specific metadata
    compression_metadata: Optional[Dict[str, Any]] = None


class ChatCompletionChunk(BaseModel):
    """Streaming response chunk"""
    id: str
    object: Literal["chat.completion.chunk"] = "chat.completion.chunk"
    created: int
    model: str
    choices: List[Dict[str, Any]]  # Simplified for streaming


class ErrorResponse(BaseModel):
    """Error response"""
    error: Dict[str, Any]
