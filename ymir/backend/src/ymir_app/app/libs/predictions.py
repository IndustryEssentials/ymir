from collections import ChainMap
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from app import crud, models
from app.api.errors.errors import PredictionNotFound, PrematurePredictions
from app.constants.state import ResultState
from app.utils.ymir_controller import ControllerClient
from common_utils.labels import UserLabels


def evaluate_predictions(
    controller_client: ControllerClient,
    user_id: int,
    project_id: int,
    user_labels: UserLabels,
    confidence_threshold: Optional[float],
    iou_threshold: Optional[float],
    require_average_iou: bool,
    need_pr_curve: bool,
    main_ck: Optional[str],
    prediction_id_mapping: Dict[str, int],
    is_instance_segmentation: bool = False,
) -> Dict:
    iou_thrs_interval = convert_to_iou_thrs_interval(iou_threshold, require_average_iou)
    f_evaluate = partial(
        controller_client.evaluate_prediction,
        user_id,
        project_id,
        user_labels,
        confidence_threshold,
        iou_thrs_interval,
        need_pr_curve,
        main_ck,
        is_instance_segmentation,
    )
    with ThreadPoolExecutor() as executor:
        res = executor.map(f_evaluate, prediction_id_mapping.keys())

    evaluations = ChainMap(*res)

    return {prediction_id_mapping[hash_]: evaluation for hash_, evaluation in evaluations.items()}


def convert_to_iou_thrs_interval(iou_threshold: Optional[float], require_average_iou: Optional[bool]) -> Optional[str]:
    """
    the underlying requires "start:end:step" format
    """
    if require_average_iou:
        return f"{iou_threshold or 0.5}:0.95:0.05"
    if not iou_threshold:
        return None
    return str(iou_threshold)


def ensure_predictions_are_ready(db: Session, prediction_ids: List[int]) -> List[models.Prediction]:
    prediction_ids = list(set(prediction_ids))
    predictions = crud.prediction.get_multi_by_ids(db, ids=prediction_ids)
    if len(prediction_ids) != len(predictions):
        raise PredictionNotFound()

    if not all(prediction.result_state == ResultState.ready for prediction in predictions):
        raise PrematurePredictions()
    return predictions
