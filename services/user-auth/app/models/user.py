from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from app.db.base import Base
import enum


class AuthProvider(str, enum.Enum):
    GOOGLE = "google"
    LOCAL = "local"
    LOCAL_GOOGLE = "local_google"


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    location = Column(String, nullable=True)
    is_teacher = Column(Boolean, default=False, nullable=False)
    academic_level = Column(Integer, default=0, nullable=False)
    is_blocked = Column(Boolean, default=False)
    failed_login_attempts = Column(Integer, default=0)
    first_login_failure = Column(DateTime, default=None)
    blocked_until = Column(DateTime, default=None)
    auth_provider = Column(
        Enum(AuthProvider), default=AuthProvider.LOCAL, nullable=False
    )
