from datetime import datetime
from typing import List, Optional, Tuple

from sqlalchemy import and_, desc, not_
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.libs.common import pagination as paginate
from app.models import ModelGroup
from app.schemas.model_group import ModelGroupCreate, ModelGroupUpdate
from app.schemas import CommonPaginationParams


class CRUDModelGroup(CRUDBase[ModelGroup, ModelGroupCreate, ModelGroupUpdate]):
    def create_model_group(
        self,
        db: Session,
        *,
        user_id: int,
        project_id: int,
        training_dataset_id: int,
        name: Optional[str] = None,
    ) -> ModelGroup:
        name = name or f"model_group_{training_dataset_id}"
        db_obj = ModelGroup(
            name=name,
            user_id=user_id,
            project_id=project_id,
            training_dataset_id=training_dataset_id,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_multi_model_groups(
        self,
        db: Session,
        *,
        user_id: int,
        project_id: int,
        name: Optional[str],
        pagination: CommonPaginationParams,
    ) -> Tuple[List[ModelGroup], int]:
        start_time, end_time = pagination.start_time, pagination.end_time
        offset, limit = pagination.offset, pagination.limit
        order_by = pagination.order_by.name
        is_desc = pagination.is_desc

        query = db.query(self.model)
        query = query.filter(self.model.user_id == user_id, self.model.visible_models, not_(self.model.is_deleted))

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
            query = query.filter(self.model.name.like(f"%{name}%"))

        if project_id is not None:
            query = query.filter(self.model.project_id == project_id)

        order_by_column = getattr(self.model, order_by)
        if is_desc:
            order_by_column = desc(order_by_column)
        query = query.order_by(order_by_column)

        # fixme
        # SQLAlchemy do not guarantee precise count
        items = query.all()
        return paginate(items, offset, limit), len(items)

    def get_from_training_dataset(self, db: Session, training_dataset_id: int) -> Optional[ModelGroup]:
        return (
            db.query(self.model)
            .filter(self.model.training_dataset_id == training_dataset_id, not_(self.model.is_deleted))
            .first()
        )


model_group = CRUDModelGroup(ModelGroup)
