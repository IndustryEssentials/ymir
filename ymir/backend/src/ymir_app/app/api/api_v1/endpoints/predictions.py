from typing import Any
from fastapi import APIRouter, Depends, Query
from fastapi.logger import logger
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.utils.data import groupby
from app.api import deps
from app.api.errors.errors import ProjectNotFound
from app.constants.state import ObjectType
from app.utils.ymir_controller import ControllerClient
from app.libs.predictions import evaluate_predictions, ensure_predictions_are_ready
from common_utils.labels import UserLabels

router = APIRouter()


@router.get("/", response_model=schemas.prediction.PredictionPaginationOut)
def list_predictions(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    project_id: int = Query(None),
    visible: bool = Query(True),
    pagination: schemas.CommonPaginationParams = Depends(),
) -> Any:
    predictions, total = crud.prediction.get_multi_with_filters(
        db,
        user_id=current_user.id,
        project_id=project_id,
        visible=visible,
        pagination=pagination,
    )
    model_wise_predictions = {k: list(v) for k, v in groupby(predictions, "model_id")}
    return {"result": {"total": total, "items": model_wise_predictions}}


@router.post("/evaluation", response_model=schemas.prediction.PredictionEvaluationOut)
def batch_evaluate_datasets(
    *,
    db: Session = Depends(deps.get_db),
    in_evaluation: schemas.prediction.PredictionEvaluationCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
    controller_client: ControllerClient = Depends(deps.get_controller_client),
    user_labels: UserLabels = Depends(deps.get_user_labels),
) -> Any:
    """
    evaluate predictions
    """
    logger.info("[evaluate] evaluate predictions with payload: %s", in_evaluation.json())

    project = crud.project.get_by_user_and_id(db, user_id=current_user.id, id=in_evaluation.project_id)
    if not project:
        raise ProjectNotFound()

    predictions = ensure_predictions_are_ready(db, prediction_ids=in_evaluation.prediction_ids)
    prediction_id_mapping = {prediction.hash: prediction.id for prediction in predictions}

    evaluations = evaluate_predictions(
        controller_client,
        current_user.id,
        in_evaluation.project_id,
        user_labels,
        in_evaluation.confidence_threshold,
        in_evaluation.iou_threshold,
        in_evaluation.require_average_iou,
        in_evaluation.need_pr_curve,
        in_evaluation.main_ck,
        prediction_id_mapping,
        is_instance_segmentation=(project.object_type == ObjectType.instance_segmentation),
    )
    return {"result": evaluations}
