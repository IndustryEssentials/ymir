from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, UniqueConstraint

from app.config import settings
from app.db.base_class import Base


class Model(Base):
    __tablename__ = "model"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    hash = Column(String(settings.HASH_LEN_LIMIT), index=True)
    name = Column(String(settings.NAME_LEN_LIMIT), index=True)
    map = Column(Float)
    parameters = Column(String(settings.PARA_LEN_LIMIT))
    task_id = Column(Integer, index=True)
    user_id = Column(Integer, index=True)
    is_deleted = Column(Boolean, default=False)
    create_datetime = Column(DateTime, default=datetime.utcnow, nullable=False)
    update_datetime = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
    __table_args__ = (
        UniqueConstraint('user_id', 'hash', name='uniq_user_hash'),
    )
