import uuid
from typing import List, Optional, Tuple

from sqlalchemy import desc, not_
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.dataset import Dataset
from app.models.dataset_group import DatasetGroup
from app.models.model import Model
from app.models.model_group import ModelGroup
from app.models.model_stage import ModelStage
from app.models.task import Task
from app.models.task_visual_relationship import TaskVisualRelationship
from app.models.visualization import Visualization
from app.schemas.visualization import VisualizationCreate, VisualizationUpdate


class CRUDVisualization(CRUDBase[Visualization, VisualizationCreate, VisualizationUpdate]):
    def create_visualization(
        self,
        db: Session,
        *,
        user_id: int,
        project_id: Optional[int],
    ) -> Visualization:

        db_obj = Visualization(
            user_id=user_id,
            tid=uuid.uuid4().hex,
            project_id=project_id
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_multi_visualizations(
        self,
        db: Session,
        *,
        user_id: int,
        name: Optional[str] = None,
        project_id: Optional[int] = None,
        offset: Optional[int] = 0,
        limit: Optional[int] = None,
        order_by: str = "create_datetime",
        is_desc: bool = True,
    ) -> Tuple[List[Visualization], int]:
        query = db.query(self.model)
        query = query.filter(self.model.user_id == user_id, not_(self.model.is_deleted))

        if project_id:
            query = query.filter(self.model.project_id == project_id)
        if name:
            query_dataset = query.join(
                TaskVisualRelationship, TaskVisualRelationship.visualization_id == self.model.id) \
                .join(Task, Task.id == TaskVisualRelationship.task_id) \
                .join(Dataset, Dataset.id == Task.dataset_id) \
                .join(DatasetGroup, DatasetGroup.id == Dataset.dataset_group_id) \
                .filter(DatasetGroup.name.like(f"%{name}%"))
            query_model = query.join(
                TaskVisualRelationship, TaskVisualRelationship.visualization_id == self.model.id) \
                .join(Task, Task.id == TaskVisualRelationship.task_id) \
                .join(ModelStage, ModelStage.id == Task.model_stage_id) \
                .join(Model, Model.id == ModelStage.model_id) \
                .join(ModelGroup, ModelGroup.id == Model.model_group_id) \
                .filter(ModelGroup.name.like(f"%{name}%"))
            query = query_dataset.union(query_model)

        order_by_column = getattr(self.model, order_by)
        if is_desc:
            order_by_column = desc(order_by_column)
        query = query.order_by(order_by_column)

        if limit:
            return query.offset(offset).limit(limit).all(), query.count()
        return query.all(), query.count()


visualization = CRUDVisualization(Visualization)
