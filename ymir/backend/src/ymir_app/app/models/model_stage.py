from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    Integer,
    String,
    UniqueConstraint
)

from app.config import settings
from app.db.base_class import Base


class ModelStage(Base):
    __tablename__ = "model_stage"
    __table_args__ = (UniqueConstraint('model_id', 'name'),)
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(settings.STRING_LEN_LIMIT), index=True)
    timestamp = Column(Integer, nullable=False)
    map = Column(Float, nullable=True)
    model_id = Column(Integer, index=True, nullable=False)

    is_deleted = Column(Boolean, default=False, nullable=False)
    create_datetime = Column(DateTime, default=datetime.utcnow, nullable=False)
    update_datetime = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False,
    )
