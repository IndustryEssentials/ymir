from operator import attrgetter
from typing import Dict, Any

from sqlalchemy.orm import Session

from app import crud, schemas
from app.constants.state import MiningStrategy
from app.schemas.dataset import MergeStrategy
from common_utils.labels import UserLabels


class IterationConversion:
    # TODO(chao): add tmi task other parameter here
    def __init__(self, db: Session, user_labels: UserLabels, parameter: schemas.RequestParameterBase):
        self.db = db
        self.parameter = parameter
        self.user_labels = user_labels

    def convert_iteration_fusion_parameter(
        self, parameter: schemas.DatasetsFusionParameter
    ) -> schemas.DatasetsFusionParameter:
        if parameter.iteration_context and parameter.iteration_context.exclude_last_result:
            iterations = crud.iteration.get_multi_by_project(db=self.db, project_id=parameter.project_id)
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

    def fusion_param_to_uniform(self, parameter: schemas.DatasetsFusionParameter) -> Dict:
        include_datasets_info = crud.dataset.get_multi_by_ids(
            self.db,
            ids=[parameter.main_dataset_id] + parameter.include_datasets,
        )

        include_datasets_info.sort(
            key=attrgetter("update_datetime"),
            reverse=(parameter.include_strategy == MergeStrategy.prefer_newest),
        )

        exclude_datasets_info = crud.dataset.get_multi_by_ids(self.db, ids=parameter.exclude_datasets)
        uniform_params = dict(
            include_datasets=[dataset_info.hash for dataset_info in include_datasets_info],
            include_strategy=parameter.include_strategy,
            exclude_datasets=[dataset_info.hash for dataset_info in exclude_datasets_info],
            include_class_ids=self.user_labels.get_class_ids(names_or_aliases=parameter.include_labels),
            exclude_class_ids=self.user_labels.get_class_ids(names_or_aliases=parameter.exclude_labels),
            sampling_count=parameter.sampling_count,
        )

        return uniform_params

    def convert_parameter(self) -> Dict:
        if isinstance(self.parameter, schemas.DatasetsFusionParameter):
            updated_parameter = self.convert_iteration_fusion_parameter(self.parameter)
            parameter = self.fusion_param_to_uniform(updated_parameter)
        else:
            raise ValueError("input parameter error")

        return parameter

    def __enter__(self) -> "IterationConversion":
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        pass
