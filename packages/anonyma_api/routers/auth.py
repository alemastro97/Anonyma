"""
Authentication API routes.

Endpoints for:
- User registration
- Login
- Token refresh
- User profile
- Usage statistics
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import timedelta

from ..auth_extended import (
    auth_manager,
    usage_manager,
    get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

router = APIRouter(prefix="/auth", tags=["authentication"])


# Request/Response Models
class UserRegister(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


class UserProfile(BaseModel):
    id: str
    email: str
    username: str
    full_name: Optional[str]
    role: str
    created_at: str
    last_login: Optional[str]


class UsageStats(BaseModel):
    daily_used: int
    daily_limit: int
    monthly_used: int
    monthly_limit: int
    total_requests: int
    avg_processing_time: Optional[float]


# Endpoints
@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister):
    """
    Register a new user (demo account).

    Creates a demo account with limited usage quota.
    """
    try:
        user = auth_manager.create_user(
            email=user_data.email,
            username=user_data.username,
            password=user_data.password,
            full_name=user_data.full_name,
            role="demo"
        )

        # Create access token
        access_token = auth_manager.create_access_token(
            data={"sub": str(user["id"])},
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": str(user["id"]),
                "email": user["email"],
                "username": user["username"],
                "full_name": user.get("full_name"),
                "role": user["role"]
            }
        }

    except Exception as e:
        if "duplicate key value" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username or email already registered"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/login", response_model=Token)
async def login(credentials: UserLogin):
    """
    Login with username/email and password.

    Returns JWT access token valid for 30 minutes.
    """
    user = auth_manager.authenticate_user(
        username=credentials.username,
        password=credentials.password
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )

    # Create access token
    access_token = auth_manager.create_access_token(
        data={"sub": str(user["id"])},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": str(user["id"]),
            "email": user["email"],
            "username": user["username"],
            "full_name": user.get("full_name"),
            "role": user["role"]
        }
    }


@router.get("/me", response_model=UserProfile)
async def get_profile(user: dict = Depends(get_current_user)):
    """
    Get current user profile.

    Requires authentication.
    """
    return {
        "id": str(user["id"]),
        "email": user["email"],
        "username": user["username"],
        "full_name": user.get("full_name"),
        "role": user["role"],
        "created_at": str(user.get("created_at", "")),
        "last_login": str(user.get("last_login", "")) if user.get("last_login") else None
    }


@router.get("/usage", response_model=UsageStats)
async def get_usage_stats(user: dict = Depends(get_current_user)):
    """
    Get usage statistics and quota information.

    Shows daily/monthly usage and limits.
    """
    stats = usage_manager.get_user_stats(user["id"])

    if not stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usage stats not found"
        )

    return {
        "daily_used": stats.get("daily_used", 0),
        "daily_limit": stats.get("daily_limit", 0),
        "monthly_used": stats.get("monthly_used", 0),
        "monthly_limit": stats.get("monthly_limit", 0),
        "total_requests": stats.get("total_requests", 0),
        "avg_processing_time": stats.get("avg_processing_time")
    }


@router.post("/demo-login", response_model=Token)
async def demo_login():
    """
    Quick demo login without registration.

    Creates a temporary session with demo limits.
    Returns demo user credentials.
    """
    # Login with default demo user
    user = auth_manager.authenticate_user(
        username="demo",
        password="demo123"
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Demo user not available"
        )

    # Create access token
    access_token = auth_manager.create_access_token(
        data={"sub": str(user["id"])},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": str(user["id"]),
            "email": user["email"],
            "username": user["username"],
            "full_name": user.get("full_name"),
            "role": user["role"]
        }
    }
