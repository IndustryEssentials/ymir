from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.task_visual_relationship import TaskVisualRelationship
from app.schemas.task_visual_relationship import TaskVisualRelationshipCreate, TaskVisualRelationshipUpdate


class CRUDTaskVisualRelationship(CRUDBase[TaskVisualRelationship, TaskVisualRelationshipCreate,
                                 TaskVisualRelationshipUpdate]):
    def create_relationship(
        self,
        db: Session,
        *,
        task_id: int,
        visualization_id: int,
    ) -> TaskVisualRelationship:

        db_obj = TaskVisualRelationship(
            task_id=task_id,
            visualization_id=visualization_id
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


task_visual_relationship = CRUDTaskVisualRelationship(TaskVisualRelationship)
