from datetime import datetime
import uuid

from sqlalchemy import Boolean, Column, DateTime, Integer, String

from auth.db.base_class import Base
from auth.config import settings


def generate_uuid() -> str:
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(100), unique=True, index=True, nullable=False)
    username = Column(String(100), index=True)
    phone = Column(String(20), unique=True, index=True)
    avatar = Column(String(100))
    hashed_password = Column(String(200), nullable=False)
    state = Column(Integer, index=True, default=1)
    role = Column(Integer, index=True, default=1)
    organization = Column(String(settings.STRING_LEN_LIMIT))
    scene = Column(String(settings.LONG_STRING_LEN_LIMIT))
    uuid = Column(String(36), default=generate_uuid, nullable=False)

    is_deleted = Column(Boolean(), default=False)
    last_login_datetime = Column(DateTime, nullable=True)
    create_datetime = Column(DateTime, default=datetime.utcnow, nullable=False)
    update_datetime = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
