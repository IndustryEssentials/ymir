from random import randint
from typing import Optional

from sqlalchemy.orm import Session

from app import crud
from app.models.task import Task


def create_visualization_record(
    db: Session,
    task: Task,
    user_id: Optional[int] = None,
    project_id: Optional[int] = None,
):
    user_id = user_id or randint(1, 20)
    record = crud.visualization.create_visualization(db, user_id=user_id, confidence=0.0005, iou=0.5)
    crud.task_visual_relationship.create_relationship(db, task_id=task.id, visualization_id=record.id)
    return record
