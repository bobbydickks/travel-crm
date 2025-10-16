from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base
import enum


class UserRole(enum.Enum):
    ADMIN = "admin"
    OPERATOR = "operator"
    ACCOUNTANT = "accountant"
    SUPERVISOR = "supervisor"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.OPERATOR)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)  # Организация пользователя
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Связи
    refresh_tokens = relationship("RefreshToken", back_populates="user")
    organization = relationship("Organization", back_populates="users")
