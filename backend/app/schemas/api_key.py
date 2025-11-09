"""
API Key schemas for request/response validation
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class APIKeyBase(BaseModel):
    """Base API key schema"""
    name: Optional[str] = Field(None, max_length=100, description="User-friendly name for the key")


class APIKeyCreate(APIKeyBase):
    """Schema for creating a new API key"""
    expires_days: Optional[int] = Field(None, ge=1, le=365, description="Number of days until expiration")


class APIKeyResponse(APIKeyBase):
    """Schema for API key response (excludes the actual key)"""
    id: UUID
    key_prefix: str  # First 8 chars for identification
    is_active: bool
    created_at: datetime
    last_used_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class APIKeyCreatedResponse(APIKeyResponse):
    """
    Schema for API key creation response

    IMPORTANT: This includes the full API key which is only shown ONCE
    """
    key: str = Field(..., description="Full API key - save this, it won't be shown again!")


class APIKeyListResponse(BaseModel):
    """Schema for listing API keys"""
    keys: list[APIKeyResponse]
    total: int
