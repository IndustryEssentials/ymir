from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String, SmallInteger
from sqlalchemy.orm import relationship

from app.config import settings
from app.db.base_class import Base
from app.models.image_config import DockerImageConfig  # noqa
from app.models.image_relationship import DockerImageRelationship
from app.models.task import Task  # noqa


class DockerImage(Base):
    __tablename__ = "docker_image"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(settings.STRING_LEN_LIMIT), index=True, nullable=False)
    url = Column(String(settings.STRING_LEN_LIMIT), index=True, nullable=False)
    hash = Column(String(settings.STRING_LEN_LIMIT), index=True)
    description = Column(String(settings.LONG_STRING_LEN_LIMIT))
    state = Column(Integer, index=True, nullable=False)  # obsolete
    related = relationship(
        "DockerImage",
        secondary=DockerImageRelationship.__table__,
        primaryjoin=id == DockerImageRelationship.__table__.c.src_image_id,
        secondaryjoin=id == DockerImageRelationship.__table__.c.dest_image_id,
        uselist=True,
    )
    configs = relationship(
        "DockerImageConfig",
        primaryjoin="foreign(DockerImageConfig.image_id)==DockerImage.id",
        uselist=True,
    )
    enable_livecode = Column(Boolean, default=False, nullable=False)
    object_type = Column(SmallInteger, index=True, default=2, nullable=False)  # obsolete

    result_state = Column(SmallInteger, index=True, nullable=False)
    task_id = Column(Integer, index=True, nullable=True)

    is_shared = Column(Boolean, default=False, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)
    is_official = Column(Boolean, default=False, index=True)
    create_datetime = Column(DateTime, default=datetime.utcnow, nullable=False)
    update_datetime = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    related_task = relationship(
        "Task",
        primaryjoin="foreign(Task.id)==DockerImage.task_id",
        backref="result_docker_image",
        uselist=False,
        viewonly=True,
    )
