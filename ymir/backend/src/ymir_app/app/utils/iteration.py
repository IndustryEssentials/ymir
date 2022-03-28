from contextlib import contextmanager
from functools import partial, singledispatch
from typing import Any, Generator

from fastapi.logger import logger
from sqlalchemy.orm import Session

from app.constants.state import MiningStrategy
from app import crud, schemas
from common_utils.labels import UserLabels


@singledispatch
def converter(task_parameters: schemas.RequestParameterBase, db: Session, user_labels: UserLabels) -> Any:
    logger.info("task_parameters to convert %s", task_parameters)


@converter.register(schemas.DatasetsFusionParameter)
def _(
    task_parameters: schemas.DatasetsFusionParameter,
    db: Session,
    user_labels: UserLabels,
) -> schemas.DatasetsFusionParameter:
    logger.info("[iteration context] updating task parameters %s", task_parameters)
    updated_parameters = convert_iteration_fusion_parameter(task_parameters, db)
    logger.info("[iteration context] task parameters updated to %s", updated_parameters)
    return updated_parameters


@contextmanager
def get_iteration_context_converter(db: Session, user_labels: UserLabels) -> Generator:
    """
    usage:
    with get_iteration_context_converter(db, user_labels) as converter:
        parameter_dict = converter(task_parameters)
    """
    converter_ = partial(converter, db=db, user_labels=user_labels)
    yield converter_


def convert_iteration_fusion_parameter(
    parameter: schemas.DatasetsFusionParameter,
    db: Session,
) -> schemas.DatasetsFusionParameter:
    if parameter.iteration_context and parameter.iteration_context.exclude_last_result:
        iterations = crud.iteration.get_multi_by_project(db=db, project_id=parameter.project_id)
        if parameter.iteration_context.mining_strategy == MiningStrategy.chunk:
            parameter.exclude_datasets += [
                one_iteration.mining_input_dataset_id
                for one_iteration in iterations
                if one_iteration.mining_input_dataset_id
            ]
        elif parameter.iteration_context.mining_strategy == MiningStrategy.dedup:
            parameter.exclude_datasets += [
                one_iteration.mining_output_dataset_id
                for one_iteration in iterations
                if one_iteration.mining_output_dataset_id
            ]
        parameter.exclude_datasets = list(set(parameter.exclude_datasets))
    return parameter
