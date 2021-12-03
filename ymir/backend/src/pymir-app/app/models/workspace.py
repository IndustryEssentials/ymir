from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String

from app.config import settings
from app.db.base_class import Base


class Workspace(Base):
    __tablename__ = "workspace"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    hash = Column(String(settings.HASH_LEN_LIMIT), index=True, unique=True)
    name = Column(String(settings.NAME_LEN_LIMIT), index=True, unique=True)
    user_id = Column(Integer, index=True)
    is_deleted = Column(Boolean, default=False)
    create_datetime = Column(DateTime, default=datetime.utcnow, nullable=False)
    update_datetime = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
