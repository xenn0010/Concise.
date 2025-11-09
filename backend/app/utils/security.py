"""
Security utilities for authentication and authorization
"""
from datetime import datetime, timedelta
from typing import Optional
import secrets
import hashlib
from passlib.context import CryptContext
from jose import JWTError, jwt

from app.config import get_settings

settings = get_settings()

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token

    Args:
        data: Data to encode in the token (usually {"sub": user_id})
        expires_delta: Optional expiration time delta

    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """
    Verify and decode a JWT token

    Args:
        token: JWT token string

    Returns:
        Decoded token payload or None if invalid
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        return None


def generate_api_key() -> tuple[str, str, str]:
    """
    Generate a new API key

    Returns:
        Tuple of (full_key, key_hash, key_prefix)
        - full_key: The complete API key to show to user (only once)
        - key_hash: SHA-256 hash to store in database
        - key_prefix: First 8 characters for display
    """
    # Generate secure random key
    random_bytes = secrets.token_bytes(32)
    full_key = f"csk_live_{secrets.token_urlsafe(32)}"

    # Hash the key for storage
    key_hash = hashlib.sha256(full_key.encode()).hexdigest()

    # Get prefix for display
    key_prefix = full_key[:12]

    return full_key, key_hash, key_prefix


def hash_api_key(api_key: str) -> str:
    """
    Hash an API key for verification

    Args:
        api_key: The full API key string

    Returns:
        SHA-256 hash of the key
    """
    return hashlib.sha256(api_key.encode()).hexdigest()
