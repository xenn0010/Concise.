"""
API Key management endpoints
Create, list, and revoke API keys
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.api_key import (
    APIKeyCreate,
    APIKeyCreatedResponse,
    APIKeyResponse,
    APIKeyListResponse
)
from app.services.auth import (
    create_api_key_for_user,
    get_user_api_keys,
    revoke_api_key
)
from app.middleware.auth import get_current_user
from app.models.user import User

router = APIRouter()


@router.get("/", response_model=APIKeyListResponse)
async def list_api_keys(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all API keys for the current user

    Returns a list of API keys (without the actual key values).
    Shows key prefix, creation date, and expiration info.
    """
    keys = get_user_api_keys(db, str(current_user.id))

    return {
        "keys": keys,
        "total": len(keys)
    }


@router.post("/", response_model=APIKeyCreatedResponse, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    key_create: APIKeyCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new API key

    Generates a new API key for the current user.

    **IMPORTANT:** The full API key is only shown ONCE in the response.
    Save it securely - you won't be able to retrieve it again!

    The key can optionally be set to expire after a specified number of days.
    """
    api_key, full_key = create_api_key_for_user(db, str(current_user.id), key_create)

    # Return the API key with the full key (only shown once!)
    return {
        **APIKeyResponse.model_validate(api_key).model_dump(),
        "key": full_key
    }


@router.delete("/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_api_key(
    key_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Revoke (delete) an API key

    Deactivates the specified API key.
    The key will no longer be valid for authentication.
    """
    success = revoke_api_key(db, str(current_user.id), key_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )

    return None
