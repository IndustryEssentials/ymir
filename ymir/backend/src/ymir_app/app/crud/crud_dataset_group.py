from datetime import datetime
from typing import List, Optional, Tuple

from sqlalchemy import and_, desc, not_
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models import DatasetGroup
from app.schemas.dataset_group import DatasetGroupCreate, DatasetGroupUpdate


class CRUDDatasetGroup(CRUDBase[DatasetGroup, DatasetGroupCreate, DatasetGroupUpdate]):
    def create_dataset_group(
        self,
        db: Session,
        *,
        user_id: int,
        project_id: int,
        name: str,
    ) -> DatasetGroup:
        db_obj = DatasetGroup(
            name=name,
            user_id=user_id,
            project_id=project_id,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_multi_dataset_groups(
        self,
        db: Session,
        *,
        user_id: int,
        project_id: Optional[int],
        name: Optional[str],
        start_time: Optional[int],
        end_time: Optional[int],
        offset: Optional[int],
        limit: Optional[int],
        order_by: str,
        is_desc: bool = True,
    ) -> Tuple[List[DatasetGroup], int]:
        query = db.query(self.model)
        query = query.filter(self.model.user_id == user_id, self.model.visible_datasets, not_(self.model.is_deleted))

        if start_time and end_time:
            _start_time = datetime.utcfromtimestamp(start_time)
            _end_time = datetime.utcfromtimestamp(end_time)
            query = query.filter(
                and_(
                    self.model.create_datetime >= _start_time,
                    self.model.create_datetime <= _end_time,
                )
            )

        if project_id:
            query = query.filter(self.model.project_id == project_id)

        if name:
            # basic fuzzy search
            query = query.filter(self.model.name.like(f"%{name}%"))

        order_by_column = getattr(self.model, order_by)
        if is_desc:
            order_by_column = desc(order_by_column)
        query = query.order_by(order_by_column)

        return query.offset(offset).limit(limit).all(), query.count()


dataset_group = CRUDDatasetGroup(DatasetGroup)
