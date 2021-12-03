from datetime import datetime
from enum import IntEnum
from typing import List, Optional, Tuple

from sqlalchemy import and_, desc, not_
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models import Model, Task
from app.models.task import TaskType
from app.schemas.model import ModelCreate, ModelUpdate


class CRUDModel(CRUDBase[Model, ModelCreate, ModelUpdate]):
    interested_fields = [
        *Model.__table__.columns,
        Task.type.label("task_type"),
        Task.name.label("task_name"),
        Task.state.label("task_state"),
        Task.parameters.label("task_parameters"),
        Task.config.label("task_config"),
    ]

    def get_with_task(self, db: Session, *, user_id: int, id: int) -> Optional[Model]:
        query = db.query(*self.interested_fields)
        query = query.join(Task, self.model.task_id == Task.id)
        query = query.filter(
            self.model.id == id,
            self.model.user_id == user_id,
            not_(self.model.is_deleted),
        )
        return query.first()

    def get_multi_models(
        self,
        db: Session,
        *,
        user_id: int,
        ids: Optional[List[int]],
        name: Optional[str],
        task_type: Optional[TaskType],
        start_time: Optional[int],
        end_time: Optional[int],
        offset: Optional[int],
        limit: Optional[int],
        order_by: Optional[str],
    ) -> Tuple[List[Model], int]:
        query = db.query(*self.interested_fields)
        query = query.join(Task, self.model.task_id == Task.id)
        query = query.filter(self.model.user_id == user_id, not_(self.model.is_deleted))
        if ids:
            query = query.filter(self.model.id.in_(ids))  # type: ignore
            return query.all(), query.count()

        if start_time and end_time:
            _start_time = datetime.utcfromtimestamp(start_time)
            _end_time = datetime.utcfromtimestamp(end_time)
            query = query.filter(
                and_(
                    self.model.create_datetime >= _start_time,
                    self.model.create_datetime <= _end_time,
                )
            )

        if name:
            # basic fuzzy search
            query = query.filter(Model.name.like(f"%{name}%"))
        if task_type:
            query = query.filter(Task.type == task_type)
        if order_by:
            query = query.order_by(desc(getattr(self.model, order_by)))
        else:
            query = query.order_by(desc(self.model.id))
        return query.offset(offset).limit(limit).all(), query.count()


model = CRUDModel(Model)
