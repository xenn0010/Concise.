"""
Authentication middleware
Handles JWT and API key authentication
"""
from fastapi import Depends, HTTPException, status, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyHeader
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models.user import User
from app.models.api_key import APIKey
from app.utils.security import verify_token
from app.services.auth import verify_api_key

# Security schemes
bearer_scheme = HTTPBearer(auto_error=False)
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def get_current_user_from_jwt(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(bearer_scheme),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Get current user from JWT token

    Args:
        credentials: HTTP authorization credentials
        db: Database session

    Returns:
        User object if authenticated, None otherwise

    Raises:
        HTTPException: If token is invalid
    """
    if not credentials:
        return None

    token = credentials.credentials

    # Verify token
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Get user ID from token
    user_id: str = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Get user from database
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )

    return user


async def get_current_user_from_api_key(
    api_key: Optional[str] = Security(api_key_header),
    db: Session = Depends(get_db)
) -> Optional[tuple[User, APIKey]]:
    """
    Get current user from API key

    Args:
        api_key: API key from header
        db: Database session

    Returns:
        Tuple of (User, APIKey) if authenticated, None otherwise

    Raises:
        HTTPException: If API key is invalid
    """
    if not api_key:
        return None

    # Verify API key
    result = verify_api_key(db, api_key)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired API key"
        )

    return result


async def get_current_user(
    jwt_user: Optional[User] = Depends(get_current_user_from_jwt),
    api_key_result: Optional[tuple[User, APIKey]] = Depends(get_current_user_from_api_key)
) -> User:
    """
    Get current user from either JWT or API key

    Supports dual authentication: JWT tokens OR API keys

    Args:
        jwt_user: User from JWT token
        api_key_result: User and API key from API key header

    Returns:
        Authenticated user

    Raises:
        HTTPException: If neither authentication method succeeds
    """
    # Try JWT first
    if jwt_user:
        return jwt_user

    # Try API key
    if api_key_result:
        user, api_key = api_key_result
        return user

    # No valid authentication
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated. Provide either Bearer token or X-API-Key header",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current active user

    Args:
        current_user: Current user from authentication

    Returns:
        User if active

    Raises:
        HTTPException: If user is not active
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user


async def get_current_verified_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Get current verified user

    Args:
        current_user: Current active user

    Returns:
        User if verified

    Raises:
        HTTPException: If user is not verified
    """
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified. Please verify your email address."
        )
    return current_user


async def get_current_api_key(
    api_key: Optional[str] = Security(api_key_header),
    db: Session = Depends(get_db)
) -> APIKey:
    """
    Get current API key (required for proxy endpoints)

    Args:
        api_key: API key from header
        db: Database session

    Returns:
        APIKey object

    Raises:
        HTTPException: If API key is invalid or missing
    """
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required. Provide X-API-Key header."
        )

    # Verify API key
    result = verify_api_key(db, api_key)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired API key"
        )

    user, api_key_obj = result
    return api_key_obj
