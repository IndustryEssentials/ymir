from datetime import datetime
from enum import IntEnum
from typing import Dict, List, Optional, Tuple

from sqlalchemy import and_, desc, not_, select, func
from sqlalchemy.orm import Session

from app import schemas
from app.constants.state import ResultState, TaskType
from app.crud.base import CRUDBase
from app.models import Model
from app.models.model_group import ModelGroup
from app.schemas.model import ModelCreate, ModelUpdate
from app.schemas import CommonPaginationParams


class CRUDModel(CRUDBase[Model, ModelCreate, ModelUpdate]):
    def get_multi_models(
        self,
        db: Session,
        *,
        user_id: int,
        project_id: Optional[int] = None,
        group_id: Optional[int] = None,
        group_name: Optional[str] = None,
        source: Optional[TaskType] = None,
        state: Optional[IntEnum] = None,
        visible: bool = True,
        pagination: CommonPaginationParams,
    ) -> Tuple[List[Model], int]:
        start_time, end_time = pagination.start_time, pagination.end_time
        offset, limit = pagination.offset, pagination.limit
        order_by = pagination.order_by.name
        is_desc = pagination.is_desc

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

        if source is not None:
            query = query.filter(self.model.source == int(source))

        if state is not None:
            query = query.filter(self.model.result_state == int(state))

        if project_id is not None:
            query = query.filter(self.model.project_id == project_id)

        if group_id is not None:
            query = query.filter(self.model.model_group_id == group_id)

        if group_name:
            # basic fuzzy search
            query = query.join(ModelGroup, ModelGroup.id == self.model.model_group_id).filter(
                ModelGroup.name.like(f"%{group_name}%")
            )

        order_by_column = getattr(self.model, order_by)
        if is_desc:
            order_by_column = desc(order_by_column)
        query = query.order_by(order_by_column)

        return query.offset(offset).limit(limit).all(), query.count()

    def create_with_version(self, db: Session, obj_in: ModelCreate) -> Model:
        stmt = (
            select(func.max(Model.version_num)).where(Model.model_group_id == obj_in.model_group_id).with_for_update()
        )
        max_version = db.execute(stmt).scalar() or 0
        version_num = int(max_version) + 1

        db_obj = Model(
            version_num=version_num,
            hash=obj_in.hash,
            description=obj_in.description,
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
        self,
        db: Session,
        task: schemas.TaskInternal,
        dest_group_id: int,
        description: Optional[str] = None,
    ) -> Model:
        model_in = ModelCreate(
            hash=task.hash,
            description=description,
            source=task.type,
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

    def update_recommonded_stage(
        self,
        db: Session,
        *,
        model_id: int,
        stage_id: int,
    ) -> Optional[Model]:
        model = self.get(db, id=model_id)
        if not model:
            return model
        model.recommended_stage = stage_id
        db.add(model)
        db.commit()
        db.refresh(model)
        return model

    def update_recommonded_stage_by_name(
        self,
        db: Session,
        *,
        model_id: int,
        stage_name: str,
    ) -> Optional[Model]:
        model = self.get(db, id=model_id)
        if not model:
            return model
        for stage in model.related_stages:
            if stage.name == stage_name:
                model.recommended_stage = stage.id
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
            model.hash = result["hash"]
            model.map = result["map"]
            model.miou = result["miou"]
            model.mask_ap = result["mask_ap"]
            model.keywords = result["keywords"]

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
