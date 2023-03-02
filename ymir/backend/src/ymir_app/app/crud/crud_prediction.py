import json
from datetime import datetime
from enum import IntEnum
from typing import Dict, List, Optional, Tuple, Union, Any

from sqlalchemy import and_, desc, not_
from sqlalchemy.orm import Session

from app import schemas, models
from app.constants.state import ResultState, TaskType
from app.crud.base import CRUDBase
from app.models import Prediction
from app.models.project import Project
from app.schemas.prediction import PredictionCreate, PredictionUpdate
from app.schemas import CommonPaginationParams


class CRUDPrediction(CRUDBase[Prediction, PredictionCreate, PredictionUpdate]):
    def get_multi_with_filters(
        self,
        db: Session,
        *,
        user_id: int,
        project_id: Optional[int] = None,
        source: Optional[TaskType] = None,
        state: Optional[IntEnum] = None,
        object_type: Optional[IntEnum] = None,
        visible: bool = True,
        allow_empty: bool = True,
        pagination: CommonPaginationParams,
    ) -> Tuple[List[Prediction], int]:
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

        if state is not None:
            query = query.filter(self.model.result_state == int(state))
        if source is not None:
            query = query.filter(self.model.source == int(source))
        if project_id is not None:
            query = query.filter(self.model.project_id == project_id)
        if not allow_empty:
            query = query.filter(self.model.asset_count > 0)

        if object_type is not None:
            query = query.join(Project, Project.id == self.model.project_id).filter(
                Project.object_type == int(object_type)
            )

        order_by_column = getattr(self.model, order_by)
        if is_desc:
            order_by_column = desc(order_by_column)
        query = query.order_by(order_by_column)

        if limit:
            return query.offset(offset).limit(limit).all(), query.count()
        return query.all(), query.count()

    def update_state(
        self,
        db: Session,
        *,
        prediction_id: int,
        new_state: ResultState,
    ) -> Optional[Prediction]:
        prediction = self.get(db, id=prediction_id)
        if not prediction:
            return prediction
        prediction.result_state = int(new_state)
        db.add(prediction)
        db.commit()
        db.refresh(prediction)
        return prediction

    def create_as_task_result(
        self,
        db: Session,
        task: Union[schemas.TaskInternal, models.Task],
        description: Optional[str] = None,
    ) -> Any:
        prediction_in = PredictionCreate(
            name=task.hash,
            hash=task.hash,
            description=description,
            source=task.type,
            project_id=task.project_id,
            user_id=task.user_id,
            task_id=task.id,
        )
        return self.create(db, obj_in=prediction_in)

    def finish(
        self,
        db: Session,
        prediction_id: int,
        result_state: ResultState = ResultState.ready,
        result: Optional[Dict] = None,
    ) -> Optional[Prediction]:
        prediction = self.get(db, id=prediction_id)
        if not prediction:
            return prediction
        prediction.result_state = int(result_state)

        if result:
            prediction.keywords = json.dumps(result["keywords"])
            prediction.asset_count = result["total_assets_count"]

        db.add(prediction)
        db.commit()
        db.refresh(prediction)
        return prediction

    def batch_toggle_visibility(self, db: Session, *, ids: List[int], action: str) -> List[Prediction]:
        objs = self.get_multi_by_ids(db, ids=ids)
        for obj in objs:
            if action == "hide":
                obj.is_visible = False
            elif action == "unhide":
                obj.is_visible = True
        db.bulk_save_objects(objs)
        db.commit()
        return objs


prediction = CRUDPrediction(Prediction)
