"""
User Model for Authentication Service
Uses shared base classes following DRY principles
"""

import enum

from sqlalchemy import Boolean, Column, DateTime, Enum, String
from sqlalchemy.orm import relationship

from backend.common.models import BaseModel


class UserRole(str, enum.Enum):
    """User roles for RBAC"""

    ADMIN = "admin"
    USER = "user"
    VIEWER = "viewer"


class User(BaseModel):
    """User model with authentication and profile information"""

    __tablename__ = "users"
    __table_args__ = {"schema": "auth"}

    # Authentication fields
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)

    # Profile fields
    full_name = Column(String(255), nullable=True)

    # Status fields
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    last_login = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, username={self.username})>"

    @property
    def role(self) -> UserRole:
        """Get user role based on is_superuser flag"""
        if self.is_superuser:
            return UserRole.ADMIN
        return UserRole.USER

    @property
    def is_admin(self) -> bool:
        """Check if user has admin role"""
        return self.is_superuser

    @property
    def can_manage_collections(self) -> bool:
        """Check if user can manage collections"""
        return self.is_superuser or self.is_active
