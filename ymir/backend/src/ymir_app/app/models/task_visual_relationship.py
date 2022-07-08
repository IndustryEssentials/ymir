from sqlalchemy import Column, Integer

from app.db.base_class import Base


class TaskVisualRelationship(Base):
    __tablename__ = "task_visual_relationship"
    task_id = Column(Integer, primary_key=True, nullable=False)
    visualization_id = Column(Integer, primary_key=True, nullable=False)
