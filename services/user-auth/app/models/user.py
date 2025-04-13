from sqlalchemy import Column, Integer, String, Boolean, DateTime
from app.db.base import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    location = Column(String, nullable=True)
    is_blocked = Column(Boolean, default=False)
    failed_login_attempts = Column(Integer, default=0)
    first_login_failure = Column(DateTime, default=None)
    blocked_until = Column(DateTime, default=None)
