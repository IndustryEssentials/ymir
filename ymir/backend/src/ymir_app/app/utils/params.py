from operator import attrgetter
from typing import Union

from sqlalchemy.orm import Session

from app import crud, schemas
from app.constants.state import MiningStrategy
from app.schemas.common import UniformParams
from app.schemas.dataset import MergeStrategy
from common_utils.labels import UserLabels


class IterationConversion:
    def __init__(
        self,
        db: Session,
        user_labels: UserLabels,
        parameter: Union[schemas.DatasetsFusionParameter],
    ):
        self.db = db
        self.parameter = parameter
        self.user_labels = user_labels

    def convert_iteration_fusion_parameter(self):
        if self.parameter.iteration_context.exclude_last_result:
            iterations = crud.iteration.get_multi_by_project(db=self.db, project_id=self.parameter.project_id)
            if self.parameter.iteration_context.mining_strategy == MiningStrategy.chunk:
                self.parameter.exclude_datasets += [
                    one_iteration.mining_input_dataset_id
                    for one_iteration in iterations
                    if one_iteration.mining_input_dataset_id
                ]
            elif self.parameter.iteration_context.mining_strategy == MiningStrategy.dedup:
                self.parameter.exclude_datasets += [
                    one_iteration.mining_output_dataset_id
                    for one_iteration in iterations
                    if one_iteration.mining_output_dataset_id
                ]

            self.parameter.exclude_datasets = list(set(self.parameter.exclude_datasets))

    def fusion_param_to_uniform(self) -> UniformParams:
        include_datasets_info = crud.dataset.get_multi_by_ids(
            self.db,
            ids=[self.parameter.main_dataset_id] + self.parameter.include_datasets,
        )

        include_datasets_info.sort(
            key=attrgetter("update_datetime"),
            reverse=(self.parameter.include_strategy == MergeStrategy.prefer_newest),
        )

        exclude_datasets_info = crud.dataset.get_multi_by_ids(self.db, ids=self.parameter.exclude_datasets)
        uniform_params = UniformParams(
            include_datasets=[dataset_info.hash for dataset_info in include_datasets_info],
            include_strategy=self.parameter.include_strategy,
            exclude_datasets=[dataset_info.hash for dataset_info in exclude_datasets_info],
            include_class_ids=self.user_labels.get_class_ids(names_or_aliases=self.parameter.include_labels),
            exclude_class_ids=self.user_labels.get_class_ids(names_or_aliases=self.parameter.exclude_labels),
            sampling_count=self.parameter.sampling_count,
        )

        return uniform_params

    def convert_parameter(self) -> UniformParams:
        # make a function mapping?
        if isinstance(self.parameter, schemas.DatasetsFusionParameter):
            self.convert_iteration_fusion_parameter()
            uniform_params = self.fusion_param_to_uniform()
        else:
            raise ValueError("input parameter error")

        return uniform_params

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
