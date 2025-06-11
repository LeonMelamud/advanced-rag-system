"""
Authentication API Endpoints
Real JWT authentication implementation using shared utilities
"""

import logging
from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from backend.auth_service.app.crud.user import UserCRUD
from backend.auth_service.app.models.user import User, UserRole
from backend.common.auth import AuthUtils, UserContext, get_current_user
from backend.common.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter()
security = HTTPBearer()


# Pydantic models for request/response
class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserRegister(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int


class UserInfo(BaseModel):
    id: str
    email: str
    username: str
    full_name: str
    role: str
    is_active: bool
    is_superuser: bool
    created_at: datetime


class PasswordChange(BaseModel):
    current_password: str
    new_password: str


@router.post("/login", response_model=Token)
async def login(user_data: UserLogin, db: AsyncSession = Depends(get_db)) -> Token:
    """Authenticate user and return JWT tokens"""
    logger.info(f"Login attempt for user: {user_data.email}")

    # Authenticate user
    user = await UserCRUD.authenticate_user(db, user_data.email, user_data.password)

    if not user:
        logger.warning(f"Failed login attempt for user: {user_data.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create token data
    token_data = {
        "sub": str(user.id),
        "email": user.email,
        "role": user.role.value,
        "username": user.username,
        "full_name": user.full_name,
    }

    # Generate token pair
    tokens = AuthUtils.create_token_pair(token_data)

    logger.info(f"Successful login for user: {user.email}")

    return Token(
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
        token_type=tokens["token_type"],
        expires_in=tokens["expires_in"],
    )


@router.post("/register", response_model=UserInfo)
async def register(user_data: UserRegister, db: AsyncSession = Depends(get_db)) -> UserInfo:
    """Register a new user"""
    logger.info(f"Registration attempt for user: {user_data.email}")

    # Create user
    user = await UserCRUD.create_user(
        db=db,
        email=user_data.email,
        username=user_data.username,
        password=user_data.password,
        full_name=user_data.full_name,
        is_superuser=False,
    )

    logger.info(f"Successful registration for user: {user.email}")

    return UserInfo(
        id=str(user.id),
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        role=user.role.value,
        is_active=user.is_active,
        is_superuser=user.is_superuser,
        created_at=user.created_at,
    )


@router.get("/me", response_model=UserInfo)
async def get_current_user_info(
    current_user: UserContext = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> UserInfo:
    """Get current user information from JWT token"""
    logger.info(f"User info request for user: {current_user.email}")

    # Get full user data from database
    user = await UserCRUD.get_user_by_id(db, current_user.user_id)

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return UserInfo(
        id=str(user.id),
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        role=user.role.value,
        is_active=user.is_active,
        is_superuser=user.is_superuser,
        created_at=user.created_at,
    )


@router.post("/logout")
async def logout(current_user: UserContext = Depends(get_current_user)) -> Dict[str, str]:
    """Logout user (token blacklisting can be implemented later)"""
    logger.info(f"Logout request for user: {current_user.email}")

    # TODO: Implement token blacklisting in Redis for enhanced security
    # For now, client-side token removal is sufficient

    return {"message": "Successfully logged out"}


@router.post("/refresh", response_model=Token)
async def refresh_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> Token:
    """Refresh JWT token using refresh token"""
    logger.info("Token refresh request")

    try:
        # Verify refresh token
        token_data = AuthUtils.verify_token(credentials.credentials, expected_type="refresh")

        # Get user from database to ensure they're still active
        user = await UserCRUD.get_user_by_id(db, token_data.user_id)

        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Create new token data
        new_token_data = {
            "sub": str(user.id),
            "email": user.email,
            "role": user.role.value,
            "username": user.username,
            "full_name": user.full_name,
        }

        # Generate new token pair
        tokens = AuthUtils.create_token_pair(new_token_data)

        logger.info(f"Token refreshed for user: {user.email}")

        return Token(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            token_type=tokens["token_type"],
            expires_in=tokens["expires_in"],
        )

    except HTTPException:
        logger.warning("Invalid refresh token provided")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: UserContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, str]:
    """Change user password"""
    logger.info(f"Password change request for user: {current_user.email}")

    success = await UserCRUD.change_password(
        db=db,
        user_id=current_user.user_id,
        current_password=password_data.current_password,
        new_password=password_data.new_password,
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to change password"
        )

    logger.info(f"Password changed successfully for user: {current_user.email}")

    return {"message": "Password changed successfully"}
