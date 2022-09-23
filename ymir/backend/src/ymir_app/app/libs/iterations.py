from typing import Dict, List
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from functools import partial

from fastapi.logger import logger
from sqlalchemy.orm import Session

from app import crud, models
from app.api.errors.errors import IterationNotFound, InvalidProject
from app.utils.ymir_viz import VizClient
from common_utils.labels import UserLabels


def calculate_mining_progress(
    db: Session, user_labels: UserLabels, user_id: int, project_id: int, iteration_id: int
) -> Dict:
    iteration = crud.iteration.get(db, id=iteration_id)
    if not iteration:
        raise IterationNotFound()
    mining_dataset = iteration.mining_dataset
    if not mining_dataset:
        logger.warning("Attempt to get mining_progress of legacy projects, skip")
        raise InvalidProject()

    training_classes = get_training_classes(db, project_id, user_labels)
    training_class_ids = list(training_classes.values())

    viz = VizClient(user_id, project_id, user_labels)
    previous_iterations = crud.project.get_previous_iterations(db, project_id=project_id, iteration_id=iteration_id)
    if not previous_iterations:
        return generate_empty_progress(viz, mining_dataset, training_class_ids)

    previous_labelled_datasets = crud.dataset.get_multi_by_ids(
        db, ids=[i.label_output_dataset_id for i in previous_iterations if i.label_output_dataset_id]
    )
    if not previous_labelled_datasets:
        logger.warning("previous iteration(%s) got NO labelled datasets", iteration_id)
        return generate_empty_progress(viz, mining_dataset, training_class_ids)

    total_mining_ratio = get_processed_assets_ratio(viz, mining_dataset, previous_labelled_datasets)
    class_wise_mining_ratio = get_class_wise_mining_ratio(
        viz, mining_dataset, previous_labelled_datasets, training_classes
    )
    negative_ratio = get_negative_ratio(viz, mining_dataset, previous_labelled_datasets, training_class_ids)

    return {
        "total_mining_ratio": total_mining_ratio,
        "class_wise_mining_ratio": class_wise_mining_ratio,
        "negative_ratio": negative_ratio,
    }


def generate_empty_progress(viz: VizClient, mining_dataset: models.Dataset, training_class_ids: List[int]) -> Dict:
    total_assets_count = mining_dataset.asset_count
    total_negative_asset_count = viz.get_negative_count(mining_dataset.hash, training_class_ids)
    return {
        "total_mining_ratio": {"processed_assets_count": 0, "total_assets_count": total_assets_count},
        "class_wise_mining_ratio": [],
        "negative_ratio": {"processed_assets_count": 0, "total_assets_count": total_negative_asset_count},
    }


def get_training_classes(db: Session, project_id: int, user_labels: UserLabels) -> Dict[str, int]:
    project = crud.project.get(db, id=project_id)
    if not project or not project.training_targets:
        raise InvalidProject()
    class_ids = user_labels.id_for_names(names=project.training_targets, raise_if_unknown=True)[0]
    return dict(zip(project.training_targets, class_ids))


def get_processed_assets_ratio(
    viz: VizClient,
    mining_dataset: models.Dataset,
    previous_labelled_datasets: List[models.Dataset],
) -> Dict:
    count_stats = viz.check_duplication([dataset.hash for dataset in previous_labelled_datasets], mining_dataset.hash)
    return {
        "processed_assets_count": mining_dataset.asset_count - count_stats["residual_count"][mining_dataset.hash],
        "total_assets_count": mining_dataset.asset_count,
    }


def get_negative_ratio(
    viz: VizClient,
    mining_dataset: models.Dataset,
    previous_labelled_datasets: List[models.Dataset],
    training_class_ids: List[int],
) -> Dict[str, int]:
    f_get_negative_count = partial(viz.get_negative_count, keyword_ids=training_class_ids)
    total_negative_asset_count = f_get_negative_count(mining_dataset.hash)

    with ThreadPoolExecutor() as executor:
        negative_counts = executor.map(f_get_negative_count, [dataset.hash for dataset in previous_labelled_datasets])

    return {
        "processed_assets_count": sum(negative_counts),
        "total_assets_count": total_negative_asset_count,
    }


def get_class_wise_mining_ratio(
    viz: VizClient,
    mining_dataset: models.Dataset,
    previous_labelled_datasets: List[models.Dataset],
    training_classes: Dict[str, int],
) -> List[Dict]:
    total_assets_counts = viz.get_class_wise_count(mining_dataset.hash)
    total_assets_counter = Counter(total_assets_counts)

    processed_assets_counter: Counter = Counter()
    with ThreadPoolExecutor() as executor:
        class_wise_counters = executor.map(
            viz.get_class_wise_count, [dataset.hash for dataset in previous_labelled_datasets]
        )
    for class_wise_counter in class_wise_counters:
        processed_assets_counter += Counter(class_wise_counter)

    return [
        {
            "class_name": class_name,
            "processed_assets_count": processed_assets_counter[class_name],
            "total_assets_count": total_assets_counter[class_name],
        }
        for class_name in training_classes
    ]
