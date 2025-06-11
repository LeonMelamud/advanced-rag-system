"""
User CRUD Operations
Database operations for user management following DRY principles
"""

from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.auth_service.app.models.user import User, UserRole
from backend.common.auth import AuthUtils, PasswordValidator


class UserCRUD:
    """User CRUD operations following DRY principles"""

    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: str) -> Optional[User]:
        """Get user by ID"""
        result = await db.execute(select(User).filter(User.id == user_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
        """Get user by email"""
        result = await db.execute(select(User).filter(User.email == email))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
        """Get user by username"""
        result = await db.execute(select(User).filter(User.username == username))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_users(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[User]:
        """Get list of users with pagination"""
        result = await db.execute(select(User).offset(skip).limit(limit))
        return result.scalars().all()

    @staticmethod
    async def create_user(
        db: AsyncSession,
        email: str,
        username: str,
        password: str,
        full_name: str,
        is_superuser: bool = False,
    ) -> User:
        """Create a new user"""

        # Validate password strength
        if not PasswordValidator.validate_password_strength(password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=PasswordValidator.get_password_requirements(),
            )

        # Check if user already exists by email
        if await UserCRUD.get_user_by_email(db, email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
            )

        # Check if username already exists
        if await UserCRUD.get_user_by_username(db, username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken"
            )

        # Hash password
        hashed_password = AuthUtils.get_password_hash(password)

        # Create user
        db_user = User(
            email=email,
            username=username,
            hashed_password=hashed_password,
            full_name=full_name,
            is_superuser=is_superuser,
            is_active=True,
        )

        try:
            db.add(db_user)
            await db.commit()
            await db.refresh(db_user)
            return db_user
        except IntegrityError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email or username already registered",
            )

    @staticmethod
    async def authenticate_user(db: AsyncSession, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password"""
        user = await UserCRUD.get_user_by_email(db, email)

        if not user:
            return None

        if not user.is_active:
            return None

        if not AuthUtils.verify_password(password, user.hashed_password):
            return None

        return user

    @staticmethod
    async def update_user(
        db: AsyncSession,
        user_id: str,
        email: Optional[str] = None,
        username: Optional[str] = None,
        full_name: Optional[str] = None,
        is_superuser: Optional[bool] = None,
        is_active: Optional[bool] = None,
    ) -> Optional[User]:
        """Update user information"""
        user = await UserCRUD.get_user_by_id(db, user_id)

        if not user:
            return None

        # Update fields if provided
        if email is not None:
            # Check if new email is already taken
            existing_user = await UserCRUD.get_user_by_email(db, email)
            if existing_user and existing_user.id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
                )
            user.email = email

        if username is not None:
            # Check if new username is already taken
            existing_user = await UserCRUD.get_user_by_username(db, username)
            if existing_user and existing_user.id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken"
                )
            user.username = username

        if full_name is not None:
            user.full_name = full_name

        if is_superuser is not None:
            user.is_superuser = is_superuser

        if is_active is not None:
            user.is_active = is_active

        try:
            await db.commit()
            await db.refresh(user)
            return user
        except IntegrityError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email or username already registered",
            )

    @staticmethod
    async def change_password(
        db: AsyncSession, user_id: str, current_password: str, new_password: str
    ) -> bool:
        """Change user password"""
        user = await UserCRUD.get_user_by_id(db, user_id)

        if not user:
            return False

        # Verify current password
        if not AuthUtils.verify_password(current_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is incorrect"
            )

        # Validate new password strength
        if not PasswordValidator.validate_password_strength(new_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=PasswordValidator.get_password_requirements(),
            )

        # Update password
        user.hashed_password = AuthUtils.get_password_hash(new_password)

        await db.commit()
        return True

    @staticmethod
    async def delete_user(db: AsyncSession, user_id: str) -> bool:
        """Delete user (soft delete by setting is_active=False)"""
        user = await UserCRUD.get_user_by_id(db, user_id)

        if not user:
            return False

        # Soft delete by deactivating
        user.is_active = False
        await db.commit()
        return True

    @staticmethod
    async def get_active_users_count(db: AsyncSession) -> int:
        """Get count of active users"""
        result = await db.execute(select(User).filter(User.is_active == True))
        return len(result.scalars().all())

    @staticmethod
    async def get_superusers(db: AsyncSession) -> List[User]:
        """Get users with superuser privileges"""
        result = await db.execute(
            select(User).filter(User.is_superuser == True, User.is_active == True)
        )
        return result.scalars().all()
