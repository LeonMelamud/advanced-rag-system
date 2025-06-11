"""Authentication utilities for Advanced RAG System"""

import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

logger = logging.getLogger(__name__)

# Configuration
SECRET_KEY = (
    "992f1fc774b181a19ecc1e1c475a8b4d86405f2ba9e1d2dc5cd00bf8fa1eb183"  # Hardcoded for testing
)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Bearer scheme
security = HTTPBearer()


class UserContext:
    """User context for authenticated requests"""

    def __init__(
        self,
        user_id: str,
        username: str,
        email: str,
        roles: List[str] = None,
        permissions: List[str] = None,
        accessible_collections: List[str] = None,
    ):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.roles = roles or []
        self.permissions = permissions or []
        self.accessible_collections = accessible_collections or []

    def has_role(self, role: str) -> bool:
        """Check if user has specific role"""
        return role in self.roles

    def has_permission(self, permission: str) -> bool:
        """Check if user has specific permission"""
        return permission in self.permissions

    def can_access_collection(self, collection_id: str) -> bool:
        """Check if user can access specific collection"""
        return collection_id in self.accessible_collections or "admin" in self.roles


class PasswordManager:
    """Password hashing and verification"""

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password"""
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)


class TokenData(BaseModel):
    """Token payload data"""

    user_id: str
    email: str
    role: str
    username: Optional[str] = None
    full_name: Optional[str] = None
    token_type: str = "access"


class PasswordValidator:
    """Password validation utilities"""

    @staticmethod
    def validate_password_strength(password: str) -> bool:
        """Validate password meets minimum requirements"""
        if len(password) < 8:
            return False

        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)

        return has_upper and has_lower and has_digit

    @staticmethod
    def get_password_requirements() -> str:
        """Get password requirements description"""
        return "Password must be at least 8 characters long and contain uppercase, lowercase, and numeric characters"


class AuthUtils:
    """Shared authentication utilities following DRY principles"""

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        """Hash a password"""
        return pwd_context.hash(password)

    @staticmethod
    def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

        to_encode.update({"exp": expire, "token_type": "access", "iat": datetime.utcnow()})

        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    @staticmethod
    def create_refresh_token(data: Dict[str, Any]) -> str:
        """Create JWT refresh token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

        to_encode.update({"exp": expire, "token_type": "refresh", "iat": datetime.utcnow()})

        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    @staticmethod
    def verify_token(token: str, expected_type: str = "access") -> TokenData:
        """Verify and decode JWT token"""
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

            # Check token type
            token_type = payload.get("token_type")
            if token_type != expected_type:
                raise credentials_exception

            # Extract user data
            user_id: str = payload.get("sub")
            email: str = payload.get("email")
            role: str = payload.get("role")
            username: str = payload.get("username")
            full_name: str = payload.get("full_name")

            if user_id is None or email is None:
                raise credentials_exception

            return TokenData(
                user_id=user_id,
                email=email,
                role=role,
                username=username,
                full_name=full_name,
                token_type=token_type,
            )

        except JWTError:
            raise credentials_exception

    @staticmethod
    def create_token_pair(user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create both access and refresh tokens"""
        access_token = AuthUtils.create_access_token(data=user_data)
        refresh_token = AuthUtils.create_refresh_token(data=user_data)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # Convert to seconds
        }


class AuthenticationError(Exception):
    """Custom authentication error"""

    pass


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> UserContext:
    """Get current authenticated user from JWT token"""
    try:
        token = credentials.credentials
        payload = AuthUtils.verify_token(token)

        # Verify token type
        if payload.token_type != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Extract user information
        user_id = payload.user_id
        username = payload.username or payload.email  # Use username from token, fallback to email
        email = payload.email
        role = payload.role

        if user_id is None or email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return UserContext(
            user_id=user_id,
            username=username,
            email=email,
            roles=[role] if role else ["user"],
            permissions=[],
            accessible_collections=[],
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_optional_user(request: Request) -> Optional[UserContext]:
    """Get current user if authenticated, None otherwise"""
    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None

        token = auth_header.split(" ")[1]
        payload = AuthUtils.verify_token(token)

        if payload.token_type != "access":
            return None

        user_id = payload.user_id
        username = payload.username or payload.email  # Use username from token, fallback to email
        email = payload.email
        role = payload.role

        if user_id is None or email is None:
            return None

        return UserContext(
            user_id=user_id,
            username=username,
            email=email,
            roles=[role] if role else ["user"],
            permissions=[],
            accessible_collections=[],
        )

    except Exception:
        return None


def require_role(required_role: str):
    """Decorator to require specific role"""

    def role_checker(user: UserContext = Depends(get_current_user)) -> UserContext:
        if not user.has_role(required_role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail=f"Role '{required_role}' required"
            )
        return user

    return role_checker


def require_permission(required_permission: str):
    """Decorator to require specific permission"""

    def permission_checker(user: UserContext = Depends(get_current_user)) -> UserContext:
        if not user.has_permission(required_permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{required_permission}' required",
            )
        return user

    return permission_checker


def require_collection_access(collection_id: str):
    """Decorator to require access to specific collection"""

    def collection_checker(user: UserContext = Depends(get_current_user)) -> UserContext:
        if not user.can_access_collection(collection_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access to collection '{collection_id}' denied",
            )
        return user

    return collection_checker


# Common role and permission constants
class Roles:
    ADMIN = "admin"
    USER = "user"
    MODERATOR = "moderator"


class Permissions:
    READ_COLLECTION = "read:collection"
    WRITE_COLLECTION = "write:collection"
    DELETE_COLLECTION = "delete:collection"
    ADMIN_COLLECTION = "admin:collection"
    CHAT_ACCESS = "chat:access"
    FILE_UPLOAD = "file:upload"
    FILE_DELETE = "file:delete"
    USER_MANAGEMENT = "user:management"


# Utility functions for creating user tokens
def create_user_tokens(
    user_id: str,
    username: str,
    email: str,
    roles: List[str] = None,
    permissions: List[str] = None,
    accessible_collections: List[str] = None,
) -> Dict[str, str]:
    """Create access and refresh tokens for user"""
    user_data = {
        "sub": user_id,
        "username": username,
        "email": email,
        "roles": roles or [],
        "permissions": permissions or [],
        "accessible_collections": accessible_collections or [],
    }

    access_token = AuthUtils.create_access_token(user_data)
    refresh_token = AuthUtils.create_refresh_token({"sub": user_id, "username": username})

    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}
