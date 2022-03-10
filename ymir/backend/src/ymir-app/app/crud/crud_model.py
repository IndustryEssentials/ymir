from datetime import datetime
from typing import Dict, List, Optional, Tuple

from sqlalchemy import and_, desc, not_
from sqlalchemy.orm import Session

from app import schemas
from app.constants.state import TaskState, ResultState
from app.crud.base import CRUDBase
from app.models import Model
from app.schemas.model import ModelCreate, ModelUpdate


class CRUDModel(CRUDBase[Model, ModelCreate, ModelUpdate]):
    def get_multi_models(
        self,
        db: Session,
        *,
        user_id: int,
        name: Optional[str],
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
            query = query.filter(self.model.name.like(f"%{name}%"))

        order_by_column = getattr(self.model, order_by)
        if is_desc:
            order_by_column = desc(order_by_column)
        query = query.order_by(order_by_column)

        return query.offset(offset).limit(limit).all(), query.count()

    def get_latest_version(self, db: Session, model_group_id: int) -> Optional[int]:
        query = db.query(self.model)
        latest_model_in_group = (
            query.filter(self.model.model_group_id == model_group_id).order_by(desc(self.model.id)).first()
        )
        if latest_model_in_group:
            return latest_model_in_group.version_num
        return None

    def create_with_version(self, db: Session, obj_in: ModelCreate) -> Model:
        # fixme
        #  add mutex lock to protect latest_version
        latest_version = self.get_latest_version(db, obj_in.model_group_id)

        db_obj = Model(
            name=obj_in.name,
            version_num=latest_version + 1 if latest_version else 0,
            hash=obj_in.hash,
            result_state=obj_in.result_state,
            model_group_id=obj_in.model_group_id,
            project_id=obj_in.project_id,
            user_id=obj_in.user_id,  # type: ignore
            task_id=obj_in.task_id,  # type: ignore
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def create_as_task_result(self, db: Session, task: schemas.TaskInternal, dest_group_id: int) -> Model:
        model_in = ModelCreate(
            name=task.hash,
            hash=task.hash,
            result_state=ResultState.processing,
            model_group_id=dest_group_id,
            project_id=task.project_id,
            user_id=task.user_id,
            task_id=task.id,
        )
        return self.create_with_version(db, obj_in=model_in)

    def update_state(
        self,
        db: Session,
        *,
        model_id: int,
        new_state: TaskState,
    ) -> Optional[Model]:
        model = self.get(db, id=model_id)
        if not model:
            return model
        model.result_state = int(new_state)
        db.add(model)
        db.commit()
        db.refresh(model)
        return model

    def finish(
        self,
        db: Session,
        model_id: int,
        result_state: ResultState = ResultState.ready,
        result: Optional[Dict] = None,
    ) -> Optional[Model]:
        model = self.get(db, id=model_id)
        if not model:
            return model
        model.result_state = int(result_state)

        if result:
            model.map = result["map"]
            model.hash = result["hash"]

        db.add(model)
        db.commit()
        db.refresh(model)
        return model


model = CRUDModel(Model)
