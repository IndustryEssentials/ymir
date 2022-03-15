from sqlalchemy import Column, Integer, UniqueConstraint

from app.db.base_class import Base


class DockerImageRelationship(Base):
    __tablename__ = "docker_image_relationship"
    src_image_id = Column(Integer, primary_key=True, index=True, nullable=False)
    dest_image_id = Column(Integer, primary_key=True, index=True, nullable=False)

    __table_args__ = (UniqueConstraint("src_image_id", "dest_image_id", name="unique_image_relationship"),)
