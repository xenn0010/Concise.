"""
Authentication service
Business logic for user authentication and authorization
"""
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException, status

from app.models.user import User
from app.models.api_key import APIKey
from app.schemas.user import UserCreate
from app.schemas.api_key import APIKeyCreate
from app.utils.security import (
    hash_password,
    verify_password,
    create_access_token,
    generate_api_key,
    hash_api_key
)


def register_user(db: Session, user_create: UserCreate) -> User:
    """
    Register a new user

    Args:
        db: Database session
        user_create: User creation schema

    Returns:
        Created user object

    Raises:
        HTTPException: If email already exists
    """
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_create.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create new user
    user = User(
        email=user_create.email,
        hashed_password=hash_password(user_create.password),
        full_name=user_create.full_name,
        company=user_create.company,
        is_verified=False  # Require email verification
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """
    Authenticate a user with email and password

    Args:
        db: Database session
        email: User email
        password: Plain text password

    Returns:
        User object if authentication successful, None otherwise
    """
    user = db.query(User).filter(User.email == email).first()

    if not user:
        return None

    if not verify_password(password, user.hashed_password):
        return None

    # Update last login timestamp
    user.last_login_at = datetime.utcnow()
    db.commit()

    return user


def create_user_token(user: User) -> dict:
    """
    Create JWT token for a user

    Args:
        user: User object

    Returns:
        Dictionary with access_token and metadata
    """
    from app.config import get_settings
    settings = get_settings()

    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60  # Convert to seconds
    }


def create_api_key_for_user(
    db: Session,
    user_id: str,
    api_key_create: APIKeyCreate
) -> tuple[APIKey, str]:
    """
    Create an API key for a user

    Args:
        db: Database session
        user_id: User's UUID
        api_key_create: API key creation schema

    Returns:
        Tuple of (APIKey object, full_key_string)
        The full_key_string is only returned once and should be shown to the user
    """
    # Generate API key
    full_key, key_hash, key_prefix = generate_api_key()

    # Calculate expiration
    expires_at = None
    if api_key_create.expires_days:
        expires_at = datetime.utcnow() + timedelta(days=api_key_create.expires_days)

    # Create API key record
    api_key = APIKey(
        user_id=user_id,
        key_hash=key_hash,
        key_prefix=key_prefix,
        name=api_key_create.name,
        expires_at=expires_at
    )

    db.add(api_key)
    db.commit()
    db.refresh(api_key)

    return api_key, full_key


def verify_api_key(db: Session, api_key_string: str) -> Optional[tuple[User, APIKey]]:
    """
    Verify an API key and return the associated user

    Args:
        db: Database session
        api_key_string: The full API key string

    Returns:
        Tuple of (User, APIKey) if valid, None otherwise
    """
    # Hash the provided key
    key_hash = hash_api_key(api_key_string)

    # Find the API key
    api_key = db.query(APIKey).filter(APIKey.key_hash == key_hash).first()

    if not api_key:
        return None

    # Check if key is valid
    if not api_key.is_valid():
        return None

    # Get the user
    user = db.query(User).filter(User.id == api_key.user_id).first()

    if not user or not user.is_active:
        return None

    # Update last used timestamp
    api_key.update_last_used()
    db.commit()

    return user, api_key


def revoke_api_key(db: Session, user_id: str, key_id: str) -> bool:
    """
    Revoke (deactivate) an API key

    Args:
        db: Database session
        user_id: User's UUID
        key_id: API key's UUID

    Returns:
        True if revoked successfully, False otherwise
    """
    api_key = db.query(APIKey).filter(
        APIKey.id == key_id,
        APIKey.user_id == user_id
    ).first()

    if not api_key:
        return False

    api_key.is_active = False
    db.commit()

    return True


def get_user_api_keys(db: Session, user_id: str) -> list[APIKey]:
    """
    Get all API keys for a user

    Args:
        db: Database session
        user_id: User's UUID

    Returns:
        List of APIKey objects
    """
    return db.query(APIKey).filter(APIKey.user_id == user_id).all()
