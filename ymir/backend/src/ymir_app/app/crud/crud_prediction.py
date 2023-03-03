import json
from typing import Dict, List, Optional, Tuple

from sqlalchemy import desc, not_
from sqlalchemy.orm import Session

from app import schemas
from app.constants.state import ResultState
from app.crud.base import CRUDBase
from app.models import Prediction
from app.schemas.prediction import PredictionCreate, PredictionUpdate
from app.schemas import CommonPaginationParams


class CRUDPrediction(CRUDBase[Prediction, PredictionCreate, PredictionUpdate]):
    def get_multi_with_filters(
        self,
        db: Session,
        *,
        user_id: int,
        project_id: Optional[int] = None,
        visible: bool = True,
        pagination: CommonPaginationParams,
    ) -> Tuple[List[Prediction], int]:
        offset, limit = pagination.offset, pagination.limit
        is_desc = pagination.is_desc

        # Subquery
        #  find models with latest predictions
        subquery = (
            db.query(self.model.project_id)
            .filter(
                self.model.user_id == user_id,
                self.model.project_id == project_id,
                self.model.is_visible == int(visible),
                not_(self.model.is_deleted),
            )
            .group_by(
                self.model.model_id,
                self.model.create_datetime,
            )
            .order_by(desc(self.model.create_datetime) if is_desc else self.model.create_datetime)
            .offset(offset)
            .limit(limit)
            .subquery()
        )

        # Query
        #  find all predictions belonging to model_ids from subquery
        query = db.query(self.model).join(subquery, self.model.model_id == subquery.c.model_id)
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
        task: schemas.TaskInternal,
        description: Optional[str] = None,
    ) -> Prediction:
        dataset_id, model_id = task.parameters["dataset_id"], task.parameters["model_id"]  # type: ignore
        prediction_in = PredictionCreate(
            name=task.hash,
            hash=task.hash,
            description=description,
            user_id=task.user_id,
            project_id=task.project_id,
            task_id=task.id,
            dataset_id=dataset_id,
            model_id=model_id,
            source=task.type,
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
