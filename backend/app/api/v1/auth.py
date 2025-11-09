"""
Authentication endpoints
User registration, login, and token management
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token
from app.services.auth import register_user, authenticate_user, create_user_token
from app.middleware.auth import get_current_user
from app.models.user import User

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_create: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Register a new user

    Creates a new user account with the provided credentials.
    The user will start with the FREE tier.
    """
    user = register_user(db, user_create)
    return user


@router.post("/login", response_model=Token)
async def login(
    user_login: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Login and get access token

    Authenticates user with email and password.
    Returns a JWT access token for subsequent requests.
    """
    user = authenticate_user(db, user_login.email, user_login.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive. Please contact support."
        )

    # Create and return token
    token_data = create_user_token(user)
    return token_data


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user information

    Returns the profile of the currently authenticated user.
    Requires JWT token or API key.
    """
    return current_user


@router.post("/refresh", response_model=Token)
async def refresh_token(
    current_user: User = Depends(get_current_user)
):
    """
    Refresh access token

    Issues a new access token for the current user.
    Useful for extending session without re-authenticating.
    """
    token_data = create_user_token(current_user)
    return token_data
