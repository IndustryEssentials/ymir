from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Integer,
    String,
)
from sqlalchemy.orm import relationship

from app.config import settings
from app.db.base_class import Base
from app.models.task import Task
from app.models.task_visual_relationship import TaskVisualRelationship


class Visualization(Base):
    __tablename__ = "visualization"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, index=True, nullable=False)
    tid = Column(String(settings.STRING_LEN_LIMIT), unique=True, nullable=False)
    project_id = Column(Integer, index=True, nullable=True)

    tasks = relationship(
        "Task",
        secondary=TaskVisualRelationship.__table__,
        primaryjoin=id == TaskVisualRelationship.__table__.c.visualization_id,
        secondaryjoin=Task.__table__.c.id == TaskVisualRelationship.__table__.c.task_id,
        uselist=True,
        viewonly=True,
    )

    is_deleted = Column(Boolean, default=False, nullable=False)
    create_datetime = Column(DateTime, default=datetime.utcnow, nullable=False)
    update_datetime = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
