from datetime import datetime
from enum import IntEnum
from typing import Dict, List, Optional, Tuple

from sqlalchemy import and_, desc, not_
from sqlalchemy.orm import Session

from app import schemas
from app.constants.state import ResultState, TaskType
from app.crud.base import CRUDBase
from app.models import Model
from app.schemas.model import ModelCreate, ModelUpdate


class CRUDModel(CRUDBase[Model, ModelCreate, ModelUpdate]):
    def get_multi_models(
        self,
        db: Session,
        *,
        user_id: int,
        project_id: Optional[int] = None,
        group_id: Optional[int] = None,
        source: Optional[TaskType] = None,
        state: Optional[IntEnum] = None,
        visible: bool = True,
        start_time: Optional[int],
        end_time: Optional[int],
        offset: Optional[int],
        limit: Optional[int],
        order_by: str,
        is_desc: bool = True,
    ) -> Tuple[List[Model], int]:
        query = db.query(self.model)
        query = query.filter(
            self.model.user_id == user_id,
            self.model.is_visible == int(visible),
            not_(self.model.is_deleted),
        )

        if start_time and end_time:
            _start_time = datetime.utcfromtimestamp(start_time)
            _end_time = datetime.utcfromtimestamp(end_time)
            query = query.filter(
                and_(
                    self.model.create_datetime >= _start_time,
                    self.model.create_datetime <= _end_time,
                )
            )

        if source:
            query = query.filter(self.model.source == int(source))

        if state:
            query = query.filter(self.model.result_state == int(state))

        if project_id is not None:
            query = query.filter(self.model.project_id == project_id)

        if group_id is not None:
            query = query.filter(self.model.model_group_id == group_id)

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

    def next_available_version(self, db: Session, model_group_id: int) -> int:
        latest_version = self.get_latest_version(db, model_group_id)
        return latest_version + 1 if latest_version is not None else 1

    def create_with_version(self, db: Session, obj_in: ModelCreate, dest_group_name: Optional[str] = None) -> Model:
        # fixme
        #  add mutex lock to protect latest_version
        version_num = self.next_available_version(db, obj_in.model_group_id)

        db_obj = Model(
            version_num=version_num,
            hash=obj_in.hash,
            source=int(obj_in.source),
            result_state=int(obj_in.result_state),
            model_group_id=obj_in.model_group_id,
            project_id=obj_in.project_id,
            user_id=obj_in.user_id,
            task_id=obj_in.task_id,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def create_as_task_result(
        self, db: Session, task: schemas.TaskInternal, dest_group_id: int, dest_group_name: str
    ) -> Model:
        model_in = ModelCreate(
            hash=task.hash,
            source=task.type,
            result_state=ResultState.processing,
            model_group_id=dest_group_id,
            project_id=task.project_id,
            user_id=task.user_id,
            task_id=task.id,
        )
        return self.create_with_version(db, obj_in=model_in, dest_group_name=dest_group_name)

    def update_state(
        self,
        db: Session,
        *,
        model_id: int,
        new_state: ResultState,
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

        if result:
            model.map = result["map"]
            model.hash = result["hash"]

        model.result_state = int(result_state)

        db.add(model)
        db.commit()
        db.refresh(model)
        return model

    def remove_group_resources(self, db: Session, *, group_id: int) -> List[Model]:
        objs = db.query(self.model).filter(self.model.model_group_id == group_id).all()
        for obj in objs:
            obj.is_deleted = True
        db.bulk_save_objects(objs)
        db.commit()
        return objs

    def batch_toggle_visibility(self, db: Session, *, ids: List[int], action: str) -> List[Model]:
        objs = self.get_multi_by_ids(db, ids=ids)
        for obj in objs:
            if action == "hide":
                obj.is_visible = False
            elif action == "unhide":
                obj.is_visible = True
        db.bulk_save_objects(objs)
        db.commit()
        return objs


model = CRUDModel(Model)
