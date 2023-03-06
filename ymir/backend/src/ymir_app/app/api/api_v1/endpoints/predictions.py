from typing import Any
from fastapi import APIRouter, Depends, Path, Query
from fastapi.logger import logger
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.utils.data import groupby
from app.api import deps
from app.api.errors.errors import (
    FailedToParseVizResponse,
    ProjectNotFound,
    PredictionNotFound,
    MissingOperations,
    RefuseToProcessMixedOperations,
    NoPredictionPermission,
)
from app.constants.state import ObjectType
from app.utils.ymir_viz import VizClient
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


@router.get("/{prediction_id}", response_model=schemas.prediction.PredictionInfoOut)
def get_prediction(
    db: Session = Depends(deps.get_db),
    prediction_id: int = Path(..., example="12"),
    current_user: models.User = Depends(deps.get_current_active_user),
    viz_client: VizClient = Depends(deps.get_viz_client),
    user_labels: UserLabels = Depends(deps.get_user_labels),
) -> Any:
    """
    Get verbose information of specific prediction
    """
    prediction = crud.prediction.get_by_user_and_id(db, user_id=current_user.id, id=prediction_id)
    if not prediction:
        raise PredictionNotFound()

    prediction_info = schemas.prediction.Prediction.from_orm(prediction).dict()

    viz_client.initialize(user_id=current_user.id, project_id=prediction.project_id, user_labels=user_labels)
    try:
        prediction_stats = viz_client.get_dataset_info(prediction.hash)
    except ValueError:
        logger.exception("[prediction info] could not convert class_id to class_name, return with basic info")
    except FailedToParseVizResponse:
        logger.exception("[prediction info] could not get prediction info from viewer, return with basic info")
    else:
        prediction_info.update(prediction_stats)

    return {"result": prediction_info}


@router.post("/batch", response_model=schemas.prediction.PredictionsOut)
def batch_update_predictions(
    *,
    db: Session = Depends(deps.get_db),
    prediction_ops: schemas.BatchOperations,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    if not prediction_ops.operations:
        raise MissingOperations()
    project = crud.project.get_by_user_and_id(db, user_id=current_user.id, id=prediction_ops.project_id)
    if not project:
        raise ProjectNotFound()
    actions = list({op.action for op in prediction_ops.operations})
    if len(actions) != 1:
        # Do not support mixed operations, for example,
        #  hide and unhide in a single batch request
        raise RefuseToProcessMixedOperations()
    action = actions[0]
    prediction_ids = list({op.id_ for op in prediction_ops.operations})
    predictions = crud.prediction.get_multi_by_ids(db, ids=prediction_ids)
    if {p.user_id for p in predictions} != {current_user.id}:
        raise NoPredictionPermission()

    predictions = crud.prediction.batch_toggle_visibility(db, ids=prediction_ids, action=action)
    return {"result": predictions}


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
