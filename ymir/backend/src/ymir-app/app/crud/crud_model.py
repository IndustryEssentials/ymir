from datetime import datetime
from typing import List, Optional, Tuple

from sqlalchemy import and_, desc, not_
from sqlalchemy.orm import Session

from app.constants.state import TaskType
from app.crud.base import CRUDBase
from app.models import Model, Task
from app.schemas.model import ModelCreate, ModelUpdate


class CRUDModel(CRUDBase[Model, ModelCreate, ModelUpdate]):
    def get_multi_models(
        self,
        db: Session,
        *,
        user_id: int,
        name: Optional[str],
        task_type: Optional[TaskType],
        start_time: Optional[int],
        end_time: Optional[int],
        offset: Optional[int],
        limit: Optional[int],
        order_by: str,
        is_desc: bool = True,
    ) -> Tuple[List[Model], int]:
        query = db.query(self.model)
        query = query.filter(self.model.user_id == user_id, not_(self.model.is_deleted))

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
            query = query.filter(Task.type == task_type.value)

        order_by_column = getattr(self.model, order_by)
        if is_desc:
            order_by_column = desc(order_by_column)
        query = query.order_by(order_by_column)

        return query.offset(offset).limit(limit).all(), query.count()


model = CRUDModel(Model)
