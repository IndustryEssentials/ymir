import json
from typing import Dict, List, Optional, Tuple

from sqlalchemy import desc, distinct, func, not_
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
        project_id: int,
        visible: bool = True,
        pagination: CommonPaginationParams,
    ) -> Tuple[List[Prediction], int]:
        offset, limit = pagination.offset, pagination.limit
        order_by = pagination.order_by.name
        is_desc = pagination.is_desc

        # Subquery
        #  find models with latest predictions
        order_by_column = getattr(self.model, order_by)
        subquery = (
            db.query(self.model.model_id)
            .filter(
                self.model.project_id == project_id,
                self.model.is_visible == int(visible),
                not_(self.model.is_deleted),
            )
            .group_by(self.model.model_id, order_by_column)
            .order_by(desc(order_by_column) if is_desc else order_by_column)
            .offset(offset)
            .limit(limit)
            .subquery()
        )

        # Query
        #  find all predictions belonging to model_ids from subquery
        query = (
            db.query(self.model)
            .join(subquery, self.model.model_id == subquery.c.model_id)
            .filter(
                self.model.is_visible == int(visible),
                not_(self.model.is_deleted),
            )
        )
        # Count distinct models
        total = (
            db.query(func.count(distinct(self.model.model_id)))
            .filter(
                self.model.project_id == project_id,
                self.model.is_visible == int(visible),
                not_(self.model.is_deleted),
            )
            .scalar()
        )

        return query.all(), total

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
        params: Dict = task.parameters  # type: ignore
        dataset_id, model_id, model_stage_id = params["dataset_id"], params["model_id"], params["model_stage_id"]
        prediction_in = PredictionCreate(
            name=task.hash,
            hash=task.hash,
            description=description,
            user_id=task.user_id,
            project_id=task.project_id,
            task_id=task.id,
            dataset_id=dataset_id,
            model_id=model_id,
            model_stage_id=model_stage_id,
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
            result["keywords"]["eval_class_ids"] = result["pred"]["eval_class_ids"]
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
