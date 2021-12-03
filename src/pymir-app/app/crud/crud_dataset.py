from datetime import datetime
from enum import IntEnum
from typing import List, Optional, Tuple

from sqlalchemy import and_, desc, not_
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models import Dataset, Task
from app.schemas.asset import Asset
from app.schemas.dataset import DatasetCreate, DatasetUpdate


class CRUDDataset(CRUDBase[Dataset, DatasetCreate, DatasetUpdate]):
    interested_fields = [
        *Dataset.__table__.columns,
        Task.type.label("task_type"),
        Task.name.label("task_name"),
        Task.hash.label("task_hash"),
        Task.state.label("task_state"),
        Task.progress.label("task_progress"),
        Task.parameters.label("task_parameters"),
        Task.config.label("task_config"),
    ]

    def get_with_task(
        self, db: Session, *, user_id: Optional[int], id: int
    ) -> Optional[Dataset]:
        query = db.query(*self.interested_fields)
        query = query.join(Task, self.model.task_id == Task.id)
        query = query.filter(not_(self.model.is_deleted))
        if id:
            query = query.filter(self.model.id == id)
        if user_id:
            query = query.filter(self.model.user_id == user_id)
        return query.first()

    def get_multi_datasets(
        self,
        db: Session,
        *,
        user_id: int,
        name: Optional[str] = None,
        type_: Optional[IntEnum] = None,
        state: Optional[IntEnum] = None,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        offset: Optional[int] = 0,
        limit: Optional[int] = None,
    ) -> Tuple[List[Dataset], int]:
        # each dataset is associate with one task
        # we need related task info as well
        query = db.query(*self.interested_fields)
        query = query.join(Task, self.model.task_id == Task.id)
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
            query = query.filter(Dataset.name.like(f"%{name}%"))
        if type_:
            query = query.filter(Dataset.type == type_)
        if state:
            query = query.filter(Task.state == state)
        query = query.order_by(desc(self.model.id))
        if limit:
            return query.offset(offset).limit(limit).all(), query.count()
        else:
            return query.all(), query.count()

    def get_datasets_of_user(
        self, db: Session, *, user_id: int
    ) -> Tuple[List[Dataset], int]:
        return self.get_multi_datasets(db, user_id=user_id)


dataset = CRUDDataset(Dataset)
